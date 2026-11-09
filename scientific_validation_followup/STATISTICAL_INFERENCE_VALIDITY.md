# Statistical Dependence and Inferential Validity

## Finding

The six H3 effect summaries are valid as deterministic descriptive comparisons across the 30 specified splits. The nominal Wilcoxon p-values, Holm-adjusted p-values, and reject/do-not-reject decisions are **not validated as population-level inference** because the 30 paired differences are not independent sampling units.

## Reconstructed dependence

All splits were independently reconstructed from the dataset labels and frozen seeds. Each seed has 7,398 training, 2,466 calibration, and 2,466 test observations. Pairwise results across the 435 seed pairs are preserved in `PAIRWISE_SPLIT_OVERLAP.csv`.

| Set | Mean shared records | Range | Mean fraction of each set | Mean Jaccard |
|---|---:|---:|---:|---:|
| training | 4,438.86 | 4,353–4,509 | 60.00% | 42.86% |
| calibration | 493.24 | 449–544 | 20.00% | 11.11% |
| test | 493.02 | 451–548 | 19.99% | 11.11% |
| shifted test, target 0.10 | 444.20 | 406–507 | 19.19% | 10.61% |
| shifted test, target 0.155 | 492.22 | 450–546 | 19.98% | 11.10% |
| shifted test, target 0.25 | 202.43 | 167–241 | 13.25% | 7.10% |

Across 30 seeds, each original observation appears on average in 18 training sets, 6 calibration sets, and 6 test sets. Some observations appear in as many as 28 training sets and 16 test sets. Reuse counts are in `OBSERVATION_REUSE_COUNTS.csv`.

The dependence is stronger than test-set overlap alone suggests. Base models share most training observations, calibrators share calibration observations, and scenario evaluations reuse test observations. Therefore seed-level metric differences share fitted-model information and evaluation losses.

## Unit of analysis

The statistical unit used by the Wilcoxon tests is the seed/split-level Brier difference. A seed is an algorithmic randomization setting, not an independently sampled person, session, site, time period, or dataset. The source population contributes one finite dataset of 12,330 sessions. Thirty seeds increase information about sensitivity to the split algorithm; they do not create 30 independent population samples.

## Wilcoxon signed-rank assumptions

| Assumption | Assessment | Reason |
|---|---|---|
| Meaningful paired differences | **PASS** | Corrected and uncorrected predictions use the same shifted sample within a seed/strategy/scenario. |
| Independent pairs/differences | **FAIL** | Training, calibration and evaluation observations overlap extensively across seeds. |
| Differences sampled from the intended inferential population | **FAIL** for population claims | Seeds sample split assignments conditional on this dataset, not independent target-population datasets or observations. |
| Symmetry of the difference distribution under the signed-rank null | **NOT VERIFIED** | Thirty dependent differences do not provide a defensible independent sample for assessing this assumption. For 0.25, all differences have one sign. |
| Ordinal/continuous differences | **PASS** | Brier differences are numeric and rankable. |
| Correct zero handling and numerical implementation | **PASS** | Pratt/approx/two-sided/no-continuity settings reproduce exactly. |

The signed-rank test is not merely a test of a median without distributional conditions; its usual null calibration relies on independent, symmetrically distributed differences. That basis is not established here.

## Holm correction

Holm's procedure controls family-wise error under broad dependence among tests **when each input p-value is valid**. It does not turn invalid seed-level p-values into valid ones. Consequently, the Holm calculations are mathematically correct transformations of the six values but do not resolve the repeated-split dependence.

## Findings that remain valid

- The saved per-seed Brier scores and paired differences are exactly reproducible.
- At target 0.25, prior correction lowered Brier in all 30 splits for all three strategies, with mean changes of approximately −0.01039 to −0.01109.
- At target 0.10, mean change was near zero for baseline and approximately +0.00030 for oversampling/class weighting.
- Counts of positive/negative split-wise differences, means, empirical ranges, quantiles, and plots of the 30 specified values are valid descriptive summaries conditional on the dataset and split schedule.
- H1 and H2 tables can likewise be retained as descriptive repeated-split comparisons, subject to their separate method-disclosure issues.

Unsupported statements include “statistically significant in the target population,” “five hypotheses were confirmed,” population confidence-interval interpretations, and any claim that 30 seeds supply 30 independent replications.

## Can existing data support defensible inference?

The existing outputs cannot support the original Wilcoxon population claims. The raw dataset may support a **new, explicitly exploratory** analysis with observations or defensible clusters as sampling units, but that would be a different inferential design—not a repair of the frozen confirmatory test.

Potential designs require assumptions not currently verified:

- Observation-level paired loss analysis on genuinely out-of-sample, non-overlapping predictions could use sessions as units only if sessions are independent and the model-training contribution is handled by a justified cross-fitting/asymptotic argument. The UCI description says sessions correspond to different users, which helps but does not prove temporal/site independence.
- A cluster bootstrap would require meaningful independent clusters and rerunning the entire fitting/calibration/shift pipeline within each resample. No cluster variable or sampling frame is documented.
- Corrected repeated-cross-validation tests depend on approximations and design conditions; they should not be substituted automatically and would still characterize this dataset rather than external-dataset generalization.
- Permuting seed-level signs preserves the same invalid independence assumption and is not a solution.
- Treating all repeated predictions as independent would be pseudoreplication.

## Publication Strategy A — Conservative empirical evaluation

Retain the reproduced effect magnitudes and split-wise consistency. Remove inferential language based on Wilcoxon/Holm, or present those p-values only as historical protocol outputs explicitly labeled non-valid for population inference. Report means, medians, empirical quantiles/ranges, sign counts, and all 30 paired differences. Describe conclusions as conditional on this dataset, seed schedule, oracle-known label shift, and model specification.

| Criterion | Assessment |
|---|---|
| Credibility | Moderate, if limitations are explicit and “confirmatory/significant” language is removed |
| Effort | Low; uses verified existing outputs |
| Limitation | No population-level uncertainty or external validation; chronology remains inconclusive |

Minimum manuscript changes: call H3 a protocol-defined repeated-split analysis; replace rejection claims with descriptive consistency statements; label t intervals as split-distribution summaries or omit them; disclose observation reuse; state that Holm does not solve split dependence.

## Publication Strategy B — Strengthened statistical inference

Predefine an inferential sampling unit before new analysis. The strongest design is one or more independent temporal, site, or institution cohorts held untouched until the full pipeline is frozen. Fit and calibrate using development data; evaluate paired per-observation losses on independent target cohorts under naturally observed or prospectively specified shift conditions. If multiple sites/time cohorts are the intended population, treat those independent clusters as the replication units; otherwise use observation-level paired loss inference with a justified sampling model and uncertainty method.

An internal-only alternative is a newly specified cross-fitting design producing exactly one out-of-sample prediction per observation per compared method, with non-overlapping evaluation folds and inference based on paired observation-level losses. It must justify session independence, account for nuisance-model estimation, keep calibration training separate, and avoid presenting internal resampling as external generalization. This is weaker than external validation.

| Criterion | External cohort design | One-prediction-per-observation cross-fitting |
|---|---|---|
| Credibility | High for the represented target population | Moderate; depends on independence and asymptotic assumptions |
| Effort | High; requires new data and a prospective protocol | Moderate/high; requires a new analysis and methodological justification |
| Main limitation | Availability and comparability of external cohorts | Still one dataset; cannot validate deployment shift or broad transportability |

New data are genuinely necessary for strong external-generalizability claims. They are not necessary for Strategy A's explicitly conditional descriptive publication.

## Required-check status

| Check | Status |
|---|---|
| Exact pairing reconstruction | PASS |
| Cross-seed overlap quantified | PASS |
| Independence of seed-level pairs | FAIL |
| Wilcoxon numerical implementation | PASS |
| Wilcoxon inferential assumptions | FAIL / NOT VERIFIED as detailed above |
| Holm resolves dependence | FAIL |
| Descriptive retention of six H3 comparisons | PASS |
| Existing frozen outputs support population inference | FAIL |

