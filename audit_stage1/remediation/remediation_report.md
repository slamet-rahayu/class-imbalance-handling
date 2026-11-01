# Stage 1 Audit Remediation Report

**Version:** `stage1-remediation-v1`  
**Decision:** **GO** for the confirmatory 30-seed experiment  
**30-seed experiment executed:** No

## Executive conclusion

All critical A07 findings are closed. Prior correction now has an explicit,
machine-readable validity boundary: Platt-calibrated correction is the primary
confirmatory path, while raw correction is retained only as naive exploratory output.
The target prior is explicitly marked `oracle_simulator`, invalid correction inputs are
rejected, and a synthetic known-label-shift test verifies the mathematics.

Fifteen automated tests pass. A seed-42 smoke run generated 36 rows and matched every
historical common field exactly (maximum numeric difference 0.0). Historical folders
were not modified. There are no unresolved CRITICAL or HIGH findings; therefore the
project is **GO**, conditional on freezing `STATISTICAL_ANALYSIS_PLAN.md` before launch.

## Closure of audit findings

| Finding | Previous status | Remediation | New status |
|---|---|---|---|
| A07-1 raw rebalanced correction interpreted as valid | CRITICAL FAIL | Marked all raw+correction `naive_exploratory`; excluded from confirmatory analysis | CLOSED |
| A07-2 test-derived target prior unlabeled | CRITICAL FAIL | Added `target_prior_source=oracle_simulator` in row and scenario metadata | CLOSED |
| A07-3 no invalid-input validation | MEDIUM FAIL | Explicit finite/range validation plus automated tests | CLOSED |
| A04 incomplete imbalance metadata | MEDIUM | Pre/post counts, effective weights and prevalence persisted | CLOSED |
| A05 convergence not recorded | MEDIUM | Iteration and warning/convergence metadata persisted | CLOSED |
| A06 incomplete scenario metadata | MEDIUM | Class counts, total, seed, prior and sample hash persisted | CLOSED |
| A08 AP mislabeled as PR-AUC | MEDIUM | Canonical `average_precision`; compatible `pr_auc` alias retained | CLOSED |
| A09 dependency/provenance gaps | MEDIUM | Lockfile, provenance document/runtime manifest, version and hashes added | CLOSED WITH NOTE |
| A10 confirmatory family ambiguity | MEDIUM | Draft statistical plan and automatic exploratory filtering added | CLOSED WITH PRE-RUN CONDITION |

## Behavioral design after remediation

Each row is classified as one of:

- `primary_prior_correction`: Platt probability with correction; confirmatory.
- `reference_no_correction`: raw or Platt reference without correction; confirmatory
  where appropriate to the prespecified contrast.
- `naive_exploratory`: raw probability with correction; never included in the primary
  correction hypothesis.

The simulation still uses the exact realized shifted-test prevalence. This is now
unambiguously an oracle simulator design and is not presented as unsupervised target
prior estimation.

## Test evidence

- Legacy/audit regression suite: 8/8 passed.
- Remediation suite: 7/7 passed.
- Synthetic likelihood-ratio/label-shift posterior: passed at `rtol=1e-12`.
- Base-model convergence in smoke: 3/3.
- Platt convergence in smoke: 3/3.
- Average precision compatibility alias maximum difference: 0.0.
- Historical result SHA-256 remained
  `4e35c9c5c05c092a585f165743e2f22aab7fc9b06f19805514e882aebebe8652`.

See `test_results.txt`, `smoke_comparison.json`, and `remediation_checks.json`.

## Reproducibility improvements

- Exact environment pins in `requirements-lock.txt`.
- Official UCI provenance, DOI `10.24432/C5F88Q`, CC BY 4.0, and local checksum.
- Runtime dataset provenance file in every new experiment output.
- Project version and source manifest.
- Training/scenario metadata sufficient to audit ROS, class weighting, convergence,
  oracle prior provenance, and sample identity.

## Remaining noncritical constraints

1. The historical local download date is unknown and honestly recorded as such.
2. Repeated seeds are repeated splits of one dataset, not independent populations.
3. The draft statistical plan must be reviewed and frozen before starting 30 seeds.
4. The 30-seed experiment was intentionally not run during remediation.

None is CRITICAL or HIGH. With the statistical plan frozen, the final decision is
**GO**.

