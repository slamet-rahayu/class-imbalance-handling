# Confirmatory Statistical Analysis Plan — Frozen Protocol

**Protocol version:** `confirmatory-30seed-v1`  
**Status:** Frozen before execution  
**Experiment execution:** Not yet performed

## 1. Scientific scope and assumptions

This experiment evaluates probability reliability under a simulated, oracle-known
class-prior shift. Shifted scenarios are created by class-conditional subsampling from
the test pool. The design therefore assumes

\[
P_{target}(X\mid Y)=P_{source}(X\mid Y),
\]

and does not claim that production shift has been observed or that the target prior can
be estimated without labels. Every corrected row must contain
`target_prior_source="oracle_simulator"`.

The only confirmatory prior-correction path is `Platt + prior correction`. All
`raw + prior correction` results have `evaluation_path="naive_exploratory"`, are
excluded before any confirmatory test, and cannot support H1–H3.

## 2. Frozen design

- Dataset: UCI Online Shoppers Purchasing Intention, local SHA-256 recorded in the
  freeze manifest.
- Seeds: every integer from **42 through 71 inclusive**, in ascending order (30 seeds).
- Split per seed: stratified 60% train, 20% natural calibration, 20% test.
- Imbalance strategies: `baseline`, `oversampling`, `class_weight`.
- Calibration conditions: `raw`, `platt`.
- Target prevalences: `0.10`, `0.155`, `0.25`.
- Prior source for the primary path: prevalence of the natural calibration set.
- Prior target: exact realized prevalence of the simulated shifted test subset, with
  provenance `oracle_simulator`.
- Probability threshold for F1: 0.5; ECE: 10 equal-width bins.
- Model and preprocessing parameters are frozen in `confirmatory_protocol.json`.

Pairing requires identical seed, split, imbalance strategy, target prevalence, and
scenario sample hash. A row is not a valid pair merely because its seed matches.

## 3. Hypotheses

### H1 — Effect of imbalance handling (secondary scientific hypothesis)

Within each prespecified calibration/shift condition, probability reliability differs
between at least two of `baseline`, `oversampling`, and `class_weight`.

- Null: paired Brier-score differences between strategies are centered at zero.
- Alternative: at least one paired strategy contrast is not centered at zero.
- Status: secondary; pairwise results are reported with multiplicity clearly separated
  from the H3 primary family.

### H2 — Effect of Platt calibration (secondary scientific hypothesis)

For a fixed seed, imbalance strategy, and prevalence scenario, Brier score differs
between `raw` and `platt` probabilities without prior correction.

- Null: paired difference `Brier_platt - Brier_raw` is centered at zero.
- Alternative: the paired difference is not centered at zero.
- Expected direction, not used to make the test one-sided: Platt has lower Brier score.
- Status: secondary.

### H3 — Effect of prior correction after Platt calibration (primary hypothesis)

For Platt-calibrated probabilities under a shifted prior, Brier score differs between
prior-corrected and uncorrected probabilities.

- Null for each contrast: paired difference
  \(d=Brier_{Platt+correction}-Brier_{Platt}\) is centered at zero.
- Alternative: the paired difference is not centered at zero.
- Expected direction, not used to make the test one-sided: \(d<0\).
- **H3 is the sole primary confirmatory hypothesis.**

## 4. Primary metric and family

The **Brier score is the sole primary metric**. Lower is better.

The primary family contains exactly six paired H3 contrasts:

| Contrast | Imbalance strategy | Target prevalence |
|---:|---|---:|
| 1 | baseline | 0.10 |
| 2 | oversampling | 0.10 |
| 3 | class_weight | 0.10 |
| 4 | baseline | 0.25 |
| 5 | oversampling | 0.25 |
| 6 | class_weight | 0.25 |

Target prevalence `0.155` is a **control scenario** because it approximates the natural
source prior. It is summarized descriptively and is not included in any primary
hypothesis test or in the six-test Holm family.

Log loss and ECE are secondary metrics. Their estimates and clearly labeled secondary
tests may be reported, but they do not alter the H3 decision. Average precision and
F1@0.5 are descriptive only.

## 5. Primary test and multiplicity

For each of the six contrasts:

1. construct 30 complete pairs using the frozen seeds and identical sample hashes;
2. calculate corrected-minus-uncorrected Brier differences;
3. apply a two-sided paired Wilcoxon signed-rank test with `zero_method="pratt"`,
   `method="approx"`, and no continuity correction;
4. adjust the six raw p-values together using Holm's step-down procedure;
5. reject the contrast-specific null when Holm-adjusted `p < 0.05`.

No contrast, metric, prevalence, or multiplicity family may be added or removed after
examining the confirmatory results without declaring a protocol deviation.

## 6. Data-quality and edge-case rules

- **Ties/zero differences:** retain zero differences and use Pratt handling. Report the
  number of positive, negative, and zero differences.
- **All-zero differences:** return Wilcoxon statistic 0, raw p-value 1, adjusted
  p-value 1, mean difference 0, and both effect sizes 0. Do not call scipy's test for
  this case.
- **Non-finite metrics:** fail the confirmatory analysis; do not drop, replace, winsorize,
  or impute the affected observation.
- **Incomplete pairs:** fail the confirmatory analysis if any expected seed is absent,
  duplicated, has a different scenario hash across the pair, or lacks either corrected
  or uncorrected Platt output. No complete-case subset analysis is confirmatory.
- **Unexpected rows:** `naive_exploratory` rows may coexist in raw output but are
  filtered before testing. Any row falsely labeled confirmatory causes validation
  failure.
- **Protocol mismatch:** the run must be rejected before output creation when its
  runtime configuration differs from the frozen protocol.

## 7. Estimation and reporting

For every primary contrast report:

- means for corrected and uncorrected Brier scores;
- paired mean difference `corrected - uncorrected`;
- a 95% t-based interval for the paired mean difference, explicitly labeled
  **descriptive interval** rather than a population confidence interval;
- Cohen's \(d_z=\bar d/s_d\);
- matched-pairs rank-biserial correlation, with zero ranks omitted from its denominator;
- counts of negative, positive, and zero differences;
- Wilcoxon statistic, raw p-value, Holm-adjusted p-value, and decision.

The 30 seeds are overlapping repeated splits of one dataset, not 30 independent samples
from a population. Consequently, intervals and effect sizes describe sensitivity to
these splits only. They must not be presented as population-generalizable uncertainty.

## 8. Secondary and descriptive reporting

- H1 and H2 are secondary and cannot override the H3 conclusion.
- Log loss and ECE use the same pairing checks; any p-values are labeled secondary and
  corrected within their own explicitly named families, never mixed with H3.
- The 0.155 control scenario is reported with paired means/differences and effect sizes,
  but no confirmatory p-value.
- Average precision and F1 are descriptive. `pr_auc` is a compatibility alias only.
- Exploratory raw+correction results, if shown, appear in a separate section with no
  confirmatory p-values.

## 9. Freeze and execution gate

`confirmatory_protocol.json` is the machine-readable configuration. The freeze manifest
must contain:

- source Git commit;
- dataset SHA-256;
- exact dependency versions;
- canonical configuration SHA-256;
- this statistical plan's SHA-256.

Every confirmatory invocation must use both `--confirmatory` and
`--protocol-manifest confirmatory_protocol_freeze.json`. `protocol_validation.py`
validates the runtime configuration, source snapshot, dataset, dependencies, plan, and
protocol hashes before the experiment output directory is created. Any mismatch is a
hard failure and must be resolved as a documented protocol amendment—not bypassed.

The authorized seed schedule is 42–71. This document freezes the protocol but does not
authorize Codex to run the experiment during plan-finalization work.

