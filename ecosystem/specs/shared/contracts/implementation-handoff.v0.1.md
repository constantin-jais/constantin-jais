# Contract — ImplementationHandoff v0.1

Status: Draft / P0 harness contract.  
Schema: `implementation-handoff.v0.1.schema.json`.

## Purpose

`ImplementationHandoff` is the canonical planning-only contract from a Rumble product to Bolt.

It allows a Rumble product to submit an approved, traceable, governed product artifact to `cos-matic` without authorizing direct implementation execution.

## Boundary

| Concern | Owner |
| --- | --- |
| Product spec/package UX | Rumble product |
| Package immutability and provenance | Gear candidate |
| Handoff validation and planning | Bolt / `cos-matic` |
| Inspection reports | Wrench |
| Execution | Bolt only, never Rumble directly |

## Non-Negotiable Rule

MVP handoff is planning-only:

```json
{
  "planning_only": true,
  "allow_execution": false,
  "requires_human_approval_for_execution": true
}
```

Any payload that permits execution must be rejected.

## Required Payload

```json
{
  "format": "canvas.bolt_handoff.v0.1",
  "kind": "planning_request",
  "source": {
    "product": "rumble-canvas",
    "workspace_id": "uuid-or-stable-id",
    "handoff_id": "uuid-or-stable-id",
    "created_by": "actor-id",
    "created_at": "timestamp"
  },
  "package": {
    "package_id": "uuid-or-stable-id",
    "version": "string",
    "package_hash": "sha256",
    "artifact_reference_id": "optional-string",
    "items": []
  },
  "planning_scope": {
    "mode": "full_package",
    "target_objects": [],
    "excluded_objects": [],
    "goal": "text"
  },
  "spec_context": {
    "charter_summary": {},
    "roles": [],
    "journeys": [],
    "screens": [],
    "actions": [],
    "domain_entities": [],
    "acceptance_criteria": []
  },
  "traceability_links": [],
  "active_waivers": [],
  "open_questions": [],
  "risks": [],
  "capability_candidates": [],
  "constraints": {
    "sovereignty": "self-hostable; no hidden external dependency",
    "data_residency": "EU/local-first where applicable",
    "non_goals": []
  },
  "requested_outputs": [
    "implementation_plan",
    "task_breakdown",
    "risk_review",
    "test_plan",
    "shared_capability_extraction_review"
  ],
  "execution_policy": {
    "planning_only": true,
    "allow_execution": false,
    "requires_human_approval_for_execution": true
  }
}
```

## Validation Gates

`cos-matic` must reject the handoff if:

1. `format` is unknown.
2. `kind` is not `planning_request`.
3. package hash is missing or malformed.
4. package has no items.
5. execution policy allows execution.
6. blocking open questions exist without accepted waiver.
7. high/critical risks exist without accepted waiver.
8. traceability coverage is below policy threshold.
9. active waivers are expired, self-approved when separation is required, or missing rationale.
10. capability candidates have no proposed owner layer when they affect implementation scope.

## Expected Bolt Responses

### Accepted for planning

```json
{
  "status": "accepted_for_planning",
  "bolt_reference": "plan-id",
  "received_hash": "sha256",
  "next": "dry_run_plan"
}
```

### Refused

```json
{
  "status": "refused",
  "reason_code": "blocking_questions_without_waiver",
  "findings": []
}
```

### Plan produced

```json
{
  "status": "plan_ready",
  "bolt_reference": "plan-id",
  "outputs": {
    "implementation_plan": "artifact-ref-or-inline-summary",
    "task_breakdown": [],
    "risk_review": [],
    "test_plan": [],
    "shared_capability_extraction_review": []
  }
}
```

## Idempotency

Submission identity is:

```text
handoff_id + payload_hash
```

Retrying the same payload must not create duplicate planning requests.

## Audit Requirements

Persist:

- actor;
- timestamp;
- payload hash;
- package hash;
- validation result;
- refusal reason or plan reference;
- requested outputs;
- execution policy.

## Fixtures Required

Minimum fixtures:

```text
specs/harness/fixtures/handoffs/canvas-minimal.valid.json
specs/harness/fixtures/handoffs/canvas-execution-forbidden.invalid.json
specs/harness/fixtures/handoffs/canvas-missing-trace.invalid.json
specs/harness/fixtures/handoffs/canvas-blocking-question-no-waiver.invalid.json
specs/harness/fixtures/handoffs/canvas-high-risk-no-waiver.invalid.json
specs/harness/fixtures/handoffs/canvas-expired-waiver.invalid.json
specs/harness/fixtures/handoffs/canvas-capability-missing-owner.warning.json
```

## CLI Target

`cos-matic` should expose through the current `cosmatic` binary:

```bash
cosmatic handoff validate <handoff.json>
cosmatic handoff validate <handoff.json> --json
cosmatic handoff plan <handoff.json> --dry-run
cosmatic handoff plan <handoff.json> --dry-run --json
```

No command in this contract may execute implementation work.
