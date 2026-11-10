# Version 11 audit summary

**The implementation is partly consistent with version 11.** Tables 1–4 and the headline claims agree with the archived results. The Platt scaling description differs from the code in two places, and fresh runs in the tested environments show small differences from the archived metrics.

| Audit status | Checks |
|---|---:|
| PASS | 28 |
| FAIL | 5 |
| WARNING | 5 |
| NOT VERIFIED | 3 |
| **Total** | **41** |

The counts refer to rows in the [formula and implementation matrix](AUDIT_REPORT.md#formula-and-implementation-matrix). The five failures are the Platt clipping threshold, the Platt fitting objective, the freeze gate on the current Windows checkout, strict numerical replay on the tested environments, and the auxiliary v2 paired-analysis CLI.

## Methodology

The audit found no critical defect in partition isolation or the primary prior correction. All 30 stratified splits were row-disjoint with the stated sizes, and the fitting code kept preprocessing, oversampling, class weighting, and base fitting within training. Platt fitting used the calibration partition. The primary prior adjustment used the calibration prevalence and the realized target prevalence after Platt scaling, as disclosed in the manuscript. Brier score, log loss, and equal-width ECE matched independent calculations.

Version 11 §2.4 specifies Platt clipping at `1e-15` and describes minimization of binary log loss. The code clips at `1e-12` and fits an L2-penalized sigmoid with `C=1`. The archived raw predictions include values that reach the clipping guard. The printed sigmoid and the code's sigmoid are mathematically equivalent after negating both fitted coefficients in the manuscript notation.

Exact predictor matches crossed partitions for 1.31% of held-out observations on average, all negative, as disclosed in the manuscript. They are distinct from row overlap and fitting leakage. Real-time feature availability, exact provenance of the pooled reliability figure, and an independently timestamped prospective freeze could not be verified.

## Numerical reproducibility

The audit recalculated all 3,240 primary metric values from archived predictions and matched the per-seed results. At 0.155, raw ROS and CW increased mean Brier by 41.07% and 41.10%. Platt reduced their raw scores by 28.92% and 28.97%. At 0.25, prior correction reduced mean Brier by 8.51% to 9.08%, with 30/30 improvements for each strategy. At 0.10, baseline changed by −0.013% and ROS and CW worsened by about 0.47% and 0.48%. Mean log loss and ECE improved across all three strategies. Percentages are changes in aggregate means.

The frozen CLI completed all 30 seeds in a temporary Linux checkout with locked dependencies. The replay selected the same test rows and reproduced the headline effects and split counts. Three cells in Tables 3–4 differed at printed precision. The independent pytest suite returned **28 passed, 1 failed** on Windows and Linux. The single failure tests strict agreement with fresh fits. A prior repository report documents byte-for-byte replay on Python 3.15.0, which was unavailable for this audit.

Revise §2.4 to record the clipping threshold, L2 penalty, and fitting settings used for the reported results. The report also identifies reporting and replay details worth documenting, including the source for Figure 2 and the tested environment. The existing numerical claims require no model rerun for a documentation correction. Adopting a different clipping threshold or an unpenalized fit would require rerunning the affected experiment.

The [full report](AUDIT_REPORT.md) includes the pipeline map, source lines, numerical comparisons, execution commands, and dispositions. All audit additions are under `audit/`.
