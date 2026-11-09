# Prediction-Level Validation

## Overall status

**PASS** for prediction-level regeneration and independent Brier score, log loss, and ECE verification. This resolves the former metric-verification gap. It does not resolve chronology or inferential-dependence failures.

## Isolation and instrumentation

The frozen commit was extracted to `scientific_validation_followup/isolated_source/` using:

```bash
git archive 2f448140cbdf5a593d1d182f26ef955d83cc717b | \
  tar -x -C scientific_validation_followup/isolated_source
python3 -m venv scientific_validation_followup/isolated_env
scientific_validation_followup/isolated_env/bin/pip install \
  -r scientific_validation_followup/isolated_source/requirements-lock.txt
```

The isolated `run_experiment.py` SHA-256 is `859f74...afcec`, identical to the freeze and original workspace file. The isolated dataset SHA-256 is `b3055e...e0d9`, also identical.

`export_predictions.py` calls the frozen split, fitting, Platt, sampling, and prior-correction helpers. It does not call the frozen evaluation function and does not change model fitting, preprocessing, samples, random generators, calibration, probability transformations, or evaluation observations. Its only added action is recording already-computed observation identifiers, labels, and probabilities. No file in `outputs_confirmatory_30_seeds/` was written.

## Export schema and inventory

- 30 gzip CSV files, one per seed, in `predictions/`.
- 567,630 wide prediction rows.
- One row per seed × strategy × prevalence scenario × observation.
- 18,921 rows per seed: three strategies × (2,315 + 2,464 + 1,528 scenario observations).
- Four explicit probability columns: raw, Platt, raw corrected, Platt corrected.
- Generic `p_prior_corrected` is explicitly null because no single value represents both frozen correction branches.
- `SCHEMA.json` documents keys and probability mapping.
- `MANIFEST.json` records SHA-256 and row count for every prediction file.
- All manifest hashes and row counts verified: **PASS**.

## Independent metric implementation

`independent_metric_verification.py` does not import `run_experiment` or any project metric function.

### Brier score

Implemented directly as `mean((p-y)**2)`.

### Log loss

Implemented as `-mean(y*log(p) + (1-y)*log1p(-p))`, after clipping to float64 machine epsilon (`2.220446049250313e-16`) and `1-epsilon`, matching the frozen sklearn numerical convention. Raw probabilities included 56 exact values equal to 1; clipping therefore matters for numerical safety. No probability was below zero or above one.

### ECE

Implemented independently with 10 equal-width bins and edges `0.0, 0.1, …, 1.0`. `np.digitize(..., right=False)` assigns internal-edge values to the bin beginning at that edge: `[0,.1)`, `[.1,.2)`, …, `[.9,1]` after last-bin clipping. Empty bins contribute zero. Probabilities at exactly 1 enter the last bin. This exactly reproduced every frozen ECE value.

## Metric comparison

Tolerance: `atol=1e-12`, `rtol=1e-10`.

| Metric | Comparisons | Max absolute difference | Mean absolute difference | Mismatches |
|---|---:|---:|---:|---:|
| Brier score | 1,080 | 5.551115123125783e-17 | 1.310680e-18 | 0 |
| Log loss | 1,080 | 1.665334536937735e-16 | 8.635068e-18 | 0 |
| ECE | 1,080 | 0 | 0 | 0 |
| **Total** | **3,240** | — | — | **0** |

No affected seed or configuration exists. The tiny Brier/log-loss differences are ordinary floating-point evaluation-order differences well below tolerance, not rounding, binning, or implementation discrepancies. Detailed values are in `METRIC_RECOMPUTATION.csv`.

## Invariant validation

| Invariant | Status | Evidence |
|---|---|---|
| All probabilities finite and within [0,1] | PASS | All four explicit columns across 567,630 rows |
| Labels only 0/1 | PASS | Unique values `[0,1]` |
| Unique observations within each evaluation sample | PASS | 270 seed/strategy/scenario groups |
| Expected scenario sizes | PASS | 2,315 at 0.10; 2,464 at 0.155; 1,528 at 0.25 |
| Realized prevalence equals label mean | PASS | All groups |
| Same IDs/labels for Platt versus corrected Platt | PASS | Probabilities coexist on the same wide keyed row |
| Source prevalence from natural calibration set | PASS | Independently reconstructed for all seeds; max error 0 |
| Bayesian odds adjustment | PASS | All 1,135,260 corrected values; max error 0 using frozen `1e-12` clipping |
| Source=target identity | PASS | Counterfactual check over exported probabilities; max error 0 after frozen clipping |
| Ranking preservation | PASS | No monotonicity failure in any raw/Platt scenario branch |
| Evaluation labels excluded from fitting/calibration | PASS | Source inspection: model uses `X_train,y_train`; calibrator uses raw `X_cal` probabilities and `y_cal`; test labels enter only sampling/evaluation |
| Repeated predictions treated as independent | FAIL in original inference | Observation reuse is quantified separately; verifier does not use repeated rows as independent inferential units |
| Prediction hashes and schema | PASS | `predictions/MANIFEST.json`, `predictions/SCHEMA.json` |

## Probability ranges

| Field | Minimum | Maximum |
|---|---:|---:|
| `p_raw` | 0.00019441425983569052 | 1.0 |
| `p_platt` | 0.00013283665363146514 | 0.9999999999999498 |
| `p_raw_prior_corrected` | 0.00011813927841450146 | 0.999999999999 |
| `p_platt_prior_corrected` | 0.00008071860173707383 | 0.999999999999 |

## Limit of this PASS

The prediction files are regenerated audit artifacts, not contemporaneously preserved primary outputs. Their exact aggregate agreement, frozen source hashes, and deterministic reproduction strongly verify the implemented computation. They cannot retrospectively prove the original freeze chronology, and they do not make overlapping split-level p-values independent.

