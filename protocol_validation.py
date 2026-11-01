"""Hard execution gate for the frozen 30-seed confirmatory protocol."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class ProtocolValidationError(RuntimeError):
    """Raised when runtime state differs from the frozen confirmatory protocol."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"Tidak dapat membaca JSON {path}: {exc}") from exc


def runtime_config_from_experiment(cfg) -> dict:
    """Return the runtime-controlled subset that must exactly match the freeze."""
    return {
        "dataset": Path(cfg.data).name,
        "seeds": list(cfg.seeds),
        "prevalences": list(cfg.prevalences),
        "test_size": cfg.test_size,
        "calibration_size": cfg.calibration_size,
        "n_bins": cfg.n_bins,
    }


def validate_runtime_config(runtime: dict, protocol: dict) -> None:
    expected = {key: protocol[key] for key in runtime}
    if canonical_json_hash(runtime) != canonical_json_hash(expected):
        differences = {
            key: {"expected": expected.get(key), "observed": runtime.get(key)}
            for key in sorted(set(expected) | set(runtime))
            if expected.get(key) != runtime.get(key)
        }
        raise ProtocolValidationError(f"Konfigurasi runtime menyimpang dari freeze: {differences}")


def installed_dependency_versions(names: list[str]) -> dict[str, str]:
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ProtocolValidationError(f"Dependency tidak terpasang: {name}") from exc
    return versions


def validate_source_commit(repo_root: Path, source_commit: str) -> None:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{source_commit}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ProtocolValidationError(f"Source commit freeze tidak ditemukan: {source_commit}")


def validate_frozen_protocol(manifest_path: Path, runtime: dict) -> dict:
    manifest_path = manifest_path.resolve()
    repo_root = manifest_path.parent
    manifest = load_json(manifest_path)
    protocol_path = repo_root / manifest["protocol_file"]
    plan_path = repo_root / manifest["statistical_plan_file"]
    dataset_path = repo_root / manifest["dataset_file"]
    protocol = load_json(protocol_path)

    checks = {
        "protocol_hash": (canonical_json_hash(protocol), manifest["configuration_sha256"]),
        "plan_hash": (sha256_file(plan_path), manifest["statistical_plan_sha256"]),
        "dataset_hash": (sha256_file(dataset_path), manifest["dataset_sha256"]),
    }
    for label, (observed, expected) in checks.items():
        if observed != expected:
            raise ProtocolValidationError(
                f"{label} tidak cocok: expected={expected}, observed={observed}"
            )

    validate_runtime_config(runtime, protocol)
    dependencies = manifest["dependencies"]
    observed_dependencies = installed_dependency_versions(list(dependencies))
    if observed_dependencies != dependencies:
        raise ProtocolValidationError(
            f"Versi dependency berbeda: expected={dependencies}, observed={observed_dependencies}"
        )

    for relative_path, expected_hash in manifest["source_files"].items():
        observed_hash = sha256_file(repo_root / relative_path)
        if observed_hash != expected_hash:
            raise ProtocolValidationError(
                f"Source berubah: {relative_path}; expected={expected_hash}, observed={observed_hash}"
            )
    validate_source_commit(repo_root, manifest["source_commit"])
    return {
        "status": "PASS",
        "protocol_version": protocol["protocol_version"],
        "configuration_sha256": manifest["configuration_sha256"],
        "source_commit": manifest["source_commit"],
    }


def validate_confirmatory_results(results: pd.DataFrame, protocol: dict) -> dict:
    """Fail closed on non-finite metrics, incomplete pairs, hashes, or bad labels."""
    required = {
        "seed", "imbalance_strategy", "calibration", "target_prevalence",
        "prior_correction", "sample_id_sha256", "evaluation_path",
        "confirmatory_analysis", "target_prior_source", "brier_score",
    }
    missing = sorted(required - set(results.columns))
    if missing:
        raise ProtocolValidationError(f"Kolom hasil konfirmatori hilang: {missing}")
    if ((results.evaluation_path == protocol["excluded_evaluation_path"])
            & results.confirmatory_analysis).any():
        raise ProtocolValidationError("naive_exploratory tidak boleh berlabel confirmatory")
    if not (results.target_prior_source == protocol["target_prior_source"]).all():
        raise ProtocolValidationError("target_prior_source bukan oracle_simulator")

    expected_seeds = set(protocol["seeds"])
    checks = 0
    for strategy in protocol["imbalance_strategies"]:
        for prevalence in protocol["primary_prevalences"]:
            condition = results[
                (results.imbalance_strategy == strategy)
                & np.isclose(results.target_prevalence, prevalence)
                & (results.calibration == "platt")
            ]
            corrected = condition[
                condition.prior_correction
                & (condition.evaluation_path == protocol["primary_evaluation_path"])
            ]
            reference = condition[
                ~condition.prior_correction
                & (condition.evaluation_path == "reference_no_correction")
            ]
            for label, frame in (("corrected", corrected), ("reference", reference)):
                if len(frame) != len(expected_seeds) or set(frame.seed) != expected_seeds:
                    raise ProtocolValidationError(
                        f"Pasangan tidak lengkap {strategy}/{prevalence}/{label}"
                    )
                if frame.seed.duplicated().any():
                    raise ProtocolValidationError(
                        f"Seed duplikat {strategy}/{prevalence}/{label}"
                    )
                if not np.isfinite(frame[protocol["primary_metric"]]).all():
                    raise ProtocolValidationError(
                        f"Metrik non-finite {strategy}/{prevalence}/{label}"
                    )
            hashes_corrected = corrected.set_index("seed").sample_id_sha256.sort_index()
            hashes_reference = reference.set_index("seed").sample_id_sha256.sort_index()
            if not hashes_corrected.equals(hashes_reference):
                raise ProtocolValidationError(
                    f"Scenario hash berbeda dalam pasangan {strategy}/{prevalence}"
                )
            checks += 1
    if checks != protocol["primary_test"]["family_size"]:
        raise ProtocolValidationError("Jumlah primary contrast tidak sama dengan enam")
    return {"status": "PASS", "complete_primary_contrasts": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    args = parser.parse_args()
    runtime = load_json(args.runtime_config)
    print(json.dumps(validate_frozen_protocol(args.manifest, runtime), indent=2))


if __name__ == "__main__":
    main()

