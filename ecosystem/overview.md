# Ecosystem Overview & Specification Control Plane

This document is the strategic control plane for the Rumble / Bolt / Wrench / Gear ecosystem.

It has four jobs:

1. Define the architectural doctrine and ownership boundaries.
2. Track the product-specification work for each Rumble product.
3. Log shared capability candidates that may become Bolt, Wrench, Gear, or shared Rumble bricks.
4. Keep decisions, open questions, and remaining work visible.

No external product inspirations are listed here. Inspirations may be used privately during discovery, but public specs must describe the ecosystem’s own product intent, language, and architecture.

---

## 1. North Star

The ecosystem exists to build sovereign, deterministic, agent-readable tools and products where user-facing needs generate reusable capabilities.

It is primarily a personal forge for intellectual enjoyment, learning, process quality, and robust working tools. The first-order goal is not market traction or startup-style prioritization. Rumble projects are dojos: they create real constraints for improving the stack, but the reliable process is more important than any single Rumble product.

The center of gravity is:

```text
idea → specification → inspection → planning → controlled execution → evidence → memory → improvement
```

The product layer does not hard-code everything. Instead:

> Rumble products express real user needs. Repeated needs become shared primitives. Shared primitives are placed in Bolt, Wrench, Gear, or a shared Rumble layer according to ownership.

This keeps products useful, the harness reusable, and the architecture resistant to scope creep.

Current cross-project status lives in `status.md`. The target self-improving process loop lives in `loop.md`.

---

## 2. Architecture Doctrine

### 2.1 Isolation by Responsibility

A repository is not defined by its technology. It is defined by the responsibility it is allowed to own.

Each repository must answer:

1. What user or system problem does it solve?
2. Which layer owns that problem?
3. What does it deliberately refuse to do?
4. Which lower-layer capabilities does it consume?
5. Which upper-layer products or agents consume it?
6. What would be a scope leak?

Rule:

> A layer may consume capabilities from lower layers, but must not absorb their responsibility.

Examples:

- A **Rumble** product may call ingestion, memory, orchestration, or artifact capabilities, but must not become a data extractor, registry, or agent runtime.
- **Bolt** may decide, sequence, and coordinate, but must not become a product UI, database, parser, or package registry.
- **Wrench** may transform, inspect, and validate, but must not decide product strategy or own persistent truth.
- **Gear** may store, transport, compile, verify, and connect, but must not contain business workflows or product logic.

### 2.2 Boundary Tests

Use these tests whenever a feature is ambiguous:

| If the feature primarily...                                             | It belongs in... |
| ----------------------------------------------------------------------- | ---------------- |
| defines what the user sees, manipulates, or experiences                 | **Rumble**       |
| decides what should happen, sequences work, or enforces execution gates | **Bolt**         |
| extracts, transforms, audits, validates, or produces evidence           | **Wrench**       |
| stores, indexes, transports, verifies, packages, syncs, or connects     | **Gear**         |

If two products need the same thing, do not duplicate it blindly. Identify the primitive and decide where it belongs.

### 2.3 Documentation Ownership and Anti-Duplication

Documentation is part of the architecture. To avoid dispersion:

- `overview.md` owns stable doctrine, layer boundaries, and architecture rules.
- `status.md` owns current maturity, next quality steps, and verification commands.
- `loop.md` owns the target idea-to-proof-to-memory process loop.
- `specs/shared/` owns reusable contracts, shared capabilities, decisions, and open questions.
- Product/tool repository READMEs own local usage, local boundary, and local commands only.
- Repository ADRs own repo-local decisions; cross-project decisions belong in `specs/shared/decision-log.md`.
- A Rumble spec may express the need for a primitive, but must not duplicate the owner primitive if it belongs in Bolt, Wrench, or Gear.

### 2.4 Strategic Directives

- **Single responsibility:** one repository, one primary responsibility, one layer.
- **No hidden ownership:** each README/spec must state what the project does not do.
- **Agent-readable by default:** commands, outputs, contracts, and decisions must be understandable by humans and LLM agents.
- **Determinism over magic:** no silent overwrites, hidden state, or untraceable decisions.
- **Sovereignty first:** core truth — data, registry, model policy, release pipeline, logic — must remain self-hostable, inspectable, and independent from US hyperscalers.
- **Offline-first where possible:** network access may improve the experience, but must not be required for core truth.
- **Evidence over claims:** specs, tests, ADRs, provenance, and audit logs matter more than informal trust.
- **Product demand drives platform work:** Bolt/Wrench/Gear bricks should be justified by at least one concrete Rumble need, preferably more than one.
- **Interactive Rumble convergence:** interactive Rumble products should converge on Rust core + Dioxus UI unless an ADR/waiver justifies an exception. `rumble-cos` remains Astro because it is a public content site.

---

## 3. Ecosystem Map

### 3.1 Rumble — Product Layer

Rumble projects own product experience, workflows, screens, and user-facing meaning.

| Product            | Mission                                                                                                       | Hard boundary                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `rumble-canvas`    | Product-conception workspace: conversation → decisions → specs → screens → implementation-ready deliverables. | Not the agent runtime, not merely a visual design canvas.                            |
| `rumble-cos`       | Personal education and sharing blog for essays, courses, resources, and ecosystem explanations.               | Not a monolithic CMS or internal workflow backend.                                   |
| `rumble-crew`      | Agentic team workspace for humans and agents: tasks, blockers, skills, status, approvals, evidence.           | Not the orchestration brain.                                                         |
| `rumble-lm`        | Sovereign learning/facilitation platform for source-grounded sessions, activities, and group engagement.      | Not a generic chatbot.                                                               |
| `rumble-note`      | Local-first block-based personal knowledge system that feeds the agentic harness.                             | Not the ingestion engine or orchestrator.                                            |
| `rumble-feed-mind` | Intelligent feed/watch pipeline that turns high-volume feeds into curated, explainable, reusable knowledge.   | Not a generic feed reader, not the shared ingestion substrate, not long-term memory. |

### 3.2 Bolt — Orchestration Layer

| Project        | Mission                                                                  | Hard boundary                                                |
| -------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `cos-matic`    | Deterministic agentic orchestrator and config/code-ops harness.          | Not a product UI, storage substrate, extractor, or registry. |
| `bolt-harness` | Proof benchmarks and harness substrate for orchestration engine designs. | Not engine code, not product runtime.                        |

### 3.3 Wrench — Tooling Layer

| Project             | Mission                                                                                                                                          | Hard boundary                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `wrench-inspect`    | General structural, design, and policy inspection.                                                                                               | Not a domain-specific DB security owner.                                                                            |
| `wrench-db-inspect` | SQL/database security inspection and forge/harness evidence for Postgres-backed `rumble-*`: pgvector, RLS, grants, migrations, tenant isolation. | Not a user-facing vault app, secrets manager, ORM, DB proxy, migration runner, or replacement for `wrench-inspect`. |

Naming clarification: `wrench-db-inspect` belongs to the Wrench tooling layer after the rename from `vault-inspector`. The former `vault-inspector` name was retired to remove ambiguity while preserving the same scope boundary.

### 3.4 Gear — Infrastructure Layer

| Project       | Mission                                                                                           | Hard boundary                  |
| ------------- | ------------------------------------------------------------------------------------------------- | ------------------------------ |
| `gear-loader` | Rich-document ingestion and canonical extraction (renamed from `wrench-loader`).                  | Not a knowledge product.       |
| `gear-memory` | Local agentic context and memory substrate: code maps, repo memory, document/search primitives.   | Not an agent brain or product. |
| `gear-depot`  | Sovereign supply-chain depot: registry proxy/cache, policy, provenance, artifact verification.    | Not a generic file store.      |
| `gear-cable`  | Rust-first release/distribution substrate: artifact plans, checksums, signatures, install floors. | Not application runtime logic. |

### 3.5 Portal — Design Substrate Layer

| Project          | Mission                                                                      | Hard boundary                                |
| ---------------- | ---------------------------------------------------------------------------- | -------------------------------------------- |
| `portal-core`    | Thin shared identity, permission, and tenant boundary primitives for Portal. | Not a full identity service, not a UI kit.   |
| `portal-forge`   | Design-system token compiler and WCAG validation harness for Portal UI.      | Not a component library, not design docs.    |
| `portal-apple`   | iOS publication bridge via UniFFI.                                           | Not a native iOS product, not native UI.     |
| `portal-android` | Android publication bridge via platform-specific runtime.                    | Not a native Android product, not native UI. |

---

## 4. Specification Method

The specs must be detailed enough for both humans and agents to implement safely.

A good spec is not only a feature list. It is a contract between product, architecture, data, services, security, and delivery.

### 4.1 Session Design Principles

Every design session must follow `specs/shared/session-design-principles.md`:

1. avoid dangerous duplication by identifying what the capability centralizes;
2. strengthen Rumble products without imposing a premature abstract platform;
3. produce contracts, boundaries, ADR candidates, and acceptance tests before code;
4. keep sovereignty as a hard filter: no mandatory US SaaS, blocking license, opaque storage, or PII/secrets in logs;
5. turn starred repositories into design capital for challenge, benchmarks, risks, and justification — not into a raw backlog.

### 4.2 Required Spec Files per Product

Target structure:

```text
specs/
  README.md
  shared/
    glossary.md
    spec-template.md
    shared-capabilities.md
    decision-log.md
    open-questions.md
  rumble-canvas/
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
  rumble-cos/
    ...same structure...
  rumble-crew/
    ...same structure...
  rumble-lm/
    ...same structure...
  rumble-note/
    ...same structure...
  rumble-feed-mind/
    ...same structure...
  harness/
    README.md
    fixtures/handoffs/
```

Shared contracts live under:

```text
specs/shared/contracts/
  implementation-handoff.v0.1.md
  app-store-release.v0.1.md
```

### 4.2 Product Charter Requirements

Each product charter must include:

- mission;
- target users;
- primary jobs-to-be-done;
- promise;
- non-goals;
- product boundaries;
- success metrics;
- risks;
- dependencies on Bolt/Wrench/Gear;
- MVP scope;
- post-MVP scope.

### 4.3 Persona and Role Requirements

For each role:

- goal;
- motivations;
- permissions;
- visible data;
- editable data;
- allowed actions;
- forbidden actions;
- edge cases;
- trust/security expectations.

Roles must be product-specific but mapped to shared permission primitives when possible.

### 4.4 Journey Requirements

Each journey must include:

- trigger;
- actor;
- preconditions;
- happy path;
- alternate paths;
- failure paths;
- recovery path;
- data created/updated;
- events emitted;
- audit requirements;
- acceptance criteria.

### 4.5 Screen Specification Requirements

Every screen spec must include:

- purpose;
- route or navigation entry;
- allowed roles;
- displayed data;
- primary actions;
- secondary actions;
- destructive actions;
- empty states;
- loading states;
- error states;
- offline states;
- permission-denied states;
- accessibility notes;
- telemetry/events;
- service/API calls;
- acceptance criteria.

For each screen, actions must be listed by role.

### 4.6 Action Specification Requirements

Every action must include:

- actor;
- intent;
- input;
- preconditions;
- business rules;
- validation rules;
- side effects;
- emitted events;
- audit log entry;
- permission check;
- idempotency behavior;
- rollback/retry behavior;
- errors;
- acceptance criteria.

### 4.7 Domain Model Requirements

The domain model must define:

- entities;
- value objects;
- aggregate boundaries where relevant;
- relationships;
- invariants;
- lifecycle states;
- state transitions;
- ownership rules;
- deletion/archive rules;
- event names;
- shared capability candidates.

### 4.8 Data Model Requirements

The data model must include:

- tables/collections;
- columns and types;
- relationships;
- indexes;
- constraints;
- RLS or authorization rules when applicable;
- audit tables/events;
- soft delete vs hard delete;
- retention policy;
- local-first/sync behavior;
- migration strategy;
- PII classification;
- backup/restore expectations.

### 4.9 Service and API Requirements

Services must be separated clearly:

- UI/application services;
- domain services;
- API endpoints;
- background jobs;
- Bolt calls;
- Wrench calls;
- Gear calls;
- external integrations, if any.

For every service/API:

- owner layer;
- inputs/outputs;
- auth requirements;
- idempotency;
- rate limits if relevant;
- failure modes;
- observability;
- test strategy.

### 4.10 Non-Functional Requirements

Each product must specify:

- security;
- privacy/RGPD;
- data residency expectations;
- offline behavior;
- sync/conflict handling;
- performance targets;
- accessibility;
- internationalization if relevant;
- observability;
- auditability;
- portability/self-hosting;
- backup/restore;
- disaster recovery;
- cost constraints.

### 4.11 Acceptance Tests

Specs should produce testable acceptance criteria:

- scenario-based Given/When/Then;
- role-based permission tests;
- screen smoke tests;
- domain invariant tests;
- API contract tests;
- migration tests;
- security/RLS tests;
- offline/sync tests where relevant.

---

## 5. Product Specification Roadmap

### Status Legend

- **Not started** — no structured spec yet.
- **Drafting** — product intent and early model being written.
- **Review** — needs challenge against architecture and shared capabilities.
- **Accepted** — ready to feed implementation planning.
- **Implemented** — implemented and verified.

| Product            | Current status              | Immediate objective                                                                                             | Main risk                                                                  |
| ------------------ | --------------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `rumble-canvas`    | Drafting / harness-critical | Finalize data/events/tests and use it to validate `ImplementationHandoff v0.1`.                                 | Building UI before the product-to-harness flow is validated.               |
| `rumble-cos`       | Not started                 | Define education-first content model and artifact publication flow.                                             | Becoming a generic CMS.                                                    |
| `rumble-crew`      | Drafting                    | Define human/agent task lifecycle, board UX, approvals, evidence, and `cos-matic` boundary.                     | Reimplementing orchestration instead of displaying/controlling it.         |
| `rumble-feed-mind` | Imported / needs alignment  | Decide product-vs-pipeline boundary, feed ingestion ownership, license policy, and curated-item export.         | Becoming a generic feed reader or duplicating Wrench/Gear primitives.      |
| `rumble-lm`        | Drafting / advanced         | Consolidate source-grounded live sessions, activities, citations, summaries, exports, analytics, and retention. | Over-expanding into LMS/asynchronous learning or generic chatbot behavior. |
| `rumble-note`      | Drafting / advanced         | Clarify local-first block model, Gear Memory boundary, and deterministic note/context handoff.                  | Absorbing ingestion/orchestration/memory responsibilities.                 |

### Recommended Order

1. **Harness P0** — validate `ImplementationHandoff v0.1` through `cos-matic` before product dev.
2. **`rumble-canvas`** — because it defines spec packages and the first product-to-harness flow.
3. **`rumble-note`** — because it defines personal knowledge primitives and local-first context.
4. **`rumble-feed-mind`** — because it creates curated external sources that can feed Note/LM/COS/agents.
5. **`rumble-lm`** — because it depends on sources, sessions, participants, and facilitation flows.
6. **`rumble-crew`** — because it depends on agent task lifecycle and Bolt integration.
7. **`rumble-cos`** — because it can publish lessons, specs, and ecosystem outputs once the content model is clear.

---

## 6. Shared Capability Registry

This section logs capabilities that appear across multiple products. Each candidate must eventually be placed in one of: shared Rumble UI/domain, Bolt, Wrench, Gear, or a dedicated repository.

Status values:

- **Candidate** — identified, not decided.
- **Discuss** — needs naming/placement decision.
- **Accepted** — owner chosen.
- **Rejected** — not shared after analysis.

| Capability                      | Needed by                                                                     | Candidate owner                                                     | Status    | Notes                                                                                                                                                                               |
| ------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workspace / project space       | All Rumbles                                                                   | Discuss: shared Rumble vs Gear                                      | Candidate | Common boundary for users, permissions, content, runs, and settings.                                                                                                                |
| Source                          | `rumble-note`, `rumble-lm`, `rumble-canvas`, `rumble-cos`, `rumble-feed-mind` | Gear Memory + Gear Loader                                           | Candidate | URL, file, note, transcript, feed item, document, dataset; needs provenance.                                                                                                        |
| Artifact                        | All Rumbles                                                                   | Gear Depot + Gear Memory                                            | Candidate | Spec, article, quiz, screen map, execution report, exported package.                                                                                                                |
| Decision record                 | `rumble-canvas`, `rumble-crew`, `rumble-lm`                                   | Bolt for operational decisions; Rumble shared for product decisions | Discuss   | Must distinguish product decisions from execution decisions.                                                                                                                        |
| Activity/event log              | All Rumbles                                                                   | Gear                                                                | Candidate | Immutable-ish history for audit, collaboration, and agent readability.                                                                                                              |
| Comment/thread                  | `rumble-canvas`, `rumble-crew`, `rumble-lm`, maybe `rumble-note`              | Shared Rumble                                                       | Candidate | User-facing collaboration primitive.                                                                                                                                                |
| Agent task                      | `rumble-crew`, `rumble-canvas`, `rumble-note`, `rumble-lm`                    | Bolt / `cos-matic`                                                  | Candidate | Rumble may display and request tasks; Bolt owns lifecycle/execution.                                                                                                                |
| Approval/gate                   | `rumble-crew`, `rumble-canvas`, `rumble-lm`                                   | Bolt + Rumble UX                                                    | Candidate | Human approval before execution, publication, or generation.                                                                                                                        |
| Skill/capability card           | `rumble-crew`, `rumble-canvas`, `rumble-note`                                 | Bolt or shared Rumble                                               | Discuss   | Reusable agent/tool capabilities exposed to users.                                                                                                                                  |
| Notification                    | All Rumbles                                                                   | Shared Rumble or service                                            | Candidate | User-facing delivery; events likely come from Gear/Bolt.                                                                                                                            |
| Permission/audit policy         | All Rumbles                                                                   | Gear + app-level adapters                                           | Candidate | Must support local-first and self-hosted operation.                                                                                                                                 |
| Source-grounded generation      | `rumble-lm`, `rumble-canvas`, `rumble-cos`, `rumble-note`                     | Bolt + Wrench + Gear Memory                                         | Candidate | Needs citations, provenance, and validation.                                                                                                                                        |
| Import pipeline                 | `rumble-note`, `rumble-lm`, `rumble-cos`, `rumble-feed-mind`                  | Gear Loader                                                         | Candidate | Files/URLs/transcripts/feed items into canonical content.                                                                                                                           |
| Feed ingestion                  | `rumble-feed-mind`, maybe `rumble-note`, `rumble-cos`                         | Gear Loader                                                         | Accepted  | Feed parsing/normalization is Gear Loader P0; polling/rules/curation remain FeedMind/Bolt.                                                                                          |
| Rule explanation                | `rumble-feed-mind`, maybe `rumble-lm`, `rumble-canvas`                        | Rumble UX + Wrench validation                                       | Candidate | Natural-language rule decisions need inspectable explanation and evidence.                                                                                                          |
| BYOK/provider policy            | `rumble-feed-mind`, `rumble-lm`, `rumble-canvas`                              | Shared security policy + Bolt/Gear adapters                         | Candidate | Model routing, key storage, redaction, and provider constraints must be consistent.                                                                                                 |
| Citation support validation     | `rumble-lm`, `rumble-canvas`, `rumble-cos`                                    | Wrench validator/inspector + Rumble UX                              | Candidate | Assess whether cited source excerpts support generated claims; human validation remains product-owned where needed.                                                                 |
| Live participation / presence   | `rumble-lm`, `rumble-crew`, maybe `rumble-canvas`                             | Shared Rumble vs Gear transport                                     | Candidate | Current activity state, presence, response submission, reconnect, and aggregate updates.                                                                                            |
| Learning/facilitation analytics | `rumble-lm`, maybe `rumble-cos`                                               | Shared Rumble first                                                 | Candidate | Aggregate participation, comprehension, confusion, consensus/divergence; avoid hidden individual profiling.                                                                         |
| Export package                  | `rumble-lm`, `rumble-canvas`, `rumble-cos`                                    | Gear artifact + Rumble UX                                           | Candidate | Audience-scoped export with included data classes, provenance, checksum, and retention/revocation metadata.                                                                         |
| Inspector reports               | `rumble-canvas`, `rumble-crew`, `rumble-cos`, `rumble-lm`                     | Wrench Inspect                                                      | Candidate | Validate specs, content, design, policy, citation support, privacy, or readiness.                                                                                                   |
| Evidence report                 | Rumbles, Bolt gates, CI/harness                                               | Wrench Inspect + domain Wrench inspectors                           | Candidate | Shared evidence model for API/browser/eval/clean-room/DB checks; `wrench-db-inspect` produces the DB-security specialization consumed by the forge/harness.                         |
| Agent/run policy gate           | `cos-matic`, `rumble-crew`, `rumble-canvas`, Wrench checks                    | `cos-matic`                                                         | Candidate | Versioned gates for secrets, destructive actions, network, license, sovereignty, citations, and human approval.                                                                     |
| Source catalog                  | `rumble-note`, `rumble-feed-mind`, `rumble-lm`, Gear Loader/Inspect           | Gear Memory                                                         | Candidate | Catalog over `SourceRef`; avoids separate `gear-source` until extraction criteria are met.                                                                                          |
| Usage ledger                    | Bolt runs, Wrench checks, Gear artifacts, Rumble handoffs                     | Gear Memory first                                                   | Candidate | Append-only technical usage events and aggregate projections without behavioral profiling.                                                                                          |
| Payload projection              | Bolt handoffs, Wrench reports, Gear manifests, agent context exports          | Gear Depot or shared Gear library                                   | Candidate | Compact projections from canonical JSON/NDJSON; never source of truth.                                                                                                              |
| Release floor                   | Gear Cable releases and installable tools                                     | Gear Cable                                                          | Candidate | Target matrix, install floors, artifact plans, checksum/signature plans, and Depot manifest handoff.                                                                                |
| App Store release adapter       | iOS-capable `rumble-*` products                                               | Gear Cable                                                          | Accepted  | Stable Gear Cable channel around pinned `rorkai/App-Store-Connect-CLI` (`asc 2.5.0`); product pipelines call `app-store-release.v0.1` actions, not upstream CLI flags directly.     |
| Design system descriptor        | `portal-forge`, `rumble-canvas`, `rumble-cos`, other UI surfaces              | Portal Forge + Gear                                                 | Candidate | Normalized form of any ingested design system: DTCG tokens, component descriptors, and WCAG validators. Needed by `rumble-canvas`, `portal-forge`, any design-system-aware product. |

### Naming Rules for Shared Bricks

When a capability becomes shared, choose a name by responsibility:

- **Rumble shared** names should describe user-facing product primitives: `thread`, `workspace`, `presence`, `notification`.
- **Bolt** names should describe orchestration primitives: `run`, `plan`, `gate`, `approval`, `agent-task`.
- **Wrench** names should describe callable capabilities: `loader`, `inspector`, `validator`, `extractor`.
- **Gear** names should describe substrate primitives: `source`, `artifact`, `memory-entry`, `event-log`, `provenance`.

Do not name a shared brick after a single product unless it truly belongs only to that product.

---

## 7. Current Decisions

| Date       | Decision                                                                                                                                                                           | Reason                                                                                                                                                                                                                                                                                  | Status   |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 2026-06-30 | Active Rumble products in scope: `rumble-canvas`, `rumble-cos`, `rumble-crew`, `rumble-feed-mind`, `rumble-lm`, `rumble-note`.                                                     | `rumble-feed-mind` is added as a feed/watch product that must align with shared Wrench/Gear/Bolt boundaries.                                                                                                                                                                            | Accepted |
| 2026-06-30 | External inspirations are private discovery context, not public spec content.                                                                                                      | Avoid cloning language and keep product identity original.                                                                                                                                                                                                                              | Accepted |
| 2026-06-30 | `overview.md` becomes the specification control plane.                                                                                                                             | Need one visible place to log doctrine, roadmap, shared bricks, and decisions.                                                                                                                                                                                                          | Accepted |
| 2026-06-30 | `rumble-canvas` should be specified first.                                                                                                                                         | It can become the internal method/tool for producing the other product specs.                                                                                                                                                                                                           | Proposed |
| 2026-06-30 | `Waiver` is first-class in `rumble-canvas` MVP, with a minimal extensible model.                                                                                                   | Exceptions to rules, missing requirements, blocking risks, or validation gates must be auditable, approvable, expirable, traceable, and consumable by Wrench/Bolt.                                                                                                                      | Accepted |
| 2026-06-30 | `rumble-canvas` uses minimal `ActorReference`, `WorkspaceMembership`, and `RoleAssignment` before a full shared identity model.                                                    | Canvas needs attribution, permissions, reviews, and waiver approvals now; account/tenant/SSO/local-first identity remain shared architecture decisions.                                                                                                                                 | Accepted |
| 2026-06-30 | High/critical waivers require distinct human Owner + Reviewer approval in Canvas MVP.                                                                                              | Sensitive exceptions must not be self-approved; Bolt/Wrench can rely on explicit approval evidence.                                                                                                                                                                                     | Accepted |
| 2026-06-30 | Rumble products integrate with Bolt through planning-only `ImplementationHandoff`; MVP Bolt target is `cos-matic`.                                                                 | Rumbles must submit approved packages and governance context to Bolt without direct execution; `cos-matic` returns plans, gates, statuses, or auditable refusals.                                                                                                                       | Accepted |
| 2026-06-30 | First Canvas-to-Bolt handoff format is `canvas.bolt_handoff.v0.1`, kind `planning_request`.                                                                                        | Bolt needs deterministic structured input; MVP preserves package identity, immutable revisions, traceability, waivers, risks, capability candidates, requested outputs, and forbids automatic execution.                                                                                | Accepted |
| 2026-06-30 | `rumble-lm` MVP is a synchronous live session product with first-class activities, citation-gated source grounding, aggregate learning signals, and post-session export.           | Keeps the product focused on facilitated collective learning instead of chatbot, quiz-only, or LMS scope. See `specs/rumble-lm/14-source-grounded-product-slice.md` and `specs/rumble-lm/15-contracts-v0.1.md`.                                                                         | Accepted |
| 2026-06-30 | `rumble-lm` consumes Wrench Loader, Gear Memory/Gear artifacts, Bolt, and Biscuit rather than duplicating ingestion, memory, orchestration, artifacts, or delegated authorization. | The P0 slice needs contracts before code and must avoid dangerous local reimplementation while keeping product UX in Rumble. Owner review: `specs/rumble-lm/16-contract-review-pack.md`; stub path: `specs/rumble-lm/17-p0-stub-implementation-plan.md`.                                | Accepted |
| 2026-06-30 | `ImplementationHandoff v0.1` is the P0 contract before Rumble development.                                                                                                         | The harness must validate/refuse/plan from structured product intent before product UIs are implemented.                                                                                                                                                                                | Accepted |
| 2026-06-30 | Bolt P0 hardening remains inside `cos-matic`; no premature `bolt-runner`.                                                                                                          | Current needs are handoff validation, planning-only runs, gates, refusals, evidence references, idempotency, and audit. A new repo is justified only by a durable runtime/service boundary.                                                                                             | Proposed |
| 2026-06-30 | `rumble-feed-mind` aligns to MIT and Rust/Dioxus convergence.                                                                                                                      | The product joins the permissive-license Rumble ecosystem; legacy frontend surfaces are migration references, not durable targets.                                                                                                                                                      | Accepted |
| 2026-06-30 | Interactive Rumble products converge on Rust core + Dioxus UI by default.                                                                                                          | Avoid frontend fragmentation and keep local-first/native/web products aligned with the Rust-first harness. `rumble-cos` remains Astro as a content site exception.                                                                                                                      | Accepted |
| 2026-06-30 | Starred-repo-derived project ideas strengthen existing repositories first instead of creating new repos.                                                                           | Avoid roadmap debt and contract fragmentation: evidence/browser/eval/clean-room harden Wrench Inspect; policy hardens `cos-matic`; source catalog and usage ledger harden Gear Memory; payload projection hardens Gear Depot/Gear libs; release floor hardens Gear Cable. See ADR 0022. | Accepted |
| 2026-07-01 | `rumble-*` iOS publication adopts `rorkai/App-Store-Connect-CLI` through the Gear Cable `app-store-release.v0.1` channel adapter, pinned initially to `asc 2.5.0`.                 | The CLI is trusted, but product pipelines must stay decoupled from upstream flag changes; release jobs remain reproducible, checksum-verified, telemetry-disabled by default, and manually gated for App Store submission.                                                              | Accepted |

---

## 8. Open Questions

### Ecosystem-level

1. Should `workspace` be a shared Rumble primitive or a Gear-level tenant/context primitive?
2. Should `source` and `artifact` be separate domain concepts everywhere, or can a source become an artifact after processing?
3. What is the minimum shared identity/auth model across all Rumbles?
4. What shared policy decides who can approve high/critical waivers across products beyond Canvas?
5. Which products require local-first behavior from day one?
6. Which specs should be written in English vs French?
7. Should specs live in this root `specs/` directory, or inside each product repository?

### Product-level

#### `rumble-canvas`

- Is it primarily a team product, a solo product, or both?
- What is the first deliverable: PRD, screen map, user story map, data model, or implementation plan?
- How strict should the human validation gates be before Bolt can execute?

#### `rumble-cos`

- Is the primary unit an article, course, resource, project page, or learning path?
- Does it need a private editorial workflow or only static/public publishing?
- Should it consume specs and artifacts from other Rumbles automatically?

#### `rumble-crew`

- What is the canonical lifecycle of an agent task?
- Are agents first-class users, service accounts, or runtime identities?
- Which actions require explicit human approval?

#### `rumble-feed-mind`

- Is it an active Rumble product or primarily a source pipeline feeding other Rumbles?
- Should feed parsing/extraction remain product-local or become Wrench capability?
- Should curated feed items become Gear `Source`, Gear `Artifact`, or both depending on lifecycle?
- How should existing legacy client behavior be migrated toward Dioxus without a big bang?
- Which feed ingestion responsibilities should move to Wrench after the product slice stabilizes?
- What BYOK/provider policy is allowed for rule evaluation and explanations?

#### `rumble-lm`

- What retention defaults should apply to raw responses, summaries, exports, and audit events?
- Should live participation/presence become shared Rumble/Gear infrastructure after MVP?
- Which generation backend policy is allowed per deployment, and how is third-party transmission prevented?

#### `rumble-note`

- What is the minimal block model?
- How does local-first sync work?
- What is the handoff from personal note to spec/task/session/source?

---

## 9. Work Log / Remaining Work

### Immediate next actions

1. Treat `ImplementationHandoff v0.1` as the P0 harness contract.
2. Use `specs/harness/01-bolt-cosmatic-hardening.md` as the Bolt/cos-matic hardening doctrine.
3. Add JSON fixtures for valid/invalid handoffs.
4. Implement `cos-matic handoff validate <handoff.json>` as a no-execution validator.
5. Implement `cos-matic handoff plan --dry-run <handoff.json>` as a planning-only report.
6. Add structured refusal, typed gates, idempotency, and minimal audit events to Bolt P0.
7. Add Wrench inspection for traceability coverage, waiver validity, and shared capability extraction.
8. Define minimal Gear artifact/provenance rules for `SpecPackage` and exported Rumble artifacts.
9. Keep `rumble-feed-mind` MIT/Rust-Dioxus aligned; document any future exception by ADR/waiver.
10. Align interactive Rumble UI plans on Rust/Dioxus, with ADRs for exceptions.
11. Only then start product UI development for `rumble-*`.

### Definition of Done for a Product Spec

A product spec is complete enough for implementation planning when:

- every role is defined;
- every MVP screen has actions by role;
- every action has business rules and acceptance criteria;
- the domain model has lifecycle states and invariants;
- the data model has permissions, audit, and retention rules;
- service boundaries identify Rumble/Bolt/Wrench/Gear ownership;
- shared capability candidates are logged;
- security/RGPD/offline requirements are explicit;
- open questions are either answered or explicitly deferred.

---

## 10. Authorized Product-to-Harness Flow

1. A Rumble spec identifies a user-facing need.
2. The need is described as screens, actions, domain rules, and acceptance tests.
3. If the need is repeated or infrastructural, it is logged in the Shared Capability Registry.
4. The owner layer is chosen:
   - Rumble shared for reusable UX/domain primitives;
   - Bolt for plans, runs, approvals, gates, and agent tasks;
   - Wrench for extraction, inspection, validation, and evidence;
   - Gear for memory, sources, artifacts, provenance, sync, and distribution.
5. The Rumble product produces an immutable/exportable package or artifact.
6. If orchestration is needed, the product emits an `ImplementationHandoff v0.1` planning request.
7. `cos-matic` validates/refuses/plans without executing.
8. Wrench reports inspect readiness, traceability, waivers, privacy, and shared-capability extraction.
9. Gear records artifact/provenance references where applicable.
10. Human approval gates decide whether execution can happen later.

This loop is the core development method of the ecosystem.
