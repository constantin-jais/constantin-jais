# Acceptance Tests — rumble-canvas

Status: Draft / harness-first.

## Contract Fixtures

Fixtures live in:

```text
specs/harness/fixtures/handoffs/
```

Required:

- `canvas-minimal.valid.json`
- `canvas-execution-forbidden.invalid.json`
- `canvas-missing-trace.invalid.json`
- `canvas-blocking-question-no-waiver.invalid.json`
- `canvas-high-risk-no-waiver.invalid.json`
- `canvas-expired-waiver.invalid.json`
- `canvas-capability-missing-owner.warning.json`

## Given / When / Then

### Valid handoff

Given an approved package with traceability and planning-only policy  
When `cosmatic handoff validate` runs  
Then validation succeeds.

### Dry-run plan

Given a valid handoff  
When `cosmatic handoff plan --dry-run` runs  
Then a planning report is produced and no execution occurs.

### Execution forbidden

Given a handoff with `allow_execution = true`  
When validation runs  
Then validation fails with `execution_forbidden`.

### Missing traceability

Given a handoff with no traceability links  
When validation runs  
Then validation fails with `missing_traceability_links`.

### Blocking question without waiver

Given an open blocking question and no accepted waiver  
When validation runs  
Then validation fails with `blocking_question_without_waiver`.

### High risk without waiver

Given a high/critical open risk and no accepted waiver  
When validation runs  
Then validation fails with `high_risk_without_waiver`.

### Expired waiver

Given an expired waiver  
When validation runs  
Then validation fails with `expired_waiver`.

### Capability missing owner

Given a capability candidate without owner layer  
When validation runs  
Then validation emits warning `capability_owner_missing` but does not block by default.

## CLI Smoke Commands

```bash
cosmatic handoff validate specs/harness/fixtures/handoffs/canvas-minimal.valid.json
cosmatic handoff validate specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run --json
```

## Product Acceptance

Canvas MVP is ready for UI implementation when:

- package/handoff fixtures pass;
- package approval rules are specified;
- data model supports immutable revisions;
- handoff payload is generated from structured fields;
- Rumble UI cannot bypass planning-only policy;
- Wrench/Gear extraction points are logged.
