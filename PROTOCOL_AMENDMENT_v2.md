# Confirmatory Protocol Amendment v2 — Execution Gate Hardening

**Base freeze:** `confirmatory-30seed-v1`  
**Amended protocol:** `confirmatory-30seed-v2`  
**Reason:** Final execution-gate hardening requested before model execution.  
**Scientific hypotheses changed:** No  
**30-seed results inspected:** No; the experiment has not run.

## Preserved without change

- Oracle-known prior-shift assumption.
- Exclusion of `naive_exploratory` from confirmatory testing.
- H3 as the sole primary confirmatory hypothesis.
- Brier score as the sole primary metric.
- Six primary contrasts: three imbalance strategies × prevalences 0.10 and 0.25.
- Prevalence 0.155 as descriptive control.
- Two-sided paired Wilcoxon, Pratt zeros, approximate method, no continuity correction.
- Holm correction across exactly six H3 contrasts.
- Seed schedule 42–71 and all split/sampling assumptions.

## Gate changes

1. Runtime validation now compares the complete effective configuration, including
   model, Platt calibration, preprocessing, ROS, class weighting, metrics, aliases,
   valid metric ranges, and statistical settings.
2. Active Git `HEAD` must equal the frozen source commit exactly. Source-file SHA-256
   checks remain mandatory.
3. Result validation covers every required numeric metric, finite values, ranges,
   count consistency, aliases, paths, validity flags, and metadata.
4. `target_prior_source` semantics are clarified:
   corrected rows use `oracle_simulator`; uncorrected rows use `not_applied`.
5. Negative tests cover model-parameter drift, Git mismatch, non-finite secondary
   metrics, wrong evaluation paths, and missing metadata.

This amendment changes validation and metadata semantics only. It does not change the
scientific estimand, primary family, dataset, model predictions, or historical results.

