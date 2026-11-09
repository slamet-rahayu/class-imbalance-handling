# Confirmatory Statistical Analysis Plan v2 — Hardened Freeze

This document incorporates `STATISTICAL_ANALYSIS_PLAN.md` (`confirmatory-30seed-v1`)
in full and applies `PROTOCOL_AMENDMENT_v2.md`. Where execution-gate metadata differs,
this v2 document controls. Scientific hypotheses and analysis remain unchanged.

## Frozen scientific analysis

- H1: imbalance-handling effect, secondary.
- H2: Platt-calibration effect, secondary.
- H3: Platt prior-corrected versus Platt uncorrected Brier score, primary.
- Sole primary metric: Brier score.
- Primary family: six paired contrasts from three imbalance strategies crossed with
  target prevalences 0.10 and 0.25.
- Prevalence 0.155: descriptive control only.
- Test: two-sided paired Wilcoxon signed-rank, `zero_method="pratt"`,
  `method="approx"`, no continuity correction.
- Multiplicity: Holm adjustment across exactly the six H3 contrasts at alpha 0.05.
- Seeds: every integer 42–71.
- Target prior: oracle-known simulator prior; no unsupervised-deployment claim.
- Raw+correction: `naive_exploratory`, excluded from all confirmatory tests.

All tie, all-zero, incomplete-pair, effect-size, descriptive-interval, and dependence
rules in v1 remain binding.

## Hardened execution semantics

The canonical effective configuration is `confirmatory_protocol_v2.json`. Validation
must compare the entire effective configuration rather than only CLI-controlled fields.
This includes model, preprocessing, calibration, imbalance handling, metric, alias,
range, and statistical parameters.

Corrected rows must carry `target_prior_source="oracle_simulator"`. Uncorrected rows do
not consume a target prior and must carry `target_prior_source="not_applied"`. Scenario
audit metadata may still record that scenarios were created by the oracle simulator.

Every result row must contain finite Brier score, log loss, average precision, its
identical `pr_auc` compatibility alias, F1, ECE, mean predicted probability, actual
prevalence, and source prevalence. Each must satisfy the ranges frozen in the v2
protocol. Sample counts must be nonnegative and sum to `n_test`.

The execution gate requires both exact active Git HEAD equality and source-file hashes.
Any source or protocol change requires another documented amendment and new manifest.
The 30-seed experiment remains unauthorized during gate hardening.
