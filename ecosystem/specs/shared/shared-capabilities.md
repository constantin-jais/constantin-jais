# Shared Capability Registry

This registry captures product needs that may become reusable bricks in Rumble, Bolt, Wrench, or Gear.

Status values:

- **Candidate** — identified, not decided.
- **Discuss** — needs naming/placement decision.
- **Accepted** — owner chosen.
- **Rejected** — not shared after analysis.

## Registry

| Capability | Needed by | Candidate owner | Status | Notes |
| --- | --- | --- | --- | --- |
| Workspace / project space | All Rumbles | Discuss: shared Rumble vs Gear | Candidate | Common boundary for users, permissions, content, runs, and settings. |
| Source | `rumble-note`, `rumble-lm`, `rumble-canvas`, `rumble-cos`, `rumble-feed-mind` | Gear Memory + Wrench Loader | Candidate | URL, file, note, transcript, feed item, document, dataset; needs provenance. |
| Artifact | All Rumbles | Gear Depot + Gear Memory | Candidate | Spec, article, quiz, screen map, execution report, exported package. |
| Decision record | `rumble-canvas`, `rumble-crew`, `rumble-lm` | Bolt for operational decisions; Rumble shared for product decisions | Discuss | Must distinguish product decisions from execution decisions. |
| Activity/event log | All Rumbles | Gear | Candidate | History for audit, collaboration, and agent readability. |
| Comment/thread | `rumble-canvas`, `rumble-crew`, `rumble-lm`, maybe `rumble-note` | Shared Rumble | Candidate | User-facing collaboration primitive. |
| Agent task | `rumble-crew`, `rumble-canvas`, `rumble-note`, `rumble-lm` | Bolt / `cos-matic` | Candidate | Rumble displays and requests tasks; Bolt owns lifecycle/execution. |
| Approval/gate | `rumble-crew`, `rumble-canvas`, `rumble-lm` | Bolt + Rumble UX | Candidate | Human approval before execution, publication, or generation. |
| Skill/capability card | `rumble-crew`, `rumble-canvas`, `rumble-note` | Bolt or shared Rumble | Discuss | Reusable agent/tool capabilities exposed to users. |
| Notification | All Rumbles | Shared Rumble or service | Candidate | User-facing delivery; events likely come from Gear/Bolt. |
| Actor reference | All Rumbles, Bolt/Wrench/Gear audit surfaces | Shared auth/profile adapter later; product-level snapshots now | Candidate | Minimal human/agent/system attribution without owning identity. |
| Workspace membership | All collaborative Rumbles | Shared Rumble + auth adapter | Candidate | Actor access to a workspace/project space. |
| Role assignment | All collaborative Rumbles | Shared Rumble + auth adapter | Candidate | Product role assignment for permission checks; distinct from spec-defined product actors. |
| Permission/audit policy | All Rumbles | Gear + app-level adapters | Candidate | Must support local-first and self-hosted operation. |
| Source-grounded generation | `rumble-lm`, `rumble-canvas`, `rumble-cos`, `rumble-note` | Bolt + Wrench + Gear Memory | Candidate | Needs citations, provenance, and validation. |
| Import pipeline | `rumble-note`, `rumble-lm`, `rumble-cos`, `rumble-feed-mind` | Wrench Loader | Candidate | Files/URLs/transcripts/feed items into canonical content. |
| Feed ingestion | `rumble-feed-mind`, maybe `rumble-note`, `rumble-cos` | Discuss: `wrench-loader` extension vs `wrench-feed-loader` | Candidate | Feed polling/parsing/normalization should not become a product-only silo if reused. |
| Rule explanation | `rumble-feed-mind`, maybe `rumble-lm`, `rumble-canvas` | Rumble product UX + Wrench validation | Candidate | Natural-language rule decisions need inspectable explanation and evaluation evidence. |
| BYOK/provider policy | `rumble-feed-mind`, `rumble-lm`, `rumble-canvas` | Shared security policy + Bolt/Gear adapters | Candidate | Model routing, key storage, redaction, and provider constraints must be consistent. |
| Citation support validation | `rumble-lm`, `rumble-canvas`, `rumble-cos` | Wrench validator/inspector + Rumble UX | Candidate | Assess whether cited source excerpts support generated claims; human validation remains product-owned where needed. |
| Live participation / presence | `rumble-lm`, `rumble-crew`, maybe `rumble-canvas` | Shared Rumble vs Gear transport | Candidate | Current activity state, presence, response submission, reconnect, and aggregate updates. |
| Learning/facilitation analytics | `rumble-lm`, maybe `rumble-cos` | Shared Rumble first | Candidate | Aggregate participation, comprehension, confusion, consensus/divergence; avoid hidden individual profiling. |
| Export package | `rumble-lm`, `rumble-canvas`, `rumble-cos` | Gear artifact + Rumble UX | Candidate | Audience-scoped export with included data classes, provenance, checksum, and retention/revocation metadata. |
| Inspector reports | `rumble-canvas`, `rumble-crew`, `rumble-cos`, `rumble-lm` | Wrench Inspect | Candidate | Validate specs, content, design, policy, citation support, privacy, or readiness. |
| Traceability link | `rumble-canvas`, later all implementation flows | Rumble Canvas first, maybe shared spec primitive | Accepted for Canvas MVP | Links goal → journey → screen → action → service → test. Critical to avoid prose-only specs. |
| Spec package | `rumble-canvas`, later `rumble-cos`, `rumble-lm`, `rumble-note` exports | Gear artifact + Rumble UX | Candidate | Immutable bundle of approved revisions with provenance and export/handoff use. |
| Implementation handoff | `rumble-canvas`, `rumble-crew`, later all `rumble-*` needing orchestration | Rumble-to-Bolt boundary object; MVP target `cos-matic`; format `canvas.bolt_handoff.v0.1` | Accepted for Canvas MVP | Planning-only request from accepted product artifact into Bolt; includes package revisions, traceability, waivers, risks, capability candidates, constraints, requested outputs, and execution policy; returns plan, gates, status, or auditable refusal. |
| Waiver | `rumble-canvas`, `rumble-crew`, `rumble-lm` | Rumble Canvas first; likely shared Rumble governance primitive, consumed by Bolt gates | Accepted for Canvas MVP | Explicit controlled exception to a blocker, risk, missing section, validation check, or approval requirement. |
| Spec section/revision | `rumble-canvas`, `rumble-cos`, maybe `rumble-lm` | Shared Rumble vs Gear revision primitive | Discuss | Structured content with status, immutable revisions, review, and package inclusion. |
| RuntimeRef | `rumble-crew`, later other agentic products | Bolt/Gear integration reference + Rumble safe projection | Candidate | Safe runtime identity/reference; never stores credentials. Needed to distinguish agent profile from execution identity. |
| RunRef | `rumble-crew`, later Canvas handoff monitoring | Bolt owns run; Rumble stores projection/reference | Candidate | Local projection of external run state, idempotency, sync status, and attempt lineage. |
| CompletionPolicy | `rumble-crew`, later any agentic task UX | Rumble governance + Bolt signal | Candidate | Controls manual review vs evidence-valid auto-close vs run-success auto-close. Must be auditable. |
| EvidenceStore | `rumble-crew`, later all evidence-producing products | Gear target; Rumble local fallback only | Discuss | Artifact/provenance storage abstraction; Rumble fallback must be extractable. |
| RuntimeLog | `rumble-crew` | Discuss: Gear artifact/log substrate + Rumble privileged viewer | Candidate | Sensitive log reference/access primitive with TTL, redaction, non-indexing, audit access event. |
| RecoveryDecision | `rumble-crew`, later agentic workflows | Rumble UX + Bolt retry/cancel seam | Candidate | Human decision after failed run: rerun, reassign, fail, cancel. |

## Naming Rules

- Rumble shared names describe user-facing product primitives: `thread`, `workspace`, `presence`, `notification`.
- Bolt names describe orchestration primitives: `run`, `plan`, `gate`, `approval`, `agent-task`.
- Wrench names describe callable capabilities: `loader`, `inspector`, `validator`, `extractor`.
- Gear names describe substrate primitives: `source`, `artifact`, `memory-entry`, `event-log`, `provenance`.

## Open Naming Discussions

| Candidate | Competing names | Placement question | Status |
| --- | --- | --- | --- |
| Workspace | `workspace`, `project`, `space`, `context` | Shared Rumble primitive or Gear tenant/context primitive? | Discuss |
| Source | `source`, `input`, `reference`, `evidence-source` | Gear Memory concept, Wrench output, or both? | Discuss |
| Artifact | `artifact`, `deliverable`, `output`, `asset` | Gear Depot package vs Gear Memory contextual object? | Discuss |
| Decision record | `decision`, `adr`, `choice`, `ruling` | Product decision vs execution gate? | Discuss |
| Traceability link | `trace`, `link`, `coverage`, `requirement-link` | Canvas-specific or shared spec primitive? | Discuss |
| Actor reference | `actor`, `actor-ref`, `principal`, `identity-ref` | Attribution snapshot vs full identity object. | Candidate |
| Workspace membership | `membership`, `participant`, `collaborator`, `access` | Shared Rumble membership vs auth adapter. | Candidate |
| Role assignment | `role-assignment`, `grant`, `permission-binding` | Product role grant vs low-level permission binding. | Candidate |
| Waiver | `waiver`, `exception`, `override`, `risk-acceptance` | Rumble-owned product/spec exception; Bolt may consume as gate exception. | Accepted for Canvas MVP |
| Spec package | `spec-package`, `deliverable`, `bundle`, `artifact` | Gear artifact name or Canvas product name? | Discuss |
| Implementation handoff | `handoff`, `plan-request`, `execution-brief`, `implementation-request` | Rumble-to-Bolt API object naming; Canvas MVP uses `ImplementationHandoff` / `canvas.bolt_handoff.v0.1`. | Accepted for Canvas MVP |
