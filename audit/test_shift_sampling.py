import hashlib
from fractions import Fraction

import numpy as np
import pandas as pd
import pytest

from conftest import OUTPUTS, PRIORS, SEEDS, indexed_by
from run_experiment import simulate_prior_shift


@pytest.mark.parametrize("offset, target, expected", [
    (0, 0.10, (2315, 232, 2083)),
    (1, 0.155, (2464, 382, 2082)),
    (2, 0.25, (1528, 382, 1146)),
])
def test_all_seeds_match_shift_counts_membership_and_hashes(splits, results, offset, target, expected):
    audits = pd.read_csv(OUTPUTS / "all_audits.csv").query("audit_type == 'shift'")
    assert len(audits) == len(SEEDS) * len(PRIORS)
    audits = indexed_by(audits, ["seed", "target_prevalence"])
    nominal = Fraction(str(target))
    for seed, (_, _, X_test, _, _, y_test) in splits.items():
        p = int(y_test.sum())
        q = len(y_test) - p
        n = int(min(p / nominal, q / (1 - nominal)))
        requested = round(n * nominal)
        assert (n, requested, n - requested) == expected
        positions = simulate_prior_shift(y_test, target, seed + offset)
        np.testing.assert_array_equal(positions, simulate_prior_shift(y_test, target, seed + offset))
        assert len(positions) == len(np.unique(positions)) == n
        assert np.all((0 <= positions) & (positions < len(y_test)))
        assert y_test.iloc[positions].sum() == requested
        ids = X_test.index.to_numpy()[positions]
        digest = hashlib.sha256(np.sort(ids).astype("<i8").tobytes()).hexdigest()
        audit = audits.loc[seed, target]
        assert (audit.n_total, audit.n_positive, audit.n_negative) == expected
        assert audit.sample_id_sha256 == digest
        group = results.query("seed == @seed and target_prevalence == @target")
        assert len(group) == 12
        assert group.sample_id_sha256.eq(digest).all()
        assert group.n_test.eq(n).all()
        assert group.n_positive.eq(requested).all()
        assert group.n_negative.eq(n - requested).all()
        np.testing.assert_allclose(group.actual_prevalence, requested / n, rtol=0, atol=1e-15)
