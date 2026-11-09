# Pipeline Map

```text
online_shoppers_intention.csv
  -> load_data() [run_experiment.py:76-88]
  -> split_data(): stratified train/calibration/test [91-104]
  -> make_preprocessor(): StandardScaler + OneHotEncoder [107-117]
  -> fit_model() [120-140]
       baseline: unweighted LogisticRegression
       oversampling: RandomOverSampler on transformed train only
       class_weight: LogisticRegression(class_weight="balanced")
  -> raw probabilities on natural calibration/test [316-324]
  -> fit_platt_scaler(logit(raw p), y_cal) [143-152]
  -> simulate_prior_shift(y_test only) [155-169, 291-314]
  -> raw or Platt probabilities for selected test positions [326-333]
  -> optional prior_correct(source=y_cal.mean, target=y_shifted.mean) [172-193, 334-340]
  -> evaluate(): Brier, log loss, AP, F1@0.5, ECE-10 [196-222]
  -> per-seed CSV/plots [363-368]
  -> combined rows, aggregate summary, audit rows [386-400]
```

## Functions and responsibilities

| Function/class | Responsibility | State learned from |
|---|---|---|
| `Config` | Experiment parameters | CLI |
| `load_data` | Schema/target conversion | CSV |
| `split_data` | Stratified split | Target labels, before preprocessing |
| `make_preprocessor` | Define numeric/categorical transforms | Column dtypes |
| `fit_model` | Fit preprocessing, optional ROS/weight, base LR | Training only |
| `fit_platt_scaler` | Fit sigmoid calibration | Natural calibration only |
| `simulate_prior_shift` | Class-conditional subsampling | Test labels only |
| `prior_correct` | Odds prior-ratio transformation | Supplied source/target priors |
| `evaluate` | Probability/classification metrics | Shifted test labels/probabilities |
| `aggregate_results` | Mean/std/count/nominal CI | Per-seed result rows |

## Critical boundary

The same natural `source_prior=y_cal.mean()` is passed to correction for all raw and
Platt branches. It is defensible for Platt-calibrated probabilities, but not for raw
ROS/class-weight scores. The target prior is computed from shifted test labels, so it
is an oracle simulator input and must not be presented as an unsupervised deployment
estimate.

