# Branch protection checklist

These settings must be applied in GitHub after the corresponding workflows and policy files are merged on the default branch.

## Recommended default branch rules

### Solo maintainer profile

Use this profile while the repository has exactly one maintainer with write access.

- Require pull request before merge when the repository is mature enough for PR flow.
- Require **0 approving reviews**; GitHub cannot let a solo maintainer approve their own PR.
- Do **not** require CODEOWNERS review while CODEOWNERS maps to the same solo maintainer.
- Dismiss stale approvals if reviews are later enabled.
- Require status checks that match the repository maturity:
  - CI / Rust CI;
  - security;
  - contracts when present;
  - release dry-run only when intentionally configured.
- Block force pushes.
- Block branch deletion.
- Resolve conversations before merge.
- Delete head branches after merge.
- Enable auto-merge so an agent can request merge completion without bypassing checks.
- Keep agent merge behavior aligned with [`agent-merge-policy.md`](agent-merge-policy.md).

The helper script for existing GitHub repos is:

```bash
scripts/apply-solo-maintainer-protection.sh --apply
```

It only harmonizes PR review settings and preserves existing required checks.

### Team maintainer profile

Switch to this profile once at least two trusted maintainers have write access.

- Require pull request before merge.
- Require at least one approving review.
- Require review from CODEOWNERS for sensitive paths.
- Dismiss stale approvals when protected files change.
- Keep the same required checks and force-push/deletion blocks as the solo profile.

## Protected paths by convention

In the team profile, CODEOWNERS must require review for:

- `.github/workflows/`
- `.github/CODEOWNERS`
- `SECURITY.md`
- dependency manifests and lockfiles
- release scripts and release plans
- audit waiver files

## Measuring success

A repository is considered adopted when:

1. `SECURITY.md` exists on the default branch;
2. `.github/CODEOWNERS` exists on the default branch;
3. CI/security/hygiene workflows expected for its maturity are visible on the default branch;
4. branch protection requires strict status checks;
5. solo profile has 0 required approvals, or team profile requires CODEOWNERS review for sensitive files;
6. auto-merge and delete-branch-on-merge are enabled;
7. secret scanning and push protection are enabled;
8. a pull request touching `.github/workflows/` requests CODEOWNERS review;
9. a failing required workflow blocks merge.

## Do not automate blindly

Branch protection changes are administrative controls. Apply them deliberately after the repo workflows are green to avoid locking maintainers out of emergency fixes.

For autonomous agents, prefer GitHub auto-merge after required checks over any direct push or admin bypass. In the team profile, required reviews still apply.
