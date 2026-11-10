from pathlib import Path

import pandas as pd
import pytest

import run_experiment as experiment


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs_confirmatory_30_seeds"
PREDICTIONS = ROOT / "scientific_validation_followup" / "predictions"
SEEDS = tuple(range(42, 72))
PRIORS = (0.10, 0.155, 0.25)


def indexed_by(frame, columns):
    indexed = frame.set_index(columns)
    assert indexed.index.is_unique
    return indexed


@pytest.fixture(scope="session")
def config(tmp_path_factory):
    return experiment.Config(
        data=ROOT / "online_shoppers_intention.csv",
        output=tmp_path_factory.mktemp("v11-audit"),
        prevalences=PRIORS,
        test_size=0.20,
        calibration_size=0.20,
        seeds=SEEDS,
        n_bins=10,
    )


@pytest.fixture(scope="session")
def dataset(config):
    return experiment.load_data(config.data)


@pytest.fixture(scope="session")
def splits(config, dataset):
    X, y = dataset
    return {seed: experiment.split_data(X, y, config, seed) for seed in SEEDS}


@pytest.fixture(scope="session")
def results():
    return pd.read_csv(OUTPUTS / "all_repetitions.csv")
