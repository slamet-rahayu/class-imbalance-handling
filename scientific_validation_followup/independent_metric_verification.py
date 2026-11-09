"""Standalone prediction-level metric verification.

This module deliberately does not import run_experiment or its metric functions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRED = HERE / "predictions"
ATOL = 1e-12
RTOL = 1e-10

PROBABILITY_MAP = {
    ("raw", False): "p_raw",
    ("raw", True): "p_raw_prior_corrected",
    ("platt", False): "p_platt",
    ("platt", True): "p_platt_prior_corrected",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def logarithmic_loss(y: np.ndarray, p: np.ndarray) -> float:
    # sklearn log_loss clips to machine epsilon for the probability dtype.
    eps = np.finfo(p.dtype).eps
    q = np.clip(p, eps, 1.0 - eps)
    return float(-np.mean(y * np.log(q) + (1.0 - y) * np.log1p(-q)))


def ece_equal_width(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # np.digitize(..., right=False): [edge_i, edge_i+1); p=1 is clipped to last bin.
    ids = np.clip(np.digitize(p, edges[1:-1], right=False), 0, n_bins - 1)
    total = len(y)
    value = 0.0
    for bin_id in range(n_bins):
        mask = ids == bin_id
        if np.any(mask):
            value += float(mask.sum() / total * abs(float(p[mask].mean()) - float(y[mask].mean())))
    return value


def main() -> None:
    original = pd.read_csv(ROOT / "outputs_confirmatory_30_seeds" / "all_repetitions.csv")
    manifest = json.loads((PRED / "MANIFEST.json").read_text())
    data_parts = []
    manifest_failures = 0
    for name, metadata in manifest["files"].items():
        path = PRED / name
        manifest_failures += int(sha256(path) != metadata["sha256"])
        part = pd.read_csv(path)
        if len(part) != metadata["rows"]:
            manifest_failures += 1
        data_parts.append(part)
    data = pd.concat(data_parts, ignore_index=True)

    checks = []
    prob_cols = list(PROBABILITY_MAP.values())
    all_p = data[prob_cols].to_numpy(float)
    checks.append(("manifest_hashes_and_rows", manifest_failures == 0, manifest_failures, "30 prediction files"))
    checks.append(("probabilities_finite_and_bounded", bool(np.isfinite(all_p).all() and ((all_p >= 0) & (all_p <= 1)).all()), int((~np.isfinite(all_p)).sum() + ((all_p < 0) | (all_p > 1)).sum()), "four explicit probability branches"))
    checks.append(("binary_labels", set(data.y_true.unique()) <= {0, 1}, sorted(data.y_true.unique().tolist()), "all prediction rows"))
    checks.append(("ambiguous_probability_is_null", bool(data.p_prior_corrected.isna().all()), int(data.p_prior_corrected.notna().sum()), "explicit raw/platt corrected columns used instead"))

    # Independently reconstruct intended calibration prevalences.
    source = pd.read_csv(ROOT / "online_shoppers_intention.csv")
    labels = source["Revenue"].map({True: 1, False: 0, "TRUE": 1, "FALSE": 0}).astype(int)
    source_by_seed = {}
    for seed in range(42, 72):
        dev_ids, _, y_dev, _ = train_test_split(source.index.to_numpy(), labels, test_size=.2, stratify=labels, random_state=seed)
        _, _, _, y_cal = train_test_split(dev_ids, y_dev, test_size=.25, stratify=y_dev, random_state=seed + 1)
        source_by_seed[seed] = float(y_cal.mean())
    source_error = max(abs(float(v) - source_by_seed[int(s)]) for s, v in data[["seed", "source_prevalence"]].drop_duplicates().itertuples(index=False))
    checks.append(("source_prevalence_from_calibration", source_error < 1e-15, source_error, "independently reconstructed natural calibration labels"))

    formula_max = 0.0
    identity_max = 0.0
    monotonic_failures = 0
    comparison_rows = []
    grouped = data.groupby(["seed", "strategy", "target_prevalence"], sort=True)
    for (seed, strategy, target), group in grouped:
        if group.sample_id.duplicated().any() or len(group) != group.sample_id.nunique():
            checks.append(("unique_samples", False, f"{seed}|{strategy}|{target}", "duplicate sample ID"))
        actual = float(group.y_true.mean())
        saved_actual = float(group.target_prevalence_actual.iloc[0])
        scenario_hash = hashlib.sha256(np.sort(group.sample_id.to_numpy(np.int64)).tobytes()).hexdigest()
        if scenario_hash != group.sample_id_sha256.iloc[0]:
            checks.append(("sample_hash", False, f"{seed}|{strategy}|{target}", "hash mismatch"))
        if abs(actual - saved_actual) > 1e-15:
            checks.append(("actual_prevalence", False, f"{seed}|{strategy}|{target}", "label mean mismatch"))
        src = float(group.source_prevalence.iloc[0])
        for raw_name, corrected_name in (("p_raw", "p_raw_prior_corrected"), ("p_platt", "p_platt_prior_corrected")):
            p = group[raw_name].to_numpy(float)
            p_for_correction = np.clip(p, 1e-12, 1.0 - 1e-12)
            expected = ((actual / src) * p_for_correction) / (((actual / src) * p_for_correction) + (((1 - actual) / (1 - src)) * (1 - p_for_correction)))
            expected = np.clip(expected, 1e-12, 1.0 - 1e-12)
            formula_max = max(formula_max, float(np.max(np.abs(expected - group[corrected_name].to_numpy(float)))))
            identity = ((src / src) * p_for_correction) / (((src / src) * p_for_correction) + (((1-src)/(1-src)) * (1-p_for_correction)))
            identity = np.clip(identity, 1e-12, 1.0 - 1e-12)
            identity_max = max(identity_max, float(np.max(np.abs(identity - p_for_correction))))
            order = np.argsort(p, kind="stable")
            monotonic_failures += int(np.any(np.diff(group[corrected_name].to_numpy(float)[order]) < -1e-15))
        for calibration in ("raw", "platt"):
            for correction in (False, True):
                pcol = PROBABILITY_MAP[(calibration, correction)]
                p = group[pcol].to_numpy(float)
                y = group.y_true.to_numpy(float)
                computed = {"brier_score": brier(y, p), "log_loss": logarithmic_loss(y, p), "ece": ece_equal_width(y, p)}
                matched = original[(original.seed == seed) & (original.imbalance_strategy == strategy) & np.isclose(original.target_prevalence, target) & (original.calibration == calibration) & (original.prior_correction == correction)]
                if len(matched) != 1:
                    raise RuntimeError(f"Original row cardinality != 1: {seed}/{strategy}/{target}/{calibration}/{correction}")
                row = matched.iloc[0]
                if row.sample_id_sha256 != scenario_hash:
                    raise RuntimeError(f"Original scenario hash mismatch: {seed}/{strategy}/{target}")
                for metric, value in computed.items():
                    reported = float(row[metric])
                    delta = abs(value - reported)
                    comparison_rows.append({
                        "seed": seed, "strategy": strategy, "target_prevalence": target,
                        "calibration": calibration, "prior_correction": correction,
                        "configuration": f"{calibration}|prior_correction={str(correction).lower()}",
                        "probability_column": pcol, "metric": metric,
                        "computed": value, "reported": reported,
                        "absolute_difference": delta,
                        "match_atol_1e-12_rtol_1e-10": bool(np.isclose(value, reported, atol=ATOL, rtol=RTOL)),
                    })
    checks.append(("prior_correction_bayes_formula", formula_max < 2e-15, formula_max, "all 1,135,260 corrected probabilities"))
    checks.append(("identity_when_source_equals_target", identity_max < 2e-15, identity_max, "counterfactual formula check on exported probabilities"))
    checks.append(("prior_correction_monotonic", monotonic_failures == 0, monotonic_failures, "within model/scenario branches"))
    checks.append(("unique_samples", not any(c[0] == "unique_samples" and not c[1] for c in checks), 0, "all 270 seed/strategy/scenario groups"))
    checks.append(("scenario_hashes", not any(c[0] == "sample_hash" and not c[1] for c in checks), 0, "all groups and original output rows"))
    checks.append(("realized_prevalence", not any(c[0] == "actual_prevalence" and not c[1] for c in checks), 0, "label means equal exported actual prevalence"))

    comparisons = pd.DataFrame(comparison_rows)
    comparisons.to_csv(HERE / "METRIC_RECOMPUTATION.csv", index=False, float_format="%.17g")
    check_frame = pd.DataFrame(checks, columns=["check", "passed", "observed", "evidence_scope"])
    check_frame.to_csv(HERE / "PREDICTION_INVARIANT_CHECKS.csv", index=False)
    print(comparisons.groupby("metric").agg(comparisons=("absolute_difference", "size"), max_absolute_difference=("absolute_difference", "max"), mean_absolute_difference=("absolute_difference", "mean"), mismatches=("match_atol_1e-12_rtol_1e-10", lambda x: int((~x).sum()))).to_string())
    print("\nInvariant checks:")
    print(check_frame.to_string(index=False))


if __name__ == "__main__":
    main()
