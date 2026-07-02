# Forge governance — branch policy as code

Branch protection for forge repositories is defined in `branch-policy.json`,
applied and drift-checked by `forge_policy.py`. Nobody edits Settings → Rules
by hand: **agents propose policy changes via pull request, a human merges,
CI applies** (see ADR 0031).

## Why approvals are 0

The forge is operated by a single GitHub account. GitHub forbids approving
your own pull request, so a `required_approving_review_count` of 1 is not a
gate — it is an unsatisfiable deadlock (proven 2026-07-02 on three repos).
The real gates are:

- **required status checks** (declared per repo in the policy, always-run
  workflows so they can never stay `expected` forever);
- **spec/decision ratification** in `specs/shared/decision-log.md` (method
  gate: merged `Proposed` documents do not open implementation gates);
- **session review**: substantive PRs get a `gh pr review --comment` with an
  explicit `VERDICT:` header, since formal approval is impossible.

## Commands

```sh
python3 ecosystem/governance/forge_policy.py check            # all repos, exit 2 on drift
python3 ecosystem/governance/forge_policy.py check --repo constantin-jais/constantin-jais
python3 ecosystem/governance/forge_policy.py apply            # converge + post-verify
python3 ecosystem/governance/forge_policy.py dump --repo OWNER/NAME   # onboarding aid
python3 -m unittest discover ecosystem/governance             # unit tests (pure core)
```

## Bootstrap (one-time, human)

1. Create a fine-grained PAT: Settings → Developer settings → Fine-grained
   tokens — Repository access: the forge repos; Permissions: Administration
   (Read and write); expiration 90 days.
2. Add it as the `FORGE_ADMIN_TOKEN` secret of this repository. With the
   token in your clipboard (macOS):

   ```sh
   pbpaste | gh secret set FORGE_ADMIN_TOKEN --repo constantin-jais/constantin-jais
   ```

   Do NOT rely on `gh secret set`'s interactive prompt from a harness `!`
   command: without a TTY it reads an empty stdin and silently stores an
   empty secret (bitten 2026-07-02). UI alternative: Settings → Secrets and
   variables → Actions.

3. First convergence: Actions → `Governance` → Run workflow (the `apply`
   job runs on `workflow_dispatch` and on every push to `main` touching
   `ecosystem/governance/`).

Renewal: when the PAT expires, generate a new one and update the secret —
the weekly drift check fails loudly when the token dies.

## Onboarding a repository

1. `forge_policy.py dump --repo OWNER/NAME` — capture its live rulesets,
   legacy protection, and settings (paste the output in the PR description).
2. Add its entry under `repos` in `branch-policy.json`, declaring its
   `required_checks` (the CI contexts that must stay green). Make sure those
   workflows run on every pull request (no `paths:` filter on the
   `pull_request` trigger — use an in-job no-op guard instead, see
   `.github/workflows/forge-health.yml` for the pattern).
3. Open the PR; merging it applies the policy to the repo.

A repo listed without `required_checks` gates on nothing but the
pull-request rule — the check mode warns about it until its CI contexts are
declared.

## Auto-merge

`allow_auto_merge` is enabled by policy. Mechanical PRs (docs, CI fixes,
dependency bumps) may set `gh pr merge --auto --squash`: GitHub merges when
the required checks pass. Decision-carrying PRs (specs, ADRs, decision-log)
stay on explicit human merge.

## Scope and security

- The apply path runs in CI with `FORGE_ADMIN_TOKEN` (fine-grained,
  Administration read/write, forge repos only, 90-day expiry, revocable,
  every use in the GitHub audit log). Interactive agent sessions never call
  the administration API directly — they edit this policy file instead.
- `check` runs on every PR touching `ecosystem/governance/` and weekly
  (drift detection), `apply` runs on push to `main`.
- The policy is explicit-list only: applying to an unlisted repo is an
  error, never a fallback.
