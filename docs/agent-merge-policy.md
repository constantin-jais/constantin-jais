# Agent merge policy

Goal: let an agent finish its own branch cleanly without weakening `main`.

## Current safe model

Agents may:

- create branches;
- open pull requests;
- update their pull request branch;
- enable auto-merge when GitHub allows it;
- rely on automatic head-branch deletion after merge.

Agents must not:

- push directly to `main`;
- disable required checks;
- bypass CODEOWNERS or required review;
- approve their own pull request using another credential;
- modify workflows, dependency manifests, security policy, release configuration, or branch protection without human review.

Repository settings should keep:

- `allow_auto_merge=true`;
- `delete_branch_on_merge=true`;
- strict required checks on `main`;
- CODEOWNERS review for sensitive files;
- secret scanning and push protection enabled.

## Why not grant a blanket merge bypass?

A blanket bypass makes the agent both author and approver. That defeats the main protection against:

- malicious or confused workflow edits;
- dependency/supply-chain regressions;
- accidental secret exposure;
- release permission escalation;
- silent weakening of future checks.

The desired autonomy is therefore **merge orchestration**, not **policy bypass**.

## Better target model

For future low-risk automation, use a two-lane policy:

1. **Sensitive lane** — human/CODEOWNER approval required.
   - `.github/workflows/`
   - `.github/CODEOWNERS`
   - `SECURITY.md`
   - dependency manifests and lockfiles
   - release scripts and release workflows
   - audit waiver files
   - auth, crypto, payment, data-retention, deployment, and permission boundaries
2. **Low-risk lane** — auto-merge allowed after required checks.
   - typo fixes;
   - non-normative docs;
   - generated reports with deterministic provenance;
   - branch-local experiments that do not affect release/security/dependency/workflow surfaces.

Do not enable the low-risk lane globally until it is implemented with explicit path rules and tested on one low-impact repository.

## Measuring success

A compliant agent PR:

- has a branch name that identifies the agent/task;
- passes all required checks;
- has no unresolved conversation;
- has required review when sensitive files are touched;
- auto-merges only after GitHub reports the PR mergeable;
- deletes the branch automatically after merge.

Useful checks:

```bash
gh pr view <number> --json mergeStateStatus,reviewDecision,statusCheckRollup,isDraft,autoMergeRequest

gh api repos/constantin-jais/<repo> \
  --jq '{allow_auto_merge, delete_branch_on_merge}'
```

## Pilot recommendation

If autonomous low-risk merge becomes necessary, pilot it on `bolt-harness` first. Keep strict checks, remove wildcard ownership only if path-based sensitive ownership is complete, and document the exact allowed paths before expanding to product repositories.
