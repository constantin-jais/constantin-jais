# Public Repository Inventory & Cleanup Ledger

Status date: 2026-07-06
Purpose: operational ledger for public repository hygiene: visibility, disposition, branch cleanup, PR cleanup, and issue cleanup.

This file is intentionally **not** the architecture source of truth:

- `overview.md` owns layer boundaries and repository responsibilities.
- `status.md` owns current maturity and next quality steps.
- `target-version.md` owns the accepted stack target.
- `governance/branch-policy.json` owns branch protection expectations.
- This file owns only the public-repo cleanup view and points back to the canonical docs.

## Update rules

- Do not delete or archive a public repository from this ledger alone. Record the decision in `specs/shared/decision-log.md` or a dedicated ADR first.
- Do not delete a branch until its PR is merged/closed and unique commits are checked.
- Prefer archiving over deletion unless there is a security/privacy reason to remove content.
- Keep counts evidence-based: refresh with `gh repo list`, `gh pr list`, `gh issue list`, `gh pr checks`, and branch listing before cleanup.
- A PR is mergeable from this ledger only when checks are green **and** the merge state is not `DIRTY`, `BEHIND`, or `UNSTABLE`.

## Evidence commands used for this snapshot

```bash
gh repo list constantin-jais --visibility public --limit 100 \
  --json name,url,isArchived,isPrivate,pushedAt,primaryLanguage

gh repo view constantin-jais/<repo> \
  --json name,defaultBranchRef,issues,pullRequests,licenseInfo,pushedAt,primaryLanguage,url,isArchived,isPrivate

gh api --paginate repos/constantin-jais/<repo>/branches?per_page=100

gh pr list --repo constantin-jais/<repo> --state open \
  --json number,title,headRefName,baseRefName,url,mergeStateStatus,reviewDecision,isDraft,updatedAt,author

gh pr checks <number> --repo constantin-jais/<repo> --watch=false
```

## Session execution log

2026-07-06:

- Created this ledger from live GitHub public repository data.
- Linked it from `status.md` and declared its ownership in `overview.md`.
- Linked the governance wave plan back to this ledger for public cleanup enumeration.
- Inspected PR checks and merge states for the active open PR queue.
- `rumble-feed-mind`: merged checked PRs #26, #25, #22, #23, and #24, resolving conflicts locally where needed and deleting their PR branches.
- `rumble-feed-mind` #21: updated from `main`; initially policy-blocked by a stale required check, then merged by auto-merge after branch protection was realigned (`5e6186031a99b7cdd22389527620ce4d81f62744`).
- `wrench-dioxus-lab` #1: resolved the README conflict, re-ran checks, merged by squash (`7e7688c0478ebf3e5c5e99dee62ab7610a78de16`), and deleted the PR branch.
- `rumble-cos` #6: resolved the `main` merge, fixed stale template smoke tests/scripts, restored coverage/e2e/static-smoke gates, pushed `c877c4d2974383f77da94783c8550d495b4e8207`; initially policy-blocked by stale required checks, then merged by auto-merge after branch protection was realigned (`69c3ec961bce126c2ff92031d7bdfd1ac116e59c`).
- `rumble-cos` #5: retargeted to `main` after #6, fixed deterministic `dioxus-cli` installation in CI, re-ran checks, merged normally (`9036c3435f20e08144eb8c10d0df1d7d7bce49f9`), and deleted the PR branch.
- Realigned GitHub required status checks for `rumble-feed-mind` and `rumble-cos` to the active gates; no admin merge bypass was used. Versioned policy drift remains a follow-up because the global governance drift check reports broader pre-existing ruleset drift.

Remote-destructive actions executed: nine checked PR merges with their PR branch deletions (`rumble-feed-mind` #21, #22, #23, #24, #25, #26; `wrench-dioxus-lab` #1; `rumble-cos` #6 and #5). No PR/issue was closed manually and no repository was archived.

## Summary

- Public repositories found: **23**.
- Public archived repositories: **0**.
- Public open PRs found: **0**.
- Public open issues found: **18** (`bolt-cos-matic`: 4, `rumble-feed-mind`: 5, `Rumble-LM`: 9).
- Main cleanup hotspots: branch cleanup watchlist, issue triage, branch-policy/ruleset drift, `dioxus-template`/`dioxus-app-template` duplication, `dioxus` fork branches, `rumble-ai-practices`, `portal-core`, `Rumble-LM`.

## Public repository inventory

| Repository | Layer / role | Disposition | Branches | Open PRs | Open issues | License | Local checkout | Next cleanup action |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `bolt-cos-matic` | Bolt factory | KEEP | 2 | 0 | 4 | MIT | `bolt-cos-matic` on `feat/stack-rule-check` | Reconcile local feature branch; triage issues #17/#41-#43. |
| `bolt-harness` | Bolt proof surface | KEEP | 1 | 0 | 0 | MIT | `bolt-harness` | No immediate cleanup. |
| `constantin-jais` | Control plane / profile repo | KEEP | 1 | 0 | 0 | Missing on GitHub | `constantin-jais` | Decide profile-repo license exemption or add license. |
| `dioxus` | External fork / upstream PR base | KEEP-REFERENCE | 19 | 0 | 0 | Apache-2.0 | `dioxus` remote points to `DioxusLabs/dioxus` | Keep while upstream PRs are active; later prune fork branches deliberately. |
| `dioxus-template` | Superseded public template candidate | DECIDE | 8 | 0 | 0 | Missing on GitHub | no matching local checkout | Decide: archive public repo, rename/adopt as canonical, or replace with `dioxus-app-template`. |
| `gear-cable` | Gear release substrate | KEEP | 1 | 0 | 0 | MIT | `gear-cable` | No immediate cleanup. |
| `gear-depot` | Gear artifact substrate | KEEP | 1 | 0 | 0 | MIT | `gear-depot` | No immediate cleanup. |
| `gear-loader` | Gear ingestion substrate | KEEP | 1 | 0 | 0 | MIT | `gear-loader` | No immediate cleanup. |
| `gear-memory` | Gear memory/provenance substrate | KEEP | 1 | 0 | 0 | MIT | `gear-memory` | No immediate cleanup. |
| `portal-android` | Portal Android shell | KEEP/FREEZE | 1 | 0 | 0 | MIT | `portal-android` | Keep frozen until Android need + SDK/NDK proof. |
| `portal-apple` | Portal Apple shell | KEEP/FREEZE | 1 | 0 | 0 | MIT | `portal-apple` | Keep frozen at proven bridge. |
| `portal-core` | Portal Rust client core | KEEP | 3 | 0 | 0 | MIT | `portal-core` | Inspect `docs/plan-2026-07` and `feat/plan-2026-07-i1-deny-gate`; PR or prune. |
| `portal-forge` | Portal token compiler | KEEP | 1 | 0 | 0 | MIT | `portal-forge` | No immediate cleanup. |
| `rumble-ai-benchmark` | Done benchmark artifact | DECIDE | 2 | 0 | 0 | MIT | `rumble-ai-benchmark` on `feat/rumble-v1` | Decide public archive vs maintained benchmark; reconcile local branch. |
| `rumble-ai-practices` | Rumble product | KEEP | 5 | 0 | 0 | MIT | `rumble-ai-practices` with no upstream tracking shown | PR or prune feature branches; set upstream tracking if needed. |
| `Rumble-Canvas` | Rumble product | KEEP | 1 | 0 | 0 | MIT | `rumble-canvas` | No immediate cleanup. |
| `rumble-cos` | Rumble content/product site | KEEP | 1 | 0 | 0 | MIT | `rumble-cos` on `main` | PR stack #6/#5 merged; follow up Dependabot-reported default-branch advisories. |
| `Rumble-Crew` | Rumble product spec | KEEP | 1 | 0 | 0 | MIT | `rumble-crew` | No immediate cleanup. |
| `rumble-feed-mind` | Rumble product / active cleanup wave | KEEP | 2 | 0 | 5 | MIT | `rumble-feed-mind` on `main` | PR cleanup complete; decide/keep archive branch, then triage issues. |
| `Rumble-LM` | Rumble flagship slice | KEEP | 2 | 0 | 9 | MIT | `rumble-lm` | Inspect branch `i3-biscuit-auth-middleware`; close stale CI issues if superseded. |
| `Rumble-Note` | Rumble product spec | KEEP | 1 | 0 | 0 | MIT | `rumble-note` | No immediate cleanup. |
| `wrench-db-inspect` | Wrench DB/security evidence | KEEP | 1 | 0 | 0 | MIT | `wrench-db-inspect` | No immediate cleanup. |
| `wrench-dioxus-lab` | Wrench evidence lab | KEEP | 2 | 0 | 0 | MIT | `wrench-dioxus-lab` | PR #1 merged; keep `gh-pages` only if serving proof artifacts, otherwise prune after Pages decision. |

## Open PR queue

No public open PR remains after the 2026-07-06 cleanup pass.

## Open issue queue

| Repository | Issues | Cleanup rule |
| --- | --- | --- |
| `bolt-cos-matic` | #17, #41, #42, #43 | Close stale smoke issue if obsolete; keep product-feedback issues only if tied to a plan. |
| `rumble-feed-mind` | #1, #4, #5, #7, #8 | Reconcile with Dioxus target and cleanup PRs; close Leptos/Tauri items if superseded. |
| `Rumble-LM` | #26, #31, #32, #33, #34, #35, #36, #37, #41 | Close stale CI-failure issues if their branches are gone; keep mobile/webview issues only if part of current flagship slice. |

## Branch cleanup watchlist

Branches with no open PR need explicit review before deletion:

- `bolt-cos-matic`: `feat/stack-rule-check`.
- `portal-core`: `docs/plan-2026-07`, `feat/plan-2026-07-i1-deny-gate`.
- `rumble-ai-practices`: `docs/plan-2026-07`, `feat/consolidate-prototype`, `feat/keycap-design-app`, `slice-b-cohort-online`.
- `Rumble-LM`: `i3-biscuit-auth-middleware`.
- `rumble-feed-mind`: `archive-2026-07-legacy-nextjs`; keep until #21/archive decision is finalized.
- `dioxus`: `blitz`, `copilot/update-dioxus-reference`, `dependabot/github_actions/actions/cache-6`, `devin/*`, `docs/login-form-cookie-hardening`, `fix/server-fn-untyped-error-status`, `hook-docs`, `jk/*`, `v0.4`, `v0.5`, `v0.6`, `v0.7`; do not prune until fork purpose is re-checked.
- `dioxus-template`: `fix/jumpstart-template-polish`, `fix-fullstack-workspace`, `native-platform`, `v0.5`, `v0.6`, `v0.7`, `v0.8`; decide repo disposition first.
- `rumble-ai-benchmark`: `gh-pages`; keep if it serves the benchmark artifact, otherwise archive after verification.
- `wrench-dioxus-lab`: `gh-pages`; keep if it serves evidence artifacts, otherwise prune after Pages decision.

## Non-public / local divergence to resolve

| Item | Observed state | Decision needed |
| --- | --- | --- |
| `wrench-inspect` | GitHub repo exists but is private; local checkout is present and governed in `branch-policy.json`. | If it belongs to the public stack, make it public; otherwise mark it explicitly private/internal in docs. |
| `dioxus-app-template` | Local git repo, dirty `Cargo.lock`, no public GitHub repo found; `target-version.md` calls it the canonical starter. | Publish/rename it or update target docs to point to `dioxus-template`. |
| `dioxus` local checkout | Local `origin` points to `DioxusLabs/dioxus`, while public fork `constantin-jais/dioxus` exists. | Decide whether local should track upstream or the fork; document the fork workflow. |

## Disposition decisions needed

| Decision | Recommended default | Reason |
| --- | --- | --- |
| `dioxus-template` vs `dioxus-app-template` | Make exactly one canonical. Archive or rename the other. | Current target names `dioxus-app-template`, but public GitHub exposes `dioxus-template`; this is the clearest duplicate. |
| `wrench-inspect` visibility | Make public if it is part of the public forge; otherwise document as private/internal. | Inventory goal is public repos; governance already references it. |
| `rumble-ai-benchmark` | Archive once branch `feat/rumble-v1` is reconciled, unless benchmark maintenance is active. | Architecture notes call it a done benchmark artifact. |
| `dioxus` fork | Keep as reference while upstream PRs are in flight; prune only after PR closure. | External fork has many upstream/reference branches that may be useful evidence. |
| `constantin-jais` license | Add license or mark profile/control-plane license exemption. | GitHub reports missing license while other forge repos are MIT. |

## Recommended cleanup order

1. Decide `dioxus-template` vs `dioxus-app-template` because this is the clearest public duplication.
2. Resolve branch-policy/ruleset drift in a dedicated governance pass before editing `branch-policy.json` again.
3. Clean branches that have no open PR after checking unique commits, starting with low-risk evidence branches (`rumble-feed-mind` archive branch, `wrench-dioxus-lab` `gh-pages`) only after purpose is confirmed.
4. Triage issues in `Rumble-LM`, `rumble-feed-mind`, then `bolt-cos-matic`.
5. Decide archive/public status for `rumble-ai-benchmark` and `wrench-inspect`.
6. Reconcile `portal-core` and `rumble-ai-practices` local/public branch divergence.
7. Refresh this file and update `status.md` only with changed high-level state.

## Safe branch deletion checklist

Before deleting any branch:

```bash
gh pr list --repo constantin-jais/<repo> --head <branch> --state all

git -C <local-checkout> fetch origin

git -C <local-checkout> log --oneline origin/main..origin/<branch>

git -C <local-checkout> branch -r --merged origin/main | grep "origin/<branch>"
```

Delete only if either the branch is merged, or the decision to abandon it is documented here or in `specs/shared/decision-log.md`.
