# Final Scientific Validity Decision

## Final status

**NOT VALIDATED**

Prediction-level computation is now independently verified, but neither critical scientific-inference issue is resolved. Prospective freeze status remains unverified, and the original Wilcoxon/Holm rejection decisions still lack defensible independent sampling units.

## A. Chronology

### Verified timeline

- Local Git records a v1 protocol at 16:10, H3 code at 16:11, and v2 hardening at 16:21 on 2026-11-01 +07:00.
- The untracked v2 freeze manifest was created locally at approximately 16:21 according to mutable file-system metadata.
- Execution logs record run start at 16:26:25.
- The v2 manifest claims `frozen_at=17:00:00`, 33 minutes 35 seconds after run start.
- No post-result protocol/source commit appears in the visible history.
- No signed tag, remote timestamp, registration record, trusted timestamp, or independent archival evidence exists.

### Classification

**CHRONOLOGY INCONCLUSIVE**

The local record is consistent with the substantive H3 specification existing before the preserved run, but local Git/file-system timestamps cannot independently establish preregistration and the explicit freeze time is false relative to the run chronology. There is also insufficient evidence to classify the freeze as definitively retrospective.

H3 must not be described as prospectively preregistered. Accurate language is “documented in the available local repository record before the preserved execution logs, without independently verifiable prospective registration.”

## B. Statistical validity

### Dependence evidence

- Mean pairwise training overlap: 4,438.86 observations (60.00%).
- Mean calibration overlap: 493.24 (20.00%).
- Mean test overlap: 493.02 (19.99%).
- Each original observation occurs on average in 18 training, 6 calibration, and 6 test splits.
- Seeds are algorithmic split settings, not independently sampled population units.

### Status of original inference

The H3 Wilcoxon and Holm calculations are numerically correct but their nominal population p-values and rejection decisions are unsupported. Independence of paired differences fails; symmetry and population-sampling interpretations are unverified. Holm only adjusts valid input p-values and cannot repair this defect.

H1, H2, and H3 may be retained as conditional descriptive repeated-split comparisons. Statements about split-wise direction and magnitude are defensible. Claims of confirmed hypotheses, population statistical significance, or 30 independent replications are not.

### Recommended publication strategy

Use **Strategy A — Conservative empirical evaluation** for the present study: report effect magnitudes, signs, empirical split distributions, and exact computational reproduction; remove or explicitly disclaim inferential rejection language. This is publishable as a transparent, dataset-conditional empirical evaluation if chronology and dependence limitations are prominent.

For strengthened inference, use a new prospectively registered design with an independently held temporal/site cohort or clearly justified independent clusters. A newly designed one-prediction-per-observation cross-fitting analysis is possible but weaker and would be a new exploratory/inferential analysis, not a repair of the frozen test.

## C. Prediction-level metric verification

### Export status

- 30 hashed gzip CSVs.
- 567,630 observation-level rows.
- Explicit raw, Platt, raw-corrected, and Platt-corrected probabilities.
- Stable original row identifiers, labels, source/realized priors, and scenario hashes.
- All schema, hash, row-count, finiteness, bounds, uniqueness, prevalence, pairing, Bayes-formula, identity, and monotonic-ranking checks passed.

### Metric results

| Metric | Comparisons | Max absolute difference | Mismatches at `atol=1e-12`, `rtol=1e-10` | Status |
|---|---:|---:|---:|---|
| Brier score | 1,080 | 5.551115123125783e-17 | 0 | PASS |
| Log loss | 1,080 | 1.665334536937735e-16 | 0 | PASS |
| ECE | 1,080 | 0 | 0 | PASS |
| **Total** | **3,240** | — | **0** | **PASS** |

ECE is confirmed as ten-bin equal-width ECE with left-closed internal bins, empty-bin omission, and probability one assigned to the final bin. Log loss uses float64 machine-epsilon clipping. Metric discrepancies are absent; tiny nonzero differences are floating-point evaluation-order effects.

This resolves the previous `NOT VERIFIED` metric status for regenerated prediction-level evidence. It does not convert regenerated predictions into contemporaneously preserved primary outputs.

## D. Remaining limitations

### Computational reproducibility

- Core frozen outputs reproduce byte-for-byte and prediction metrics reproduce independently.
- The repository's generic v2 statistical wrapper remains broken because it loads the v1 protocol; the historical direct workaround command is not preserved.
- Prediction records are audit regenerations, not original run artifacts.

### Statistical inference

- Repeated splits are dependent.
- Nominal Wilcoxon/Holm decisions lack validated population interpretation.
- T-based intervals and Cohen's dz summarize split variability, not population uncertainty.
- H1/H2 use SciPy's automatic Wilcoxon method while H3 uses the frozen approximate method.

### Scientific generalizability

- One dataset and one model family were evaluated.
- Shift is oracle-known and simulated by class-conditional subsampling.
- Pure label shift assumes stable `P(X|Y)` and is not demonstrated for a deployment population.
- There is no external temporal/site validation or operational target-prior estimation.

### Missing provenance evidence

- No independently immutable protocol timestamp or preregistration.
- The v2 freeze manifest is not Git-tracked and its declared time conflicts with execution.
- Dataset download date and upstream byte checksum/version were not preserved.
- No evidence excludes unpreserved preliminary executions before the visible run.

## E. Resolution table

| Critical issue | Outcome |
|---|---|
| Direct Brier/log-loss/ECE verification unavailable | **RESOLVED — PASS** using regenerated prediction-level evidence |
| Freeze chronology discrepancy | **UNRESOLVED — CHRONOLOGY INCONCLUSIVE** |
| Independence/inferential validity | **UNRESOLVED — original nominal inference unsupported** |

## Publication decision

The work is scientifically defensible for publication only under conservative descriptive framing, transparent chronology language, and explicit removal/disclaimer of population-significance claims. New data are not required for such a conditional empirical report. New independent data or a separately justified inferential design are required for strong confirmatory, population-generalizable, or deployment claims.

Exact manuscript replacements are provided in `MANUSCRIPT_CORRECTIONS.md`; supporting details are in `FREEZE_CHRONOLOGY_INVESTIGATION.md`, `STATISTICAL_INFERENCE_VALIDITY.md`, and `PREDICTION_LEVEL_VALIDATION.md`.

