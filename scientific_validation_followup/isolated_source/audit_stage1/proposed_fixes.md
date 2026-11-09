# Proposed Fixes — Not Applied

No behavioral fix below has been applied. Historical artifacts remain unchanged.

## P1 — Separate confirmatory and exploratory correction (CRITICAL)

- Primary confirmatory path: Platt-calibrated probability followed by prior correction.
- Retain raw+correction only as `correction_validity="naive_exploratory"`, or remove it
  from the confirmatory estimand.
- Do not silently substitute post-ROS prevalence as source prior: raw weighted/ROS
  scores are not guaranteed calibrated probabilities under that prior.
- Verification: synthetic label-shift fixture with known calibrated source posterior.

## P2 — Declare target-prior provenance (CRITICAL)

Add `target_prior_source` with values such as `oracle_simulator`, `known_external`, or
`estimated_<method>`. Current simulation must use `oracle_simulator`. Claims must not
describe it as unsupervised deployment correction.

## P3 — Validate correction inputs (MEDIUM)

Before correction, reject non-finite probabilities and require finite
`0 < source_prior,target_prior < 1`. Add tests for NaN, Inf, 0, and 1.

## P4 — Complete scenario and training audit metadata (MEDIUM)

Persist `n_positive`, `n_negative`, `n_total`, scenario hash and optionally indices;
persist pre/post-ROS class counts, effective class weights, `n_iter_`, and convergence
status. This is logging only and need not alter predictions.

## P5 — Rename AP and prespecify statistics (MEDIUM)

Rename future `pr_auc` field to `average_precision` (or document an immutable alias).
Before 30 seeds, prespecify primary metrics, contrasts, Holm families, handling of the
invalid raw+correction branch, and the limited interpretation of repeated splits.

## P6 — Pin provenance (MEDIUM)

Add dataset URL/DOI/license/download date, a lockfile or frozen environment, and put
the project under version control so source and result manifests can cite a commit.

