"""Eksperimen class imbalance, calibration, dan class-prior shift.

Jalankan dengan: python run_experiment.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET = "Revenue"
IMBALANCE_STRATEGIES = ("baseline", "oversampling", "class_weight")
CALIBRATION_METHODS = ("raw", "platt")
EPS = 1e-12
PROJECT_VERSION = "stage1-remediation-v1"
DATASET_PROVENANCE = {
    "repository": "UCI Machine Learning Repository",
    "dataset_id": 468,
    "title": "Online Shoppers Purchasing Intention Dataset",
    "url": "https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset",
    "doi": "10.24432/C5F88Q",
    "license": "CC BY 4.0",
    "citation": "Sakar, C. & Kastro, Y. (2018). Online Shoppers Purchasing Intention Dataset.",
    "local_download_date": "not_recorded",
}


@dataclass(frozen=True)
class Config:
    data: Path
    output: Path
    prevalences: tuple[float, ...]
    test_size: float
    calibration_size: float
    seeds: tuple[int, ...]
    n_bins: int


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("online_shoppers_intention.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--prevalences", nargs="+", type=float, default=[0.10, 0.155, 0.25])
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--calibration-size", type=float, default=0.20)
    parser.add_argument(
        "--seeds", nargs="+", type=int, default=[42],
        help="Satu atau lebih seed pengulangan, misalnya --seeds 42 43 44",
    )
    parser.add_argument("--n-bins", type=int, default=10)
    args = parser.parse_args()

    if args.test_size + args.calibration_size >= 1:
        parser.error("test-size + calibration-size harus kurang dari 1")
    if any(not 0 < p < 1 for p in args.prevalences):
        parser.error("setiap prevalence harus berada di antara 0 dan 1")
    return Config(
        data=args.data,
        output=args.output,
        prevalences=tuple(args.prevalences),
        test_size=args.test_size,
        calibration_size=args.calibration_size,
        seeds=tuple(args.seeds),
        n_bins=args.n_bins,
    )


def load_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)
    if TARGET not in df.columns:
        raise ValueError(f"Kolom target {TARGET!r} tidak ditemukan")
    if df.isna().any().any():
        raise ValueError("Dataset mengandung missing value; tentukan strategi imputasi dahulu")

    y = df[TARGET].map({True: 1, False: 0, "TRUE": 1, "FALSE": 0})
    if y.isna().any():
        y = pd.to_numeric(df[TARGET], errors="coerce")
    if y.isna().any() or set(y.unique()) != {0, 1}:
        raise ValueError("Revenue harus berupa target biner TRUE/FALSE atau 0/1")
    return df.drop(columns=TARGET), y.astype(int)


def split_data(X, y, cfg: Config, seed: int):
    # Test dipisahkan dahulu; calibration diambil dari bagian development.
    X_dev, X_test, y_dev, y_test = train_test_split(
        X, y, test_size=cfg.test_size, stratify=y, random_state=seed
    )
    cal_fraction_of_dev = cfg.calibration_size / (1.0 - cfg.test_size)
    X_train, X_cal, y_train, y_cal = train_test_split(
        X_dev,
        y_dev,
        test_size=cal_fraction_of_dev,
        stratify=y_dev,
        random_state=seed + 1,
    )
    return X_train, X_cal, X_test, y_train, y_cal, y_test


def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric = [
        column for column in X.columns if pd.api.types.is_numeric_dtype(X[column].dtype)
    ]
    categorical = [column for column in X.columns if column not in numeric]
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )


def fit_model(X_train, y_train, strategy: str, seed: int) -> tuple[Pipeline, dict]:
    preprocessor = make_preprocessor(X_train)
    X_transformed = preprocessor.fit_transform(X_train)

    class_weight = "balanced" if strategy == "class_weight" else None
    if strategy == "oversampling":
        sampler = RandomOverSampler(random_state=seed)
        X_transformed, y_fit = sampler.fit_resample(X_transformed, y_train)
    else:
        y_fit = y_train

    model = LogisticRegression(
        class_weight=class_weight,
        max_iter=2000,
        solver="liblinear",
        random_state=seed,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(X_transformed, y_fit)
    convergence_warning = any(issubclass(item.category, ConvergenceWarning) for item in caught)

    before_counts = y_train.value_counts().reindex([0, 1], fill_value=0)
    after_counts = pd.Series(y_fit).value_counts().reindex([0, 1], fill_value=0)
    n_before = int(len(y_train))
    if strategy == "class_weight":
        weights = {
            "0": n_before / (2 * int(before_counts[0])),
            "1": n_before / (2 * int(before_counts[1])),
        }
    else:
        weights = {"0": 1.0, "1": 1.0}
    metadata = {
        "strategy": strategy,
        "train_n_before": n_before,
        "train_negative_before": int(before_counts[0]),
        "train_positive_before": int(before_counts[1]),
        "train_n_after": int(len(y_fit)),
        "train_negative_after": int(after_counts[0]),
        "train_positive_after": int(after_counts[1]),
        "train_prevalence_after": float(after_counts[1] / len(y_fit)),
        "class_weight_negative": weights["0"],
        "class_weight_positive": weights["1"],
        "base_n_iter": int(np.max(model.n_iter_)),
        "base_max_iter": int(model.max_iter),
        "base_converged": bool(not convergence_warning and np.max(model.n_iter_) < model.max_iter),
        "base_convergence_warning": convergence_warning,
    }

    # Pipeline dirakit dari komponen yang sudah fit supaya prediksi aman dan ringkas.
    return Pipeline([("preprocess", preprocessor), ("model", model)]), metadata


def fit_platt_scaler(probabilities: np.ndarray, y_cal: pd.Series) -> LogisticRegression:
    logits = np.log(np.clip(probabilities, EPS, 1 - EPS) / np.clip(1 - probabilities, EPS, 1))
    calibrator = LogisticRegression(solver="lbfgs", random_state=0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        calibrator.fit(logits.reshape(-1, 1), y_cal)
    calibrator._audit_convergence_warning = any(
        issubclass(item.category, ConvergenceWarning) for item in caught
    )
    return calibrator


def apply_platt(calibrator: LogisticRegression, probabilities: np.ndarray) -> np.ndarray:
    logits = np.log(np.clip(probabilities, EPS, 1 - EPS) / np.clip(1 - probabilities, EPS, 1))
    return calibrator.predict_proba(logits.reshape(-1, 1))[:, 1]


def simulate_prior_shift(y: pd.Series, target_prior: float, seed: int) -> np.ndarray:
    """Ambil subset terbesar yang sedekat mungkin dengan prevalensi target."""
    rng = np.random.default_rng(seed)
    y_array = np.asarray(y)
    positive = np.flatnonzero(y_array == 1)
    negative = np.flatnonzero(y_array == 0)
    max_n = min(len(positive) / target_prior, len(negative) / (1 - target_prior))
    total = max(2, int(np.floor(max_n)))
    n_positive = min(len(positive), max(1, int(round(total * target_prior))))
    n_negative = min(len(negative), max(1, total - n_positive))
    chosen = np.concatenate(
        [rng.choice(positive, n_positive, replace=False), rng.choice(negative, n_negative, replace=False)]
    )
    rng.shuffle(chosen)
    return chosen


def prior_correct(probabilities: np.ndarray, source_prior: float, target_prior: float) -> np.ndarray:
    """Saerens-style correction under pure prior probability shift."""
    p_input = np.asarray(probabilities, dtype=float)
    if not np.all(np.isfinite(p_input)):
        raise ValueError("probabilities harus seluruhnya finite")
    if np.any((p_input < 0) | (p_input > 1)):
        raise ValueError("probabilities harus berada pada interval [0, 1]")
    for name, prior in (("source_prior", source_prior), ("target_prior", target_prior)):
        if not np.isfinite(prior) or not 0 < prior < 1:
            raise ValueError(f"{name} harus finite dan berada pada interval terbuka (0, 1)")
    p = np.clip(p_input, EPS, 1 - EPS)
    odds = p / (1 - p)
    prior_odds_ratio = (target_prior / (1 - target_prior)) / (source_prior / (1 - source_prior))
    corrected_odds = odds * prior_odds_ratio
    return np.clip(corrected_odds / (1 + corrected_odds), EPS, 1 - EPS)


def verify_prior_correction(probabilities, source_prior: float, target_prior: float) -> None:
    """Validasi implementasi odds correction terhadap bentuk Bayes ekuivalen."""
    p = np.clip(np.asarray(probabilities), EPS, 1 - EPS)
    numerator = (target_prior / source_prior) * p
    denominator = numerator + ((1 - target_prior) / (1 - source_prior)) * (1 - p)
    expected = np.clip(numerator / denominator, EPS, 1 - EPS)
    actual = prior_correct(p, source_prior, target_prior)
    if not np.allclose(actual, expected, rtol=1e-10, atol=1e-12):
        raise AssertionError("Implementasi prior correction tidak ekuivalen dengan rumus Bayes")
    # Transformasi harus monoton sehingga ranking probabilitas tidak berubah.
    order = np.argsort(p)
    if np.any(np.diff(actual[order]) < -1e-12):
        raise AssertionError("Prior correction mengubah urutan/ranking probabilitas")


def calibration_bins(y_true, probabilities, n_bins: int):
    edges = np.linspace(0, 1, n_bins + 1)
    ids = np.clip(np.digitize(probabilities, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for bin_id in range(n_bins):
        mask = ids == bin_id
        if mask.any():
            rows.append((mask.sum(), probabilities[mask].mean(), y_true[mask].mean()))
    return rows


def expected_calibration_error(y_true, probabilities, n_bins: int) -> float:
    bins = calibration_bins(np.asarray(y_true), np.asarray(probabilities), n_bins)
    n = len(y_true)
    return float(sum(count / n * abs(confidence - frequency) for count, confidence, frequency in bins))


def evaluate(y_true, probabilities, n_bins: int) -> dict[str, float]:
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "brier_score": brier_score_loss(y_true, probabilities),
        "log_loss": log_loss(y_true, probabilities, labels=[0, 1]),
        "average_precision": average_precision_score(y_true, probabilities),
        # Alias hanya untuk kompatibilitas dengan artefak historis.
        "pr_auc": average_precision_score(y_true, probabilities),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "ece": expected_calibration_error(y_true, probabilities, n_bins),
        "mean_predicted_probability": float(np.mean(probabilities)),
    }


def save_plots(results: pd.DataFrame, curves: list[dict], output: Path) -> None:
    prevalences = sorted(results["target_prevalence"].unique())
    fig, axes = plt.subplots(
        len(IMBALANCE_STRATEGIES),
        len(prevalences),
        figsize=(5 * len(prevalences), 14),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    for ax, strategy, prevalence in zip(
        axes.flat,
        np.repeat(IMBALANCE_STRATEGIES, len(prevalences)),
        np.tile(prevalences, len(IMBALANCE_STRATEGIES)),
    ):
        selected = [c for c in curves if c["strategy"] == strategy and c["prevalence"] == prevalence]
        for curve in selected:
            bins = curve["bins"]
            ax.plot(
                [row[1] for row in bins],
                [row[2] for row in bins],
                marker="o",
                label=f'{curve["calibration"]}, correction={curve["correction"]}',
            )
        ax.plot([0, 1], [0, 1], "k--", linewidth=1)
        ax.set_title(f"{strategy} | prior={prevalence:.1%}")
        ax.grid(alpha=0.25)
    for ax in axes[-1, :]:
        ax.set_xlabel("Mean predicted probability")
    for ax in axes[:, 0]:
        ax.set_ylabel("Observed frequency")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(output / "reliability_diagrams.png", dpi=180)
    plt.close(fig)

    summary = results.groupby(["calibration", "prior_correction"])[["brier_score", "log_loss"]].mean()
    ax = summary.plot.bar(subplots=True, figsize=(10, 7), rot=0, legend=False, title=["Mean Brier score", "Mean log loss"])
    ax[-1].set_xlabel("Calibration, prior correction")
    plt.tight_layout()
    plt.savefig(output / "metric_summary.png", dpi=180)
    plt.close()


def run_repetition(cfg: Config, seed: int, output: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    output.mkdir(parents=True, exist_ok=True)
    X, y = load_data(cfg.data)
    X_train, X_cal, X_test, y_train, y_cal, y_test = split_data(X, y, cfg, seed)

    train_ids, cal_ids, test_ids = set(X_train.index), set(X_cal.index), set(X_test.index)
    if train_ids & cal_ids or train_ids & test_ids or cal_ids & test_ids:
        raise AssertionError(f"Data leakage terdeteksi pada split seed={seed}")
    if train_ids | cal_ids | test_ids != set(X.index):
        raise AssertionError(f"Split seed={seed} tidak mencakup seluruh observasi")

    split_summary = pd.DataFrame(
        [
            {"seed": seed, "split": "train", "n": len(y_train), "positive_prevalence": y_train.mean()},
            {"seed": seed, "split": "calibration", "n": len(y_cal), "positive_prevalence": y_cal.mean()},
            {"seed": seed, "split": "test_original", "n": len(y_test), "positive_prevalence": y_test.mean()},
        ]
    )
    split_summary.to_csv(output / "split_summary.csv", index=False)
    source_prior = float(y_cal.mean())
    records, curves = [], []
    # Setiap strategi harus dinilai pada observasi shifted test yang identik.
    shifted_indices = {
        target_prior: simulate_prior_shift(y_test, target_prior, seed + index)
        for index, target_prior in enumerate(cfg.prevalences)
    }
    audit_records = []
    scenario_metadata = {}
    for target_prior, positions in shifted_indices.items():
        original_ids = X_test.index.to_numpy()[positions]
        if len(np.unique(original_ids)) != len(original_ids):
            raise AssertionError("Duplikasi observasi terdeteksi dalam shifted test set")
        if not set(original_ids).issubset(test_ids):
            raise AssertionError("Shift sampling mengambil observasi di luar test set")
        audit_records.append(
            {
                "seed": seed,
                "target_prevalence": target_prior,
                "n_shifted_test": len(original_ids),
                "unique_observations": len(np.unique(original_ids)),
                "all_from_test": True,
                "sample_id_sha256": hashlib.sha256(
                    np.sort(original_ids).astype(np.int64).tobytes()
                ).hexdigest(),
                "n_positive": int(y_test.iloc[positions].sum()),
                "n_negative": int(len(positions) - y_test.iloc[positions].sum()),
                "n_total": int(len(positions)),
                "target_prior_source": "oracle_simulator",
            }
        )
        scenario_metadata[target_prior] = audit_records[-1]

    training_records = []
    for strategy in IMBALANCE_STRATEGIES:
        model, training_metadata = fit_model(X_train, y_train, strategy, seed)
        p_cal_raw = model.predict_proba(X_cal)[:, 1]
        p_test_raw = model.predict_proba(X_test)[:, 1]
        platt = fit_platt_scaler(p_cal_raw, y_cal)
        training_records.append(
            {
                "seed": seed,
                **training_metadata,
                "calibration_n": int(len(y_cal)),
                "calibration_negative": int((y_cal == 0).sum()),
                "calibration_positive": int((y_cal == 1).sum()),
                "platt_n_iter": int(np.max(platt.n_iter_)),
                "platt_max_iter": int(platt.max_iter),
                "platt_converged": bool(
                    not platt._audit_convergence_warning and np.max(platt.n_iter_) < platt.max_iter
                ),
                "platt_convergence_warning": bool(platt._audit_convergence_warning),
            }
        )
        probabilities_by_method = {
            "raw": p_test_raw,
            "platt": apply_platt(platt, p_test_raw),
        }

        for target_prior in cfg.prevalences:
            indices = shifted_indices[target_prior]
            y_shifted = y_test.iloc[indices].to_numpy()
            actual_prior = float(y_shifted.mean())

            for calibration_method in CALIBRATION_METHODS:
                base_probabilities = probabilities_by_method[calibration_method][indices]
                for correction in (False, True):
                    probabilities = (
                        prior_correct(base_probabilities, source_prior, actual_prior)
                        if correction
                        else base_probabilities
                    )
                    if correction:
                        verify_prior_correction(base_probabilities, source_prior, actual_prior)
                    if correction and calibration_method == "platt":
                        evaluation_path = "primary_prior_correction"
                        correction_validity = "calibrated_confirmatory"
                        confirmatory = True
                    elif correction:
                        evaluation_path = "naive_exploratory"
                        correction_validity = "naive_exploratory"
                        confirmatory = False
                    else:
                        evaluation_path = "reference_no_correction"
                        correction_validity = "not_applied"
                        confirmatory = True
                    scenario = scenario_metadata[target_prior]
                    record = {
                        "project_version": PROJECT_VERSION,
                        "seed": seed,
                        "imbalance_strategy": strategy,
                        "calibration": calibration_method,
                        "target_prevalence": target_prior,
                        "actual_prevalence": actual_prior,
                        "prior_correction": correction,
                        "n_test": len(indices),
                        "source_prevalence": source_prior,
                        "source_prior_basis": "natural_calibration_set",
                        "target_prior_source": "oracle_simulator",
                        "evaluation_path": evaluation_path,
                        "prior_correction_validity": correction_validity,
                        "confirmatory_analysis": confirmatory,
                        "n_positive": scenario["n_positive"],
                        "n_negative": scenario["n_negative"],
                        "sample_id_sha256": scenario["sample_id_sha256"],
                        **evaluate(y_shifted, probabilities, cfg.n_bins),
                    }
                    records.append(record)
                    curves.append(
                        {
                            "strategy": strategy,
                            "prevalence": target_prior,
                            "calibration": calibration_method,
                            "correction": correction,
                            "bins": calibration_bins(y_shifted, probabilities, cfg.n_bins),
                        }
                    )

    results = pd.DataFrame(records)
    audit = pd.DataFrame(audit_records)
    training = pd.DataFrame(training_records)
    results.to_csv(output / "experiment_results.csv", index=False)
    audit.to_csv(output / "leakage_audit.csv", index=False)
    training.to_csv(output / "training_metadata.csv", index=False)
    save_plots(results, curves, output)
    return (
        results,
        pd.concat([split_summary.assign(audit_type="split"), audit.assign(audit_type="shift")]),
        training,
    )


def aggregate_results(results: pd.DataFrame) -> pd.DataFrame:
    factors = [
        "imbalance_strategy", "calibration", "target_prevalence", "prior_correction"
    ]
    metrics = ["brier_score", "log_loss", "average_precision", "pr_auc", "f1", "ece", "mean_predicted_probability"]
    summary = results.groupby(factors, as_index=False)[metrics].agg(["mean", "std", "count"])
    summary.columns = [
        "_".join(column).rstrip("_") if isinstance(column, tuple) else column
        for column in summary.columns
    ]
    for metric in metrics:
        summary[f"{metric}_ci95"] = 1.96 * summary[f"{metric}_std"] / np.sqrt(summary[f"{metric}_count"])
    return summary


def run(cfg: Config) -> pd.DataFrame:
    cfg.output.mkdir(parents=True, exist_ok=True)
    all_results, all_audits, all_training = [], [], []
    dataset_bytes = cfg.data.read_bytes()
    dataset_manifest = {
        "project_version": PROJECT_VERSION,
        **DATASET_PROVENANCE,
        "local_path": str(cfg.data),
        "local_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
        "local_size_bytes": len(dataset_bytes),
    }
    (cfg.output / "dataset_provenance.json").write_text(
        json.dumps(dataset_manifest, indent=2) + "\n", encoding="utf-8"
    )
    repetitions_dir = cfg.output / "repetitions"
    for seed in cfg.seeds:
        print(f"Menjalankan seed {seed} ...")
        results, audit, training = run_repetition(cfg, seed, repetitions_dir / f"seed_{seed}")
        all_results.append(results)
        all_audits.append(audit)
        all_training.append(training)

    combined = pd.concat(all_results, ignore_index=True)
    combined.to_csv(cfg.output / "all_repetitions.csv", index=False)
    aggregate_results(combined).to_csv(cfg.output / "aggregate_summary.csv", index=False)
    pd.concat(all_audits, ignore_index=True).to_csv(cfg.output / "all_audits.csv", index=False)
    pd.concat(all_training, ignore_index=True).to_csv(
        cfg.output / "training_metadata.csv", index=False
    )
    return combined


if __name__ == "__main__":
    configuration = parse_args()
    experiment_results = run(configuration)
    print(
        f"Selesai: {len(configuration.seeds)} seed dan "
        f"{len(experiment_results)} baris kombinasi dievaluasi"
    )
    print(f"Hasil tersimpan di: {configuration.output.resolve()}")
    print(experiment_results.sort_values("brier_score").head(10).to_string(index=False))
