# Bolt / cos-matic Evidence-Gated Planning P0

Status: Draft / P0 contract.
Date: 2026-06-30.

## Purpose

Define how `cos-matic` consumes Rumble handoffs, Wrench evidence, Gear references, and Biscuit authorization references to produce deterministic planning reports, gates, or refusals without becoming a product UI, memory store, parser, registry, or uncontrolled execution runtime.

## Responsibility Charter

Bolt centralizes orchestration primitives that are dangerous to duplicate in Rumbles:

- handoff receipt;
- validation;
- planning-only lifecycle;
- typed gates;
- structured refusals;
- evidence reference checks;
- idempotency/attempt lineage;
- minimal audit events.

Bolt does not own:

- product UX or product decisions;
- source extraction, parsing, inspection, or validation evidence generation;
- durable source/artifact/memory/provenance storage;
- full auth or identity provider;
- execution runtime in P0.

Rule:

> Bolt can decide whether a planning request is accepted, blocked, or refused. It cannot decide product meaning, store evidence bodies, or execute implementation work in P0.

## P0 Objects

| Object | Owner | Purpose |
| --- | --- | --- |
| `PlanningRequest` | Bolt / `cos-matic` | Planning-only request derived from an `ImplementationHandoff` plus evidence refs. |
| `EvidenceRef` | Bolt shape, points to Wrench/Gear/Biscuit/Rumble | Safe reference to evidence with hash, status, state, provenance, and summary. |
| `GateResult` | Bolt | Typed gate outcome: Wrench passed, Gear context fresh, Biscuit right present, sovereignty policy, etc. |
| `PlanReport` | Bolt | Dry-run plan with referenced evidence and gates; no execution side effects. |
| `RunIntent` | Bolt | P0 intent marker: `planning_only`, execution not allowed, human approval required. |
| `RefusalReport` | Bolt | First-class negative output with reason code, severity, safe findings, remediation. |
| `AuditEvent` | Bolt shape, later Gear-compatible | Safe append-only transition reference without raw PII/secrets. |

Schema: `cosmatic-planning.v0.1.schema.json`.
Fixtures: `fixtures/planning/`.

## Evidence Inputs

Bolt consumes evidence by reference only:

- `ImplementationHandoff` from Rumble Canvas or other Rumbles;
- `LoaderEvidenceReport` / Wrench inspection reports;
- Gear `SourceRef`, `MemoryEntry`, `CodeMap`, `ArtifactRef` refs;
- Biscuit delegated authorization verification refs;
- human approval refs when future execution is considered.

Bolt must not store raw report bodies, source excerpts, runtime logs, credentials, embeddings, or PII in planning reports/audit metadata.

## Gate Policy

P0 blocking gates:

| Gate | Blocks when |
| --- | --- |
| `execution_permission` | any P0 request tries to authorize execution. |
| `wrench_report_passed` | required report is missing, failed, high/critical, or quarantined. |
| `gear_context_fresh` | source/memory/code/artifact ref is stale, deleted, anonymized, revoked, or unknown when current truth is required. |
| `biscuit_right_present` | required delegated right/scope is absent, expired, revoked, or unverifiable. |
| `sovereignty_policy` | mandatory US SaaS, opaque storage, blocking license, PII logs, or unapproved provider transmission appears. |
| `risk_waiver` | high/critical risk lacks valid non-expired waiver with reviewer separation. |
| `artifact_integrity` | required artifact/package/report hash or manifest ref is missing. |

## Refusal Codes

P0 refusal codes:

- `execution_policy_forbidden`;
- `stale_context`;
- `deleted_or_revoked_context`;
- `quarantined_evidence`;
- `missing_required_evidence`;
- `invalid_waiver`;
- `missing_authorization_right`;
- `sovereignty_policy_blocked`;
- `handoff_hash_conflict`;
- `unsafe_metadata`.

Refusals include safe findings and remediation hints. They never leak raw content.

## Idempotency

- Identity is `handoff_id + payload_hash`.
- Same identity returns equivalent plan/refusal refs.
- Same `handoff_id` with a different payload hash is `handoff_hash_conflict`.
- Every transition emits an audit event.

## Agent-Readable Output

Plan reports are agent-readable because they are structured and reference-backed:

- evidence IDs, hashes, states, statuses;
- gate result IDs;
- ordered plan steps;
- no hidden graph expansion;
- no embedded instructions from reports/artifacts;
- no raw secrets or private content.

## Consumer Alignment

| Consumer | Uses Bolt for | Must not duplicate |
| --- | --- | --- |
| `rumble-canvas` | implementation handoff planning, package readiness gates | local planner/execution approval semantics |
| `rumble-crew` | task/run intent, gates, recovery planning | bespoke run/gate/retry lifecycle |
| `rumble-lm` | source-grounded activity/export planning gates | local evidence trust policy for execution |
| `rumble-note` | note-context handoff planning | hidden agent memory policy or execution trigger |
| `rumble-feed-mind` | curated export/handoff planning | feed pipeline orchestration gates inside product |
| Wrench | evidence production consumed by Bolt | orchestration decisions |
| Gear | refs/provenance consumed by Bolt | planning/gate decisions |

## Acceptance Tests

- Given a valid planning-only request with active Gear refs, passing Wrench evidence, and a valid Biscuit planning right, Bolt emits `PlanReport.status=plan_ready` and `dry_run_only=true`.
- Given `allow_execution=true`, Bolt refuses with `execution_policy_forbidden`.
- Given Gear ref state `stale`, Bolt refuses or blocks with `stale_context` / `gear_context_fresh`.
- Given Wrench evidence status `quarantined`, Bolt refuses with `quarantined_evidence`.
- Given missing Biscuit right, Bolt refuses with `missing_authorization_right`.
- Given unsafe metadata keys such as `api_key` or `raw_log`, validation fails/refuses with `unsafe_metadata`.
- Given mandatory US SaaS or blocking license for core truth, sovereignty gate blocks planning.
- Given a refusal, output contains safe summaries and refs only.
- Given the same request identity twice, Bolt returns equivalent result without duplicate planning run.

## Starred Repository Design Pressure

| Input | Use | Boundary |
| --- | --- | --- |
| `Goldziher/ai-rulez` | deterministic diagnostics and safe-write comparison | comparator only |
| `github/spec-kit` / `Fission-AI/OpenSpec` | spec-driven change lifecycle | no ungated executable specs |
| `simstudioai/sim`, `multica-ai/multica`, `gastownhall/gastown` | run/task/workspace UX pressure | Rumble Crew UX, not Bolt P0 UI |
| `claude-task-master`, `Fabric` | decomposition/prompt organization risks | no unreviewed prompt packs or automation imports |

## ADRs

- `../shared/adrs/0011-bolt-p0-inside-cosmatic.md`
- `../shared/adrs/0017-bolt-planning-only-lifecycle.md`
- `../shared/adrs/0018-bolt-refusal-first-class.md`
- `../shared/adrs/0019-bolt-evidence-refs-not-storage.md`
- `../shared/adrs/0020-bolt-sovereignty-gate-blocking.md`
- `../shared/adrs/0021-bolt-starred-repos-design-benchmarks.md`
