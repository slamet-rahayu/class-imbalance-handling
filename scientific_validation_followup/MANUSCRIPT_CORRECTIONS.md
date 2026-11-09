# Manuscript Consistency Review

## Scope limitation

No standalone manuscript file or METHOD section was available. This review covers the method-bearing repository documents: `README.md`, both statistical analysis plans, `STAGE3_EXECUTION_REPORT.md`, `FINAL_EXECUTION_GATE_REPORT.md`, and the Stage-4 report/draft. Statements not present in those files are **UNVERIFIED**.

## Claim-by-claim assessment

| Topic / current claim | Status | Evidence and required action |
|---|---|---|
| Logistic Regression used liblinear, L2, C=1, max_iter=2000, seed-specific random state | **SUPPORTED** | Frozen source/config and regenerated predictions agree. |
| Numeric variables standardized; categorical variables one-hot encoded with unknown categories ignored; preprocessing fit on training only | **SUPPORTED** | `make_preprocessor` and `fit_model`; split reconstruction confirms isolation. |
| ROS is training-only | **SUPPORTED** | Applied after train-only transformation. |
| ROS “balances the classes” | **SUPPORTED**, but ratio should be explicit | `sampling_strategy="auto"` raises the minority count to the majority count; it does not generate a user-selected arbitrary ratio. |
| Class weighting uses “balanced” weighting | **SUPPORTED**, but formula should be explicit | Effective weight for class c is `n_samples/(2*n_c)` and is passed only to the base LR. |
| Platt scaling is fitted on an independent natural calibration split | **SUPPORTED** relative to train/test partitions | It is independent of that seed's train and test rows, not an independently sampled external dataset. |
| Platt scaling uses a raw model decision score | **INCORRECT** if stated | It fits LR to `logit(clip(base predict_proba, 1e-12, 1-1e-12))`. Do not describe this merely as an unspecified raw decision score. |
| Bayesian correction uses the source training prevalence or post-ROS prevalence | **INCORRECT** if stated | It uses the natural calibration-set prevalence for every branch. Raw corrected ROS/class-weight rows are explicitly naive/exploratory. |
| Target prevalence equals the requested decimal exactly | **NEEDS REVISION** | Correction uses the realized label mean after integer class-conditional subsampling, not the nominal target. Scenario sizes are 2,315, 2,464 and 1,528. |
| ECE uses ten equal-width bins | **SUPPORTED** | Boundaries are `[0,.1), …, [.9,1]`; internal-edge values enter the upper bin; empty bins contribute zero. |
| All Wilcoxon analyses use approximate p-values with no continuity correction | **INCORRECT** | H3 does; H1/H2 call SciPy defaults (`method="auto"`) and can use exact p-values. |
| Holm family is six H3 Brier tests | **SUPPORTED** numerically | The six values and adjustment exactly reproduce. |
| H1/H2 families are clearly the same as H3 | **INCORRECT** | H1 adjusts 27 contrasts per metric; H2 adjusts 9 per metric. AP/F1 also receive inferential tests despite being designated descriptive. |
| Thirty seeds are 30 independent replications | **INCORRECT** | Test splits share ~20% and training splits ~60% pairwise on average. |
| Wilcoxon/Holm decisions establish population statistical significance | **INCORRECT** | Underlying seed-level p-values lack independent sampling units; Holm does not repair that failure. |
| Intervals are population confidence intervals | **INCORRECT** if stated | They are at most descriptive split-schedule intervals; the plan partially acknowledges this. |
| H3 was prospectively preregistered/prespecified | **UNVERIFIED** | Local commits precede recorded output creation, but no independently immutable timestamp exists and the declared freeze time follows run start. |
| Metrics were directly verified from preserved primary predictions | **INCORRECT** historically; now **SUPPORTED** only for regenerated audit predictions | New audit exports reproduce all 3,240 Brier/log-loss/ECE values with zero tolerance failures. |

## Exact replacement wording

### Design and preprocessing

> For each seed, the dataset was partitioned by stratified sampling into 60% training, 20% natural calibration, and 20% test subsets. Numeric features were standardized and categorical features were one-hot encoded (`handle_unknown="ignore"`) using transformations fitted only on the training subset.

### Imbalance handling

> Random oversampling was applied only to transformed training data with `sampling_strategy="auto"`, duplicating minority-class training observations until the minority and majority counts were equal. The class-weighted model used scikit-learn's `balanced` weights, (w_c=n/(2n_c)), without resampling.

### Platt calibration

> For each fitted base model, a logistic calibration model (L2, C=1, lbfgs, max_iter=100) was fitted on the natural calibration subset using the logit of the base model's clipped predicted probability, `logit(clip(p,1e-12,1-1e-12))`, as its single input. The test subset was not used to fit either model.

### Prior correction and simulated prevalence

> Bayesian prior-odds correction used the natural calibration-set prevalence as the source prior and the realized positive fraction of each class-conditionally subsampled test scenario as the target prior. Because scenario counts are integers, realized prevalence need not equal the nominal target exactly. Correction of uncalibrated raw probabilities was retained only as a naive exploratory branch.

### ECE

> ECE was calculated with ten equal-width bins on [0,1]. Internal boundary values were assigned to the bin beginning at that boundary, empty bins contributed zero, and a probability of one was assigned to the final bin.

### Statistical procedure

> The archived H3 procedure calculated six two-sided Pratt Wilcoxon signed-rank statistics using SciPy's approximate method without continuity correction and applied one Holm adjustment across those six Brier-score comparisons. H1 and H2 tables used SciPy's default automatic Wilcoxon method and separate per-metric Holm families (27 H1 and 9 H2 contrasts per metric).

### Dependence and interpretation

> The 30 seed-level results are overlapping resplits of one dataset, not independent population replications. Their paired differences quantify sensitivity to the specified split schedule. The archived Wilcoxon and Holm values are reported for computational transparency, but their nominal p-values are not interpreted as valid population-level significance tests because seed-level independence is not satisfied.

### Chronology

> The H3 specification appears in local Git commits whose recorded timestamps precede preserved execution logs. No independently timestamped preregistration is available, and the freeze manifest's declared time follows the recorded run start; prospective preregistration therefore cannot be independently verified.

### Results language

Replace “five of six hypotheses were confirmed/rejected after Holm” with:

> In the 30 specified overlapping splits, prior correction reduced Brier score in all splits at target prevalence 0.25 for all three strategies. At target 0.10, the mean change was negligible for baseline and was a small deterioration for ROS and class weighting. These are descriptive repeated-split findings conditional on this dataset and design.

Replace “significant improvement” with “consistent split-wise reduction” unless a new defensible inferential design is completed.

