# Branch protection checklist

These settings must be applied in GitHub after the corresponding workflows and policy files are merged on the default branch.

## Recommended default branch rules

- Require pull request before merge.
- Require at least one approving review.
- Require review from CODEOWNERS.
- Dismiss stale approvals when protected files change.
- Require status checks that match the repository maturity:
  - CI / Rust CI;
  - security;
  - contracts when present;
  - release dry-run only when intentionally configured.
- Block force pushes.
- Restrict bypass to documented emergency maintainers.
- Delete head branches after merge.
- Enable auto-merge so an agent can request merge completion without bypassing checks/reviews.
- Keep agent merge behavior aligned with [`agent-merge-policy.md`](agent-merge-policy.md).

## Protected paths by convention

CODEOWNERS must require review for:

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
5. CODEOWNERS review is required for sensitive files;
6. auto-merge and delete-branch-on-merge are enabled;
7. secret scanning and push protection are enabled;
8. a pull request touching `.github/workflows/` requests CODEOWNERS review;
9. a failing required workflow blocks merge.

## Do not automate blindly

Branch protection changes are administrative controls. Apply them deliberately after the repo workflows are green to avoid locking maintainers out of emergency fixes.

For autonomous agents, prefer GitHub auto-merge after required checks/reviews over any direct push or admin bypass.
