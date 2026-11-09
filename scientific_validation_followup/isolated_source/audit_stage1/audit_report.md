# Stage 1 — Audit Metodologi dan Source Code

**Executed:** 2026-11-01 15:50 WIB  
**Specification:** `CODEX_STAGE1_AUDIT_SPEC.md` v1.0  
**Decision for confirmatory 30-seed experiment:** **NO-GO**

## Executive summary

The repository reproduces its 10-seed historical output exactly in the current
environment. Dataset schema, split isolation, train-only preprocessing, test-only
scenario sampling, probability metrics, and the mathematical odds-correction formula
were verified by code inspection and eight passing isolated tests. A seed-42 smoke run
produced 36/36 matching rows with maximum numeric difference 0.0.

The project is nevertheless **NO-GO** for a confirmatory 30-seed run because A07 has
unresolved critical findings:

1. the natural calibration prevalence is used as source prior for raw ROS and
   class-weight probabilities, although those scores are not calibrated source
   posteriors under that prior (`run_experiment.py:289,331-340`); and
2. target prior is calculated from shifted test labels and used directly without being
   identified as an `oracle-known` simulator input (`run_experiment.py:326-350`).

The first issue affects the methodological interpretation of **90 raw+correction rows**
(10 seeds × 3 imbalance strategies × 3 prevalences). They may remain historical
exploratory results, but must not enter the confirmatory prior-correction estimand as if
all branches had the same theoretical validity. Platt+correction is the defensible main
path, subject to explicitly declaring the oracle target prior.

## Scope and evidence

Audited inputs:

- experiment entry point: `run_experiment.py`;
- statistical entry point: `audit_and_paired_analysis.py`;
- dataset: `online_shoppers_intention.csv`;
- historical results: `outputs_10_seeds/` and `audit_results_10_seeds/`;
- environment declaration: `requirements.txt` and live virtual environment;
- flow diagram and README.

Available historical artifacts include 360 raw result rows, 36 aggregate rows, 60
audit rows, all 10 per-seed folders, statistical outputs, and plots. Missing or not
verifiable: authoritative dataset download record/checksum, Git commit SHA, lockfile,
post-ROS counts, model convergence metadata, full scenario indices, and target-prior
provenance metadata.

## Audit matrix

| ID | Control | Severity | Status | Primary evidence |
|---|---|---:|---|---|
| A01 | Dataset integrity | MEDIUM | NEEDS_REVIEW | dataset hash; test lines 34–38 |
| A02 | Splitting/independence | CRITICAL | PASS | `run_experiment.py:91-104,275-279`; test 40–51 |
| A03 | Preprocessing | CRITICAL | PASS | `run_experiment.py:107-122`; test 53–63 |
| A04 | Imbalance handling | MEDIUM | NEEDS_REVIEW | `run_experiment.py:120-140` |
| A05 | Model/calibration | MEDIUM | NEEDS_REVIEW | `run_experiment.py:131-152,316-324` |
| A06 | Prior-shift simulation | MEDIUM | NEEDS_REVIEW | `run_experiment.py:155-169,291-314`; test 65–71 |
| A07 | Prior correction | CRITICAL | FAIL | `run_experiment.py:172-193,289,326-350`; tests 73–94 |
| A08 | Metrics/output | MEDIUM | NEEDS_REVIEW | `run_experiment.py:196-222,341-350`; tests 96–112 |
| A09 | Reproducibility | MEDIUM | NEEDS_REVIEW | manifest and smoke comparison |
| A10 | Statistical traceability | MEDIUM | NEEDS_REVIEW | `audit_and_paired_analysis.py:42-113,197-251` |

Full observed/expected/impact/fix/test fields are in `audit_findings.csv`.

## Detailed findings

### A01 — Dataset integrity: NEEDS_REVIEW

Local file has 12,330 rows, 18 columns including target, 17 predictors, no missing
values, and binary `Revenue` (1,908 positive; 10,422 negative; prevalence 15.4745%).
Target is removed before feature processing (`run_experiment.py:76-88`). SHA-256 is
`b3055ee355f59134d851d32641183cb4a8b45def7124d2f50442a042f358e0d9`.
The repository does not provide an authoritative UCI URL/download date/license or an
external checksum, so external provenance is `NOT_VERIFIABLE` even though local
integrity checks pass. No rows were deduplicated.

### A02 — Splitting and independence: PASS

The first stratified split holds out 20% test; the second takes 25% of the remaining
80%, yielding 60/20/20 total (`run_experiment.py:91-104`). Seed 42 sizes are exactly
7,398/2,466/2,466. Assertions enforce disjoint and complete index sets
(`run_experiment.py:275-279`). Repeated splitting at seed 42 was deterministic.
No hyperparameter search exists and no test label is used for model fitting.

### A03 — Preprocessing: PASS

Numeric columns receive `StandardScaler`; categorical columns (Month, VisitorType,
Weekend) receive `OneHotEncoder(handle_unknown="ignore")`
(`run_experiment.py:107-117`). The transformer is fit using training data only at
lines 120–122; calibration/test are passed to pipeline prediction only. A synthetic
test perturbation did not change train scaler statistics.

### A04 — Imbalance handling: NEEDS_REVIEW

Baseline, ROS, and class-weight branches are mutually exclusive. ROS operates only on
encoded/scaled training rows (`run_experiment.py:124-129`); class weighting is model
only. ROS after one-hot encoding merely replicates existing rows, so it does not create
fractional dummy variables. However, post-ROS counts/prevalence and effective balanced
weights are not persisted, preventing artifact-only verification.

### A05 — Model and calibration: NEEDS_REVIEW

Base model configuration is LogisticRegression with `solver="liblinear"`,
`max_iter=2000`, and per-repetition seed (`run_experiment.py:131-137`). The frozen base
model predicts on the natural calibration set; Platt fits an LR to logit(raw
probability) and calibration labels (`run_experiment.py:143-152,316-324`). Calibration
is not resampled or used to refit the base model. This input is equivalent to an affine
calibration of the base logistic decision score, subject to clipping. Historical
`n_iter_` and convergence status are not saved, so convergence for all historical fits
is not independently verifiable from artifacts.

### A06 — Class-prior shift simulation: NEEDS_REVIEW

Scenarios sample uniformly within label classes from the test pool only, without
replacement (`run_experiment.py:155-169`). The same positions are reused across all
strategies for a seed (`run_experiment.py:291-295`). Uniqueness/subset assertions and a
sample hash are saved (`run_experiment.py:296-314`). Tests verify actual prevalence is
within one observation of target. Counts by class and full indices are not saved;
overlap between prevalence scenarios is allowed but not quantified. This is a
conditional subsampling simulation, not evidence of production shift.

### A07 — Prior probability correction: FAIL

The implementation at `run_experiment.py:172-178` correctly applies the prior odds
ratio. Unit tests verified identity, monotonicity, bounds, direction, near-boundary
probabilities, and equivalence to
`expit(logit(p)+logit(pi_target)-logit(pi_source))`.

Three issues remain:

- **CRITICAL:** `source_prior=y_cal.mean()` at line 289 is applied to every raw and
  Platt branch. It represents the natural source distribution for Platt outputs, but
  raw ROS/class-weight scores are not calibrated source probabilities. Their corrected
  results must be labeled naive/exploratory.
- **CRITICAL:** target prior is computed from `y_shifted.mean()` at lines 328–335. This
  is legitimate as an oracle simulator condition, but output lacks provenance and may
  be misread as an unsupervised deployment method.
- **MEDIUM:** invalid priors and NaN/Inf probability inputs are not explicitly rejected.
  The audit test confirms NaN propagates and +Inf is silently clipped.

### A08 — Metrics and output: NEEDS_REVIEW

Brier/log loss receive probabilities; F1 uses threshold 0.5 with `zero_division=0`;
ECE uses ten equal-width bins and skips empty bins (`run_experiment.py:196-220`). Tests
match sklearn on a fixture. `pr_auc` is computed using `average_precision_score`, not
trapezoidal PR area, so its name is ambiguous. The historical key is complete and
unique for 360 rows, but output lacks scenario class counts and target-prior provenance.
Aggregation groups by strategy, calibration, prevalence and correction
(`run_experiment.py:371-383`), so it does not collapse those scenarios into one row.

### A09 — Reproducibility: NEEDS_REVIEW

All identified random sources receive seeds: split, ROS, scenario sampler, and model.
A separate seed-42 smoke run reproduced historical rows exactly. Environment and hashes
are in `reproducibility_manifest.json`. Long-term reproducibility is incomplete because
`requirements.txt` specifies lower bounds rather than exact pins, no lockfile exists,
and the directory is not a Git worktree, so no commit SHA can identify the revision.

### A10 — Statistical traceability: NEEDS_REVIEW

Pairing pivots on seed within fixed strategy/calibration/prevalence conditions
(`audit_and_paired_analysis.py:81-103`). Difference is explicitly B−A and metric
direction is encoded at lines 42–78. Holm families are per comparison and metric
(`audit_and_paired_analysis.py:105-113`), with imbalance comparisons later corrected
together per metric. Ten repeated splits of one dataset are not independent population
samples; CI/p-values measure split sensitivity, not population generalizability. The
current statistical analysis also includes the invalid raw+correction branch, so it
cannot be the confirmatory primary analysis unchanged.

## Tests and smoke result

Command:

```text
.venv/bin/python -m unittest discover -s audit_stage1/tests -v
```

Result: **8 tests passed, exit code 0**. Controls covered: schema/target, split
isolation/size/determinism, train-only preprocessing, scenario subset/uniqueness/prior,
prior-correction math/bounds/current non-finite behavior, sklearn metric equivalence,
and historical key completeness.

Smoke command:

```text
.venv/bin/python run_experiment.py \
  --output audit_stage1/smoke_test_results/seed_42 --seeds 42
```

Result: **PASS**, 36 rows, columns equal, maximum numeric absolute difference 0.0,
all nonnumeric fields equal. Historical output was not overwritten.

## Impact on the 360 historical results

- Raw and Platt results without correction remain reproducible descriptive results.
- Platt+correction results are mathematically coherent under label-shift assumptions,
  but are **oracle-target-prior simulations** and must be labeled accordingly.
- The 90 raw+correction rows are exploratory/naive and must not support the primary
  confirmatory claim about theoretically valid prior correction.
- Because convergence metadata is absent, historical convergence is not fully proven;
  no convergence warning appeared during the reproducible smoke run.
- A full 10-seed rerun is not required merely to preserve the baseline, but the
  confirmatory 30-seed design must resolve A07 and metadata issues first.

## Decision and next action

**NO-GO** for confirmatory 30 seeds while A07-1 and A07-2 are unresolved. Approval
should be sought for the behavioral/design patch described in `proposed_fixes.md`.
After that patch, rerun the isolated tests, add a synthetic known-label-shift test,
prespecify primary statistical contrasts, and run a new smoke output before authorizing
the 30-seed experiment.

