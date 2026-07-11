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
| `libre-ai/boussole-politique` | autonomous civic product | keep | profile, local-first boundary, Rust contracts and deterministic assets |
| `libre-ai/ai-practices` | product dojo | keep | profile, visual and protected quality gates |
| `libre-ai/benchmarks` | evidence | keep | profile, visual and published Pages artifact |
| `libre-ai/dioxus-app-template` | generated distribution | keep | Portal mirror check and deployed Pages smoke |
| `libre-ai/client-kit` | infrastructure | keep canonical | renamed with redirect; four imported histories, adapters, forge and template |
| `libre-ai/bolt` | infrastructure | keep canonical | engine/harness histories and boundary checks |
| `libre-ai/wrench` | infrastructure | keep canonical | inspectors/lab histories and evidence checks |
| `libre-ai/gear` | infrastructure | keep canonical | Context/Supply histories and workspace isolation |

Every row above has an entry in both the public repository profile catalogue and branch policy. The profile validator rejects private visibility, duplicate slugs, non-canonical URLs and profile/policy drift.

## Ratified topology migration

ADR 0045 ratifies these serial changes; a row remains `planned` until live metadata, policy, profiles, consumers and local paths all agree.

| Current | Target | State | Compatibility rule |
| --- | --- | --- | --- |
| `libre-ai/portal` | `libre-ai/client-kit` | complete | GitHub redirect verified; crate/schema identifiers unchanged |
| `libre-ai/bolt` | `libre-ai/agent-factory` | planned | GitHub redirect; engine/binary/contract identifiers unchanged |
| `libre-ai/wrench` | `libre-ai/proof-kit` | planned | GitHub redirect; qualified release and archive names unchanged |
| `libre-ai/gear` | `libre-ai/context-kit` + `libre-ai/artifact-supply` | planned split | path-history extraction; full-history Gear retained as archived compatibility repository |
| `constantin-jais/constantin-jais` | `libre-ai/ecosystem` | blocked | GitHub Support privacy gate remains mandatory |

## Superseded source repositories

| Family | State | Exit condition |
| --- | --- | --- |
| Portal sources (4) | archived | complete — histories, checks and consumers verified in `libre-ai/client-kit` |
| Bolt sources (2) | migration freeze | release/manual workflow continuity from `libre-ai/bolt` |
| Wrench sources (3) | migration freeze | release and evidence-Pages continuity from `libre-ai/wrench` |
| Gear sources (4) | migration freeze | package/release continuity from isolated Gear workspaces |

A migration freeze permits security remediation only. It does not permit feature work or divergent documentation.

## Control plane

The control plane remains in its current namespace while GitHub Support processes inaccessible pull-request refs left by the privacy history rewrite. Transfer is allowed only after:

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
