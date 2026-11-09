"""Independent, read-only audit of confirmatory-30seed-v2.

This script does not import project modules. It writes only the requested audit CSV.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs_confirmatory_30_seeds"
RESULTS = OUT / "all_repetitions.csv"
METRICS = ("brier_score", "log_loss", "average_precision", "f1", "ece")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def holm(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, float)
    order = np.argsort(values, kind="stable")
    ordered = values[order]
    adjusted_ordered = np.minimum(1.0, np.maximum.accumulate((len(values) - np.arange(len(values))) * ordered))
    adjusted = np.empty_like(values)
    adjusted[order] = adjusted_ordered
    return adjusted


def wilcoxon(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    d = np.asarray(b, float) - np.asarray(a, float)
    if np.all(d == 0):
        return 0.0, 1.0
    r = stats.wilcoxon(d, zero_method="pratt", alternative="two-sided", method="approx", correction=False)
    return float(r.statistic), float(r.pvalue)


def main() -> None:
    rows: list[dict] = []
    data = pd.read_csv(RESULTS)
    reported_h3 = pd.read_csv(OUT / "statistical_analysis" / "confirmatory_h3_primary.csv")

    # Integrity manifest: exclude output_hashes.json itself (not listed by design).
    manifest = json.loads((OUT / "output_hashes.json").read_text())
    mismatches = [(p, expected, sha(OUT / p)) for p, expected in manifest["files"].items() if sha(OUT / p) != expected]
    rows.append({"requirement": 1, "check": "frozen_output_hash_manifest", "status": "PASS" if not mismatches else "FAIL", "group": "all", "metric": "sha256", "computed": len(mismatches), "reported": 0, "absolute_difference": len(mismatches), "detail": f"Checked {len(manifest['files'])} listed files; mismatches={len(mismatches)}"})

    # Reconstruct every split and shifted sample independently from dataset labels.
    source = pd.read_csv(ROOT / "online_shoppers_intention.csv")
    y = source["Revenue"].map({True: 1, False: 0, "TRUE": 1, "FALSE": 0}).astype(int)
    audits = pd.read_csv(OUT / "all_audits.csv")
    reconstructed = []
    for seed in range(42, 72):
        dev_idx, test_idx, y_dev, y_test = train_test_split(source.index.to_numpy(), y, test_size=.2, stratify=y, random_state=seed)
        train_idx, cal_idx, y_train, y_cal = train_test_split(dev_idx, y_dev, test_size=.25, stratify=y_dev, random_state=seed + 1)
        reconstructed.append((seed, "split_disjoint", len(set(train_idx)&set(cal_idx)) + len(set(train_idx)&set(test_idx)) + len(set(cal_idx)&set(test_idx)), 0))
        for offset, prior in enumerate((.1, .155, .25)):
            rng = np.random.default_rng(seed + offset)
            ya = np.asarray(y_test)
            pos, neg = np.flatnonzero(ya == 1), np.flatnonzero(ya == 0)
            total = max(2, int(np.floor(min(len(pos)/prior, len(neg)/(1-prior)))))
            npos = min(len(pos), max(1, int(round(total*prior))))
            nneg = min(len(neg), max(1, total-npos))
            chosen = np.concatenate([rng.choice(pos, npos, replace=False), rng.choice(neg, nneg, replace=False)])
            rng.shuffle(chosen)
            ids = test_idx[chosen]
            digest = hashlib.sha256(np.sort(ids).astype(np.int64).tobytes()).hexdigest()
            observed = audits[(audits.seed == seed) & (audits.audit_type == "shift") & np.isclose(audits.target_prevalence, prior)].iloc[0]
            ok = digest == observed.sample_id_sha256 and len(np.unique(ids)) == len(ids) and int(ya[chosen].sum()) == int(observed.n_positive) and len(ids)-int(ya[chosen].sum()) == int(observed.n_negative)
            reconstructed.append((seed, f"shift_{prior}", int(ok), 1))
    failed = sum(a != b for _, _, a, b in reconstructed)
    rows.append({"requirement": 2, "check": "independent_split_reconstruction", "status": "PASS" if failed == 0 else "FAIL", "group": "30 seeds", "metric": "failed_checks", "computed": failed, "reported": 0, "absolute_difference": failed, "detail": "Reconstructed train/cal/test indices using frozen split algorithm."})
    rows.append({"requirement": 6, "check": "independent_shift_reconstruction", "status": "PASS" if failed == 0 else "FAIL", "group": "90 scenarios", "metric": "failed_checks", "computed": failed, "reported": 0, "absolute_difference": failed, "detail": "Recomputed no-replacement class-stratified samples, counts, and sample hashes."})

    # Manual Bayes prior correction cases, without calling project code.
    cases = [(0.2, .155, .1, 0.13151750972762646), (0.5, .155, .25, 0.6450381679389313), (0.8, .5, .25, 0.5714285714285715)]
    maxerr = 0.0
    for p, src, tgt, expected in cases:
        got = ((tgt/src)*p) / (((tgt/src)*p) + (((1-tgt)/(1-src))*(1-p)))
        maxerr = max(maxerr, abs(got-expected))
    rows.append({"requirement": 5, "check": "manual_bayes_prior_correction", "status": "PASS" if maxerr < 1e-15 else "FAIL", "group": "3 hand-calculated cases", "metric": "max_absolute_error", "computed": maxerr, "reported": 0, "absolute_difference": maxerr, "detail": "Used Bayes prior-ratio equation independently."})

    # Six H3 tests and one Holm family.
    h3_rows = []
    for strategy in ("baseline", "oversampling", "class_weight"):
        for prevalence in (.1, .25):
            g = data[(data.imbalance_strategy == strategy) & (data.calibration == "platt") & np.isclose(data.target_prevalence, prevalence)]
            wide = g.pivot(index=["seed", "sample_id_sha256"], columns="prior_correction", values="brier_score").sort_index()
            stat, p = wilcoxon(wide[False].to_numpy(), wide[True].to_numpy())
            d = wide[True].to_numpy() - wide[False].to_numpy()
            h3_rows.append((strategy, prevalence, len(d), d.mean(), stat, p))
    adj = holm(np.array([x[5] for x in h3_rows]))
    for (strategy, prevalence, n, mean_d, stat, p), p_adj in zip(h3_rows, adj):
        rep = reported_h3[(reported_h3.imbalance_strategy == strategy) & np.isclose(reported_h3.target_prevalence, prevalence)].iloc[0]
        for metric, got, expected in (("mean_difference", mean_d, rep.mean_difference_corrected_minus_uncorrected), ("wilcoxon_statistic", stat, rep.wilcoxon_statistic), ("wilcoxon_p_raw", p, rep.wilcoxon_p_raw), ("wilcoxon_p_holm", p_adj, rep.wilcoxon_p_holm)):
            delta = abs(float(got)-float(expected))
            rows.append({"requirement": 8, "check": "H3_independent_recomputation", "status": "PASS" if delta < 1e-14 else "FAIL", "group": f"{strategy}|{prevalence}", "metric": metric, "computed": got, "reported": expected, "absolute_difference": delta, "detail": f"n_pairs={n}; Pratt/approx/two-sided/no continuity correction"})

    # Independently recompute H1/H2 raw Wilcoxon values and their declared Holm families.
    for filename, req in (("secondary_h1_imbalance.csv", 9), ("secondary_h2_calibration.csv", 9)):
        report = pd.read_csv(OUT / "statistical_analysis" / filename)
        raw_p = []
        computed = []
        for _, row in report.iterrows():
            if req == 9 and filename.startswith("secondary_h1"):
                g = data[(data.calibration == row.calibration) & np.isclose(data.target_prevalence, row.target_prevalence) & (data.prior_correction == bool(row.prior_correction))]
                w = g.pivot(index=["seed", "sample_id_sha256"], columns="imbalance_strategy", values=row.metric)
            else:
                g = data[(data.imbalance_strategy == row.imbalance_strategy) & np.isclose(data.target_prevalence, row.target_prevalence) & (data.prior_correction == bool(row.prior_correction))]
                w = g.pivot(index=["seed", "sample_id_sha256"], columns="calibration", values=row.metric)
            d = w[row.level_b].to_numpy() - w[row.level_a].to_numpy()
            if np.all(d == 0):
                stat, p = 0.0, 1.0
            else:
                rr = stats.wilcoxon(d, zero_method="pratt", alternative="two-sided")
                stat, p = float(rr.statistic), float(rr.pvalue)
            computed.append((stat, p)); raw_p.append(p)
        # Published families are per metric (H1 27 tests/metric; H2 9 tests/metric).
        calc_adj = np.empty(len(report))
        for metric in METRICS:
            ix = np.flatnonzero(report.metric.to_numpy() == metric)
            calc_adj[ix] = holm(np.asarray(raw_p)[ix])
        worst = max(max(abs(computed[i][0]-report.iloc[i].wilcoxon_statistic), abs(computed[i][1]-report.iloc[i].wilcoxon_p), abs(calc_adj[i]-report.iloc[i].wilcoxon_p_holm)) for i in range(len(report)))
        rows.append({"requirement": 9, "check": filename.replace(".csv", ""), "status": "PASS" if worst < 1e-14 else "FAIL", "group": f"{len(report)} rows", "metric": "max_absolute_difference", "computed": worst, "reported": 0, "absolute_difference": worst, "detail": "Recomputed pair construction, scipy auto-method Pratt Wilcoxon, and Holm within each metric family."})

    pd.DataFrame(rows).to_csv(ROOT / "INDEPENDENT_RECOMPUTATION.csv", index=False)


if __name__ == "__main__":
    main()
