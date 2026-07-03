# Agent merge policy

Goal: let an agent finish its own branch cleanly without weakening `main`.

## Current safe model

Agents may:

- create branches;
- open pull requests;
- update their pull request branch;
- enable or complete auto-merge when GitHub allows it;
- merge a solo-maintainer PR after required checks pass when branch protection requires 0 approvals;
- rely on automatic head-branch deletion after merge.

Agents must not:

- push directly to `main`;
- disable required checks;
- bypass a required review when the team-maintainer profile is active;
- approve their own pull request using another credential;
- modify workflows, dependency manifests, security policy, release configuration, or branch protection without explicit human instruction.

Repository settings should keep:

- `allow_auto_merge=true`;
- `delete_branch_on_merge=true`;
- strict required checks on `main`;
- 0 required approvals in solo-maintainer mode, because self-approval is impossible and fake reviewers are worse than checks;
- CODEOWNERS review for sensitive files once there are at least two trusted maintainers;
- secret scanning and push protection enabled.

## Why not grant a blanket merge bypass?

A blanket bypass makes the agent both author and approver. That defeats the main protection against:

- malicious or confused workflow edits;
- dependency/supply-chain regressions;
- accidental secret exposure;
- release permission escalation;
- silent weakening of future checks.

The desired autonomy is therefore **merge orchestration under explicit branch protection**, not fake approval or blanket policy bypass.

## Better target model

For future low-risk automation, use a two-lane policy:

1. **Sensitive lane** — in team-maintainer mode, human/CODEOWNER approval required.
   - `.github/workflows/`
   - `.github/CODEOWNERS`
   - `SECURITY.md`
   - dependency manifests and lockfiles
   - release scripts and release workflows
   - audit waiver files
   - auth, crypto, payment, data-retention, deployment, and permission boundaries
2. **Solo sensitive lane** — in solo-maintainer mode, no fake review; require explicit human instruction in chat plus required checks green.
3. **Low-risk lane** — auto-merge allowed after required checks.
   - typo fixes;
   - non-normative docs;
   - generated reports with deterministic provenance;
   - branch-local experiments that do not affect release/security/dependency/workflow surfaces.

Do not enable path-based low-risk automation globally until it is implemented with explicit path rules and tested on one low-impact repository.

## Measuring success

A compliant agent PR:

- has a branch name that identifies the agent/task;
- passes all required checks;
- has no unresolved conversation;
- has required review when the team-maintainer profile requires it, or explicit solo-maintainer instruction when reviews are intentionally set to 0;
- auto-merges only after GitHub reports the PR mergeable;
- deletes the branch automatically after merge.

Useful checks:

```bash
gh pr view <number> --json mergeStateStatus,reviewDecision,statusCheckRollup,isDraft,autoMergeRequest

gh api repos/constantin-jais/<repo> \
  --jq '{allow_auto_merge, delete_branch_on_merge}'
```

## Pilot recommendation

If autonomous low-risk merge becomes necessary, pilot it on `bolt-harness` first. Keep strict checks, use the solo-maintainer profile only while there is a single maintainer, and document the exact allowed paths before expanding to product repositories.
