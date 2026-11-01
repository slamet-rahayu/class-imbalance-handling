# Stage 1 Remediation Change Log

## P1 — Confirmatory path separation

- Added `evaluation_path`, `prior_correction_validity`, and
  `confirmatory_analysis` to every result row.
- `Platt + correction` is `primary_prior_correction` and
  `calibrated_confirmatory`.
- Every `raw + correction` branch is `naive_exploratory` and excluded from
  confirmatory analysis.
- Updated statistical analysis to detect remediated output and select only valid paths.

## P2 — Target prior provenance

- Added `target_prior_source="oracle_simulator"` to results and scenario audits.
- Added `source_prior_basis="natural_calibration_set"`.
- Confirmatory plan explicitly limits inference to oracle-known prior simulation.

## P3 — Correction validation

- Reject non-finite probabilities, probabilities outside `[0,1]`, non-finite priors,
  and priors outside `(0,1)`.
- Added boundary, identity, direction, and synthetic known-label-shift tests.

## P4 — Audit metadata

- Added positive/negative/total scenario counts and stable sample hash.
- Added pre/post-ROS counts and prevalence.
- Added derived class weights.
- Added base/calibrator iteration counts, maximum iterations, convergence flags, and
  convergence-warning flags.
- Added combined `training_metadata.csv` output.

## P5 — Metric and statistical naming

- Added canonical `average_precision` field.
- Retained `pr_auc` as a value-identical historical compatibility alias.
- Removed hard-coded 10-seed/360-row validation from statistical analysis.
- Added `STATISTICAL_ANALYSIS_PLAN.md` and confirmatory-path filtering.

## P6 — Reproducibility and provenance

- Added official UCI identifier, URL, DOI, citation, and CC BY 4.0 license.
- Added local dataset SHA-256 and runtime `dataset_provenance.json`.
- Added exact `requirements-lock.txt`.
- Added project version and source/hash manifest.
- Initialized local version control and committed source snapshot
  `f333c3caf10add20e66b4c164b2b6116b7c7b40d`.
- Original local download date remains explicitly `not_recorded`.

## Historical preservation

No file in `outputs_10_seeds/` or `audit_results_10_seeds/` was modified. Seed-42
smoke predictions and metrics match all historical common columns exactly.

