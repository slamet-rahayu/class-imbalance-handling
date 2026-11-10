import numpy as np
from scipy.optimize import root
from scipy.special import expit, logit

import run_experiment as experiment


def test_platt_clips_inputs_and_uses_positive_class_sigmoid(monkeypatch):
    class FitSpy:
        def __init__(self, **kwargs):
            self.classes_ = np.array([0, 1])

        def fit(self, X, y):
            self.fit_inputs = X[:, 0]

        def predict_proba(self, X):
            p = expit(0.75 * X[:, 0] - 0.2)
            return np.column_stack((1 - p, p))

    monkeypatch.setattr(experiment, "LogisticRegression", FitSpy)
    p = np.array([0, 1e-13, 0.1, 0.5, 0.9, 1 - 1e-13, 1])
    z = logit(np.clip(p, 1e-12, 1 - 1e-12))
    # The separate complement clip avoids subtracting 1 - EPS from 1.
    z[-2:] = -z[0]
    calibrator = experiment.fit_platt_scaler(p, np.arange(len(p)) % 2)
    np.testing.assert_allclose(calibrator.fit_inputs, z, atol=1e-12, rtol=1e-12)
    np.testing.assert_allclose(experiment.apply_platt(calibrator, p), expit(0.75 * z - 0.2))


def test_platt_fits_penalized_loss_and_differs_from_unpenalized_fit():
    p = np.array([0.1, 0.1, 0.25, 0.4, 0.6, 0.75, 0.9, 0.9])
    y = np.array([0, 1, 0, 0, 1, 1, 0, 1])
    z = logit(p)
    calibrator = experiment.fit_platt_scaler(p, y)

    def score(params, penalty):
        slope, intercept = params
        residual = expit(slope * z + intercept) - y
        return np.array([z @ residual + penalty * slope, residual.sum()])

    penalized = root(score, [0.0, 0.0], args=(1.0,))
    unpenalized = root(score, [0.0, 0.0], args=(0.0,))
    assert penalized.success and unpenalized.success
    fit = [calibrator.coef_[0, 0], calibrator.intercept_[0]]
    np.testing.assert_allclose(fit, penalized.x, rtol=0, atol=2e-4)
    assert abs(fit[0] - unpenalized.x[0]) > 0.01
