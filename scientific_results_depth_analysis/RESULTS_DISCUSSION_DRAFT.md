# Results and Discussion — Revision Draft

## 3.2 Effects of Imbalance Handling and Calibration

ROS versus Baseline at nominal 0.155: brier_score 0.085497 → 0.120614 (delta +0.035117; 30/30 worsened); log_loss 0.294588 → 0.442608 (delta +0.148020; 30/30 worsened); ece 0.037969 → 0.180434 (delta +0.142465; 30/30 worsened). CW versus Baseline at nominal 0.155: brier_score 0.085497 → 0.120634 (delta +0.035137; 30/30 worsened); log_loss 0.294588 → 0.442600 (delta +0.148012; 30/30 worsened); ece 0.037969 → 0.181019 (delta +0.143050; 30/30 worsened).

Baseline calibration at nominal 0.155: brier_score delta +0.000225 (+0.26%; 11/30 improved); log_loss delta +0.000360 (+0.12%; 12/30 improved); ece delta +0.000523 (+1.38%; 16/30 improved). ROS calibration at nominal 0.155: brier_score delta -0.034882 (-28.92%; 30/30 improved); log_loss delta -0.146228 (-33.04%; 30/30 improved); ece delta -0.133518 (-74.00%; 30/30 improved). CW calibration at nominal 0.155: brier_score delta -0.034952 (-28.97%; 30/30 improved); log_loss delta -0.146400 (-33.08%; 30/30 improved); ece delta -0.133787 (-73.91%; 30/30 improved).

These changes describe the thirty specified overlapping splits. Rebalancing altered raw probability performance, whereas fitting a separate probability mapping on the natural calibration sample reduced much of the observed error for ROS and CW. This pattern is compatible with, but does not demonstrate, a probability-scale explanation.

## 3.3 Prior Probability Correction

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

Negative paired differences denote improvement. The high- and low-prevalence scenarios should be interpreted separately rather than collapsed into an overall claim of benefit. Mean changes, variation, and directional counts are descriptive characteristics of this split schedule.

## 3.4 Discussion

ROS changes the class distribution seen during fitting and CW changes the weighted fitting objective. These mechanisms can change the probability scale relative to natural prevalence; the observed raw error increases are consistent with this explanation but do not isolate it causally. Platt calibration learns a new probability mapping on the natural calibration partition and can reduce these differences. Baseline already reflects natural training prevalence, and finite calibration data, model misspecification, and calibration regularization can plausibly limit or reverse its gain; none of these mechanisms was isolated here. Bayes correction is exact only under its source-probability and pure-label-shift assumptions. Imperfect source calibration and finite-sample variation can coexist with small worsening at low prevalence. Brier measures squared probability error, log loss penalizes confident errors strongly, and ECE averages bin discrepancies; disagreement does not identify a proven cause. For purchase prediction, validate probability quality and practical decision thresholds on appropriate target data rather than selecting a strategy from rebalancing or discrimination alone.

The reference-scenario pattern is qualitatively compatible with the calibration concerns reported by van den Goorbergh et al. (2022) and Piccininni et al. (2024). These studies evaluated clinical risk prediction and different correction designs; their findings do not directly validate the present purchase-prediction experiment. Ledwaba and Mokoena (2026), as reported in the publisher abstract, examined calibration and prior correction across multiple datasets and models. That broader setting offers context, not a replication of the present design. See LITERATURE_EVIDENCE.md for verified titles, authors, source sections, and scope limitations.

Thirty overlapping splits describe a finite dataset and fixed pipeline. Improvement counts are not population success probabilities. Oracle correction used realized test-subset prevalence, so unknown-prior deployment effectiveness was not evaluated. ECE is a bin-based estimate affected by sample size, bin boundaries and probability distribution; it is not a Brier decomposition. No universal superiority or causal mechanism is established. Freeze chronology remains inconclusive. Duplicate-valued rows and feature-availability risks remain as documented in PREPROCESSING_AUDIT_REPORT.md. No new fitting, resampling, simulations, or inferential procedures were performed.
