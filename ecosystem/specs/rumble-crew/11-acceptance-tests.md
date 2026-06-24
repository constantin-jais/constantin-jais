# Acceptance Tests — rumble-crew

## Scope

This document defines MVP acceptance tests for `rumble-crew`.

Tests are written at product/spec level. Implementation can translate them into unit, integration, API, UI, RLS/security, and end-to-end tests.

---

## Test Layers

| Layer | Purpose |
| --- | --- |
| Domain invariant tests | Lifecycle, policies, state transitions. |
| API contract tests | Inputs, outputs, idempotency, errors. |
| Permission/security tests | Roles, human-only approvals, raw logs, execution gates. |
| Integration tests | `cos-matic` request/event sync. |
| UI smoke tests | Board, task detail, review queue, evidence, run detail. |
| Data migration tests | Local evidence extraction to Gear-compatible ref. |
| Audit tests | Critical event append-only behavior and exports. |

---

## Domain Invariant Tests

### Test: Run success does not always close task

Given a task has `completion_mode=manual_review_required`  
And latest run status becomes `succeeded`  
When `cos-matic` event is ingested  
Then task status becomes `in_review` or remains awaiting evidence/review  
And task is not `done`.

### Test: Auto-close low-risk trusted task

Given workspace `execution_mode=trusted_execution`  
And task `risk_level=low`  
And task `completion_mode=auto_close_if_run_succeeded`  
And selected skill card has `auto_closable=true`  
And there are no open blockers or pending approvals  
And task context has not changed since run request  
When trusted `cos-matic` event reports run `succeeded`  
Then task status becomes `done`  
And `auto_close_applied` activity event is appended.

### Test: High-risk task cannot auto-close

Given task `risk_level=high`  
And task has `completion_mode=auto_close_if_run_succeeded`  
When run status becomes `succeeded`  
Then task is not auto-closed  
And `auto_close_blocked` records reason `risk_level_not_allowed`.

### Test: Open blocker prevents done

Given task has an open blocker with severity `blocking`  
When evidence is accepted or run succeeds with auto-close policy  
Then task does not become `done`  
And UI exposes blocker as completion blocker.

### Test: Failed run requires recovery decision

Given a task has active run  
When `cos-matic` reports run `failed`  
Then `RunRef.recovery_state=needs_decision`  
And task is not automatically `failed`  
And review/recovery queue shows rerun/reassign/fail/cancel options.

### Test: One active run by default

Given task has a run with status `queued`, `claimed`, `running`, or `waiting_for_approval`  
When user requests another run  
Then API returns `active_run_exists` unless explicit parallel policy exists.

---

## Permission and Security Tests

### Test: Agent cannot approve

Given actor has `actor_type=agent`  
When actor submits approval decision  
Then API returns `permission_denied`  
And approval status remains unchanged.

### Test: Runtime service cannot approve

Given actor has `actor_type=runtime_service`  
When actor submits approval decision  
Then API returns `permission_denied`.

### Test: Reviewer can approve assigned approval

Given human actor has Reviewer / Approver role  
And approval is in `requested` state  
When actor approves with valid target version  
Then approval becomes `approved`  
And `approval_granted` is appended.

### Test: Stale approval target blocked

Given approval targets hash `h1`  
And target changes to hash `h2`  
When reviewer approves using `h1`  
Then API returns `stale_target`  
And approval remains `requested`.

### Test: Execution disabled blocks run

Given workspace `execution_mode=disabled`  
When authorized user requests run  
Then API returns `policy_denied`  
And no external `cos-matic` request is sent.

### Test: Planning-only blocks execution

Given workspace `execution_mode=planning_only`  
When run request asks `allow_execution=true`  
Then API returns `policy_denied` or downgrades to planning-only according to endpoint contract  
And no execution-capable request is sent.

### Test: Trusted execution permits run request

Given workspace `execution_mode=trusted_execution`  
And `cos-matic` integration is configured  
And task has valid agent assignment and skill card  
And required approvals are satisfied  
When authorized user requests run  
Then `RunRef` is created  
And `crew.cosmatic.run_request.v0.1` is sent.

### Test: Raw logs disabled blocks access

Given workspace `raw_logs_enabled=false`  
And owner requests privileged raw logs  
Then API returns `policy_denied`.

### Test: Raw log access is audited

Given workspace `raw_logs_enabled=true`  
And actor has `logs:raw:read`  
When actor opens privileged raw logs  
Then log content or fetch reference is returned according to policy  
And `runtime_log_accessed` activity event is appended  
And event payload does not include raw log body.

### Test: Raw logs are not indexed

Given raw runtime log contains a unique token-like string  
When user searches workspace  
Then search does not return result from raw log body.

---

## API Contract Tests

### Test: Create task validates required fields

Given actor can create tasks  
When actor submits task without title or goal  
Then API returns `validation_failed`.

### Test: Create task idempotency

Given actor sends `POST /workspaces/{id}/tasks` with idempotency key K  
When request is retried with same payload and K  
Then same task result is returned  
And no duplicate task is created.

### Test: Run request idempotency

Given actor sends `POST /tasks/{id}/run-requests` with idempotency key K  
When request is retried with same payload and K  
Then same `RunRef` is returned  
And no second run is created.

### Test: Idempotency key reuse with different payload blocked

Given key K was used for payload A  
When client reuses K with payload B  
Then API returns `conflict`.

### Test: Approval sync failure visible

Given approval decision is recorded locally  
And sync to `cos-matic` fails  
When API returns response  
Then approval status or sync field indicates `sync_failed`  
And retry path is available.

---

## Integration Tests With `cos-matic`

### Test: Inbound event authentication

Given inbound event lacks valid integration authentication  
When event endpoint receives it  
Then API returns `permission_denied`  
And no projection is updated.

### Test: Duplicate inbound event is idempotent

Given event with `source_event_id=E1` was processed  
When same event is received again  
Then no duplicate activity event is created  
And state remains consistent.

### Test: Unknown run reference rejected safely

Given inbound event references unknown `run_ref_id`  
When event is received  
Then API returns `not_found` or records integration error  
And no unrelated task is mutated.

### Test: Gate request creates approval

Given `cos-matic` sends `gate_requested` for known run  
When event is ingested  
Then `Approval` is created in `requested` state  
And review queue shows it.

### Test: Evidence produced creates submitted evidence

Given `cos-matic` sends `evidence_produced` with valid artifact ref  
When event is ingested  
Then `Evidence` is created in `submitted` state  
And task appears in evidence review queue.

---

## Evidence and Gear-Extraction Tests

### Test: Local evidence has extraction metadata

Given evidence is stored using Rumble local fallback  
When evidence record is created  
Then `storage_backend=rumble_local`  
And `extractable=true`  
And `content_hash` is present  
And `migration_status` is set.

### Test: Evidence migration verifies hash

Given local evidence blob exists  
When it is exported to Gear-compatible artifact  
Then exported artifact hash matches `content_hash`  
And evidence `artifact_ref` is updated  
And `migration_status=verified`.

### Test: Unavailable evidence cannot be accepted by default

Given evidence artifact is unavailable  
When reviewer attempts acceptance  
Then API blocks acceptance unless explicit policy exception exists.

### Test: Rejected evidence requires reason

Given evidence is submitted  
When reviewer rejects without reason  
Then API returns `validation_failed`.

---

## UI Smoke Tests

### Test: Board distinguishes task and run status

Given task is `in_review`  
And latest run is `succeeded`  
When board loads  
Then card shows both task status and run status separately.

### Test: Review queue groups decision types

Given workspace has pending approval, submitted evidence, open blocker, and failed run  
When review queue opens  
Then each item appears in the correct section.

### Test: Run detail is not runtime console

Given user opens run detail  
Then screen shows run projection, gates, evidence, failure context, and safe logs/references  
And does not expose arbitrary command execution or plan editing controls.

### Test: Agents & Skills shows drift warning

Given `SkillCard.source=cos_matic` and `drift_status=drifted`  
When user opens skill card or assigns it  
Then UI shows drift warning  
And execution is blocked or requires confirmation according to policy.

### Test: Timeline redaction marker

Given event payload has redacted fields  
When timeline renders  
Then redaction marker is visible.

---

## Audit Tests

### Test: Critical event append-only

Given `approval_granted` event exists  
When correction is needed  
Then system creates superseding/correction event  
And does not mutate/delete original critical event.

### Test: Audit export excludes raw logs by default

Given task has privileged raw logs  
When normal audit export is requested  
Then export includes log metadata/redaction marker  
And does not include raw log body.

### Test: Task terminal transition includes reason

Given user cancels or fails task  
When transition is applied  
Then activity event includes actor and reason.

### Test: Auto-close audit explains policy

Given task auto-closes after run success  
When timeline is inspected  
Then event shows completion policy, skill card, run ref, and no-blockers/no-approvals checks.

---

## Data and Migration Tests

### Test: Hard delete blocked for audited task

Given task has approvals/evidence/runs/activity events  
When user attempts hard delete  
Then operation is blocked or converted to archive/redaction flow.

### Test: Restore marks run projections stale

Given workspace is restored from backup  
When task with previous active run is loaded  
Then run projection is marked stale/unknown until resynced.

### Test: Read model recomputation

Given board read model is missing  
When recomputation runs from tasks/run refs/activity events  
Then board displays consistent task cards.

---

## Non-Regression Boundary Tests

### Test: Rumble does not plan execution

Given run request is created  
Then payload contains task intent, constraints, selected skill/runtime refs, and execution policy  
And does not contain internal step-by-step orchestration plan authored by Rumble.

### Test: Rumble does not store credentials

Given workspace has RuntimeRef and integration settings  
When database records are inspected  
Then no runtime credential/token/private key is stored in Rumble tables.

### Test: Generic PM scope blocked

Given user requests sprint velocity/roadmap/capacity planning feature in MVP  
Then product spec classifies it as post-MVP/non-goal unless tied directly to agentic supervision.

---

## Minimum Definition of Done for MVP Implementation

MVP implementation cannot be considered done unless these scenarios pass:

1. Trusted execution request with idempotency.
2. Execution disabled/planning-only denial.
3. Human-only approval.
4. Run succeeded review-first behavior.
5. Low-risk auto-close behavior.
6. Failed run recovery decision.
7. Evidence local fallback with extraction metadata.
8. Raw log privileged access audit.
9. Duplicate inbound event idempotency.
10. Board/task/review/run UI smoke paths.
