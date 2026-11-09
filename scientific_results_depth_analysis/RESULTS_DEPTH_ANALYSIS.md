# Scientific Results Depth Analysis

## 1. Executive Summary

Stored experiment data were complete and consistent: 30 seeds, 1,080 metric rows, 36 configurations and 3,240 verified metric comparisons. Main summaries contain 27 configurations; nine Raw + Prior configurations are exploratory. All additional comparisons are descriptive.

## 2. Data Sources and Verification

Primary file: outputs_confirmatory_30_seeds/all_repetitions.csv. Keys: seed, imbalance_strategy, target_prevalence, calibration, prior_correction; pairing adds sample_id_sha256 and validates sample counts. Metrics: brier_score, log_loss, ece. Row project_version=stage1-remediation-v1 is a source-code label; v2 identity is established by execution_manifest.json, protocol and source commit, not that label alone. No historical 10-seed outputs were pooled. aggregate_summary.csv means were checked against recomputed means. training_metadata.csv and all_audits.csv provide training/scenario counts; prediction files are regenerated audit outputs, not original contemporaneous exports. The existing notebook is a reporting consumer and was inspected without execution. No reference PDF/bibliography for the named studies was found in repository searches; online sources are documented separately.

Input hashes and execution metadata are recorded in VALIDATION_MANIFEST.json. Prediction manifest: 30 hashed files.

## 3. Supporting Metrics Results

ROS versus Baseline at nominal 0.155: brier_score 0.085497 → 0.120614 (delta +0.035117; 30/30 worsened); log_loss 0.294588 → 0.442608 (delta +0.148020; 30/30 worsened); ece 0.037969 → 0.180434 (delta +0.142465; 30/30 worsened).

CW versus Baseline at nominal 0.155: brier_score 0.085497 → 0.120634 (delta +0.035137; 30/30 worsened); log_loss 0.294588 → 0.442600 (delta +0.148012; 30/30 worsened); ece 0.037969 → 0.181019 (delta +0.143050; 30/30 worsened).

Baseline calibration at nominal 0.155: brier_score delta +0.000225 (+0.26%; 11/30 improved); log_loss delta +0.000360 (+0.12%; 12/30 improved); ece delta +0.000523 (+1.38%; 16/30 improved).

ROS calibration at nominal 0.155: brier_score delta -0.034882 (-28.92%; 30/30 improved); log_loss delta -0.146228 (-33.04%; 30/30 improved); ece delta -0.133518 (-74.00%; 30/30 improved).

CW calibration at nominal 0.155: brier_score delta -0.034952 (-28.97%; 30/30 improved); log_loss delta -0.146400 (-33.08%; 30/30 improved); ece delta -0.133787 (-73.91%; 30/30 improved).

Full scenario results and mean/SD/n are in SUPPORTING_METRICS_SUMMARY.csv and MANUSCRIPT_TABLES.md.

## 4. Paired Descriptive Variability

Baseline Platt + Prior vs Platt, target 0.10, brier_score: 0.064756 → 0.064748; delta -0.000008, SD 0.000648, median -0.000082, range [-0.001757, +0.001336], relative change -0.01%; improved/worsened/unchanged 16/14/0 (mixed).

Baseline Platt + Prior vs Platt, target 0.10, log_loss: 0.240310 → 0.231922; delta -0.008388, SD 0.002031, median -0.008167, range [-0.013123, -0.004677], relative change -3.49%; improved/worsened/unchanged 30/0/0 (all improved).

Baseline Platt + Prior vs Platt, target 0.10, ece: 0.043837 → 0.029888; delta -0.013950, SD 0.004990, median -0.014331, range [-0.024832, -0.004351], relative change -31.82%; improved/worsened/unchanged 30/0/0 (all improved).

Baseline Platt + Prior vs Platt, target 0.25, brier_score: 0.122106 → 0.111718; delta -0.010388, SD 0.001415, median -0.010433, range [-0.013261, -0.006160], relative change -8.51%; improved/worsened/unchanged 30/0/0 (all improved).

Baseline Platt + Prior vs Platt, target 0.25, log_loss: 0.390702 → 0.371397; delta -0.019305, SD 0.003735, median -0.019873, range [-0.025389, -0.010357], relative change -4.94%; improved/worsened/unchanged 30/0/0 (all improved).

Baseline Platt + Prior vs Platt, target 0.25, ece: 0.075469 → 0.052095; delta -0.023374, SD 0.007063, median -0.023618, range [-0.040166, -0.012167], relative change -30.97%; improved/worsened/unchanged 30/0/0 (all improved).

ROS Platt + Prior vs Platt, target 0.10, brier_score: 0.064694 → 0.064996; delta +0.000303, SD 0.000601, median +0.000308, range [-0.001490, +0.001501], relative change +0.47%; improved/worsened/unchanged 11/19/0 (mixed).

ROS Platt + Prior vs Platt, target 0.10, log_loss: 0.242335 → 0.233898; delta -0.008437, SD 0.002031, median -0.008090, range [-0.013074, -0.004753], relative change -3.48%; improved/worsened/unchanged 30/0/0 (all improved).

ROS Platt + Prior vs Platt, target 0.10, ece: 0.048156 → 0.034329; delta -0.013827, SD 0.004722, median -0.014228, range [-0.022146, -0.003611], relative change -28.71%; improved/worsened/unchanged 30/0/0 (all improved).

ROS Platt + Prior vs Platt, target 0.25, brier_score: 0.122199 → 0.111141; delta -0.011059, SD 0.001308, median -0.011200, range [-0.013591, -0.007090], relative change -9.05%; improved/worsened/unchanged 30/0/0 (all improved).

ROS Platt + Prior vs Platt, target 0.25, log_loss: 0.391188 → 0.371988; delta -0.019200, SD 0.003717, median -0.019660, range [-0.025130, -0.009977], relative change -4.91%; improved/worsened/unchanged 30/0/0 (all improved).

ROS Platt + Prior vs Platt, target 0.25, ece: 0.081865 → 0.064395; delta -0.017470, SD 0.005859, median -0.017632, range [-0.032100, -0.005507], relative change -21.34%; improved/worsened/unchanged 30/0/0 (all improved).

CW Platt + Prior vs Platt, target 0.10, brier_score: 0.064666 → 0.064975; delta +0.000309, SD 0.000611, median +0.000295, range [-0.001441, +0.001598], relative change +0.48%; improved/worsened/unchanged 11/19/0 (mixed).

CW Platt + Prior vs Platt, target 0.10, log_loss: 0.242252 → 0.233826; delta -0.008426, SD 0.002055, median -0.008091, range [-0.013114, -0.004594], relative change -3.48%; improved/worsened/unchanged 30/0/0 (all improved).

CW Platt + Prior vs Platt, target 0.10, ece: 0.048042 → 0.034716; delta -0.013326, SD 0.005115, median -0.014046, range [-0.022858, -0.001846], relative change -27.74%; improved/worsened/unchanged 30/0/0 (all improved).

CW Platt + Prior vs Platt, target 0.25, brier_score: 0.122125 → 0.111037; delta -0.011088, SD 0.001317, median -0.011265, range [-0.013552, -0.007154], relative change -9.08%; improved/worsened/unchanged 30/0/0 (all improved).

CW Platt + Prior vs Platt, target 0.25, log_loss: 0.390905 → 0.371695; delta -0.019211, SD 0.003730, median -0.019705, range [-0.025203, -0.010168], relative change -4.91%; improved/worsened/unchanged 30/0/0 (all improved).

CW Platt + Prior vs Platt, target 0.25, ece: 0.082328 → 0.064104; delta -0.018224, SD 0.005636, median -0.018063, range [-0.029820, -0.005805], relative change -22.14%; improved/worsened/unchanged 30/0/0 (all improved).

All additional comparisons span all three prevalences, yielding 63 comparison–scenario–metric rows and 1,890 recorded seed-level differences. The relative-change denominator is the mean reference metric, not the comparator or the mean of per-seed ratios.

## 5. Consistency Across Repeated Splits

| comparison | target_prevalence | metric | splits_improved | splits_worsened | splits_unchanged | direction_pattern |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline Platt + Prior vs Platt | 0.100000 | brier_score | 16 | 14 | 0 | mixed |
| Baseline Platt + Prior vs Platt | 0.100000 | log_loss | 30 | 0 | 0 | all improved |
| Baseline Platt + Prior vs Platt | 0.100000 | ece | 30 | 0 | 0 | all improved |
| Baseline Platt + Prior vs Platt | 0.250000 | brier_score | 30 | 0 | 0 | all improved |
| Baseline Platt + Prior vs Platt | 0.250000 | log_loss | 30 | 0 | 0 | all improved |
| Baseline Platt + Prior vs Platt | 0.250000 | ece | 30 | 0 | 0 | all improved |
| Baseline Platt vs Raw | 0.100000 | brier_score | 14 | 16 | 0 | mixed |
| Baseline Platt vs Raw | 0.100000 | log_loss | 16 | 14 | 0 | mixed |
| Baseline Platt vs Raw | 0.100000 | ece | 14 | 16 | 0 | mixed |
| Baseline Platt vs Raw | 0.155000 | brier_score | 11 | 19 | 0 | mixed |
| Baseline Platt vs Raw | 0.155000 | log_loss | 12 | 18 | 0 | mixed |
| Baseline Platt vs Raw | 0.155000 | ece | 16 | 14 | 0 | mixed |
| Baseline Platt vs Raw | 0.250000 | brier_score | 11 | 19 | 0 | mixed |
| Baseline Platt vs Raw | 0.250000 | log_loss | 14 | 16 | 0 | mixed |
| Baseline Platt vs Raw | 0.250000 | ece | 11 | 19 | 0 | mixed |
| ROS Platt + Prior vs Platt | 0.100000 | brier_score | 11 | 19 | 0 | mixed |
| ROS Platt + Prior vs Platt | 0.100000 | log_loss | 30 | 0 | 0 | all improved |
| ROS Platt + Prior vs Platt | 0.100000 | ece | 30 | 0 | 0 | all improved |
| ROS Platt + Prior vs Platt | 0.250000 | brier_score | 30 | 0 | 0 | all improved |
| ROS Platt + Prior vs Platt | 0.250000 | log_loss | 30 | 0 | 0 | all improved |
| ROS Platt + Prior vs Platt | 0.250000 | ece | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.100000 | brier_score | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.100000 | log_loss | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.100000 | ece | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.155000 | brier_score | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.155000 | log_loss | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.155000 | ece | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.250000 | brier_score | 17 | 13 | 0 | mixed |
| ROS Platt vs Raw | 0.250000 | log_loss | 30 | 0 | 0 | all improved |
| ROS Platt vs Raw | 0.250000 | ece | 30 | 0 | 0 | all improved |
| CW Platt + Prior vs Platt | 0.100000 | brier_score | 11 | 19 | 0 | mixed |
| CW Platt + Prior vs Platt | 0.100000 | log_loss | 30 | 0 | 0 | all improved |
| CW Platt + Prior vs Platt | 0.100000 | ece | 30 | 0 | 0 | all improved |
| CW Platt + Prior vs Platt | 0.250000 | brier_score | 30 | 0 | 0 | all improved |
| CW Platt + Prior vs Platt | 0.250000 | log_loss | 30 | 0 | 0 | all improved |
| CW Platt + Prior vs Platt | 0.250000 | ece | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.100000 | brier_score | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.100000 | log_loss | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.100000 | ece | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.155000 | brier_score | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.155000 | log_loss | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.155000 | ece | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.250000 | brier_score | 17 | 13 | 0 | mixed |
| CW Platt vs Raw | 0.250000 | log_loss | 30 | 0 | 0 | all improved |
| CW Platt vs Raw | 0.250000 | ece | 30 | 0 | 0 | all improved |
| ROS Raw vs Baseline Raw | 0.100000 | brier_score | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.100000 | log_loss | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.100000 | ece | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.155000 | brier_score | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.155000 | log_loss | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.155000 | ece | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.250000 | brier_score | 10 | 20 | 0 | mixed |
| ROS Raw vs Baseline Raw | 0.250000 | log_loss | 0 | 30 | 0 | all worsened |
| ROS Raw vs Baseline Raw | 0.250000 | ece | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.100000 | brier_score | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.100000 | log_loss | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.100000 | ece | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.155000 | brier_score | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.155000 | log_loss | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.155000 | ece | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.250000 | brier_score | 10 | 20 | 0 | mixed |
| CW Raw vs Baseline Raw | 0.250000 | log_loss | 0 | 30 | 0 | all worsened |
| CW Raw vs Baseline Raw | 0.250000 | ece | 0 | 30 | 0 | all worsened |

### Agreement with Brier direction

| comparison | target_prevalence | supporting_metric | brier_mean_delta | supporting_mean_delta | mean_direction_agrees |
| --- | --- | --- | --- | --- | --- |
| Baseline Platt + Prior vs Platt | 0.100000 | log_loss | -0.000008 | -0.008388 | True |
| Baseline Platt + Prior vs Platt | 0.100000 | ece | -0.000008 | -0.013950 | True |
| Baseline Platt + Prior vs Platt | 0.250000 | log_loss | -0.010388 | -0.019305 | True |
| Baseline Platt + Prior vs Platt | 0.250000 | ece | -0.010388 | -0.023374 | True |
| CW Platt + Prior vs Platt | 0.100000 | log_loss | 0.000309 | -0.008426 | False |
| CW Platt + Prior vs Platt | 0.100000 | ece | 0.000309 | -0.013326 | False |
| CW Platt + Prior vs Platt | 0.250000 | log_loss | -0.011088 | -0.019211 | True |
| CW Platt + Prior vs Platt | 0.250000 | ece | -0.011088 | -0.018224 | True |
| ROS Platt + Prior vs Platt | 0.100000 | log_loss | 0.000303 | -0.008437 | False |
| ROS Platt + Prior vs Platt | 0.100000 | ece | 0.000303 | -0.013827 | False |
| ROS Platt + Prior vs Platt | 0.250000 | log_loss | -0.011059 | -0.019200 | True |
| ROS Platt + Prior vs Platt | 0.250000 | ece | -0.011059 | -0.017470 | True |

## 6. Comparison with Previous Studies

# Literature evidence and scope

Verified against online primary sources on 7 November 2026. No named reference full text or bibliography was found locally; repository PDFs were generated figures. Evidence below is restricted to the source sections actually inspected. Published findings were not independently reproduced, and source availability does not certify study quality.

## van den Goorbergh et al. (2022)

Ruben van den Goorbergh, Maarten van Smeden, Dirk Timmerman, and Ben Van Calster. *The harm of class imbalance corrections for risk prediction models: illustration and simulation using logistic regression*. Journal of the American Medical Informatics Association, 29(9), 1525–1534. DOI: 10.1093/jamia/ocac093.

Evidence: [PubMed author abstract](https://pubmed.ncbi.nlm.nih.gov/35686364/), Abstract—Objective, Material and methods, Results; [publisher Discussion](https://academic.oup.com/jamia/article/29/9/1525/6605096?login=false). The authors evaluated standard/ridge LR using simulations and ovarian-cancer data, comparing no correction, random under/oversampling, and SMOTE. They reported minority-risk overestimation without better AUROC after correction. The current raw ROS pattern is qualitatively compatible. CW, purchase prediction, independent Platt calibration, and oracle target shift differ from those comparisons; no equality of effect sizes is asserted.

## Piccininni et al. (2024)

Marco Piccininni, Maximilian Wechsung, Ben Van Calster, Jessica L. Rohmann, Stefan Konigorski, and Maarten van Smeden. *Understanding random resampling techniques for class imbalance correction and their consequences on calibration and discrimination of clinical risk prediction models*. Journal of Biomedical Informatics, 155, 104666. DOI: 10.1016/j.jbi.2024.104666.

Evidence: [UMC Utrecht institutional publication record](https://researchinformation.umcutrecht.nl/en/publications/understanding-random-resampling-techniques-for-class-imbalance-co/), Abstract—Methods/Results and bibliographic section. Mathematical reasoning, two simulation mechanisms, and International Stroke Trial data examined LR/tree models and a plug-in correction for artificial balancing. The abstract reports better calibration with the correction while retaining discrimination. This contextualizes probability adjustment but is not the same as Platt followed by oracle target-prior correction here. Detailed tables were not inspected; no numerical cross-study comparison is made.

## Ledwaba and Mokoena (2026)

Kagiso Ledwaba and Tshepo Mokoena. *Probability Calibration Under Class-Prevalence Shift: A Reproducible Multi-Dataset Stress Test*. Interdisciplinary Journal of AI, Machine Learning & Data Science, 1(3), e012. Published 26 October 2026. DOI displayed by publisher: 10.66261/73c9df20.

Evidence: [publisher article page](https://ijaimlds.com/ijaimlds/article/view/113), Abstract, Data Availability Statement, How to Cite. The abstract describes three UCI datasets (breast cancer, wine, digits), LR/random forests/histogram boosting, 20 repetitions, separate calibration pools, Platt/isotonic calibration, and prevalence resampling. It reports overall probability improvements following correction. This provides related context; the full text and underlying data were not examined, and the present low-prevalence deterioration cautions against treating an overall literature result as universal. DOI registration and affiliations were not independently authenticated beyond the publisher record.

## Separation of evidence

- Current-experiment facts: computed solely from stored per-seed metrics and recorded separately in the generated CSVs.
- Previous-study findings: limited to the accessible author abstracts and identified sections above.
- Explanatory hypotheses: shifts in the fitted probability scale, finite calibration variability, regularization, and imperfect label-shift assumptions are possible mechanisms; this analysis does not isolate them experimentally.


## 7. Scientific Interpretation

ROS changes the class distribution seen during fitting and CW changes the weighted fitting objective. These mechanisms can change the probability scale relative to natural prevalence; the observed raw error increases are consistent with this explanation but do not isolate it causally. Platt calibration learns a new probability mapping on the natural calibration partition and can reduce these differences. Baseline already reflects natural training prevalence, and finite calibration data, model misspecification, and calibration regularization can plausibly limit or reverse its gain; none of these mechanisms was isolated here. Bayes correction is exact only under its source-probability and pure-label-shift assumptions. Imperfect source calibration and finite-sample variation can coexist with small worsening at low prevalence. Brier measures squared probability error, log loss penalizes confident errors strongly, and ECE averages bin discrepancies; disagreement does not identify a proven cause. For purchase prediction, validate probability quality and practical decision thresholds on appropriate target data rather than selecting a strategy from rebalancing or discrimination alone.

## 8. Limitations of the Analysis

Thirty overlapping splits describe a finite dataset and fixed pipeline. Improvement counts are not population success probabilities. Oracle correction used realized test-subset prevalence, so unknown-prior deployment effectiveness was not evaluated. ECE is a bin-based estimate affected by sample size, bin boundaries and probability distribution; it is not a Brier decomposition. No universal superiority or causal mechanism is established. Freeze chronology remains inconclusive. Duplicate-valued rows and feature-availability risks remain as documented in PREPROCESSING_AUDIT_REPORT.md. No new fitting, resampling, simulations, or inferential procedures were performed.

## 9. Recommended Manuscript Revisions

Add Table A for reference calibration and Table B for paired correction effects. Report delta SD and full empirical range as split variability. Keep Raw + Prior in the exploratory supplement. Distinguish mean-direction agreement from all-split agreement. Use author–year citations only within the evidence scope stated in LITERATURE_EVIDENCE.md. Avoid equating low ECE with complete calibration or low Brier.

## 10. Final Conclusions

The stored results support a prevalence-dependent descriptive account of probability quality. Supporting metrics can agree in direction with Brier in some conditions and disagree in others; the explicit counts and differences above preserve this distinction. The findings characterize this dataset and pipeline, without population inference.
