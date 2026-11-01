# Confirmatory Protocol Readiness Report

**Protocol:** `confirmatory-30seed-v1`  
**Readiness decision:** **GO — protocol frozen; experiment not executed**  
**Source snapshot:** `afebd2cce291c532bc2d0e640d7d88dcec9290d0`

## Requirements closure

| Requirement | Status | Evidence |
|---|---|---|
| Oracle-known assumption retained | PASS | Plan §1–2; protocol `target_prior_source` |
| `naive_exploratory` excluded | PASS | Plan §1/§6; result validator |
| H1/H2/H3 explicit; H3 primary | PASS | Plan §3 |
| Brier sole primary metric | PASS | Plan §4; protocol JSON |
| Six primary contrasts | PASS | Plan §4; `family_size=6` |
| Prevalence 0.155 descriptive control | PASS | Plan §4/§8 |
| Two-sided paired Wilcoxon + Holm | PASS | Plan §5; frozen test parameters |
| Ties/zeros/non-finite/incomplete rules | PASS | Plan §6; automated rejection tests |
| Estimates, descriptive intervals, effects | PASS | Plan §7 |
| Dependence acknowledged | PASS | Plan §7 |
| Seeds fixed at 42–71 | PASS | Plan §2; protocol JSON |
| Freeze manifest complete | PASS | `confirmatory_protocol_freeze.json` |
| Runtime mismatch rejected | PASS | `protocol_validation.py`; tests |
| 30-seed experiment not run | PASS | No confirmatory output created |

## Frozen primary analysis

H3 compares Platt-calibrated Brier score with versus without oracle prior correction.
Exactly six paired contrasts are tested: three imbalance strategies crossed with target
prevalences 0.10 and 0.25. Each contrast requires all 30 seeds and identical scenario
hashes. The two-sided Wilcoxon signed-rank test uses Pratt zero handling and approximate
p-values; Holm adjustment is applied once across the six raw p-values.

The 0.155 scenario is a no-shift control and receives no confirmatory p-value. Log loss
and ECE are secondary; average precision and F1 are descriptive.

## Automated execution gate

`run_experiment.py --confirmatory` validates the freeze before creating its output
directory. Validation covers:

- exact seed order and membership;
- prevalences and split/bin parameters;
- canonical protocol hash and plan hash;
- dataset hash;
- exact dependency versions;
- source-file hashes and existence of the frozen Git commit.

A missing manifest or any mismatch is a hard error. Post-run result validation rejects
non-finite Brier values, missing/duplicate seed pairs, mismatched sample hashes,
incorrect oracle provenance, and exploratory rows mislabeled as confirmatory.

## Test result

The final automated suite contains 8 legacy audit tests, 7 remediation tests, and 12
protocol/analysis validation tests. All 27 tests pass. No 30-seed model training was invoked.

## Authorized future command

The command below is documented for a later, separately authorized run and was **not**
executed during finalization:

```bash
python run_experiment.py \
  --confirmatory \
  --protocol-manifest confirmatory_protocol_freeze.json \
  --output outputs_confirmatory_30_seeds \
  --seeds 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 \
  --prevalences 0.10 0.155 0.25 \
  --test-size 0.20 \
  --calibration-size 0.20 \
  --n-bins 10
```

Final readiness decision: **GO**.
