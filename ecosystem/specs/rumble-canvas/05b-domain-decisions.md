# Domain Decisions — rumble-canvas

## Decision: Dual-Format Spec Content

**Status:** Accepted  
**Date:** 2026-06-30

`rumble-canvas` uses a dual-format content model:

1. **Structured fields are the canonical machine contract.**
2. **Markdown is the human-readable rendering and export format.**

---

## Rationale

`rumble-canvas` must serve both humans and agents.

Humans need readable documents:

- product charters;
- journeys;
- reviews;
- comments;
- exported specs.

Agents and services need structured contracts:

- validation rules;
- role/action matrices;
- traceability links;
- acceptance criteria;
- service boundaries;
- handoff payloads;
- test generation inputs.

Markdown alone is readable but too weak for deterministic validation. Structured JSON alone is precise but poor for human authoring and review.

Therefore, critical product objects must store structured fields, while Markdown is generated from or synchronized with those fields for reading, editing, review, and export.

---

## Rule

For each spec object:

```text
structured fields = source of truth for validation, agents, services, tests
markdown          = projection for humans and export
```

If a conflict exists between structured fields and Markdown, structured fields win.

---

## Applies To

The dual-format rule applies to:

- `SpecSectionRevision`
- `ProductCharter`
- `RoleDefinition`
- `JourneyDefinition`
- `ScreenDefinition`
- `ActionDefinition`
- `DecisionRecord`
- `OpenQuestion`
- `RiskFlag`
- `Waiver`
- `CapabilityCandidate`
- `SpecPackage`
- `ImplementationHandoff`

---

## Example: ActionDefinition

### Structured Fields

```json
{
  "name": "Approve section",
  "actor_role": "Reviewer",
  "intent": "Validate a spec section before package approval",
  "preconditions": [
    "section.status == ready_for_review",
    "actor.has_permission('approve_section')"
  ],
  "business_rules": [
    "approval targets a specific revision",
    "requested changes block package approval"
  ],
  "events_emitted": ["section_approved"],
  "audit_required": true,
  "acceptance_criteria": [
    "Given a ready section, when Reviewer approves it, then approved_revision_id is set",
    "Given a section changes after approval, then a new draft revision is created"
  ]
}
```

### Markdown Projection

```md
## Action: Approve section

A Reviewer approves a spec section once it is ready for review. The approval targets a specific revision and is recorded in the audit log. If the section changes later, the approval does not silently apply to the new revision.
```

---

## Consequences

### Positive

- Specs become machine-checkable.
- Bolt handoff can consume deterministic payloads.
- Wrench inspections can validate missing fields and contradictions.
- Acceptance tests can be generated from structured criteria.
- Markdown remains readable and exportable.

### Negative / Cost

- More modeling work upfront.
- UI must manage structured editing, not only free text.
- Import/export must handle projection and drift.
- Data model must support both structured content and Markdown rendering.

---

## Implementation Guidance

MVP should not over-engineer a full schema engine.

Recommended MVP approach:

- store core objects in structured columns/JSON;
- store optional prose as Markdown fields;
- generate export Markdown from structured fields;
- store exported Markdown snapshots inside `SpecPackage` artifacts;
- validate required structured fields before review/package/handoff.

---

## Decision: First-Class Traceability Links

**Status:** Accepted  
**Date:** 2026-06-30

`rumble-canvas` treats traceability as a first-class product concept.

A spec must not only describe product intent. It must connect intent to implementation and validation.

---

## Rationale

Without traceability, specs become readable prose but remain hard to verify.

`TraceabilityLink` makes it possible to answer:

- Which job-to-be-done justifies this journey?
- Which journey introduces this screen?
- Which screen exposes this action?
- Which action requires this domain entity or service?
- Which acceptance test covers this business rule?
- Which product need justifies this shared capability candidate?

This is required for agentic development because Bolt/Wrench/Gear need structured context, not only narrative text.

---

## Rule

Every implementation-relevant object should be linkable to its upstream reason and downstream verification.

Canonical chain:

```text
JobToBeDone
→ JourneyDefinition
→ ScreenDefinition
→ ActionDefinition
→ DomainEntity / ServiceContract
→ AcceptanceTest
→ CapabilityCandidate when shared extraction is needed
```

The chain does not need to be complete at draft time, but missing traceability must appear in completeness/readiness checks.

---

## Consequences

### Positive

- Specs become inspectable by Wrench.
- Bolt handoff can preserve why each task exists.
- Tests can be traced back to business intent.
- Shared capability extraction becomes evidence-based.
- Scope creep is easier to detect.

### Cost

- More links to manage in the UI.
- Need validation rules to avoid noisy or stale links.
- Data model must store typed object references.

---

## MVP Guidance

MVP should support typed links between:

- charter jobs and journeys;
- journeys and screens;
- screens and actions;
- actions and acceptance criteria;
- actions and capability candidates;
- spec package items and included objects.

Post-MVP can add richer graph visualization and coverage reports.

---

## Decision: First-Class Minimal Waivers

**Status:** Accepted  
**Date:** 2026-06-30

`rumble-canvas` treats `Waiver` as a first-class MVP entity, but keeps the model minimal and extensible.

A waiver is a controlled exception that permits progress despite an unmet rule, incomplete requirement, blocking question, review objection, risk, or validation check.

---

## Rationale

Waivers are not ordinary comments. They are explicit risk-bearing decisions.

If waivers are buried in Markdown or overloaded into risk/question fields, Canvas loses:

- auditability;
- expiry checks;
- approval evidence;
- Wrench validation hooks;
- Bolt gate context;
- traceability to affected implementation/tests.

---

## Rule

A waiver must have:

- a target;
- a status;
- a reason;
- risk level and category;
- an accountable owner;
- an approver when accepted;
- optional expiry, conditions, and compensating controls.

Only an accepted, non-expired waiver can unblock package approval, handoff, or validation gates.

---

## Approval Policy — Canvas MVP

- Low/medium waivers may be accepted by an active human Owner.
- High/critical waivers require an active human Owner plus a distinct active human Reviewer.
- Security, privacy, or compliance waivers require a reviewer with relevant review responsibility.
- Agent and system actors cannot accept waivers.
- Expired or revoked waivers stop unblocking their target.

---

## Consequences

### Positive

- Exceptions become auditable and inspectable.
- Wrench can detect expired, unapproved, or high-risk waivers.
- Bolt can receive explicit gate exceptions instead of ambiguous prose.
- Risk acceptance remains visible instead of disappearing into status fields.

### Cost

- Requires UI and policy handling for waiver creation/review.
- Requires lifecycle checks during package approval and handoff.
- Cross-product waiver policy remains to be standardized later.

---

## Decision: Minimal Actor/Membership/RoleAssignment

**Status:** Accepted  
**Date:** 2026-06-30

Canvas MVP uses:

- `ActorReference` for attribution;
- `WorkspaceMembership` for access to a workspace;
- `RoleAssignment` for workspace permissions.

This is deliberately smaller than a full shared identity/auth model.

---

## Rationale

Canvas needs collaboration and governance immediately:

- authorship attribution;
- section review;
- package approval;
- waiver approval;
- agent suggestion boundaries;
- audit logs.

But the ecosystem has not yet settled shared account, tenant, SSO, local-first identity, or cross-product policy.

The MVP therefore stores enough to enforce Canvas permissions without claiming ownership of identity infrastructure.

---

## Rule

- Every auditable action records an `ActorReference`.
- Workspace access goes through active `WorkspaceMembership`.
- Permissions derive from active `RoleAssignment` values.
- At least one active human Owner must exist per workspace.
- Agents may suggest but cannot approve, accept waivers, own workspaces, or execute implementation.

---

## Consequences

### Positive

- Canvas can support solo and small-team workflows.
- Waiver/review/package approvals become enforceable.
- Full shared identity can be introduced later behind the same references.

### Cost

- Some policy duplication may exist until a shared auth/profile layer is defined.
- Local-first identity and cross-product membership semantics remain open.

---

## Decision: Bolt Handoff Targets `cos-matic` for MVP

**Status:** Accepted  
**Date:** 2026-06-30

All `rumble-*` products integrate with Bolt through a planning-only `ImplementationHandoff`.

For the MVP, the concrete Bolt implementation target is `cos-matic`.

Canvas never triggers direct implementation execution. It submits an approved package plus the governance and traceability context needed for safe planning.

---

## Rationale

Rumble products own user-facing workflows and product meaning. Bolt owns orchestration, gates, runs, and execution safety.

The handoff boundary keeps this separation explicit:

- Canvas produces the approved product/spec package.
- Canvas includes decisions, accepted waivers, risks, traceability links, and constraints.
- `cos-matic` receives the handoff as a planning request.
- `cos-matic` returns a plan, gates, status, or auditable refusal.
- Any execution remains outside Canvas and behind Bolt gates.

---

## Rule

An MVP handoff must be:

- based on an approved `SpecPackage`;
- planning-only;
- immutable or hashable once submitted;
- explicit about included decisions, waivers, risks, traceability links, and constraints;
- rejected or refused audibly if the package is incomplete, unsafe, or outside policy.

Canvas must not call implementation tools directly, bypass Bolt gates, or treat a successful handoff as execution approval.

---

## Expected `cos-matic` Responses

`cos-matic` may return:

- an acknowledged planning request;
- a generated plan reference;
- required gates or approvals;
- validation errors;
- policy refusals;
- failure status with retry/export context.

---

## Consequences

### Positive

- Product specs remain separate from execution orchestration.
- The MVP has a concrete integration target without hard-coding all future Bolt internals.
- Waivers and risks become explicit gate context.
- Handoff failures/refusals are auditable instead of ambiguous.

### Cost

- `07-services-and-apis.md` must define the exact handoff payload and adapter contract.
- `08-events-and-workflows.md` must define handoff, plan, gate, refusal, and retry events.
- `cos-matic` API compatibility must be tracked as the harness evolves.

---

## Decision: First Bolt Handoff Format

**Status:** Accepted  
**Date:** 2026-06-30

Canvas MVP uses `canvas.bolt_handoff.v0.1` as its first structured handoff format to Bolt.

The payload is a `planning_request`, not an execution request.

---

## Rationale

Bolt needs deterministic context to produce a safe implementation plan:

- approved package identity;
- included immutable revisions;
- planning scope;
- structured spec context;
- traceability links;
- active waivers;
- open risks/questions;
- shared capability candidates;
- requested planning outputs;
- explicit execution policy.

Markdown export remains useful for humans, but Bolt handoff must be structured.

---

## Rule

A Canvas-to-Bolt MVP handoff must use:

```text
format = canvas.bolt_handoff.v0.1
kind   = planning_request
```

It must include:

- `source`;
- `package`;
- `planning_scope`;
- `spec_context`;
- `traceability_links`;
- `active_waivers`;
- `open_questions`;
- `risks`;
- `capability_candidates`;
- `constraints`;
- `requested_outputs`;
- `execution_policy`.

The execution policy must include:

```json
{
  "planning_only": true,
  "allow_execution": false,
  "requires_human_approval_for_execution": true
}
```

---

## Consequences

### Positive

- Bolt receives machine-readable planning context.
- The approved package version and revision IDs remain auditable.
- Waivers and risks are explicit instead of buried in prose.
- MVP cannot accidentally trigger implementation execution.

### Cost

- Requires payload validation before submission.
- Requires versioning once Bolt evolves the format.
- Requires a Rumble-side adapter to assemble package + traceability + risks + waivers.

---

## Open Follow-Up Decisions

| Question | Impact | Status |
| --- | --- | --- |
| Should Markdown be editable directly or only generated from structured fields? | High | Open |
| Should each object store a cached Markdown rendering? | Medium | Open |
| Which structured fields are required for MVP vs post-MVP? | High | Open |
| Should spec schemas be versioned? | High | Open |
| What minimum traceability coverage is required before package approval? | High | Open |
| Should traceability links be manually authored, suggested by agents, or both? | Medium | Open |
| What is the shared cross-product policy for high/critical waivers? | High | Open beyond Canvas MVP |
| How does local-first identity sync work for workspace memberships? | High | Open |
| Which Bolt-side validation errors are blocking vs advisory? | High | Open |
| When does `canvas.bolt_handoff.v0.1` graduate to a shared Bolt contract? | Medium | Open |
