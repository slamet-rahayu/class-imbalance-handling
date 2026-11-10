import numpy as np

from run_experiment import calibration_bins, evaluate


def reference_metrics(y, p):
    brier = np.square(p - y).mean()
    eps = np.finfo(p.dtype).eps
    safe = np.clip(p, eps, 1 - eps)
    log_loss = -np.where(y == 1, np.log(safe), np.log1p(-safe)).mean()
    # Match the intended left-closed bins using interval masks instead of digitize.
    edges = np.linspace(0, 1, 11)
    residual = p - y
    ece = 0.0
    for index, (left, right) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        upper = (p <= right) if index == 9 else (p < right)
        ece += abs(residual[(p >= left) & upper].sum()) / len(y)
    return np.array([brier, log_loss, ece])


def test_metrics_against_hand_calculation():
    y = np.array([0, 1, 0, 1])
    p = np.array([0.04, 0.07, 0.5, 0.97])
    metrics = evaluate(y, p, n_bins=10)
    assert np.isclose(metrics["brier_score"], (0.04**2 + 0.93**2 + 0.5**2 + 0.03**2) / 4)
    assert np.isclose(metrics["log_loss"], -np.log(0.96 * 0.07 * 0.5 * 0.97) / 4)
    assert np.isclose(metrics["ece"], (abs(0.04 + 0.07 - 1) + 0.5 + 0.03) / 4)


def test_equal_width_bins_endpoints_internal_edges_and_empty_bins():
    p = np.array([0.0, np.nextafter(0.1, 0), 0.1, 0.5, 0.9, 1.0])
    y = np.array([1, 0, 1, 0, 1, 0])
    np.testing.assert_allclose(calibration_bins(y, p, 10), [
        (2, p[1] / 2, 0.5), (1, 0.1, 1), (1, 0.5, 0), (2, 0.95, 0.5),
    ])
    metrics = evaluate(y, p, n_bins=10)
    np.testing.assert_allclose(
        [metrics[name] for name in ("brier_score", "log_loss", "ece")],
        reference_metrics(y, p), rtol=0, atol=1e-14,
    )
