"""Observation-level instrumentation for the frozen commit.

The script imports only fitting/transformation helpers from an isolated Git archive.
It does not call or change the frozen evaluator and does not modify frozen outputs.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "isolated_source"
PREDICTIONS = HERE / "predictions"
sys.path.insert(0, str(SOURCE))

from run_experiment import (  # noqa: E402
    Config,
    apply_platt,
    fit_model,
    fit_platt_scaler,
    load_data,
    prior_correct,
    simulate_prior_shift,
    split_data,
)

SEEDS = tuple(range(42, 72))
PRIORS = (0.10, 0.155, 0.25)
STRATEGIES = ("baseline", "oversampling", "class_weight")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    PREDICTIONS.mkdir(parents=True, exist_ok=True)
    cfg = Config(
        data=SOURCE / "online_shoppers_intention.csv",
        output=HERE / "unused_frozen_output",
        prevalences=PRIORS,
        test_size=0.20,
        calibration_size=0.20,
        seeds=SEEDS,
        n_bins=10,
    )
    X, y = load_data(cfg.data)
    manifest = {"instrumentation": "wide probability bundle; no metric functions called", "source_commit": "2f448140cbdf5a593d1d182f26ef955d83cc717b", "files": {}}
    for seed in SEEDS:
        X_train, X_cal, X_test, y_train, y_cal, y_test = split_data(X, y, cfg, seed)
        source_prior = float(y_cal.mean())
        shifted = {prior: simulate_prior_shift(y_test, prior, seed + offset) for offset, prior in enumerate(PRIORS)}
        parts = []
        for strategy in STRATEGIES:
            model, _ = fit_model(X_train, y_train, strategy, seed)
            p_cal_raw = model.predict_proba(X_cal)[:, 1]
            p_test_raw = model.predict_proba(X_test)[:, 1]
            platt = fit_platt_scaler(p_cal_raw, y_cal)
            p_test_platt = apply_platt(platt, p_test_raw)
            for target_prior, positions in shifted.items():
                sample_ids = X_test.index.to_numpy()[positions].astype(np.int64)
                labels = y_test.iloc[positions].to_numpy(dtype=np.int8)
                actual = float(labels.mean())
                scenario_hash = hashlib.sha256(np.sort(sample_ids).astype(np.int64).tobytes()).hexdigest()
                raw = p_test_raw[positions]
                calibrated = p_test_platt[positions]
                parts.append(pd.DataFrame({
                    "seed": seed,
                    "strategy": strategy,
                    "target_prevalence": target_prior,
                    "configuration": "wide_probability_bundle",
                    "sample_id": sample_ids,
                    "y_true": labels,
                    "p_raw": raw,
                    "p_platt": calibrated,
                    "p_prior_corrected": np.nan,
                    "p_raw_prior_corrected": prior_correct(raw, source_prior, actual),
                    "p_platt_prior_corrected": prior_correct(calibrated, source_prior, actual),
                    "source_prevalence": source_prior,
                    "target_prevalence_actual": actual,
                    "sample_id_sha256": scenario_hash,
                }))
        result = pd.concat(parts, ignore_index=True)
        path = PREDICTIONS / f"seed_{seed}_predictions.csv.gz"
        result.to_csv(path, index=False, float_format="%.17g", compression={"method": "gzip", "compresslevel": 9, "mtime": 0})
        manifest["files"][path.name] = {"sha256": file_sha256(path), "rows": int(len(result))}
        print(f"seed={seed} rows={len(result)} sha256={manifest['files'][path.name]['sha256']}", flush=True)
    schema = {
        "format": "gzip-compressed CSV, one wide record per seed/strategy/scenario/sample",
        "primary_key": ["seed", "strategy", "target_prevalence", "sample_id"],
        "null_fields": {"p_prior_corrected": "Always null because the frozen implementation has two distinct corrected branches; use explicit raw/platt corrected fields."},
        "probability_mapping": {
            "raw + no correction": "p_raw",
            "raw + correction (naive_exploratory)": "p_raw_prior_corrected",
            "platt + no correction": "p_platt",
            "platt + correction (primary_prior_correction)": "p_platt_prior_corrected",
        },
        "sample_id": "Zero-based row index in the frozen CSV dataset.",
        "sample_id_sha256": "SHA-256 of sorted int64 sample IDs, matching frozen scenario audit semantics.",
    }
    schema_path = PREDICTIONS / "SCHEMA.json"
    schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    manifest["schema_sha256"] = file_sha256(schema_path)
    (PREDICTIONS / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
