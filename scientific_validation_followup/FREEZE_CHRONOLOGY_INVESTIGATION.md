# Freeze Chronology Investigation

## Classification

**CHRONOLOGY INCONCLUSIVE**

The available local evidence is consistent with the H3 design being written before the recorded execution, but it does not independently establish a prospective freeze. It also does not prove that the design was created retrospectively after seeing the 30-seed results. The explicit `frozen_at` value is demonstrably inconsistent with the recorded execution chronology and cannot be used as evidence of a valid freeze.

## Verified timeline (Asia/Jakarta, UTC+07:00)

| Time | Evidence | Event | Evidentiary status |
|---|---|---|---|
| 16:02:26 | Git commit `f333c3c`; author and committer dates | Stage-1 remediation, initial experiment implementation | Local Git evidence only |
| 16:10:09 | Git commit `606a5a2`; reflog | v1 statistical plan and machine-readable protocol committed | Local Git evidence only |
| 16:11:19 | Git commit `afebd2c`; reflog | H3 primary-analysis function committed | Local Git evidence only |
| 16:11:33 | Git commit `439ea06`; reflog | v1 freeze manifest committed | Local Git evidence only |
| 16:20:45 | file-system birth/modify times | v2 protocol, plan and amendment working-tree files created | Mutable local metadata |
| 16:21:21 | Git commit `2f44814`; author/committer dates and reflog | v2 protocol, plan, amendment, source hardening committed | Local Git evidence only |
| 16:21:31 | file-system birth/modify time | `confirmatory_protocol_freeze_v2.json` created; this file is not tracked by Git | Mutable local metadata |
| 16:26:25 | execution log and manifest | 30-seed execution recorded as starting | Project-generated record |
| 16:26:30–16:27:45 | output directory/file birth times | Frozen output files created | Mutable local metadata consistent with logs |
| 16:27:40 | execution manifest birth time | execution manifest created | Mutable local metadata |
| 16:28:07 | report birth time | `STAGE3_EXECUTION_REPORT.md` created | Mutable local metadata |
| 17:00:00 | v2 freeze manifest content | Claimed `frozen_at` | Contradicted by the run beginning 33m35s earlier |

## What existed before the recorded run

The parent history shows that the substantive H3 design existed in v1 before the run: H3 as sole primary hypothesis, Brier score as primary metric, three strategies × target prevalences 0.10/0.25, two-sided Pratt Wilcoxon, approximate method, no continuity correction, six-test Holm family, and seeds 42–71. Commit `2f44814` added v2 execution-gate hardening without changing those scientific hypotheses, according to both its diff and `PROTOCOL_AMENDMENT_v2.md`.

No later Git commit modifies the v2 protocol, H3 procedure, or frozen source. The 30-seed result directory and Stage-3 report are untracked, so Git cannot establish their creation order; their file-system times and logs are mutually consistent with a 16:26–16:28 run.

## What cannot be verified

- There is no signed or annotated tag.
- There is no remote hosting timestamp, registry deposit, trusted timestamp service, email record, or independent witness record.
- All commits use a local synthetic identity (`codex-remediation@local.invalid`).
- Author dates, committer dates, reflog entries, file birth/modification times, and JSON timestamps are all locally controlled and can be rewritten.
- `confirmatory_protocol_freeze_v2.json` is untracked, so no Git object timestamps it.
- There is no evidence explaining why `frozen_at` was set to 17:00, no timezone conversion supporting it, and no record identifying it as a later administrative freeze.
- There is no independently immutable evidence showing whether the author had inspected any unpreserved preliminary 30-seed execution before the local commits.

Author and committer timestamps can differ because Git records authorship and repository insertion separately; here they are identical. Neither is a trusted timestamp. File-system times record local file-system events and can change through copying, restoration, or deliberate alteration. Their agreement strengthens internal consistency but does not prove preregistration.

## Post-result modifications

Within the visible Git history, no protocol/source commit occurs after the recorded result time. The working-tree v2 freeze manifest's later *declared* time is not accompanied by a later file-system creation time or later commit. This does not support a finding of a confirmed retrospective rewrite. Conversely, absence of a later commit does not establish prospective registration because local history is not independently anchored.

## Implication for H3 terminology

H3 must **not** be described as “prospectively preregistered” or as having a “prospective immutable freeze.” The evidence supports narrower wording:

> The H3 analysis specification is recorded in local Git commits whose recorded timestamps precede the preserved execution logs. Because no independently timestamped preregistration or immutable external record is available, prospective specification cannot be independently verified; H3 is reported as a documented analysis specification rather than a preregistered confirmatory test.

The numerical H3 comparisons may be retained, but “confirmatory” should be qualified or replaced with “protocol-defined in the available local repository record.” This preserves the historical record without claiming a level of prospective evidence that is unavailable.

## Commands used

```bash
git log --all --decorate --date=iso-strict --pretty=fuller --stat --reverse
git tag --list --format='%(refname:short) %(creatordate:iso-strict) %(objectname)'
git log --all --follow --date=iso-strict -- <file>
git reflog --all --date=iso-strict
git show -s --format='%H%n%P%n%aI%n%cI%n%B' 2f448140cbdf5a593d1d182f26ef955d83cc717b
stat -f 'birth=%SB modify=%Sm change=%Sc size=%z' <file>
```

## Status by required check

| Check | Status |
|---|---|
| Git history, parents, timestamps, tags | PASS — inspected; no tags found |
| Protocol/plan file history | PASS — inspected |
| Logs, manifests and freeze records | PASS — inspected |
| Scientific procedure present before recorded run in local history | PASS — local evidence supports it |
| Independently immutable prospective freeze | NOT VERIFIED |
| Protocol modification after preserved results | NOT VERIFIED beyond visible local history; none found |
| Timestamp/timezone explanation for 17:00 | NOT VERIFIED |

