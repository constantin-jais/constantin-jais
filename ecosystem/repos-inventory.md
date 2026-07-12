# Public repository inventory and migration ledger

Status date: 2026-07-11

This file tracks public topology and disposition. It does not override [`governance/repo-profiles.json`](governance/repo-profiles.json), [`status.md`](status.md), or architecture decisions.

## Safety rules

- Inventory and freeze precede transfer, rename, archive or deletion.
- Compare all branch, tag and pull-request refs before moving history.
- Keep private project names and metadata out of public profiles and reports.
- Prefer archive to deletion unless privacy or security requires removal.
- Never archive a source repository until release, package and Pages consumers have moved.
- Historical crate, schema and contract identifiers are changed only through an explicit compatibility migration.

## Canonical public repositories

| Repository | Domain | Disposition | Evidence |
| --- | --- | --- | --- |
| `libre-ai/website` | institutional | keep | profile, visual, Dioxus CI and browser smoke |
| `libre-ai/sessions` | product | keep | profile, visual and protected Rust gates |
| `libre-ai/feed-radar` | product | keep | profile, visual and protected Rust gates |
| `libre-ai/spec-studio` | product | keep | profile, visual and handoff checks |
| `libre-ai/agent-board` | product specification | keep | profile, visual and repository hygiene |
| `libre-ai/notebook` | product specification | keep | profile, visual and repository hygiene |
| `libre-ai/boussole-politique` | autonomous civic product | keep | profile, local-first boundary, Rust contracts, deterministic assets and portable analytical dry-run |
| `libre-ai/ai-practices` | product dojo | keep | profile, visual and protected quality gates |
| `libre-ai/benchmarks` | evidence | keep | profile, visual and published Pages artifact |
| `libre-ai/dioxus-app-template` | generated distribution | keep | Client Kit mirror check and deployed Pages smoke |
| `libre-ai/client-kit` | infrastructure | keep canonical | renamed with redirect; four imported histories, adapters, forge and template |
| `libre-ai/agent-factory` | infrastructure | keep canonical | renamed with redirect; engine/harness histories, boundary checks and installable `engine-v0.1.0-alpha.6` release |
| `libre-ai/proof-kit` | infrastructure | keep canonical | renamed with redirect; inspectors/lab histories, evidence checks and corrected installable `db-inspect-v0.1.0-alpha.7` release |
| `libre-ai/context-kit` | infrastructure | keep canonical | `context/` path history, independent workspace and supply-chain CI |
| `libre-ai/artifact-supply` | infrastructure | keep canonical | `supply/` path history, independent workspace and supply-chain CI |
| `libre-ai/gear` | compatibility infrastructure | archived | full pre-split history and old paths; zero active consumers and no new feature ownership |

Every row above has an entry in both the public repository profile catalogue and branch policy. The profile validator rejects private visibility, duplicate slugs, non-canonical URLs and profile/policy drift.

## Ratified topology migration

ADR 0045 ratifies these serial changes; a row remains `planned` until live metadata, policy, profiles, consumers and local paths all agree.

| Current | Target | State | Compatibility rule |
| --- | --- | --- | --- |
| `libre-ai/portal` | `libre-ai/client-kit` | complete | GitHub redirect verified; crate/schema identifiers unchanged |
| `libre-ai/bolt` | `libre-ai/agent-factory` | complete | GitHub redirect verified; engine/binary/contract identifiers unchanged |
| `libre-ai/wrench` | `libre-ai/proof-kit` | complete | repository/release redirects verified; Pages moved to `/proof-kit/`; qualified release/archive names unchanged |
| `libre-ai/gear` | `libre-ai/context-kit` + `libre-ai/artifact-supply` | complete | path histories, independent CI and consumer migration verified; full-history Gear archived at `0c7f35f` |
| `constantin-jais/constantin-jais` | `libre-ai/ecosystem` | blocked | GitHub Support privacy gate remains mandatory |

## Superseded source repositories

| Family | State | Exit condition |
| --- | --- | --- |
| Portal sources (4) | archived | complete — histories, checks and consumers verified in `libre-ai/client-kit` |
| Bolt sources (2) | retired after verified consolidation | engine release continuity restored in `libre-ai/agent-factory`; historical alpha.1–alpha.5 remain source-only |
| Wrench sources (3) | retired or archived | release and evidence-Pages continuity moved to `libre-ai/proof-kit` |
| Gear sources (4) | deleted after verified bundles; no published releases | active code and path history preserved in Gear, Context Kit and Artifact Supply |

A migration freeze permits security remediation only. It does not permit feature work or divergent documentation.

## Control plane

The control plane remains in its current namespace. A fresh 2026-07-12 mirror audit confirms that 152 changed pre-rewrite commits remain reachable from GitHub pull-request refs, while zero remain reachable from public branches or tags. Transfer is allowed only after:

1. Support confirms cache and hidden-ref cleanup;
2. a fresh public-history privacy scan passes;
3. a mirror bundle and ref manifest are refreshed;
4. required checks and the governance token target are prepared for the new namespace.

## Automated dependency queue

Dependabot pull requests are a separate maintenance queue. They are not migration evidence and are not bulk-merged. Each update must pass the owning repository's protected checks and receive a compatibility review, especially major-version GitHub Actions and runtime dependency updates.

Live query:

```sh
for repo in website sessions feed-radar spec-studio agent-board notebook \
  ai-practices benchmarks dioxus-app-template portal bolt wrench gear; do
  gh pr list --repo "libre-ai/$repo" --state open \
    --json number,title,author,mergeStateStatus
 done
```

## Verification and archive checklist

Before archiving a superseded source:

```sh
# Refs and unique commits
git ls-remote --heads --tags <source-url>
git log --oneline <target-main>..<source-ref>

# Consumers and published surfaces
rg -n '<source-slug>|<source-url>' <public-checkouts>
gh release list --repo <owner/source>
gh api repos/<owner/source>/pages

# Target health
gh pr checks <target-pr> --repo libre-ai/<target>
gh run list --repo libre-ai/<target> --branch main --limit 10
```

Record release/Pages redirects or compatibility shims before the archive mutation. Archive operations remain serial and require a post-operation visibility, ruleset and URL check.
