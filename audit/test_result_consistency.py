import hashlib
import itertools
import json

import numpy as np
import pandas as pd
from scipy.special import expit, logit

import run_experiment as experiment
from conftest import OUTPUTS, PREDICTIONS, PRIORS, ROOT, SEEDS, indexed_by
from test_metrics import reference_metrics


STRATEGIES = ("baseline", "oversampling", "class_weight")
CONDITIONS = ["imbalance_strategy", "calibration", "target_prevalence", "prior_correction"]
KEY = ["seed", *CONDITIONS]
METRICS = ["brier_score", "log_loss", "ece"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_archives_match_recorded_hashes(config):
    manifest = json.loads((OUTPUTS / "output_hashes.json").read_text())
    assert len(manifest["files"]) == manifest["file_count"] == 198
    for name, expected in manifest["files"].items():
        assert sha256(OUTPUTS / name) == expected, name
    run = json.loads((OUTPUTS / "execution_manifest.json").read_text())
    assert sha256(config.data) == run["dataset_sha256"]
    prediction_manifest = json.loads((PREDICTIONS / "MANIFEST.json").read_text())
    assert prediction_manifest["source_commit"] == run["source_commit"]
    # The tracked schema may have Git's CRLF checkout conversion. The manifest uses LF.
    schema = (PREDICTIONS / "SCHEMA.json").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(schema).hexdigest() == prediction_manifest["schema_sha256"]
    assert set(prediction_manifest["files"]) == {f"seed_{seed}_predictions.csv.gz" for seed in SEEDS}
    for name, expected in prediction_manifest["files"].items():
        assert sha256(PREDICTIONS / name) == expected["sha256"], name


def test_per_seed_exports_and_all_aggregate_columns(results):
    expected_keys = set(itertools.product(SEEDS, STRATEGIES, ("raw", "platt"), PRIORS, (False, True)))
    combined = indexed_by(results, KEY).sort_index()
    assert set(combined.index) == expected_keys
    per_seed = pd.concat([
        pd.read_csv(OUTPUTS / "repetitions" / f"seed_{seed}" / "experiment_results.csv")
        for seed in SEEDS
    ])
    per_seed = indexed_by(per_seed, KEY).sort_index()
    pd.testing.assert_frame_equal(combined, per_seed)

    exported = pd.read_csv(OUTPUTS / "aggregate_summary.csv").set_index(CONDITIONS).sort_index()
    produced = experiment.aggregate_results(results).set_index(CONDITIONS).sort_index()
    pd.testing.assert_frame_equal(exported, produced, rtol=0, atol=1e-14)
    groups = results.groupby(CONDITIONS)
    for field in ("brier_score", "log_loss", "ece", "average_precision", "pr_auc", "f1",
                  "mean_predicted_probability"):
        manual = groups[field].agg(["mean", "std", "count"]).sort_index()
        assert manual["count"].eq(30).all()
        manual["ci95"] = 1.96 * manual["std"] / np.sqrt(manual["count"])
        for statistic in manual.columns:
            np.testing.assert_allclose(exported[f"{field}_{statistic}"], manual[statistic], atol=1e-14)


def test_prediction_rows_reconstruct_metrics_and_oracle_correction(results, dataset, splits):
    X, y = dataset
    keys = pd.Series(list(X.itertuples(index=False, name=None)), index=X.index)
    indexed = indexed_by(results, KEY)
    path = ROOT / "cross-partition-duplicate-audit-570066kd" / "evaluation_exclusion_by_seed.csv"
    exclusions = indexed_by(pd.read_csv(path), ["seed", "strategy", "calibration"])
    variants = {
        ("raw", False): "p_raw", ("platt", False): "p_platt",
        ("raw", True): "p_raw_prior_corrected", ("platt", True): "p_platt_prior_corrected",
    }
    checked = 0
    for seed in SEEDS:
        train, cal, test, _, y_cal, _ = splits[seed]
        source = y_cal.mean()
        train_cal_keys = set(keys.loc[train.index.union(cal.index)])
        predictions = pd.read_csv(PREDICTIONS / f"seed_{seed}_predictions.csv.gz")
        assert len(predictions) == 18921
        assert predictions.seed.eq(seed).all()
        groups = predictions.groupby(["strategy", "target_prevalence"])
        assert set(groups.groups) == set(itertools.product(STRATEGIES, PRIORS))
        reference_ids = {}
        for (strategy, target), rows in groups:
            ids = rows.sample_id.to_numpy()
            assert rows.sample_id.is_unique
            assert rows.sample_id.isin(test.index).all()
            np.testing.assert_array_equal(np.sort(ids), reference_ids.setdefault(target, np.sort(ids)))
            labels = rows.y_true.to_numpy()
            np.testing.assert_array_equal(labels, y.loc[ids])
            realized = labels.mean()
            digest = hashlib.sha256(np.sort(ids).astype("<i8").tobytes()).hexdigest()
            assert rows.sample_id_sha256.eq(digest).all()
            np.testing.assert_allclose(rows.source_prevalence, source, rtol=0, atol=1e-15)
            np.testing.assert_allclose(rows.target_prevalence_actual, realized, rtol=0, atol=1e-15)
            for (calibration, correction), name in variants.items():
                row = indexed.loc[(seed, strategy, calibration, target, correction)]
                p = rows[name].to_numpy()
                assert np.all(np.isfinite(p) & (0 <= p) & (p <= 1))
                assert row.sample_id_sha256 == digest
                assert row.n_test == len(labels)
                np.testing.assert_allclose([row.source_prevalence, row.actual_prevalence],
                                           [source, realized], rtol=0, atol=1e-15)
                if correction:
                    base = rows[f"p_{calibration}"].to_numpy()
                    expected = expit(logit(np.clip(base, 1e-12, 1 - 1e-12)) + logit(realized) - logit(source))
                    np.testing.assert_allclose(p, np.clip(expected, 1e-12, 1 - 1e-12), rtol=0, atol=1e-14)
                    assert row.target_prior_source == "oracle_simulator"
                    assert row.evaluation_path == (
                        "primary_prior_correction" if calibration == "platt" else "naive_exploratory"
                    )
                else:
                    assert row.target_prior_source == "not_applied"
                metrics = reference_metrics(labels, p)
                np.testing.assert_allclose(metrics, row[METRICS].to_numpy(dtype=float), rtol=0, atol=1e-11)
                checked += len(metrics)
                if target == 0.155 and not correction:
                    keep = ~keys.loc[ids].isin(train_cal_keys).to_numpy()
                    excluded = reference_metrics(labels[keep], p[keep])
                    recorded = exclusions.loc[seed, strategy, calibration]
                    np.testing.assert_allclose(
                        [metrics[0], excluded[0], metrics[1], excluded[1]],
                        recorded[["brier_all", "brier_unexposed", "logloss_all", "logloss_unexposed"]],
                        rtol=0, atol=1e-11,
                    )
    assert checked == 3240


def test_manuscript_table_2_displayed_precision(results):
    expected = {
        ("baseline", "raw"): [0.08550, 0.00233, 0.29459, 0.00985, 0.03797, 0.00613],
        ("baseline", "platt"): [0.08572, 0.00253, 0.29495, 0.00995, 0.03849, 0.00736],
        ("oversampling", "raw"): [0.12061, 0.00329, 0.44261, 0.01565, 0.18043, 0.00629],
        ("oversampling", "platt"): [0.08573, 0.00250, 0.29638, 0.01005, 0.04692, 0.00757],
        ("class_weight", "raw"): [0.12063, 0.00309, 0.44260, 0.01528, 0.18102, 0.00569],
        ("class_weight", "platt"): [0.08568, 0.00253, 0.29620, 0.01006, 0.04723, 0.00754],
    }
    reference = results.query("target_prevalence == 0.155 and not prior_correction")
    for key, group in reference.groupby(["imbalance_strategy", "calibration"]):
        actual = group[METRICS].agg(["mean", "std"]).to_numpy().T.ravel()
        np.testing.assert_array_equal(np.round(actual, 5), expected[key])


def test_manuscript_tables_3_and_4_displayed_precision(results):
    expected_brier = {
        (0.10, "baseline"): [0.064756, 0.064748, -0.000008, 0.000648, 16],
        (0.10, "oversampling"): [0.064694, 0.064996, 0.000303, 0.000601, 11],
        (0.10, "class_weight"): [0.064666, 0.064975, 0.000309, 0.000611, 11],
        (0.25, "baseline"): [0.122106, 0.111718, -0.010388, 0.001415, 30],
        (0.25, "oversampling"): [0.122199, 0.111141, -0.011059, 0.001308, 30],
        (0.25, "class_weight"): [0.122125, 0.111037, -0.011088, 0.001317, 30],
    }
    expected_secondary = {
        (0.10, "baseline"): [0.240310, 0.231922, 0.043837, 0.029888],
        (0.10, "oversampling"): [0.242335, 0.233898, 0.048156, 0.034329],
        (0.10, "class_weight"): [0.242252, 0.233826, 0.048042, 0.034716],
        (0.25, "baseline"): [0.390702, 0.371397, 0.075469, 0.052095],
        (0.25, "oversampling"): [0.391188, 0.371988, 0.081865, 0.064395],
        (0.25, "class_weight"): [0.390905, 0.371695, 0.082328, 0.064104],
    }
    shifted = results.query("calibration == 'platt' and target_prevalence != 0.155")
    for key, group in shifted.groupby(["target_prevalence", "imbalance_strategy"]):
        paired = group.pivot(index=["seed", "sample_id_sha256"], columns="prior_correction", values=METRICS)
        assert len(paired) == 30 and not paired.isna().any().any()
        before, after = paired["brier_score"][False], paired["brier_score"][True]
        delta = after - before
        brier = [before.mean(), after.mean(), delta.mean(), delta.std(ddof=1), (delta < 0).sum()]
        np.testing.assert_array_equal(np.round(brier, 6), expected_brier[key])
        np.testing.assert_array_equal(np.round(paired[METRICS[1:]].mean(), 6), expected_secondary[key])


def test_headline_relative_changes_use_means_and_direction_counts(results):
    reference = results.query("target_prevalence == 0.155 and not prior_correction")
    means = reference.groupby(["imbalance_strategy", "calibration"]).brier_score.mean()
    for strategy in ("oversampling", "class_weight"):
        raw, platt = means[strategy, "raw"], means[strategy, "platt"]
        assert round(100 * (raw / means["baseline", "raw"] - 1)) == 41
        assert round(100 * (platt / raw - 1)) == -29

    shifted = results.query("calibration == 'platt' and target_prevalence != 0.155")
    for (target, strategy), group in shifted.groupby(["target_prevalence", "imbalance_strategy"]):
        paired = group.pivot(index=["seed", "sample_id_sha256"], columns="prior_correction", values=METRICS)
        before = paired.xs(False, axis=1, level="prior_correction")
        after = paired.xs(True, axis=1, level="prior_correction")
        ratio_of_means = 100 * (after.mean() / before.mean() - 1)
        mean_of_ratios = 100 * (after / before - 1).mean()
        assert abs(ratio_of_means.brier_score - mean_of_ratios.brier_score) > 0.001
        assert ratio_of_means.log_loss < 0 and ratio_of_means.ece < 0
        improved = (after.brier_score < before.brier_score).sum()
        if target == 0.25:
            assert -9.1 <= ratio_of_means.brier_score <= -8.5
            assert improved == 30
        elif strategy == "baseline":
            assert abs(ratio_of_means.brier_score) < 0.02
            assert improved == 16
        else:
            assert 0.4 <= ratio_of_means.brier_score <= 0.5
            assert improved == 11


def test_fresh_repetitions_match_saved_primary_metrics(monkeypatch, config, results):
    # Run the original numerical path and direct its CSV writes into pytest's temp tree.
    monkeypatch.setattr(experiment, "save_plots", lambda *_: None)
    refitted = pd.concat([
        experiment.run_repetition(config, seed, config.output / f"fresh-seed-{seed}")[0]
        for seed in SEEDS
    ])
    refitted = indexed_by(refitted, KEY).sort_index()
    saved = indexed_by(results, KEY).sort_index()
    pd.testing.assert_index_equal(refitted.index, saved.index)
    pd.testing.assert_series_equal(refitted.sample_id_sha256, saved.sample_id_sha256)
    np.testing.assert_allclose(refitted[METRICS], saved[METRICS], rtol=0, atol=1e-10)
