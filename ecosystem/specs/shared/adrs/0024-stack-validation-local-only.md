# ADR-0024 — Stack validation stays local-only until explicit provisioning approval

- Status: Accepted
- Date: 2026-07-02
- Related: `../decision-log.md`, `../../../remaining-work.md`, `../../harness/04-stack-validation-tooling.md`

## Context

The ecosystem now has a coherent target stack across Rumble, Portal, Bolt, Wrench, and Gear. The next risk is not choosing technologies; it is accidentally turning stack exploration into paid infrastructure, hidden provider coupling, or premature platform automation.

The stack challenge accepted these outcomes:

- Rust service and Astro static publication are mature enough for GO.
- PostgreSQL/SQLx and Biscuit/OIDC are useful but conditional on real persistence, multi-tenant, or organizational identity needs.
- DB security gates are mandatory when PostgreSQL is used.
- Dioxus/PWA and RAG are promising but require local spikes before commitment.
- Redis, SwiftUI, and Compose wait for proven product pressure.
- Paid infrastructure, live providers, and provisioning are not allowed by default.

## Decision

Adopt a **local-only stack validation program** before any stack-specific implementation or provisioning.

Allowed by default:

- reading repositories and docs;
- generating scorecards, ADR candidates, fixtures, and dry-run plans;
- running local checks, local tests, local smoke tests, and local containers when explicitly requested;
- writing configuration examples that do not create remote resources.

Forbidden without a separate explicit human approval:

- creating or activating cloud apps, databases, buckets, queues, registries, secrets, or add-ons;
- calling paid AI/runtime providers;
- storing real PII or secrets in fixtures, prompts, logs, traces, or reports;
- adding mandatory US hyperscaler or proprietary SaaS dependencies to core truth;
- presenting dry-run readiness as production readiness.

## Stack decision matrix

| Track | Decision | Evidence required before promotion |
| --- | --- | --- |
| Rust service: Tokio, Axum, tracing, SQLx-ready | GO | fmt, clippy, tests, license/advisory audit, local smoke. |
| Astro/MDX/Bun static publication | GO | static build, self-hosted assets, no tracking/CDN by default, smoke. |
| PostgreSQL + SQLx | Conditional GO | durable persistence need, migrations, local fixtures, DB security evidence. |
| OIDC/Keycloak + Biscuit | Conditional GO | org/multi-tenant need, allow/deny policy fixtures, token redaction proof. |
| DB security / RLS / grants / pgvector | GO as gate | sanitized schema/migration fixtures and Wrench DB evidence. |
| Dioxus/PWA + Portal | SPIKE LOCAL | wasm32 check, mobile smoke, Portal boundary, no JS-readable auth token. |
| RAG / pgvector / citation generation | SPIKE LOCAL STRICT | fixture-first retrieval/generation, citation validation, redaction, retention policy. |
| Redis / persisted queues | WAIT | product slice proves critical jobs, fanout, retries, or durability. |
| SwiftUI / Compose through Portal | WAIT | PWA proof plus native product need and local SDK/build evidence. |
| Paid infra / provisioning / live providers | NO-GO | requires a later explicit approval ADR or runbook gate. |

## Consequences

- `pi -p` sessions must start from a stated local validation target and expected evidence.
- Stack choices remain hypotheses until their local gates produce evidence.
- The accepted stack posture is auditable in the shared decision log, status cockpit, remaining work, and harness tooling spec.
- Deployment/provider work remains recommendation or dry-run until a human explicitly changes the operating mode.
