"""Tests for the frozen confirmatory protocol and fail-closed pair validation."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from protocol_validation import (
    ProtocolValidationError,
    canonical_json_hash,
    validate_confirmatory_results,
    validate_runtime_config,
)


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = json.loads((ROOT / "confirmatory_protocol.json").read_text())


def valid_runtime():
    return {
        "dataset": PROTOCOL["dataset"],
        "seeds": PROTOCOL["seeds"],
        "prevalences": PROTOCOL["prevalences"],
        "test_size": PROTOCOL["test_size"],
        "calibration_size": PROTOCOL["calibration_size"],
        "n_bins": PROTOCOL["n_bins"],
    }


def synthetic_results():
    rows = []
    for strategy in PROTOCOL["imbalance_strategies"]:
        for prevalence in PROTOCOL["primary_prevalences"]:
            for seed in PROTOCOL["seeds"]:
                sample_hash = f"{strategy}-{prevalence}-{seed}"
                rows.extend([
                    {
                        "seed": seed, "imbalance_strategy": strategy,
                        "calibration": "platt", "target_prevalence": prevalence,
                        "prior_correction": False, "sample_id_sha256": sample_hash,
                        "evaluation_path": "reference_no_correction",
                        "confirmatory_analysis": True,
                        "target_prior_source": "oracle_simulator",
                        "brier_score": 0.10,
                    },
                    {
                        "seed": seed, "imbalance_strategy": strategy,
                        "calibration": "platt", "target_prevalence": prevalence,
                        "prior_correction": True, "sample_id_sha256": sample_hash,
                        "evaluation_path": "primary_prior_correction",
                        "confirmatory_analysis": True,
                        "target_prior_source": "oracle_simulator",
                        "brier_score": 0.09,
                    },
                ])
    return pd.DataFrame(rows)


class ProtocolValidationTests(unittest.TestCase):
    def test_canonical_hash_ignores_key_order(self):
        self.assertEqual(canonical_json_hash({"a": 1, "b": 2}), canonical_json_hash({"b": 2, "a": 1}))

    def test_frozen_runtime_is_accepted(self):
        validate_runtime_config(valid_runtime(), PROTOCOL)

    def test_every_runtime_deviation_is_rejected(self):
        mutations = {
            "seed_schedule": ("seeds", PROTOCOL["seeds"][:-1]),
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


if __name__ == "__main__":
    unittest.main()
