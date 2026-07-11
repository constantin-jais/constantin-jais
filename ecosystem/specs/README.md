# Ecosystem Specifications

This directory contains the product specifications for active Rumble dojos and selected shared Portal/Bolt/Wrench/Gear capability specs.

The goal is not to write static documentation or rank products by business potential. The goal is to create implementation-ready learning and process contracts that connect:

- product intent;
- roles and permissions;
- screens and actions;
- domain logic;
- data models;
- services and APIs;
- security/RGPD constraints;
- shared Portal/Bolt/Wrench/Gear capabilities.

## Active Rumble Dojos

| Product | Spec status | Learning role | Purpose |
| --- | --- | --- | --- |
| `rumble-canvas` | `contract-first` / harness producer | Specification, ambiguity, decisions, traceability, handoff. | Product-conception workspace: conversations → decisions → specs → packages → handoffs. |
| `rumble-libre-ia` | `usable` public site / ecosystem spec incomplete | Transmission, clarity, publication, public documentation. | Education and sharing blog. |
| `rumble-crew` | `contract-first` | Human/agent tasks, approvals, evidence, recovery. | Human/agent teamwork workspace. |
| `rumble-feed-mind` | `dojo` / ready for scoped implementation planning | Watch pipeline, ingestion pressure, rules, BYOK, export. | Intelligent feed/watch pipeline producing curated knowledge for the harness. |
| `rumble-lm` | `contract-first` / P0 stub | Pedagogy, citations, live sessions, grounding. | Source-grounded learning and facilitation platform. |
| `rumble-note` | `contract-first` | Local-first PKM, privacy, memory exports. | Local-first block-based personal knowledge system. |

## Shared Capability Specs

| Capability | Spec status | Purpose |
| --- | --- | --- |
| `portal-*` | Accepted placement / repo-local specs | Client platform: design tokens, accessibility, i18n UI, Rust-first bindings, and web/native adapters for Rumble products. |
| `gear-loader` | Accepted placement / migration from former `wrench-loader` specs | Canonical ingestion/extraction for files, URLs, feeds, code, OCR/STT candidates, and evidence reports. Historical `wrench-loader` specs remain migration references until schema paths are renamed. |
| `wrench-db-inspect` | Draft/prototype | SQL/database security inspection for PostgreSQL, RLS, grants, migrations, `pgvector`, tenant isolation, and ecosystem/harness evidence for Postgres-backed `rumble-*`. |
| Stack validation tooling | P0 spec | Local-only tools for project status, stack detection, scorecards, dependency audit, and local smoke before implementation or provisioning. |

## Spec Rule

Every product spec must identify when a need is product-specific and when it should become a shared capability.

Do not copy shared primitive definitions into each Rumble spec. Link to the shared contract/registry and document only the product-specific instantiation, constraints, and open questions.

`constantin-jais/ecosystem/specs/` is the canonical ecosystem specification root. Do not create or edit a parallel root-level `Documents/specs/` tree; use repository-local `docs/` only for local usage, ADRs, runbooks, implementation notes, and commands.

Shared capabilities are logged in:

- `shared/shared-capabilities.md`

Shared contracts and release runbooks include:

- `shared/contracts/implementation-handoff.v0.1.md`
- `shared/contracts/app-store-release.v0.1.md`
- `shared/runbooks/ios-appstore-release.md`
- `harness/stack-project-maturity.v0.1.schema.json`
- `harness/04-stack-validation-tooling.md`
- `harness/stack-target-version.v0.1.schema.json`

Session doctrine, decisions, and unresolved questions are logged in:

- `shared/session-design-principles.md`
- `shared/decision-log.md`
- `shared/open-questions.md`

## Product Spec Structure

Each product should eventually contain:

```text
00-product-charter.md
01-personas-and-roles.md
02-user-journeys.md
03-information-architecture.md
04-screens-and-actions.md
05-domain-model.md
06-data-model.md
07-services-and-apis.md
08-events-and-workflows.md
09-permissions-security-rgpd.md
10-non-functional-requirements.md
11-acceptance-tests.md
12-open-questions.md
```

Use `shared/spec-template.md` as the canonical template.
