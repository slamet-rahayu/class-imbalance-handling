# Method–Implementation Discrepancies

| Severity | Status | Discrepancy | Scientific consequence |
|---|---|---|---|
| Critical | **FAIL** | `confirmatory_protocol_freeze_v2.json` records `frozen_at=2026-11-01T17:00:00+07:00`, but the run manifest/log records start `2026-11-01T16:26:25+07:00`. | The recorded protocol was not frozen before the recorded run. A confirmatory/pre-specified interpretation is not auditable. |
| Critical | **FAIL** | H3 uses 30 overlapping repeated splits of the same 12,330 records as Wilcoxon replicates. | The paired differences are dependent. Nominal Wilcoxon p-values and Holm decisions do not have their standard repeated-sample interpretation; they describe split sensitivity only. |
| High | **FAIL** | `audit_and_paired_analysis.py:333` hard-codes `confirmatory_protocol.json` (v1). The generic wrapper failed with `KeyError: 'metric_ranges'`; official tables were then made by direct function invocation. No exact direct command or standalone script is preserved. | End-to-end analysis reproduction is not available through the declared entry point, although independent reconstruction matches the tables. |
| Medium | **FAIL** | H3 explicitly calls Wilcoxon with `method="approx"` and `correction=False`; H1/H2 use `stats.wilcoxon` defaults (`method="auto"`). | Secondary p-values can be exact rather than approximate. The saved values are reproducible, but method disclosure is incomplete and differs across hypotheses. |
| Medium | **FAIL** | The plan calls average precision and F1 descriptive, but H1/H2 tables include Wilcoxon, t-test, Holm p-values, and significance flags for both metrics. | These tests should be labeled exploratory or omitted; they are not part of a clearly prespecified inferential family. |
| Medium | **FAIL** | The v1 plan says secondary log loss/ECE use the same pairing checks; the official `paired_table` pivots only on seed. H3 official code also pivots on seed alone, even though the frozen pair keys include `sample_id_sha256`. A validator checks H3 hashes beforehand, but H1/H2 have no equivalent hash validation in the table builder. | Present data pair correctly, but the analysis functions do not themselves enforce the declared pairing identity and could silently accept mismatched scenario samples. |
| Low | **FAIL** | Protocol labels `configuration_sha256` are a canonical parsed-JSON hash (`0964...`), whereas the byte SHA-256 of `confirmatory_protocol_v2.json` is `8266...`. | Gate code is correct, but the label can be misread as a file hash. Both should be reported explicitly. |
| Low | **FAIL** | Dataset provenance has `local_download_date="not_recorded"` and no independently preserved upstream checksum/version identifier. | The local file is internally stable and matches UCI's documented shape/class counts, but exact byte identity to the originally downloaded upstream artifact is not independently provable. |

## Implementation facts that do match the method

- Train/calibration/test split is stratified and disjoint.
- Standardization and one-hot encoding fit on training only.
- Random oversampling is training-only, after preprocessing, without replacement restrictions being relevant to synthetic generation (ROS duplicates training rows only).
- Class weighting is `balanced` and model-only.
- Platt calibration fits only on the natural calibration set using clipped-probability logits.
- Prior correction implements the Bayes prior-odds ratio correctly.
- Shift simulation is class-conditional, without replacement within each scenario, and paired consistently across methods.
- The H3 six-test Holm family and saved values match the frozen numerical procedure exactly.

