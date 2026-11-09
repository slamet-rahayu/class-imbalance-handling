# Manuscript Tables

## Table A. Probability performance at nominal reference prevalence 0.155

| strategy | target_prevalence | configuration | n_splits | brier_score_mean | brier_score_sd | log_loss_mean | log_loss_sd | ece_mean | ece_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.155000 | Platt | 30 | 0.085722 | 0.002525 | 0.294948 | 0.009954 | 0.038493 | 0.007359 |
| baseline | 0.155000 | Raw | 30 | 0.085497 | 0.002330 | 0.294588 | 0.009846 | 0.037969 | 0.006127 |
| class_weight | 0.155000 | Platt | 30 | 0.085682 | 0.002531 | 0.296200 | 0.010058 | 0.047231 | 0.007539 |
| class_weight | 0.155000 | Raw | 30 | 0.120634 | 0.003092 | 0.442600 | 0.015282 | 0.181019 | 0.005690 |
| oversampling | 0.155000 | Platt | 30 | 0.085732 | 0.002502 | 0.296380 | 0.010047 | 0.046916 | 0.007567 |
| oversampling | 0.155000 | Raw | 30 | 0.120614 | 0.003286 | 0.442608 | 0.015648 | 0.180434 | 0.006288 |

## Table B. Effects of prior correction on probabilistic performance

| comparison | target_prevalence | metric | mean_reference | mean_comparator | mean_paired_difference | sd_paired_difference | splits_improved | splits_worsened | splits_unchanged | relative_change_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline Platt + Prior vs Platt | 0.100000 | brier_score | 0.064756 | 0.064748 | -0.000008 | 0.000648 | 16 | 14 | 0 | -0.012757 |
| Baseline Platt + Prior vs Platt | 0.100000 | log_loss | 0.240310 | 0.231922 | -0.008388 | 0.002031 | 30 | 0 | 0 | -3.490333 |
| Baseline Platt + Prior vs Platt | 0.100000 | ece | 0.043837 | 0.029888 | -0.013950 | 0.004990 | 30 | 0 | 0 | -31.821317 |
| Baseline Platt + Prior vs Platt | 0.250000 | brier_score | 0.122106 | 0.111718 | -0.010388 | 0.001415 | 30 | 0 | 0 | -8.507325 |
| Baseline Platt + Prior vs Platt | 0.250000 | log_loss | 0.390702 | 0.371397 | -0.019305 | 0.003735 | 30 | 0 | 0 | -4.941095 |
| Baseline Platt + Prior vs Platt | 0.250000 | ece | 0.075469 | 0.052095 | -0.023374 | 0.007063 | 30 | 0 | 0 | -30.971037 |
| ROS Platt + Prior vs Platt | 0.100000 | brier_score | 0.064694 | 0.064996 | 0.000303 | 0.000601 | 11 | 19 | 0 | 0.467974 |
| ROS Platt + Prior vs Platt | 0.100000 | log_loss | 0.242335 | 0.233898 | -0.008437 | 0.002031 | 30 | 0 | 0 | -3.481574 |
| ROS Platt + Prior vs Platt | 0.100000 | ece | 0.048156 | 0.034329 | -0.013827 | 0.004722 | 30 | 0 | 0 | -28.713267 |
| ROS Platt + Prior vs Platt | 0.250000 | brier_score | 0.122199 | 0.111141 | -0.011059 | 0.001308 | 30 | 0 | 0 | -9.049870 |
| ROS Platt + Prior vs Platt | 0.250000 | log_loss | 0.391188 | 0.371988 | -0.019200 | 0.003717 | 30 | 0 | 0 | -4.908150 |
| ROS Platt + Prior vs Platt | 0.250000 | ece | 0.081865 | 0.064395 | -0.017470 | 0.005859 | 30 | 0 | 0 | -21.339871 |
| CW Platt + Prior vs Platt | 0.100000 | brier_score | 0.064666 | 0.064975 | 0.000309 | 0.000611 | 11 | 19 | 0 | 0.477486 |
| CW Platt + Prior vs Platt | 0.100000 | log_loss | 0.242252 | 0.233826 | -0.008426 | 0.002055 | 30 | 0 | 0 | -3.478300 |
| CW Platt + Prior vs Platt | 0.100000 | ece | 0.048042 | 0.034716 | -0.013326 | 0.005115 | 30 | 0 | 0 | -27.738208 |
| CW Platt + Prior vs Platt | 0.250000 | brier_score | 0.122125 | 0.111037 | -0.011088 | 0.001317 | 30 | 0 | 0 | -9.079093 |
| CW Platt + Prior vs Platt | 0.250000 | log_loss | 0.390905 | 0.371695 | -0.019211 | 0.003730 | 30 | 0 | 0 | -4.914433 |
| CW Platt + Prior vs Platt | 0.250000 | ece | 0.082328 | 0.064104 | -0.018224 | 0.005636 | 30 | 0 | 0 | -22.135902 |

Baseline: unweighted logistic regression; ROS: random oversampling; CW: class weighting; ECE: 10-bin equal-width expected calibration error; SD: sample standard deviation (ddof=1). Means and SDs describe 30 overlapping repetitions, not population inference. Delta = comparator minus reference; negative changes indicate improvement. Relative change = 100 × (mean comparator − mean reference) / mean reference. Use six decimal places for manuscript scores/SDs and two for percentage changes; retain full precision in CSV. Counts are exact integer counts, and unchanged means exact zero in stored values. Table A uses nominal 0.155, distinct from the source prevalence and realized scenario prevalence.

## Supplementary Table C. Full main descriptive summaries

| strategy | target_prevalence | configuration | analysis_scope | n_splits | brier_score_mean | brier_score_sd | log_loss_mean | log_loss_sd | ece_mean | ece_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.100000 | Platt | main | 30 | 0.064756 | 0.002199 | 0.240310 | 0.008985 | 0.043837 | 0.005116 |
| baseline | 0.100000 | Platt + Prior | main | 30 | 0.064748 | 0.002249 | 0.231922 | 0.008871 | 0.029888 | 0.005416 |
| baseline | 0.100000 | Raw | main | 30 | 0.064699 | 0.002298 | 0.240262 | 0.008732 | 0.042860 | 0.003771 |
| baseline | 0.155000 | Platt | main | 30 | 0.085722 | 0.002525 | 0.294948 | 0.009954 | 0.038493 | 0.007359 |
| baseline | 0.155000 | Platt + Prior | main | 30 | 0.085707 | 0.002523 | 0.294946 | 0.009953 | 0.038411 | 0.007281 |
| baseline | 0.155000 | Raw | main | 30 | 0.085497 | 0.002330 | 0.294588 | 0.009846 | 0.037969 | 0.006127 |
| baseline | 0.250000 | Platt | main | 30 | 0.122106 | 0.004254 | 0.390702 | 0.014180 | 0.075469 | 0.007472 |
| baseline | 0.250000 | Platt + Prior | main | 30 | 0.111718 | 0.003726 | 0.371397 | 0.013239 | 0.052095 | 0.010974 |
| baseline | 0.250000 | Raw | main | 30 | 0.121593 | 0.003500 | 0.389968 | 0.013855 | 0.073960 | 0.005782 |
| class_weight | 0.100000 | Platt | main | 30 | 0.064666 | 0.002136 | 0.242252 | 0.009257 | 0.048042 | 0.004993 |
| class_weight | 0.100000 | Platt + Prior | main | 30 | 0.064975 | 0.002190 | 0.233826 | 0.009079 | 0.034716 | 0.005278 |
| class_weight | 0.100000 | Raw | main | 30 | 0.119085 | 0.003398 | 0.444268 | 0.015917 | 0.210448 | 0.005645 |
| class_weight | 0.155000 | Platt | main | 30 | 0.085682 | 0.002531 | 0.296200 | 0.010058 | 0.047231 | 0.007539 |
| class_weight | 0.155000 | Platt + Prior | main | 30 | 0.085666 | 0.002529 | 0.296199 | 0.010057 | 0.047158 | 0.007460 |
| class_weight | 0.155000 | Raw | main | 30 | 0.120634 | 0.003092 | 0.442600 | 0.015282 | 0.181019 | 0.005690 |
| class_weight | 0.250000 | Platt | main | 30 | 0.122125 | 0.004362 | 0.390905 | 0.014581 | 0.082328 | 0.009345 |
| class_weight | 0.250000 | Platt + Prior | main | 30 | 0.111037 | 0.003826 | 0.371695 | 0.013774 | 0.064104 | 0.010297 |
| class_weight | 0.250000 | Raw | main | 30 | 0.123096 | 0.004042 | 0.441773 | 0.019596 | 0.130290 | 0.005991 |
| oversampling | 0.100000 | Platt | main | 30 | 0.064694 | 0.002106 | 0.242335 | 0.009202 | 0.048156 | 0.005094 |
| oversampling | 0.100000 | Platt + Prior | main | 30 | 0.064996 | 0.002165 | 0.233898 | 0.009017 | 0.034329 | 0.005297 |
| oversampling | 0.100000 | Raw | main | 30 | 0.119007 | 0.003645 | 0.444115 | 0.016303 | 0.209867 | 0.006280 |
| oversampling | 0.155000 | Platt | main | 30 | 0.085732 | 0.002502 | 0.296380 | 0.010047 | 0.046916 | 0.007567 |
| oversampling | 0.155000 | Platt + Prior | main | 30 | 0.085715 | 0.002500 | 0.296379 | 0.010046 | 0.047026 | 0.007583 |
| oversampling | 0.155000 | Raw | main | 30 | 0.120614 | 0.003286 | 0.442608 | 0.015648 | 0.180434 | 0.006288 |
| oversampling | 0.250000 | Platt | main | 30 | 0.122199 | 0.004300 | 0.391188 | 0.014454 | 0.081865 | 0.009631 |
| oversampling | 0.250000 | Platt + Prior | main | 30 | 0.111141 | 0.003742 | 0.371988 | 0.013616 | 0.064395 | 0.010234 |
| oversampling | 0.250000 | Raw | main | 30 | 0.123180 | 0.004127 | 0.442073 | 0.019805 | 0.129740 | 0.006612 |

## Supplementary Table D. Raw + Prior — exploratory only

| strategy | target_prevalence | configuration | analysis_scope | n_splits | brier_score_mean | brier_score_sd | log_loss_mean | log_loss_sd | ece_mean | ece_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.100000 | Raw + Prior (exploratory) | exploratory | 30 | 0.064664 | 0.002285 | 0.231982 | 0.008862 | 0.028997 | 0.004353 |
| baseline | 0.155000 | Raw + Prior (exploratory) | exploratory | 30 | 0.085483 | 0.002330 | 0.294586 | 0.009844 | 0.038059 | 0.006168 |
| baseline | 0.250000 | Raw + Prior (exploratory) | exploratory | 30 | 0.111284 | 0.003446 | 0.370559 | 0.013105 | 0.050624 | 0.008262 |
| class_weight | 0.100000 | Raw + Prior (exploratory) | exploratory | 30 | 0.090302 | 0.002989 | 0.356506 | 0.014993 | 0.144095 | 0.004994 |
| class_weight | 0.155000 | Raw + Prior (exploratory) | exploratory | 30 | 0.120784 | 0.003113 | 0.442845 | 0.015155 | 0.181367 | 0.005706 |
| class_weight | 0.250000 | Raw + Prior (exploratory) | exploratory | 30 | 0.160575 | 0.004613 | 0.546377 | 0.020420 | 0.221401 | 0.006780 |
| oversampling | 0.100000 | Raw + Prior (exploratory) | exploratory | 30 | 0.090300 | 0.003097 | 0.356568 | 0.015326 | 0.143711 | 0.005372 |
| oversampling | 0.155000 | Raw + Prior (exploratory) | exploratory | 30 | 0.120764 | 0.003305 | 0.442831 | 0.015498 | 0.180781 | 0.006295 |
| oversampling | 0.250000 | Raw + Prior (exploratory) | exploratory | 30 | 0.160491 | 0.004923 | 0.546290 | 0.020820 | 0.220637 | 0.007486 |