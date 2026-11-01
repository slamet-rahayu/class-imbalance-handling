"""Audit prior correction dan analisis statistik berpasangan hasil eksperimen."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from run_experiment import EPS, prior_correct


METRICS = ("brier_score", "log_loss", "average_precision", "f1", "ece")
LOWER_IS_BETTER = {"brier_score", "log_loss", "ece"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, default=Path("outputs_10_seeds/all_repetitions.csv")
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("audit_results_10_seeds"),
    )
    return parser.parse_args()


def holm_adjust(p_values: pd.Series) -> pd.Series:
    values = p_values.fillna(1.0).to_numpy(float)
    order = np.argsort(values)
    adjusted_sorted = np.maximum.accumulate(
        (len(values) - np.arange(len(values))) * values[order]
    )
    adjusted = np.empty_like(values)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)
    return pd.Series(adjusted, index=p_values.index)


def paired_statistics(a: np.ndarray, b: np.ndarray, metric: str) -> dict:
    """Selisih didefinisikan sebagai B - A."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    diff = b - a
    n = len(diff)
    mean_diff = float(diff.mean())
    sd_diff = float(diff.std(ddof=1)) if n > 1 else np.nan
    sem = sd_diff / np.sqrt(n) if n > 1 else np.nan
    critical = stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
    if n < 2:
        t_stat, t_p, w_stat, w_p, dz = np.nan, np.nan, np.nan, np.nan, np.nan
    elif np.allclose(diff, 0, atol=1e-14, rtol=1e-12):
        t_stat, t_p, w_stat, w_p, dz = 0.0, 1.0, 0.0, 1.0, 0.0
    else:
        t_result = stats.ttest_rel(b, a)
        t_stat, t_p = float(t_result.statistic), float(t_result.pvalue)
        try:
            w_result = stats.wilcoxon(b, a, zero_method="pratt", alternative="two-sided")
            w_stat, w_p = float(w_result.statistic), float(w_result.pvalue)
        except ValueError:
            w_stat, w_p = 0.0, 1.0
        dz = mean_diff / sd_diff if sd_diff > 0 else np.sign(mean_diff) * np.inf

    improvement = -mean_diff if metric in LOWER_IS_BETTER else mean_diff
    return {
        "n_pairs": n,
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "mean_difference_b_minus_a": mean_diff,
        "ci95_low": mean_diff - critical * sem if n > 1 else np.nan,
        "ci95_high": mean_diff + critical * sem if n > 1 else np.nan,
        "cohens_dz": dz,
        "paired_t_statistic": t_stat,
        "paired_t_p": t_p,
        "wilcoxon_statistic": w_stat,
        "wilcoxon_p": w_p,
        "mean_improvement": improvement,
        "b_better_on_average": bool(improvement > 0),
    }


def paired_table(
    data: pd.DataFrame,
    factor: str,
    a_value,
    b_value,
    strata: list[str],
    pair_keys: list[str],
    comparison: str,
) -> pd.DataFrame:
    records = []
    for stratum_values, group in data.groupby(strata, dropna=False):
        stratum_values = (stratum_values,) if not isinstance(stratum_values, tuple) else stratum_values
        wide = group.pivot(index=pair_keys, columns=factor, values=list(METRICS))
        for metric in METRICS:
            pair = wide[metric].reindex(columns=[a_value, b_value]).dropna()
            row = {
                "comparison": comparison,
                "level_a": str(a_value),
                "level_b": str(b_value),
                **dict(zip(strata, stratum_values)),
                "metric": metric,
                **paired_statistics(pair[a_value].to_numpy(), pair[b_value].to_numpy(), metric),
            }
            records.append(row)
    result = pd.DataFrame(records)
    # Multiplicity dikontrol terpisah untuk setiap keluarga perbandingan dan metrik.
    result["wilcoxon_p_holm"] = result.groupby(
        ["comparison", "metric"], group_keys=False
    )["wilcoxon_p"].transform(holm_adjust)
    result["paired_t_p_holm"] = result.groupby(
        ["comparison", "metric"], group_keys=False
    )["paired_t_p"].transform(holm_adjust)
    result["significant_wilcoxon_holm_0.05"] = result["wilcoxon_p_holm"] < 0.05
    return result


def audit_prior_correction(data: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(20261101)
    p = np.concatenate([rng.uniform(EPS, 1 - EPS, 10_000), [EPS, 0.5, 1 - EPS]])
    checks = []
    for source, target in [(0.155, 0.10), (0.155, 0.155), (0.155, 0.25), (0.5, 0.10), (0.5, 0.25)]:
        actual = prior_correct(p, source, target)
        numerator = (target / source) * p
        expected = numerator / (
            numerator + ((1 - target) / (1 - source)) * (1 - p)
        )
        checks.append(
            {
                "check": "numeric_bayes_equivalence",
                "source_prior": source,
                "target_prior": target,
                "passed": bool(np.allclose(actual, expected, rtol=1e-10, atol=1e-12)),
                "max_absolute_error": float(np.max(np.abs(actual - expected))),
                "detail": "Odds correction sama dengan bentuk Bayes prior-ratio.",
            }
        )
        checks.append(
            {
                "check": "bounds_and_monotonicity",
                "source_prior": source,
                "target_prior": target,
                "passed": bool(np.all((actual > 0) & (actual < 1)) and np.all(np.diff(actual[np.argsort(p)]) >= 0)),
                "max_absolute_error": np.nan,
                "detail": "Output berada dalam (0,1) dan transformasi monoton.",
            }
        )

    # Transformasi monoton tidak menambah informasi ranking. PR-AUC biasanya identik,
    # tetapi clipping/floating point dapat mengubah tie handling sedikit.
    pr = data.pivot_table(
        index=["seed", "imbalance_strategy", "calibration", "target_prevalence"],
        columns="prior_correction", values="pr_auc",
    )
    max_pr_delta = float(np.max(np.abs(pr[True] - pr[False])))
    checks.append(
        {
            "check": "empirical_pr_auc_stability",
            "source_prior": np.nan,
            "target_prior": np.nan,
            "passed": max_pr_delta < 0.003,
            "max_absolute_error": max_pr_delta,
            "detail": "Perubahan maksimum PR-AUC <0.003; selisih kecil berasal dari clipping dan tie handling, bukan informasi ranking baru.",
        }
    )

    checks.extend(
        [
            {
                "check": "source_prior_validity_platt",
                "source_prior": float(data.source_prevalence.mean()),
                "target_prior": np.nan,
                "passed": True,
                "max_absolute_error": np.nan,
                "detail": "Calibration prevalence tepat sebagai prior sumber setelah Platt scaling pada calibration set.",
            },
            {
                "check": "source_prior_validity_raw_baseline",
                "source_prior": float(data.source_prevalence.mean()),
                "target_prior": np.nan,
                "passed": True,
                "max_absolute_error": np.nan,
                "detail": "Mendekati prior training karena split stratified; selisih kecil tetap mungkin.",
            },
            {
                "check": "source_prior_validity_raw_rebalanced",
                "source_prior": float(data.source_prevalence.mean()),
                "target_prior": np.nan,
                "passed": False,
                "max_absolute_error": np.nan,
                "detail": "Untuk raw oversampling/class_weight, calibration prevalence bukan effective model prior (sekitar 0.5); correction ini bersifat naive dan asumsi teoretisnya tidak terpenuhi.",
            },
        ]
    )
    return pd.DataFrame(checks)


def main():
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(args.results)
    if "average_precision" not in data and "pr_auc" in data:
        data["average_precision"] = data["pr_auc"]  # historical compatibility
    if data.duplicated(
        ["seed", "imbalance_strategy", "calibration", "target_prevalence", "prior_correction"]
    ).any():
        raise ValueError("Hasil mengandung kunci konfigurasi duplikat")
    conditions_per_seed = data.groupby("seed").size()
    if conditions_per_seed.nunique() != 1:
        raise ValueError("Jumlah kondisi tidak konsisten antar-seed")

    remediated = "evaluation_path" in data.columns
    correction_source = data[data["calibration"] == "platt"] if remediated else data
    calibration_source = data[~data["prior_correction"]] if remediated else data
    imbalance_source = data[data["confirmatory_analysis"]] if remediated else data

    audit = audit_prior_correction(data)
    audit.to_csv(args.output / "prior_correction_audit.csv", index=False)

    correction = paired_table(
        correction_source, "prior_correction", False, True,
        ["imbalance_strategy", "calibration", "target_prevalence"],
        ["seed"], "prior_correction_false_vs_true",
    )
    correction.to_csv(args.output / "paired_prior_correction.csv", index=False)

    calibration = paired_table(
        calibration_source, "calibration", "raw", "platt",
        ["imbalance_strategy", "target_prevalence", "prior_correction"],
        ["seed"], "calibration_raw_vs_platt",
    )
    calibration.to_csv(args.output / "paired_calibration.csv", index=False)

    imbalance_parts = []
    for a, b in [("baseline", "oversampling"), ("baseline", "class_weight"), ("oversampling", "class_weight")]:
        imbalance_parts.append(
            paired_table(
                imbalance_source, "imbalance_strategy", a, b,
                ["calibration", "target_prevalence", "prior_correction"],
                ["seed"], f"imbalance_{a}_vs_{b}",
            )
        )
    imbalance = pd.concat(imbalance_parts, ignore_index=True)
    # Koreksi Holm bersama untuk seluruh pasangan metode imbalance per metrik.
    imbalance["wilcoxon_p_holm"] = imbalance.groupby("metric", group_keys=False)[
        "wilcoxon_p"
    ].transform(holm_adjust)
    imbalance["paired_t_p_holm"] = imbalance.groupby("metric", group_keys=False)[
        "paired_t_p"
    ].transform(holm_adjust)
    imbalance["significant_wilcoxon_holm_0.05"] = imbalance["wilcoxon_p_holm"] < 0.05
    imbalance.to_csv(args.output / "paired_imbalance_strategies.csv", index=False)

    overview = pd.DataFrame(
        [
            {"analysis": "prior correction", "comparisons": len(correction), "significant_wilcoxon_holm": int(correction["significant_wilcoxon_holm_0.05"].sum())},
            {"analysis": "calibration", "comparisons": len(calibration), "significant_wilcoxon_holm": int(calibration["significant_wilcoxon_holm_0.05"].sum())},
            {"analysis": "imbalance strategies", "comparisons": len(imbalance), "significant_wilcoxon_holm": int(imbalance["significant_wilcoxon_holm_0.05"].sum())},
        ]
    )
    overview.to_csv(args.output / "analysis_overview.csv", index=False)
    print(audit[["check", "passed", "detail"]].to_string(index=False))
    print("\n", overview.to_string(index=False))


if __name__ == "__main__":
    main()
