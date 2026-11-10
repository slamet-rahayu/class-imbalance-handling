import numpy as np
import pytest
from scipy.special import expit, logit

from run_experiment import prior_correct


@pytest.mark.parametrize("target", [232 / 2315, 382 / 2464, 0.25, 381 / 2466])
def test_prior_correction_matches_bayes_and_logit_forms(target):
    source = 381 / 2466
    probabilities = np.r_[0.0, np.geomspace(1e-15, 0.5, 50), 0.97, 1.0]
    p = np.clip(probabilities, 1e-12, 1 - 1e-12)
    weighted_positive = p * target / source
    weighted_negative = (1 - p) * (1 - target) / (1 - source)
    bayes = weighted_positive / (weighted_positive + weighted_negative)
    shifted_logit = expit(logit(p) + logit(target) - logit(source))
    actual = prior_correct(probabilities, source, target)
    for expected in (bayes, shifted_logit):
        np.testing.assert_allclose(actual, np.clip(expected, 1e-12, 1 - 1e-12), atol=1e-15)
    assert np.all((0 <= actual) & (actual <= 1))
    assert np.all(np.diff(actual) >= 0)


def test_equal_priors_preserve_interior_and_clip_endpoints():
    p = np.array([0.0, 1e-13, 0.01, 0.5, 0.99, 1 - 1e-13, 1.0])
    np.testing.assert_allclose(prior_correct(p, 0.15, 0.15), np.clip(p, 1e-12, 1 - 1e-12))
    np.testing.assert_allclose(prior_correct(p[2:5], 0.15, 0.15), p[2:5], rtol=1e-15)


@pytest.mark.parametrize("p, source, target", [
    (np.nan, 0.15, 0.25), (-0.1, 0.15, 0.25), (1.1, 0.15, 0.25),
    (0.5, 0, 0.25), (0.5, 0.15, 1), (0.5, 0.15, np.inf),
])
def test_invalid_inputs_are_rejected(p, source, target):
    with pytest.raises(ValueError):
        prior_correct(np.array([p]), source, target)
