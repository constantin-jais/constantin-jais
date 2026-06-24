# Services and APIs — rumble-canvas

## Scope

This document defines the first MVP service boundary for Canvas-to-Bolt handoff.

The MVP handoff is planning-only. It must never trigger implementation execution directly.

---

## Rumble App Service: `HandoffService.prepareBoltHandoff()`

### Owner Layer

Rumble Canvas.

### Input

- `workspace_id`
- `package_id`
- `planning_scope`
- `created_by`

### Output

- `ImplementationHandoff` in `draft` or `validated` status.
- Canonical payload using `canvas.bolt_handoff.v0.1`.
- `payload_hash`.

### Auth

- Actor must have active `Owner` role, or delegated `Editor` handoff permission.
- Package must belong to the workspace.

### Business Rules

- Package must be approved.
- Included package revisions must be immutable.
- Payload kind must be `planning_request`.
- Execution policy must set:
  - `planning_only: true`;
  - `allow_execution: false`;
  - `requires_human_approval_for_execution: true`.
- Active waivers, open questions, risks, and traceability links must be included.

### Idempotency

Repeated preparation with the same package, scope, and source state should produce the same canonical payload hash.

### Failure Modes

- Package missing or not approved.
- Actor lacks permission.
- Planning scope references unknown objects.
- Required traceability/package metadata missing.
- Payload validation fails.

### Observability

Emit:

- `implementation_handoff_created`
- `implementation_handoff_validated`
- `implementation_handoff_validation_failed`

### Tests

- Given an approved package, preparing handoff creates a canonical payload.
- Given an unapproved package, preparation is blocked.
- Given execution policy allows execution, validation fails.
- Given active waivers exist, they appear in payload.

---

## Rumble-to-Bolt API: `HandoffService.submitToBolt()`

### Owner Layer

Rumble Canvas owns submission request and audit. Bolt owns receipt, validation, and planning lifecycle.

### Input

- `implementation_handoff_id`
- canonical `payload`
- `payload_hash`

### Output

- Updated `ImplementationHandoff` status:
  - `submitted`;
  - `acknowledged`;
  - `failed`.
- Optional `bolt_reference`.
- Validation or transport errors.

### Auth

- Same actor authorization as preparation.
- Handoff must be `validated` before submission.

### Idempotency

- Submission should be idempotent by `handoff_id` + `payload_hash`.
- Retrying the same payload must not create duplicate Bolt planning requests unless explicitly forced.

### Failure Modes

- Bolt unavailable.
- Bolt rejects format/version.
- Bolt rejects payload validation.
- Network/transport timeout.
- Response hash/reference mismatch.

### Observability

Emit:

- `bolt_handoff_submitted`
- `bolt_handoff_acknowledged`
- `bolt_handoff_failed`

Persist:

- request timestamp;
- actor;
- payload hash;
- Bolt response/reference;
- validation errors.

### Tests

- Given a valid handoff, submission records Bolt acknowledgement.
- Given Bolt is unavailable, payload remains retryable/exportable.
- Given Bolt rejects validation, errors are stored without mutating the approved package.
- Given MVP mode, no execution run is created.

---

## Canonical Payload Contract

```json
{
  "format": "canvas.bolt_handoff.v0.1",
  "kind": "planning_request",
  "source": {
    "product": "rumble-canvas",
    "workspace_id": "uuid",
    "handoff_id": "uuid",
    "created_by": "actor-id",
    "created_at": "timestamp"
  },
  "package": {
    "package_id": "uuid",
    "version": "string",
    "package_hash": "sha256",
    "artifact_reference_id": "optional-string",
    "items": []
  },
  "planning_scope": {
    "mode": "full_package | slice",
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

---

## Non-Goals

- No direct implementation execution from Canvas MVP.
- No Bolt run lifecycle ownership in Canvas.
- No hidden mutation of approved spec packages.
- No Markdown-only handoff as the canonical API format.
