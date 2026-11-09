"""Non-destructive Stage-1 audit tests; no historical artifact is modified."""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, log_loss

from run_experiment import (
    Config,
    EPS,
    calibration_bins,
    evaluate,
    load_data,
    make_preprocessor,
    prior_correct,
    simulate_prior_shift,
    split_data,
)


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "online_shoppers_intention.csv"


class Stage1AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y = load_data(DATA)
        cls.cfg = Config(DATA, ROOT / "unused", (0.10, 0.155, 0.25), 0.2, 0.2, (42,), 10)

    def test_a01_schema_target_and_missingness(self):
        self.assertEqual(self.X.shape, (12330, 17))
        self.assertEqual(set(self.y.unique()), {0, 1})
        self.assertFalse(self.X.isna().any().any())
        self.assertNotIn("Revenue", self.X.columns)

    def test_a02_split_is_disjoint_complete_sized_and_deterministic(self):
        first = split_data(self.X, self.y, self.cfg, 42)
        second = split_data(self.X, self.y, self.cfg, 42)
        X_train, X_cal, X_test, y_train, y_cal, y_test = first
        sets = [set(X_train.index), set(X_cal.index), set(X_test.index)]
        self.assertEqual([len(x) for x in sets], [7398, 2466, 2466])
        self.assertFalse(sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
        self.assertEqual(set.union(*sets), set(self.X.index))
        for a, b in zip(first[::2], second[::2]):
            self.assertListEqual(a.index.tolist(), b.index.tolist())
        for split_y in (y_train, y_cal, y_test):
            self.assertLess(abs(float(split_y.mean()) - float(self.y.mean())), 0.001)

    def test_a03_preprocessor_fit_is_independent_of_test_values(self):
        X_train, _, X_test, *_ = split_data(self.X, self.y, self.cfg, 42)
        p1 = make_preprocessor(X_train).fit(X_train)
        changed_test = X_test.copy()
        numeric = changed_test.select_dtypes(include=np.number).columns
        changed_test.loc[:, numeric] = changed_test[numeric] + 1_000_000
        p2 = make_preprocessor(X_train).fit(X_train)
        np.testing.assert_allclose(
            p1.named_transformers_["numeric"].mean_,
            p2.named_transformers_["numeric"].mean_,
        )

    def test_a06_scenarios_are_unique_test_subsets_with_expected_prior(self):
        _, _, X_test, _, _, y_test = split_data(self.X, self.y, self.cfg, 42)
        for offset, target in enumerate(self.cfg.prevalences):
            positions = simulate_prior_shift(y_test, target, 42 + offset)
            self.assertEqual(len(positions), len(np.unique(positions)))
            self.assertTrue(set(positions).issubset(set(range(len(X_test)))))
            self.assertLessEqual(abs(float(y_test.iloc[positions].mean()) - target), 1 / len(positions))

    def test_a07_prior_correction_math_identity_bounds_and_direction(self):
        p = np.array([EPS, 1e-6, 0.01, 0.2, 0.5, 0.99, 1 - EPS])
        identity = prior_correct(p, 0.155, 0.155)
        np.testing.assert_allclose(identity, p, rtol=1e-9, atol=1e-12)
        corrected = prior_correct(p, 0.155, 0.25)
        expected = expit(logit(np.clip(p, EPS, 1 - EPS)) + logit(0.25) - logit(0.155))
        np.testing.assert_allclose(corrected, expected, rtol=1e-9, atol=1e-12)
        self.assertTrue(np.all((corrected > 0) & (corrected < 1)))
        self.assertTrue(np.all(np.diff(corrected) >= 0))
        self.assertTrue(np.all(corrected >= p))
        self.assertTrue(np.all(corrected[1:-1] > p[1:-1]))
        decreased = prior_correct(p, 0.155, 0.10)
        self.assertTrue(np.all(decreased <= p))
        self.assertTrue(np.all(decreased[1:-1] < p[1:-1]))

    def test_a07_nonfinite_inputs_are_rejected_after_remediation(self):
        for values in ([0.2, np.nan], [0.2, np.inf], [-0.1, 0.2], [0.2, 1.1]):
            with self.assertRaises(ValueError):
                prior_correct(np.asarray(values), 0.155, 0.25)
        for source, target in ((0, 0.25), (1, 0.25), (0.155, 0), (0.155, 1), (np.nan, 0.25)):
            with self.assertRaises(ValueError):
                prior_correct(np.array([0.2]), source, target)

    def test_a08_metrics_match_sklearn_and_bins_are_equal_width(self):
        y = np.array([0, 0, 1, 1, 1])
        p = np.array([0.05, 0.40, 0.35, 0.80, 0.95])
        result = evaluate(y, p, 10)
        self.assertAlmostEqual(result["brier_score"], brier_score_loss(y, p))
        self.assertAlmostEqual(result["log_loss"], log_loss(y, p, labels=[0, 1]))
        self.assertAlmostEqual(result["pr_auc"], average_precision_score(y, p))
        self.assertAlmostEqual(result["average_precision"], average_precision_score(y, p))
        self.assertAlmostEqual(result["f1"], f1_score(y, p >= 0.5, zero_division=0))
        self.assertEqual(sum(row[0] for row in calibration_bins(y, p, 10)), len(y))

    def test_a08_historical_output_keys_and_completeness(self):
        result = pd.read_csv(ROOT / "outputs_10_seeds" / "all_repetitions.csv")
        keys = ["seed", "imbalance_strategy", "calibration", "target_prevalence", "prior_correction"]
        self.assertEqual(len(result), 360)
        self.assertFalse(result.duplicated(keys).any())
        self.assertEqual(result.seed.nunique(), 10)
        self.assertTrue(np.isfinite(result[["brier_score", "log_loss", "pr_auc", "f1", "ece"]]).all().all())


if __name__ == "__main__":
    unittest.main()
