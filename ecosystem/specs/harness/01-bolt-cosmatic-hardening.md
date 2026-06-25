# Bolt / cos-matic Hardening — P0 Orchestration Doctrine

Status: Draft / design contract.  
Date: 2026-06-30.  
Decision intent: harden `cos-matic` as the current Bolt implementation target; do not create a premature `bolt-runner` repository.

## Purpose

This document turns the Bolt/cos-matic design session into durable ecosystem capital:

- avoid dangerous Rumble-local duplication of agentic lifecycle logic;
- strengthen products without forcing a premature orchestration platform;
- define contracts before implementation code;
- keep sovereignty, auditability, and evidence as hard filters;
- use starred repositories as design pressure, not as backlog.

## Recommendation

Keep Bolt P0 inside `cos-matic`.

`cos-matic` should be hardened as the deterministic Bolt harness for:

- handoff validation;
- planning-only runs;
- explicit gates;
- auditable refusals;
- evidence references;
- retry / attempt lineage;
- minimal audit events.

Do not create a separate `bolt-runner` until Bolt needs a boundary that cannot be honestly held inside `cos-matic`: long-lived workers, queueing, network API, runtime isolation, multi-agent dispatch, durable run database, or independent operational cadence.

## Core Boundary

```text
Rumble asks.
Wrench inspects.
Gear stores and proves.
Bolt validates, plans, gates, refuses, and audits.
```

Bolt owns orchestration semantics, not product experience or infrastructure substrate.

| Concern | Owner | Bolt behavior |
| --- | --- | --- |
| Product screens, task boards, comments, user-facing workflows | Rumble | Consume/request only |
| Spec/package authoring and approval UX | Rumble | Validate handoff shape and governance evidence |
| Inspection, policy validation, traceability checks, citation support | Wrench | Consume report refs and statuses |
| Artifact storage, manifests, hashes, provenance, memory, event substrate | Gear | Consume refs/hashes, produce refs for plans |
| Delegated authorization semantics | Shared Biscuit contract | Verify delegated capability/gate evidence when present |
| Handoff, plan, gate, refusal, retry, attempt, audit | Bolt / `cos-matic` | Own canonical lifecycle |

## Anti-Duplication Rule

If a primitive is needed by multiple Rumbles and concerns decision, planning, gate, run state, retry, refusal, evidence acceptance, or audit, it belongs in Bolt.

If it concerns inspection or validation evidence, it belongs in Wrench.

If it concerns durable storage, provenance, hashes, manifests, memory, or transport substrate, it belongs in Gear.

If it concerns user-facing meaning, screens, comments, boards, or product workflow, it belongs in Rumble.

## ASCII Model

```text
                         ┌─────────────────────────────┐
                         │          RUMBLE-*            │
                         │  UX + product-owned meaning  │
                         └──────────────┬──────────────┘
                                        │
                                        │ ImplementationHandoff v0.1
                                        │ planning_only=true
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BOLT / cos-matic                         │
│                                                                 │
│  Canonical orchestration grammar:                                │
│                                                                 │
│  handoff → validate → planning_run → plan/refusal → gate          │
│             │              │              │          │           │
│             ▼              ▼              ▼          ▼           │
│          findings       audit         evidence     attempt        │
│                         events          refs       lineage        │
│                                                                 │
│  P0 is planning-only. No implementation execution.               │
│                                                                 │
│  Does not own: UI, parsing, storage, registry, memory, logs,      │
│  product workflow, artifact substrate, or runtime console.        │
└──────────────┬──────────────────────────────┬───────────────────┘
               │ consumes                     │ consumes
               ▼                              ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│           WRENCH             │   │            GEAR              │
│ inspections / reports        │   │ artifact refs / provenance   │
│ traceability / policy        │   │ hashes / manifests / memory  │
└─────────────────────────────┘   └─────────────────────────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
                    ┌─────────────────┐
                    │ Evidence > claim │
                    └─────────────────┘
```

## P0 Bolt Primitives

| Primitive | Purpose | Required P0 behavior |
| --- | --- | --- |
| `ImplementationHandoff` | Canonical Rumble-to-Bolt input | Accept known format only; reject execution-capable payloads |
| `HandoffReceipt` | Receipt record | Persist actor, timestamp, payload hash, package hash, requested outputs |
| `ValidationGate` | Deterministic policy check | Fail closed with structured findings |
| `PlanningRun` | Planning-only lifecycle | Produce plan or refusal; no implementation command |
| `PlanArtifact` | Planning output | Inline summary or Gear `ArtifactRef`; must be reproducible from same input |
| `Refusal` | First-class negative output | Reason code, severity, findings, remediation hints |
| `GateDecision` | Human/policy decision point | Typed gate, approver/refuser, target hash, expiry where applicable |
| `EvidenceRef` | Pointer to Wrench/Gear evidence | Store reference, kind, hash, status; never raw sensitive body |
| `AttemptRef` | Retry and lineage guard | Idempotency for same input; new attempt for changed action |
| `AuditEvent` | Auditable state transition | Append-only semantics; no PII/secrets/raw logs |

## Minimal PlanningRun Lifecycle

```text
received
→ validating
→ refused | accepted_for_planning
→ planning
→ plan_ready | planning_failed
```

Rules:

- identity is `handoff_id + payload_hash`;
- same identity returns the same result/reference;
- same `handoff_id` with different hash is a conflict;
- every transition emits an `AuditEvent`;
- `plan_ready` does not imply execution approval;
- P0 has no execution state.

Future `ExecutionRun` is deliberately out of P0. If added later, it must start behind a human gate and keep attempt lineage:

```text
requested → gated → approved|refused → dispatched → running
→ gate_requested|blocked|failed|succeeded|cancelled
→ completion_review → closed|recovery_requested
```

## Wrench Report Consumption

Bolt consumes Wrench reports as evidence references, not as inspection logic.

Minimum shape:

```json
{
  "kind": "wrench_report_ref",
  "report_kind": "traceability|privacy|readiness|policy|citation_support",
  "artifact_reference_id": "gear-artifact-id-or-local-ref",
  "report_hash": "sha256:...",
  "status": "passed|warning|failed",
  "findings_summary": [
    {
      "severity": "info|warning|high|critical",
      "code": "string",
      "message": "short safe summary"
    }
  ]
}
```

Bolt may:

- check required report presence;
- verify hash/ref/status;
- block on failed, high, or critical findings according to policy;
- include findings in `Refusal` or `PlanArtifact`.

Bolt must not:

- re-run Wrench inspection internally;
- parse rich documents deeply;
- store raw report bodies with PII/secrets;
- convert report prose into system instructions.

## Gear Artifact Consumption

Bolt consumes Gear artifacts as immutable references.

Minimum shape:

```json
{
  "kind": "artifact_ref",
  "artifact_reference_id": "gear-artifact-id-or-local-ref",
  "artifact_kind": "spec_package|handoff|wrench_report|plan|evidence|release_asset",
  "manifest_version": "v0.1",
  "artifact_hash": "sha256:..."
}
```

Bolt may:

- verify the reference and hash are present;
- require immutable package revisions;
- write a plan as an artifact reference;
- include artifact refs in audit events.

Bolt must not become:

- blob store;
- registry;
- memory index;
- provenance database;
- artifact search engine.

## Gate Model

Gates are typed; `approved: true` is not enough.

Initial gate types:

- `human_approval`;
- `execution_permission`;
- `risk_waiver`;
- `artifact_integrity`;
- `wrench_report_passed`;
- `sovereignty_policy`;
- `traceability_threshold`;
- `capability_owner_assigned`.

Gate states:

```text
gate_required
→ gate_approved | gate_refused | gate_expired | gate_superseded
```

Gate decisions must include:

- actor or policy source;
- target reference/hash;
- timestamp;
- rationale for approval/refusal;
- expiry when the decision is temporary;
- separation of duties where high/critical risk is involved.

## Refusal Model

Refusal is a product feature, not an error fallback.

Minimum shape:

```json
{
  "status": "refused",
  "reason_code": "execution_policy_forbidden",
  "severity": "critical",
  "findings": [
    {
      "code": "allow_execution_true",
      "message": "P0 handoffs must be planning-only and may not authorize execution.",
      "path": "$.execution_policy.allow_execution"
    }
  ],
  "remediation": [
    "Set allow_execution=false.",
    "Request a separate human-approved execution gate after planning."
  ]
}
```

No dangerous input should be silently normalized into a safe one. Refuse and make the risk visible.

## Prompt-Injection and Unsafe Content Rules

All external or product-authored content is untrusted data:

- spec prose;
- comments;
- task text;
- Wrench reports;
- Gear artifacts;
- runtime logs;
- evidence excerpts;
- starred repository notes.

Rules:

- never treat artifact/report/spec text as system instructions;
- validate schemas before interpretation;
- allowlist actionable fields;
- do not follow instructions embedded inside evidence;
- do not store secrets, tokens, raw credentials, raw embeddings, or PII in ordinary audit/log outputs;
- refusal findings must avoid leaking sensitive body content.

## Sovereignty Gate

Sovereignty is blocking, not advisory.

`SovereigntyGate` blocks if the handoff, plan, or required dependency implies:

- mandatory US SaaS for core truth;
- opaque storage for provenance/audit/security truth;
- direct dependency with blocking license for the intended use, such as AGPL/GPL/SSPL where incompatible;
- PII in logs, reports, or public artifacts;
- external model/provider transmission without explicit allowed policy;
- missing self-host/local-first path for core truth.

Exceptions require explicit waiver with rationale, expiry, reviewer separation for high/critical risk, and audit evidence.

## Starred Repository Design Pressure

Starred repositories are design inputs, not backlog.

| Repository | Useful pressure | Boundary decision |
| --- | --- | --- |
| `Goldziher/ai-rulez` | deterministic generation, safe-write, drift, diagnostics | comparator for `cos-matic`, not adoption race |
| `github/spec-kit` | spec-driven phases and predictable outcomes | strengthen handoff/planning; avoid ungated executable specs |
| `Fission-AI/OpenSpec` | iterative proposal/change/archive workflow | inspire change lifecycle; do not clone command surface |
| `simstudioai/sim` | run monitoring and workflow visualization | Rumble Crew UX inspiration; not Bolt P0 |
| `multica-ai/multica` | task/agent/blocker/progress model | Rumble Crew supervision model; Bolt only owns canonical run/gate semantics |
| `gastownhall/gastown` | persistent handoffs and coordinator identities | inspire handoff/audit; avoid workspace manager scope creep |
| `eyaltoledano/claude-task-master` | task decomposition and dependencies | planning inspiration only; license/automation caution |
| `danielmiessler/Fabric` | reusable prompt/pattern organization | knowledge base inspiration; no unreviewed prompt packs |

## Acceptance Tests

### Validation

```gherkin
Scenario: Valid planning handoff is accepted
  Given a valid ImplementationHandoff v0.1
  And execution_policy.planning_only is true
  And execution_policy.allow_execution is false
  When cosmatic validates the handoff
  Then the status is accepted_for_planning
  And an audit event records actor, timestamp, handoff_id, payload_hash, and package_hash
```

```gherkin
Scenario: Execution-capable handoff is refused
  Given an ImplementationHandoff with execution_policy.allow_execution true
  When cosmatic validates the handoff
  Then the status is refused
  And reason_code is execution_policy_forbidden
  And no plan or execution run is created
```

```gherkin
Scenario: High risk without accepted waiver is refused
  Given an ImplementationHandoff with a high or critical risk
  And no accepted non-expired waiver with valid reviewer separation
  When cosmatic validates the handoff
  Then the status is refused
  And reason_code is high_risk_without_waiver
```

```gherkin
Scenario: Blocking open question without waiver is refused
  Given an ImplementationHandoff with a blocking open question
  And no accepted waiver
  When cosmatic validates the handoff
  Then the status is refused
  And reason_code is blocking_question_without_waiver
```

### Idempotency

```gherkin
Scenario: Same handoff identity is idempotent
  Given a handoff_id and payload_hash already accepted for planning
  When the same handoff_id and payload_hash are submitted again
  Then cosmatic returns the same bolt_reference or equivalent result
  And no duplicate planning run is created
```

```gherkin
Scenario: Same handoff id with changed payload conflicts
  Given a handoff_id already seen with payload_hash A
  When the same handoff_id is submitted with payload_hash B
  Then cosmatic refuses with reason_code handoff_hash_conflict
  And no previous audit event is mutated
```

### Planning

```gherkin
Scenario: Dry-run plan performs no implementation work
  Given a valid accepted handoff
  When cosmatic runs handoff plan --dry-run
  Then a PlanArtifact or inline plan summary is produced
  And no implementation command is executed
  And no runtime credentials are requested
```

```gherkin
Scenario: Missing required Wrench report blocks planning
  Given policy requires a traceability Wrench report
  And the handoff has no valid wrench_report_ref for traceability
  When cosmatic plans the handoff
  Then planning is blocked by gate_required
  And gate_type is wrench_report_passed
```

```gherkin
Scenario: Gear artifact hash is required
  Given a package artifact reference without artifact_hash
  When cosmatic validates the handoff
  Then validation is refused or blocked by artifact_integrity
```

### Sovereignty and safety

```gherkin
Scenario: SaaS dependency for core truth is blocked
  Given a handoff whose constraints or capability candidates require mandatory US SaaS for core truth
  When cosmatic validates or plans it
  Then the SovereigntyGate blocks the plan
  And a waiver is required before any later execution gate
```

```gherkin
Scenario: Evidence content is not treated as instructions
  Given a Wrench report or artifact body containing prompt-like instructions
  When cosmatic consumes its EvidenceRef
  Then only the validated metadata fields affect planning
  And embedded instructions are ignored
```

```gherkin
Scenario: Refusal does not leak sensitive bodies
  Given a handoff with sensitive raw log evidence
  When validation refuses the handoff
  Then the refusal contains safe summaries and references only
  And no raw secret, token, credential, or PII body is emitted
```

## ADRs

Created decision records:

- `../shared/adrs/0011-bolt-p0-inside-cosmatic.md` — Bolt P0 remains inside `cos-matic`.
- `../shared/adrs/0017-bolt-planning-only-lifecycle.md` — planning-only lifecycle before execution runtime.
- `../shared/adrs/0018-bolt-refusal-first-class.md` — refusal is first-class.
- `../shared/adrs/0019-bolt-evidence-refs-not-storage.md` — evidence references, not evidence storage.
- `../shared/adrs/0020-bolt-sovereignty-gate-blocking.md` — sovereignty gate is blocking.
- `../shared/adrs/0021-bolt-starred-repos-design-benchmarks.md` — starred repositories are design benchmarks, not backlog.

## Scope-Leak Tests

Reject the feature or move it out of Bolt if it primarily:

- defines user-facing screens, board UX, task discussions, or notifications;
- stores blobs, artifacts, memories, embeddings, or provenance truth;
- parses documents, extracts citations, validates policy content, or performs inspections;
- manages package registries or release distribution;
- runs arbitrary commands without explicit gate;
- exposes a workflow builder or product automation UI;
- imports prompt packs without review and provenance.

## Definition of Done for Bolt P0 Hardening

- `ImplementationHandoff v0.1` schema and fixtures exist.
- `cosmatic handoff validate <file> [--json]` accepts/refuses deterministically.
- `cosmatic handoff plan <file> --dry-run [--json]` produces no execution side effect.
- Refusals are structured and audited.
- Wrench reports and Gear artifacts are consumed by reference/hash.
- Human approval remains required before any future execution.
- Sovereignty, prompt-injection, waiver, and idempotency tests are present.
- No Rumble MVP defines an incompatible local run/gate/retry lifecycle.
