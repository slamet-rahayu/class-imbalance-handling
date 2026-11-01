# Confirmatory Statistical Analysis Plan (30 Seeds — Draft)

This plan must be frozen before the 30-seed run.

## Primary path and estimand

- Primary correction path: `Platt + prior correction`.
- Comparator: the same Platt-calibrated model without correction, paired by seed,
  imbalance strategy, and prevalence scenario.
- Target prior provenance: `oracle_simulator`; conclusions concern an oracle-known
  prior-shift simulation, not unsupervised deployment estimation.
- `raw + correction` is `naive_exploratory` and excluded from confirmatory hypothesis
  testing.

## Primary metrics

- Brier score and log loss: lower is better.
- ECE is secondary because of binning sensitivity.
- Average precision and F1@0.5 are descriptive discrimination/decision metrics.

## Pairing and multiplicity

- Pair on identical seed, split, scenario hash, imbalance strategy, and prevalence.
- Primary test: two-sided Wilcoxon signed-rank; paired mean difference, 95% CI, and
  Cohen's dz reported descriptively.
- Holm correction is applied across the prespecified prevalence × imbalance contrasts
  separately for each primary metric.
- Repeated splits of one dataset quantify split sensitivity and are not independent
  population samples; no population-generalization claim will be based on seed CIs.

