# Reproducibility Report — `confirmatory-30seed-v2`

## Status

**PASS for deterministic core-output reproduction; FAIL for the declared end-to-end analysis entry point; NOT VERIFIED for direct metric recomputation from preserved predictions.**

## Environment reconstruction

- Source: `git archive 2f448140cbdf5a593d1d182f26ef955d83cc717b`
- Temporary root: `/tmp/confirmatory-audit.JtU9th`
- Python: 3.15.0
- Dependencies: fresh venv installed from `requirements-lock.txt`; all frozen scientific versions matched (`numpy 2.5.4`, `pandas 3.1.0`, `scikit-learn 1.9.1`, `imbalanced-learn 0.14.2`, `scipy 1.18.1`, `matplotlib 3.11.2`).
- Scientific configuration: seeds 42–71; prevalences 0.10/0.155/0.25; test 0.20; calibration 0.20; 10 ECE bins.

The reproduction omitted `--confirmatory` only because a Git archive intentionally contains no `.git` directory and the gate requires `git rev-parse HEAD` to equal the frozen commit. No scientific setting changed. This deviation is documented and limits the check to deterministic computational reproduction rather than a retest of the Git gate.

## Byte-for-byte comparison

| File | Reproduced SHA-256 | Frozen SHA-256 | Result |
|---|---|---|---|
| `all_repetitions.csv` | `029f422cdb4cfc5fc8306e8db44595935eea042e5b6136c5eaa87af7f4d1c9e5` | same | PASS |
| `aggregate_summary.csv` | `060a9021d85cdc609d6119dcab0d7a825c7c0ae412a909f40837ddb1ba6d7bc0` | same | PASS |
| `all_audits.csv` | `347cacb296148110e0b62bcedf4f799ab70902c98f3fc50f2e299cc370f8806d` | same | PASS |
| `training_metadata.csv` | `c351bdd5238f7c4400ae71abfcb35cfbdee1744aed171db3bfdbd8303251a73f` | same | PASS |

`cmp -s` returned 0 for all four files.

## Integrity and provenance checks

- All 198 files listed in `output_hashes.json`: PASS, zero mismatches.
- Dataset local SHA-256: PASS against freeze (`b3055e...e0d9`).
- Source file hashes: PASS against freeze.
- Canonical parsed protocol hash: PASS (`0964b1...a818`).
- Statistical-plan byte hash: PASS.
- Active repository HEAD at audit time: PASS (`2f448140...`).
- Exact original upstream dataset bytes: NOT VERIFIED; no download date or upstream checksum is preserved.

## Analysis reproduction

Independent audit code (which does not import project modules) exactly reproduced:

- all 6 H3 Wilcoxon statistics and raw p-values;
- all 6 Holm-adjusted H3 p-values;
- all 135 H1 table rows' Wilcoxon/Holm values;
- all 45 H2 table rows' Wilcoxon/Holm values;
- all 90 shifted-scenario hashes and class counts.

The repository's own generic analysis command is not reproducible for v2 because it loads the v1 protocol filename and raises `KeyError: 'metric_ranges'`. The logged workaround directly invoked frozen helper functions, but its exact command/script was not preserved.

## Prediction-level limitation

No frozen file contains per-observation true labels and predicted probabilities for each condition. Consequently, Brier score, log loss, and ECE are **NOT VERIFIED by direct recomputation from frozen prediction-level output**. Their exact clean-run reproduction is strong determinism evidence but is not an independent calculation from preserved primary predictions.

## Chronology failure

The declared freeze time is 17:00 +07; the run began at 16:26:25 +07 on the same date. This is a reproducibility/provenance failure even though the current source snapshot and numerical outputs are internally consistent.

