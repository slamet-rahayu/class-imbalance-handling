import itertools

import numpy as np
import pandas as pd

import run_experiment as experiment
from conftest import OUTPUTS, ROOT, SEEDS, indexed_by


def test_dataset_and_all_stratified_partitions(config, dataset, splits):
    X, y = dataset
    assert X.shape == (12330, 17)
    assert y.value_counts().to_dict() == {0: 10422, 1: 1908}
    assert not X.isna().any().any()
    assert tuple(splits) == config.seeds == SEEDS
    for X_train, X_cal, X_test, y_train, y_cal, y_test in splits.values():
        parts = [set(part.index) for part in (X_train, X_cal, X_test)]
        assert all(a.isdisjoint(b) for a, b in itertools.combinations(parts, 2))
        assert set.union(*parts) == set(X.index)
        assert (len(y_train), len(y_cal), len(y_test)) == (7398, 2466, 2466)
        assert (int(y_train.sum()), int(y_cal.sum())) in {(1145, 381), (1144, 382)}
        assert int(y_test.sum()) == 382
        for xs, ys in zip((X_train, X_cal, X_test), (y_train, y_cal, y_test), strict=True):
            pd.testing.assert_series_equal(ys, y.loc[xs.index])


def test_duplicate_overlap_is_distinct_from_row_index_overlap(dataset, splits):
    X, y = dataset
    keys = pd.Series(list(X.itertuples(index=False, name=None)), index=X.index)
    duplicate = keys.duplicated(keep=False)
    assert (keys[duplicate].nunique(), duplicate.sum(), keys.duplicated().sum()) == (76, 201, 125)
    assert not y[duplicate].any()
    path = ROOT / "cross-partition-duplicate-audit-570066kd" / "cross_partition_by_seed.csv"
    recorded = indexed_by(pd.read_csv(path), "seed")
    for seed, (train, cal, test, _, _, y_test) in splits.items():
        exposed = keys.loc[test.index].isin(set(keys.loc[train.index.union(cal.index)]))
        assert int(exposed.sum()) == recorded.loc[seed, "test_either_n"]
        assert not y_test[exposed].any()


def test_fitting_scope_on_production_repetition_path(monkeypatch, config, splits):
    train, cal, test, y_train, y_cal, y_test = splits[42]
    fit_calls, calibration_calls, evaluation_calls = [], [], []
    original_model = experiment.fit_model
    original_calibrator = experiment.fit_platt_scaler
    original_evaluate = experiment.evaluate

    def fit_model(X, y, strategy, seed):
        pd.testing.assert_frame_equal(X, train)
        pd.testing.assert_series_equal(y, y_train)
        model, metadata = original_model(X, y, strategy, seed)
        preprocessing = model.named_steps["preprocess"]
        numeric, categorical = preprocessing.transformers[:2]
        assert set(categorical[2]) == {"Month", "VisitorType"}
        assert set(numeric[2]) == set(X.columns) - set(categorical[2])
        np.testing.assert_allclose(
            preprocessing.named_transformers_["numeric"].mean_,
            X[numeric[2]].to_numpy(dtype=float).mean(axis=0),
        )
        assert model.named_steps["model"].class_weight == (
            "balanced" if strategy == "class_weight" else None
        )
        expected_positive = 6253 if strategy == "oversampling" else 1145
        assert (metadata["train_negative_after"], metadata["train_positive_after"]) == (
            6253, expected_positive,
        )
        fit_calls.append((strategy, model.predict_proba(cal)[:, 1]))
        return model, metadata

    def fit_platt(p, y):
        pd.testing.assert_series_equal(y, y_cal)
        np.testing.assert_allclose(p, fit_calls[-1][1], rtol=0, atol=0)
        calibrator = original_calibrator(p, y)
        calibration_calls.append(calibrator)
        return calibrator

    def evaluate(y, p, bins):
        evaluation_calls.append((y.copy(), p.copy(), bins))
        return original_evaluate(y, p, bins)

    monkeypatch.setattr(experiment, "fit_model", fit_model)
    monkeypatch.setattr(experiment, "fit_platt_scaler", fit_platt)
    monkeypatch.setattr(experiment, "evaluate", evaluate)
    monkeypatch.setattr(experiment, "save_plots", lambda *_: None)
    rows, _, _ = experiment.run_repetition(config, 42, config.output / "instrumented-seed-42")
    assert [strategy for strategy, _ in fit_calls] == list(experiment.IMBALANCE_STRATEGIES)
    assert len({id(calibrator) for calibrator in calibration_calls}) == 3
    assert len(evaluation_calls) == len(rows) == 36
    for row, (labels, p, bins) in zip(rows.itertuples(), evaluation_calls, strict=True):
        offset = config.prevalences.index(row.target_prevalence)
        positions = experiment.simulate_prior_shift(y_test, row.target_prevalence, 42 + offset)
        np.testing.assert_array_equal(labels, y_test.iloc[positions])
        assert bins == 10
        assert row.source_prevalence == y_cal.mean()
        assert row.actual_prevalence == labels.mean()
        assert len(p) == len(labels)


def test_training_metadata_all_90_models(splits):
    fit = indexed_by(pd.read_csv(OUTPUTS / "training_metadata.csv"), ["seed", "strategy"])
    assert set(fit.index) == set(itertools.product(SEEDS, experiment.IMBALANCE_STRATEGIES))
    assert fit[["base_converged", "platt_converged"]].all().all()
    assert not fit[["base_convergence_warning", "platt_convergence_warning"]].any().any()
    for (seed, strategy), row in fit.iterrows():
        train_positive = int(splits[seed][3].sum())
        train_negative = 7398 - train_positive
        cal_positive = int(splits[seed][4].sum())
        assert (row.train_n_before, row.train_negative_before, row.train_positive_before) == (
            7398, train_negative, train_positive,
        )
        assert (row.calibration_n, row.calibration_negative, row.calibration_positive) == (
            2466, 2466 - cal_positive, cal_positive,
        )
        assert row.train_negative_after == train_negative
        assert row.train_positive_after == (train_negative if strategy == "oversampling" else train_positive)
        expected = [7398 / (2 * train_negative), 7398 / (2 * train_positive)] if strategy == "class_weight" else [1, 1]
        np.testing.assert_allclose([row.class_weight_negative, row.class_weight_positive], expected)
