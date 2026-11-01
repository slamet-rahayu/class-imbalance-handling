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
    """Return every effective scientific/statistical setting used by the code."""
    from run_experiment import effective_runtime_config

    return effective_runtime_config(cfg)


def validate_runtime_config(runtime: dict, protocol: dict) -> None:
    expected = protocol.get("effective_config", protocol)
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
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ProtocolValidationError("Git HEAD tidak dapat dibaca")
    active_head = result.stdout.strip()
    if active_head != source_commit:
        raise ProtocolValidationError(
            f"Git HEAD berbeda dari freeze: expected={source_commit}, observed={active_head}"
        )


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
    effective = protocol.get("effective_config", protocol)
    required = {
        "seed", "imbalance_strategy", "calibration", "target_prevalence",
        "prior_correction", "sample_id_sha256", "evaluation_path",
        "confirmatory_analysis", "target_prior_source", "source_prior_basis",
        "prior_correction_validity", "project_version", "n_test", "n_positive",
        "n_negative", *effective["metric_ranges"].keys(),
    }
    missing = sorted(required - set(results.columns))
    if missing:
        raise ProtocolValidationError(f"Kolom hasil konfirmatori hilang: {missing}")
    numeric_columns = list(effective["metric_ranges"])
    if not np.isfinite(results[numeric_columns].to_numpy(dtype=float)).all():
        raise ProtocolValidationError("Satu atau lebih metrik numerik non-finite")
    for metric, (lower, upper) in effective["metric_ranges"].items():
        values = results[metric].to_numpy(dtype=float)
        if np.any(values < lower) or (upper is not None and np.any(values > upper)):
            raise ProtocolValidationError(f"Metrik di luar rentang: {metric}")
    if not np.allclose(results["average_precision"], results["pr_auc"], rtol=0, atol=1e-15):
        raise ProtocolValidationError("Alias pr_auc tidak identik dengan average_precision")
    if (results.n_test <= 0).any() or (results.n_positive < 0).any() or (results.n_negative < 0).any():
        raise ProtocolValidationError("Metadata jumlah sampel tidak valid")
    if not (results.n_positive + results.n_negative == results.n_test).all():
        raise ProtocolValidationError("n_positive + n_negative tidak sama dengan n_test")
    if not (results.source_prior_basis == effective["source_prior_basis"]).all():
        raise ProtocolValidationError("source_prior_basis tidak sesuai protokol")

    corrected = results.prior_correction.astype(bool)
    uncorrected = ~corrected
    if not (results.loc[corrected, "target_prior_source"] == effective["corrected_target_prior_source"]).all():
        raise ProtocolValidationError("Corrected rows wajib memakai oracle_simulator")
    if not (results.loc[uncorrected, "target_prior_source"] == effective["uncorrected_target_prior_source"]).all():
        raise ProtocolValidationError("Uncorrected rows wajib memakai target_prior_source=not_applied")

    expected_primary = corrected & (results.calibration == "platt")
    expected_naive = corrected & (results.calibration == "raw")
    expected_reference = uncorrected
    if not (results.loc[expected_primary, "evaluation_path"] == effective["primary_evaluation_path"]).all():
        raise ProtocolValidationError("Platt corrected memiliki evaluation_path salah")
    if not (results.loc[expected_naive, "evaluation_path"] == effective["excluded_evaluation_path"]).all():
        raise ProtocolValidationError("Raw corrected harus naive_exploratory")
    if not (results.loc[expected_reference, "evaluation_path"] == "reference_no_correction").all():
        raise ProtocolValidationError("Uncorrected rows harus reference_no_correction")
    if not (results.loc[expected_primary, "prior_correction_validity"] == "calibrated_confirmatory").all():
        raise ProtocolValidationError("Validity metadata Platt corrected salah")
    if not (results.loc[expected_naive, "prior_correction_validity"] == "naive_exploratory").all():
        raise ProtocolValidationError("Validity metadata raw corrected salah")
    if not (results.loc[expected_reference, "prior_correction_validity"] == "not_applied").all():
        raise ProtocolValidationError("Validity metadata uncorrected salah")
    if not results.loc[expected_primary | expected_reference, "confirmatory_analysis"].all():
        raise ProtocolValidationError("Jalur valid tidak berlabel confirmatory")
    if results.loc[expected_naive, "confirmatory_analysis"].any():
        raise ProtocolValidationError("naive_exploratory tidak boleh berlabel confirmatory")

    if ((results.evaluation_path == effective["excluded_evaluation_path"])
            & results.confirmatory_analysis).any():
        raise ProtocolValidationError("naive_exploratory tidak boleh berlabel confirmatory")

    expected_seeds = set(effective["seeds"])
    checks = 0
    for strategy in effective["imbalance_strategies"]:
        for prevalence in effective["primary_prevalences"]:
            condition = results[
                (results.imbalance_strategy == strategy)
                & np.isclose(results.target_prevalence, prevalence)
                & (results.calibration == "platt")
            ]
            corrected = condition[
                condition.prior_correction
                & (condition.evaluation_path == effective["primary_evaluation_path"])
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
                if not np.isfinite(frame[effective["primary_metric"]]).all():
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
    if checks != effective["primary_test"]["family_size"]:
        raise ProtocolValidationError("Jumlah primary contrast tidak sama dengan enam")
    return {"status": "PASS", "complete_primary_contrasts": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    args = parser.parse_args()
    runtime_document = load_json(args.runtime_config)
    runtime = runtime_document.get("effective_config", runtime_document)
    print(json.dumps(validate_frozen_protocol(args.manifest, runtime), indent=2))


if __name__ == "__main__":
    main()

