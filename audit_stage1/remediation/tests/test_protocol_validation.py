"""Tests for the frozen confirmatory protocol and fail-closed pair validation."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from audit_and_paired_analysis import confirmatory_h3_analysis
from protocol_validation import (
    ProtocolValidationError,
    canonical_json_hash,
    validate_confirmatory_results,
    validate_frozen_protocol,
    validate_runtime_config,
    validate_source_commit,
)
from run_experiment import Config, run


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = json.loads((ROOT / "confirmatory_protocol_v2.json").read_text())
EFFECTIVE = PROTOCOL["effective_config"]


def valid_runtime():
    return copy.deepcopy(EFFECTIVE)


def synthetic_results():
    rows = []
    for strategy in EFFECTIVE["imbalance_strategies"]:
        for prevalence in EFFECTIVE["primary_prevalences"]:
            for seed in EFFECTIVE["seeds"]:
                sample_hash = f"{strategy}-{prevalence}-{seed}"
                base = {
                        "seed": seed, "imbalance_strategy": strategy,
                        "calibration": "platt", "target_prevalence": prevalence,
                        "sample_id_sha256": sample_hash,
                        "confirmatory_analysis": True,
                        "source_prior_basis": "natural_calibration_set",
                        "project_version": "stage1-remediation-v1",
                        "n_test": 100, "n_positive": int(prevalence * 100),
                        "n_negative": 100 - int(prevalence * 100),
                        "brier_score": 0.10, "log_loss": 0.30,
                        "average_precision": 0.60, "pr_auc": 0.60,
                        "f1": 0.50, "ece": 0.05,
                        "mean_predicted_probability": prevalence,
                        "actual_prevalence": prevalence,
                        "source_prevalence": 0.155,
                }
                rows.extend([
                    {
                        **base, "prior_correction": False,
                        "evaluation_path": "reference_no_correction",
                        "target_prior_source": "not_applied",
                        "prior_correction_validity": "not_applied",
                    },
                    {
                        **base, "prior_correction": True,
                        "evaluation_path": "primary_prior_correction",
                        "target_prior_source": "oracle_simulator",
                        "prior_correction_validity": "calibrated_confirmatory",
                        "brier_score": 0.09,
                    },
                ])
    return pd.DataFrame(rows)


class ProtocolValidationTests(unittest.TestCase):
    def test_canonical_hash_ignores_key_order(self):
        self.assertEqual(canonical_json_hash({"a": 1, "b": 2}), canonical_json_hash({"b": 2, "a": 1}))

    def test_frozen_runtime_is_accepted(self):
        validate_runtime_config(valid_runtime(), PROTOCOL)

    def test_full_freeze_manifest_is_accepted(self):
        result = validate_frozen_protocol(
            ROOT / "confirmatory_protocol_freeze_v2.json", valid_runtime()
        )
        self.assertEqual(result["status"], "PASS")

    def test_every_runtime_deviation_is_rejected(self):
        mutations = {
            "seed_schedule": ("seeds", EFFECTIVE["seeds"][:-1]),
            "prevalence": ("prevalences", [0.10, 0.20, 0.25]),
            "test_size": ("test_size", 0.25),
            "calibration_size": ("calibration_size", 0.15),
            "bins": ("n_bins", 15),
            "dataset": ("dataset", "other.csv"),
        }
        for name, (key, value) in mutations.items():
            with self.subTest(name=name):
                runtime = valid_runtime()
                runtime[key] = value
                with self.assertRaises(ProtocolValidationError):
                    validate_runtime_config(runtime, PROTOCOL)

    def test_confirmatory_run_rejects_mismatch_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "must_not_exist"
            cfg = Config(
                ROOT / "online_shoppers_intention.csv",
                output,
                (0.10, 0.155, 0.25),
                0.20,
                0.20,
                tuple(range(42, 71)),  # seed 71 deliberately missing
                10,
                True,
                ROOT / "confirmatory_protocol_freeze_v2.json",
            )
            with self.assertRaises(ProtocolValidationError):
                run(cfg)
            self.assertFalse(output.exists())

    def test_complete_six_contrast_results_are_accepted(self):
        result = validate_confirmatory_results(synthetic_results(), PROTOCOL)
        self.assertEqual(result["complete_primary_contrasts"], 6)

    def test_incomplete_pair_is_rejected(self):
        data = synthetic_results().iloc[:-1].copy()
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_nonfinite_primary_metric_is_rejected(self):
        data = synthetic_results()
        data.loc[0, "brier_score"] = np.nan
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_nonfinite_secondary_metric_is_rejected(self):
        data = synthetic_results()
        data.loc[0, "log_loss"] = np.inf
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_modified_model_parameter_is_rejected(self):
        runtime = valid_runtime()
        runtime["model"]["C"] = 0.5
        with self.assertRaises(ProtocolValidationError):
            validate_runtime_config(runtime, PROTOCOL)

    def test_mismatched_git_head_is_rejected(self):
        with self.assertRaises(ProtocolValidationError):
            validate_source_commit(ROOT, "0" * 40)

    def test_incorrect_evaluation_path_is_rejected(self):
        data = synthetic_results()
        data.loc[data.prior_correction.idxmax(), "evaluation_path"] = "reference_no_correction"
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_missing_required_metadata_is_rejected(self):
        data = synthetic_results().drop(columns=["source_prior_basis"])
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_mismatched_sample_hash_is_rejected(self):
        data = synthetic_results()
        data.loc[1, "sample_id_sha256"] = "different"
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(data, PROTOCOL)

    def test_naive_row_cannot_be_confirmatory(self):
        data = synthetic_results()
        extra = data.iloc[[0]].copy()
        extra["evaluation_path"] = "naive_exploratory"
        extra["confirmatory_analysis"] = True
        with self.assertRaises(ProtocolValidationError):
            validate_confirmatory_results(pd.concat([data, extra]), PROTOCOL)

    def test_primary_analysis_has_exact_six_contrasts(self):
        result = confirmatory_h3_analysis(synthetic_results(), PROTOCOL)
        self.assertEqual(len(result), 6)
        self.assertEqual(set(result.metric), {"brier_score"})
        self.assertEqual(set(result.target_prevalence), {0.10, 0.25})

    def test_all_zero_primary_differences_have_p_one_and_zero_effects(self):
        data = synthetic_results()
        data.loc[data.prior_correction, "brier_score"] = 0.10
        result = confirmatory_h3_analysis(data, PROTOCOL)
        self.assertTrue((result.wilcoxon_statistic == 0).all())
        self.assertTrue((result.wilcoxon_p_raw == 1).all())
        self.assertTrue((result.wilcoxon_p_holm == 1).all())
        self.assertTrue((result.cohens_dz == 0).all())
        self.assertTrue((result.rank_biserial == 0).all())


if __name__ == "__main__":
    unittest.main()
