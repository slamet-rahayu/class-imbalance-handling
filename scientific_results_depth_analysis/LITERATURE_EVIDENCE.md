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
