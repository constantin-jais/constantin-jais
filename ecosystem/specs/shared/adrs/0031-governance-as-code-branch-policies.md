# ADR 0031 — Governance as Code for Branch Policies

Status: Accepted
Date: 2026-07-02
Decision owner: Ecosystem Architecture

## Context

On 2026-07-02 the ecosystem lost its second GitHub account (`Cos-su` absorbed
into `constantin-jais`). GitHub forbids approving one's own pull request, so
every classic branch protection requiring 1 approving review became an
unsatisfiable deadlock — including for the owner, since `enforce_admins` was
enabled. Two additional defects surfaced the same day:

1. Required status checks pointed at path-filtered workflows: PRs outside
   the filtered paths (e.g. spec-only `.md` changes) wait forever on checks
   that will never run (`expected` state).
2. Branch protection was configured by hand in the UI, per repo: not
   versioned, not reproducible, divergent across ~18 repos, and not operable
   by agents — while the harness's goal is that agents deliver tools
   end-to-end. The permission classifier rightly blocks interactive agent
   sessions from editing protections (self-serving bypass), so manual UI
   editing was the only path left.

## Decision

1. **Branch policy is code.** `ecosystem/governance/branch-policy.json` is
   the single source of truth for branch protection across ecosystem repos,
   expressed as GitHub rulesets (named, disableable without loss, idempotent
   API). Legacy classic protections are removed as repos onboard.
2. **Agents propose, humans ratify, CI applies.** Policy changes travel as
   pull requests editing the JSON; merging is the ratification; the
   `governance` workflow applies with a dedicated fine-grained PAT
   (`FORGE_ADMIN_TOKEN`, Administration read/write, ecosystem repos only).
   Interactive sessions never call the administration API.
3. **Approvals drop to 0; real gates remain.** Formal GitHub approval is
   impossible on a single-account ecosystem and is retired as theater. Gates
   that actually hold: required status checks (per-repo, declared in the
   policy), spec/decision ratification in `decision-log.md`, and session
   reviews posted as PR comments with an explicit `VERDICT:` header.
4. **Required checks must be satisfiable.** Any workflow backing a required
   check runs on every pull request, with an in-job no-op guard for
   irrelevant paths — never a `paths:` filter on the `pull_request` trigger.
5. **Auto-merge is opt-in per PR.** `allow_auto_merge` is enabled;
   mechanical PRs may use `--auto` (merge on green checks); decision-carrying
   PRs stay on explicit human merge.
6. **Drift is checked weekly** and on every governance PR; divergence fails
   loudly.

## Consequences

- Agents deliver end-to-end again: open PR → checks run and pass →
  auto-merge or one-line human merge. No more UI detours or deadlocks.
- Protection semantics are preserved minus the theater: force-push and
  deletion blocked, conversation resolution required, stale reviews
  dismissed, strict up-to-date checks kept.
- New attack surface, accepted and bounded: `FORGE_ADMIN_TOKEN` can rewrite
  rulesets of listed repos. Mitigations: fine-grained scope, 90-day expiry,
  audit-logged use, applied only from CI on merged (i.e. ratified) policy.
- Onboarding is explicit: a repo enters the policy via a PR carrying its
  `dump` output and its required-check contexts; unlisted repos are never
  touched.

## Acceptance Tests

- `ecosystem_policy.py check` exits 0 on a converged repo, 2 with a readable
  report on any drift (enforcement, approvals, checks, bypass actors,
  legacy protection, repo settings).
- A spec-only `.md` PR on this repo triggers both required checks, which
  no-op quickly and report success.
- `python3 -m unittest discover ecosystem/governance` is green.
