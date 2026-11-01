"""Automated checks for Stage-1 remediation P1-P6."""

import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np

from run_experiment import (
    Config,
    DATASET_PROVENANCE,
    evaluate,
    prior_correct,
    run_repetition,
)


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "online_shoppers_intention.csv"
HISTORICAL_HASH = "4e35c9c5c05c092a585f165743e2f22aab7fc9b06f19805514e882aebebe8652"


class RemediationTests(unittest.TestCase):
    def test_p1_paths_separate_primary_and_naive(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(DATA, Path(tmp), (0.10, 0.155, 0.25), 0.2, 0.2, (42,), 10)
            results, audit, training = run_repetition(cfg, 42, Path(tmp))
        corrected = results[results.prior_correction]
        platt = corrected[corrected.calibration == "platt"]
        raw = corrected[corrected.calibration == "raw"]
        self.assertTrue((platt.evaluation_path == "primary_prior_correction").all())
        self.assertTrue(platt.confirmatory_analysis.all())
        self.assertTrue((platt.prior_correction_validity == "calibrated_confirmatory").all())
        self.assertTrue((raw.evaluation_path == "naive_exploratory").all())
        self.assertFalse(raw.confirmatory_analysis.any())
        self.assertTrue((raw.prior_correction_validity == "naive_exploratory").all())

    def test_p2_oracle_metadata_and_scenario_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(DATA, Path(tmp), (0.10,), 0.2, 0.2, (42,), 10)
            results, audit, _ = run_repetition(cfg, 42, Path(tmp))
        self.assertTrue((results.target_prior_source == "oracle_simulator").all())
        self.assertTrue((audit.loc[audit.audit_type == "shift", "target_prior_source"] == "oracle_simulator").all())
        self.assertTrue((results.n_positive + results.n_negative == results.n_test).all())
        self.assertTrue(results.sample_id_sha256.str.len().eq(64).all())

    def test_p3_prior_validation(self):
        invalid_probabilities = [np.array([np.nan]), np.array([np.inf]), np.array([-0.1]), np.array([1.1])]
        for values in invalid_probabilities:
            with self.assertRaises(ValueError):
                prior_correct(values, 0.2, 0.4)
        for source, target in [(0, 0.4), (1, 0.4), (0.2, 0), (0.2, 1), (np.nan, 0.4)]:
            with self.assertRaises(ValueError):
                prior_correct(np.array([0.5]), source, target)

    def test_p3_synthetic_known_label_shift(self):
        source_prior, target_prior = 0.20, 0.50
        likelihood_ratio = np.array([0.25, 1.0, 4.0, 10.0])
        source_posterior = (
            likelihood_ratio * source_prior
            / (likelihood_ratio * source_prior + 1 - source_prior)
        )
        expected_target = (
            likelihood_ratio * target_prior
            / (likelihood_ratio * target_prior + 1 - target_prior)
        )
        np.testing.assert_allclose(
            prior_correct(source_posterior, source_prior, target_prior),
            expected_target,
            rtol=1e-12,
            atol=1e-12,
        )

    def test_p4_training_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(DATA, Path(tmp), (0.10,), 0.2, 0.2, (42,), 10)
            _, _, training = run_repetition(cfg, 42, Path(tmp))
        self.assertEqual(set(training.strategy), {"baseline", "oversampling", "class_weight"})
        ros = training.set_index("strategy").loc["oversampling"]
        self.assertEqual(ros.train_positive_after, ros.train_negative_after)
        self.assertTrue(training.base_converged.all())
        self.assertTrue(training.platt_converged.all())
        self.assertGreater(training.set_index("strategy").loc["class_weight", "class_weight_positive"], 1)

    def test_p5_average_precision_alias(self):
        y = np.array([0, 1, 1])
        p = np.array([0.1, 0.7, 0.9])
        metrics = evaluate(y, p, 10)
        self.assertIn("average_precision", metrics)
        self.assertEqual(metrics["average_precision"], metrics["pr_auc"])

    def test_p6_provenance_and_historical_immutability(self):
        self.assertEqual(DATASET_PROVENANCE["dataset_id"], 468)
        self.assertEqual(DATASET_PROVENANCE["doi"], "10.24432/C5F88Q")
        self.assertEqual(DATASET_PROVENANCE["license"], "CC BY 4.0")
        historical = ROOT / "outputs_10_seeds" / "all_repetitions.csv"
        self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), HISTORICAL_HASH)
        self.assertTrue((ROOT / "requirements-lock.txt").exists())


if __name__ == "__main__":
    unittest.main()
