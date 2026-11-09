# Independent Scientific Validity Audit — `confirmatory-30seed-v2`

## Conclusion

**NOT VALIDATED: one or more critical failures were found.**

The numerical outputs are genuine in the limited, auditable sense that their hashes are intact, all reported H3/H1/H2 statistics independently recompute, and a fresh-environment execution reproduced the four core CSVs byte-for-byte. This does **not** validate the experiment as confirmatory evidence. The recorded chronology says the experiment began at `2026-11-01T16:26:25+07:00`, while the alleged freeze time is `2026-11-01T17:00:00+07:00`. The run therefore precedes the recorded freeze by 33 minutes 35 seconds. In addition, the six H3 Wilcoxon tests use 30 overlapping repeated splits of one dataset as though the 30 paired differences were independent observations; their nominal p-values and rejection decisions do not support population-level inference.

## Scope and non-modification statement

The audit did not modify `confirmatory_protocol_v2.json`, `confirmatory_protocol_freeze_v2.json`, project source, or `outputs_confirmatory_30_seeds/`. Independent code is in `independent_scientific_audit.py`; audit deliverables are new files. A reproduction ran in `/tmp/confirmatory-audit.JtU9th` from `git archive 2f448140...`, not in the frozen output directory.

## Requirement-level decisions

| # | Status | Independent finding and evidence |
|---:|---|---|
| 1 | **FAIL** | Dataset SHA-256 (`b3055e...e0d9`), canonical protocol hash (`0964b1...a818`), plan hash, source hashes, commit, dependency versions, and all 198 output-manifest hashes match. UCI metadata agrees on DOI, license, 12,330 rows, and 1,908/10,422 class counts. However, provenance records `local_download_date="not_recorded"`, no source-file checksum supplied by UCI was preserved, and—critically—the run started before the stated freeze time. Evidence: `confirmatory_protocol_freeze_v2.json`, `outputs_confirmatory_30_seeds/execution_manifest.json`, `dataset_provenance.json`, `output_hashes.json`. |
| 2 | **PASS** | Independent split reconstruction for all 30 seeds found disjoint 60/20/20 train/calibration/test partitions. Preprocessing is fitted only on `X_train`; calibration and test use transform-only prediction. Evidence: `run_experiment.py:141-219,364-420`; `INDEPENDENT_RECOMPUTATION.csv`. |
| 3 | **PASS** | ROS occurs after train-only preprocessing and only on transformed training rows. Clean reproduction and metadata show ROS balances each training set; class weighting is `class_weight="balanced"` only in the model, with independently consistent effective weights. Evidence: `run_experiment.py:170-215`; `outputs_confirmatory_30_seeds/training_metadata.csv`; byte-identical reproduction. |
| 4 | **PASS** | For each seed/strategy, Platt receives `logit(clip(base_model.predict_proba(X_cal)))` and `y_cal`; it never receives test labels or test probabilities during fitting. Frozen parameters are LR/lbfgs/L2/C=1/max_iter=100/random_state=0. All 90 calibrators report convergence, and clean reproduction is byte-identical. This validates implementation, not the assumption that finite-sample calibration is perfect. Evidence: `run_experiment.py:222-236,419-440`; training metadata. |
| 5 | **PASS** | Three manually calculated Bayes prior-ratio cases matched to floating-point precision; monotonic odds conversion in source is algebraically correct. Exact test values are recorded in the independent script and CSV. |
| 6 | **PASS** | Independently reconstructed all 90 shifted samples from labels and seeds. Every sample used no replacement, had unique IDs, matched positive/negative/total counts, came from its seed's test pool, and matched its saved SHA-256. The same scenario hash is used across strategy/calibration/correction branches. Evidence: `INDEPENDENT_RECOMPUTATION.csv`, `all_audits.csv`. |
| 7 | **NOT VERIFIED** | No prediction-level probabilities or labels are preserved. Brier score, log loss, and ECE therefore cannot be recomputed directly from frozen prediction outputs. A rerun reproduces them byte-for-byte but is not direct recomputation from preserved predictions. |
| 8 | **PASS** | Independently recomputed all six H3 corrected-minus-uncorrected Brier contrasts with two-sided Pratt Wilcoxon, `method="approx"`, no continuity correction, then one six-test Holm family. All statistics and p-values match exactly; see CSV. |
| 9 | **PASS** | Independently reconstructed and matched all 135 H1 rows and 45 H2 rows, including pairing, Wilcoxon values, and per-metric Holm families. The actual secondary implementation uses SciPy's default `auto` method, not the H3 `approx` method. Family/method disclosure deficiencies are recorded separately. |
| 10 | **PASS** | A clean virtual environment from the frozen commit and exact lockfile reproduced `all_repetitions.csv`, `aggregate_summary.csv`, `all_audits.csv`, and `training_metadata.csv` byte-for-byte. The run omitted `--confirmatory` because `git archive` has no `.git` metadata and the gate requires exact Git HEAD; all scientific CLI settings were identical. |
| 11 | **FAIL** | Material method/implementation discrepancies exist: run-before-freeze chronology; broken generic v2 analysis entry point; undocumented direct analysis invocation; H1/H2 `auto` Wilcoxon versus explicitly frozen H3 `approx`; inferential tests on metrics called descriptive; and pair hashes not included in the H3 pivot index inside the official analysis function. See `METHOD_IMPLEMENTATION_DISCREPANCIES.md`. |
| 12 | **FAIL** | The 30 results are overlapping perturbations of one finite dataset, not independent samples. Standard Wilcoxon null distributions, Holm-adjusted p-values, t intervals, and Cohen's dz do not acquire population-level validity from repeated splits. The manuscript/report acknowledges limited generalizability, but still issues hypothesis-test rejection decisions using a procedure whose independence basis is not met. |

## Key independently recomputed H3 results

| Strategy | Target | Mean corrected − uncorrected | Raw p | Holm p | Audit |
|---|---:|---:|---:|---:|---|
| baseline | 0.10 | -0.000008260906881 | 0.9917945644 | 0.9917945644 | exact match |
| baseline | 0.25 | -0.01038792203 | 0.000001734398 | 0.000010406386 | exact match |
| oversampling | 0.10 | +0.000302750163 | 0.008729667754 | 0.02618900326 | exact match |
| oversampling | 0.25 | -0.01105889362 | 0.000001734398 | 0.000010406386 | exact match |
| class_weight | 0.10 | +0.000308773590 | 0.01319416987 | 0.02638833973 | exact match |
| class_weight | 0.25 | -0.01108783008 | 0.000001734398 | 0.000010406386 | exact match |

These are correct calculations conditional on the saved per-seed summaries. Their nominal inferential interpretation is not validated.

## Commands

```bash
sha256sum online_shoppers_intention.csv confirmatory_protocol_v2.json \
  STATISTICAL_ANALYSIS_PLAN_v2.md run_experiment.py protocol_validation.py \
  audit_and_paired_analysis.py requirements-lock.txt

.venv/bin/python independent_scientific_audit.py

audit_tmp=$(mktemp -d /tmp/confirmatory-audit.XXXXXX)
git archive 2f448140cbdf5a593d1d182f26ef955d83cc717b | tar -x -C "$audit_tmp"
python3 -m venv "$audit_tmp/.audit-venv"
"$audit_tmp/.audit-venv/bin/pip" install -r "$audit_tmp/requirements-lock.txt"
"$audit_tmp/.audit-venv/bin/python" run_experiment.py \
  --output reproduction_outputs --seeds 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 \
  --prevalences 0.10 0.155 0.25 --test-size 0.20 --calibration-size 0.20 --n-bins 10
```

## Evidence inventory

- Frozen configuration and gate: `confirmatory_protocol_v2.json`, `confirmatory_protocol_freeze_v2.json`, `protocol_validation.py`
- Implementation: `run_experiment.py`, `audit_and_paired_analysis.py`
- Frozen outputs: `outputs_confirmatory_30_seeds/`
- Independent values: `INDEPENDENT_RECOMPUTATION.csv`
- Reproduction details: `REPRODUCIBILITY_REPORT.md`
- Method mismatches: `METHOD_IMPLEMENTATION_DISCREPANCIES.md`

