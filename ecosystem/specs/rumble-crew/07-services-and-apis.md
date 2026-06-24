# Services and APIs — rumble-crew

## Scope

This document defines MVP service boundaries and API contracts for `rumble-crew`.

The API must preserve the product boundary:

- `rumble-crew` owns workspace UX, task state, approvals, evidence review, blockers, comments, boards, and local projections.
- `cos-matic` owns orchestration, execution planning, gate enforcement, runtime status, and execution evidence production.
- Gear may own artifact/provenance/event-log storage.
- Wrench may produce inspection reports attached as evidence.

---

## API Challenge / Boundary Checks

### Check 1: Does this endpoint decide execution strategy?

If yes, it does not belong in `rumble-crew`.

`rumble-crew` may request a run with bounded context, including real execution when `execution_mode=trusted_execution`. It must not choose internal tool sequence, retry plan, or runtime execution steps.

### Check 2: Does this endpoint store secrets?

If yes, reject for MVP.

`RuntimeRef` stores safe labels/opaque IDs only. Credentials belong to the runtime/integration substrate, not product task records.

### Check 3: Does this endpoint create generic PM features?

If yes, defer.

MVP APIs should serve agentic supervision: task, run ref, approval, blocker, evidence, timeline, agent/skill metadata.

### Check 4: Does this endpoint expose raw runtime logs?

If yes, it must require privileged raw-log permission, workspace raw-log enablement, no indexing, TTL/retention, and an audit event `runtime_log_accessed`.

---

## Service Groups

| Service | Owner layer | Purpose |
| --- | --- | --- |
| Workspace Service | Rumble Crew | Workspaces, members, settings. |
| Board Query Service | Rumble Crew | Board/read models and filters. |
| Task Service | Rumble Crew | Task lifecycle and assignment. |
| Run Request Service | Rumble-to-Bolt seam | Request/cancel/rerun through `cos-matic`; keep local `RunRef`. |
| Approval Service | Rumble + Bolt seam | Human approval UX and sync to Bolt gates. |
| Blocker Service | Rumble + Bolt seam | Human and runtime blocker reporting/resolution. |
| Evidence Service | Rumble + Gear/Bolt/Wrench seam | Evidence records, review status, artifact refs. |
| Agent/Skill Service | Rumble projection + Bolt sync | Agent profiles and skill cards. |
| Timeline/Audit Service | Rumble projection + Gear candidate | Activity events and exports. |
| Runtime Log Service | Rumble sensitive-data boundary | Privileged access to raw/redacted runtime logs. |
| Integration Service | Rumble-to-Bolt seam | `cos-matic` status, capability sync, event ingestion. |

---

## API Conventions

### Format

- JSON over HTTP for MVP.
- Stable event names and object IDs.
- All mutating requests require authentication and permission checks.
- All mutating requests should support `Idempotency-Key` header where duplicate risk exists.

### Common Headers

| Header | Required | Notes |
| --- | --- | --- |
| `Authorization` | Yes in multi-user mode | Bearer/session depending deployment. |
| `Idempotency-Key` | Required for create/run/rerun/decision/cancel | Prevent duplicate side effects. |
| `X-Request-Id` | Recommended | Traceability. |

### Common Error Shape

```json
{
  "error": {
    "code": "permission_denied",
    "message": "Human-readable message",
    "details": {},
    "retryable": false,
    "correlation_id": "optional"
  }
}
```

### Common Error Codes

| Code | Meaning |
| --- | --- |
| `validation_failed` | Input invalid/missing. |
| `permission_denied` | Actor cannot perform action. |
| `not_found` | Object absent or hidden. |
| `conflict` | State/version conflict. |
| `stale_target` | Target changed/superseded. |
| `approval_required` | Human approval required first. |
| `active_run_exists` | MVP allows one active run per task. |
| `integration_unavailable` | `cos-matic`/external system unavailable. |
| `sync_failed` | Local action recorded but external sync failed. |
| `policy_denied` | Workspace policy blocks action. |

### Actor Context

Every mutation records an `ActorRef` snapshot:

```json
{
  "actor_id": "usr_123",
  "actor_type": "human",
  "display_name": "Ada",
  "source": "workspace_member"
}
```

Agent/runtime/system events must be explicitly typed and cannot satisfy human approval requirements.

---

## Workspace Service

### `GET /workspaces/{workspace_id}`

#### Owner layer

Rumble Crew.

#### Input

Path `workspace_id`.

#### Output

Workspace summary, actor permissions, integration status summary.

#### Auth

Workspace read permission.

#### Idempotency

Read-only.

#### Failure modes

- `not_found`
- `permission_denied`

#### Observability

Record request ID and actor, no sensitive payload.

#### Tests

- owner can read;
- observer can read allowed fields;
- non-member denied.

---

### `GET /workspaces/{workspace_id}/settings`

Returns members, approval policy, integration status, runtime refs metadata according to permissions.

### `PATCH /workspaces/{workspace_id}/approval-policy`

#### Owner layer

Rumble Crew.

#### Input

```json
{
  "policy_version": "string-current-version",
  "approval_policy": {
    "start": { "required_for_risk": ["high", "critical"] },
    "scope": { "required_when_ambiguity": true },
    "risk": { "required_for_risk": ["high", "critical"] },
    "completion": { "required_for_agent_tasks": true }
  }
}
```

#### Output

Updated policy with new version.

#### Auth

Workspace owner.

#### Idempotency

Use `Idempotency-Key` for repeated save. Version prevents lost updates.

#### Failure modes

- `permission_denied`
- `validation_failed`
- `conflict`

#### Observability

Audit policy change with before/after hash.

#### Tests

- last valid policy preserved on failed update;
- policy changes do not mutate historical approvals.

---

## Board Query Service

### `GET /workspaces/{workspace_id}/board`

#### Owner layer

Rumble Crew.

#### Input

Query filters:

- `task_status`;
- `run_status`;
- `assignee_type`;
- `agent_profile_id`;
- `skill_card_id`;
- `risk_level`;
- `needs_attention`;
- `updated_since`.

#### Output

```json
{
  "board": {
    "id": "uuid",
    "columns": [
      {
        "id": "uuid",
        "name": "Blocked",
        "task_status_filter": ["blocked"],
        "cards": [
          {
            "task_id": "uuid",
            "title": "Investigate failing tests",
            "task_status": "blocked",
            "assignee": { "type": "agent_profile", "id": "uuid", "label": "Code agent" },
            "skill_card": { "id": "uuid", "name": "Code change" },
            "latest_run_status": "waiting_for_approval",
            "open_blockers": 1,
            "pending_approvals": 1,
            "evidence_status": "none",
            "risk_level": "medium",
            "last_activity_at": "timestamp"
          }
        ]
      }
    ]
  }
}
```

#### Auth

Workspace read; card fields redacted by object permission.

#### Idempotency

Read-only.

#### Failure modes

- `permission_denied`
- `validation_failed`

#### Observability

Track query latency and result count.

#### Tests

- task/run status shown separately;
- stale run state shown when sync stale;
- observer receives read-only cards.

---

## Task Service

### `POST /workspaces/{workspace_id}/tasks`

#### Owner layer

Rumble Crew.

#### Input

```json
{
  "title": "Fix failing CI",
  "goal": "CI passes on main branch candidate",
  "description": "Context and constraints",
  "constraints": ["do not change public API"],
  "expected_evidence": ["test_report", "diff"],
  "risk_level": "medium",
  "initial_assignment": {
    "assignee_type": "agent_profile",
    "assignee_ref": "uuid",
    "skill_card_id": "uuid"
  }
}
```

#### Output

Created task summary and assignment if any.

#### Auth

`task:create`.

#### Idempotency

Required. Same key returns existing task result.

#### Failure modes

- `validation_failed`
- `permission_denied`
- `policy_denied`

#### Observability

Audit `task_created`, `task_assigned`.

#### Tests

- title/goal required;
- disabled skill card rejected;
- workspace archived rejects creation.

---

### `GET /tasks/{task_id}`

Returns full task detail according to permissions:

- task;
- assignments;
- current/latest run refs;
- blockers;
- approvals;
- evidence;
- comments summary;
- actor permissions;
- next action suggestions.

### `PATCH /tasks/{task_id}`

Updates editable task fields.

Rules:

- cannot edit terminal tasks except allowed metadata/comment paths;
- editing task context while active run exists requires warning/policy;
- updates create activity event.

### `POST /tasks/{task_id}/assignments`

Creates/revokes/supersedes assignment.

Input:

```json
{
  "assignee_type": "agent_profile",
  "assignee_ref": "uuid",
  "skill_card_id": "uuid",
  "reason": "Use code-change agent"
}
```

Rules:

- reassignment does not delete prior assignment;
- active run blocks reassignment unless cancellation/supersession policy allows;
- agent assignment validates skill compatibility.

---

## Run Request Service

## Boundary Contract: RumbleCrewRunRequest → `cos-matic`

`rumble-crew` sends bounded task intent. `cos-matic` returns a run/gate/refusal/projection. Rumble does not send a step-by-step execution plan unless Bolt explicitly produced it earlier.

### Contract: `crew.cosmatic.run_request.v0.1`

```json
{
  "format": "crew.cosmatic.run_request.v0.1",
  "kind": "agent_task_run_request",
  "source": {
    "product": "rumble-crew",
    "workspace_id": "uuid",
    "task_id": "uuid",
    "run_ref_id": "uuid",
    "requested_by": "actor-id",
    "requested_at": "timestamp"
  },
  "task": {
    "title": "string",
    "goal": "string",
    "description": "string",
    "constraints": [],
    "expected_evidence": [],
    "risk_level": "low|medium|high|critical"
  },
  "assignment": {
    "agent_profile_id": "uuid",
    "skill_card_id": "uuid",
    "runtime_ref_id": "uuid-or-null"
  },
  "approvals": {
    "satisfied_approval_ids": [],
    "pending_approval_ids": []
  },
  "context": {
    "safe_context_refs": [],
    "inline_context": {},
    "redaction_policy": "workspace-default"
  },
  "execution_policy": {
    "mode": "trusted_execution",
    "allow_execution": true,
    "requires_human_approval_for_new_gates": true,
    "max_attempts": 1,
    "auto_close_policy": "manual_review_required | auto_close_if_evidence_valid | auto_close_if_run_succeeded"
  },
  "requested_outputs": [
    "status_projection",
    "gate_requests",
    "evidence_references",
    "failure_context"
  ]
}
```

### `POST /tasks/{task_id}/run-requests`

#### Owner layer

Rumble-to-Bolt seam. Rumble creates `RunRef`; Bolt executes.

#### Input

```json
{
  "assignment_id": "uuid",
  "skill_card_id": "uuid",
  "runtime_ref_id": "uuid-or-null",
  "context_snapshot": {},
  "request_mode": "start_or_queue",
  "reason": "Initial run"
}
```

#### Output

```json
{
  "run_ref": {
    "id": "uuid",
    "task_id": "uuid",
    "bolt_provider": "cos-matic",
    "external_run_id": "optional",
    "status": "queued|unknown",
    "sync_status": "current|sync_failed"
  },
  "bolt_response": {
    "status": "accepted|rejected|gate_required|unavailable",
    "external_reference": "optional",
    "message": "optional"
  }
}
```

#### Auth

`run:request`.

#### Idempotency

Required. Prevent duplicate run attempts.

#### Failure modes

- `approval_required`
- `active_run_exists`
- `integration_unavailable`
- `policy_denied`
- `validation_failed`
- `sync_failed`

#### Observability

Record request hash, Bolt response, latency, sync status.

#### Tests

- duplicate idempotency key returns same run ref;
- approval requirement creates/returns approval instead of active run;
- failed Bolt call preserves retryable local state.

---

### `POST /tasks/{task_id}/rerun-requests`

Creates new `RunRef` linked to prior run/evidence.

Input:

```json
{
  "previous_run_ref_id": "uuid",
  "previous_evidence_id": "uuid-or-null",
  "reason": "Evidence rejected: missing test report",
  "updated_context": {},
  "assignment_id": "uuid"
}
```

Rules:

- reason required;
- active run blocks rerun;
- retry policy/approval may apply;
- rejection reason included in context sent to Bolt.

---

### `POST /runs/{run_ref_id}/cancel-request`

Requests Bolt to cancel active run.

Rules:

- cancellation is a request, not guaranteed immediate termination;
- local task may show cancellation pending;
- Bolt acknowledgement updates `RunRef`.

---

## Approval Service

## Boundary Contract: RumbleCrewApprovalDecision → `cos-matic`

### Contract: `crew.cosmatic.approval_decision.v0.1`

```json
{
  "format": "crew.cosmatic.approval_decision.v0.1",
  "approval_id": "uuid",
  "task_id": "uuid",
  "run_ref_id": "uuid-or-null",
  "external_gate_id": "optional-string",
  "decision": "approved|rejected",
  "decided_by": "actor-id",
  "decided_at": "timestamp",
  "reason": "string",
  "conditions": {},
  "target_version": {
    "target_type": "run|task|evidence|blocker",
    "target_id": "uuid-or-string",
    "version_or_hash": "string"
  }
}
```

### `GET /workspaces/{workspace_id}/review-queue`

Returns pending approvals, submitted evidence, open blocking blockers, failed runs.

### `GET /approvals/{approval_id}`

Returns approval detail with target context and actor permissions.

### `POST /approvals/{approval_id}/decision`

#### Owner layer

Rumble decision record + Bolt gate sync if applicable.

#### Input

```json
{
  "decision": "approved",
  "reason": "Reviewed risk and scope",
  "conditions": {},
  "target_version_ack": "hash-or-version"
}
```

#### Output

Updated approval and sync result.

#### Auth

`approval:decide` and human actor requirement.

#### Idempotency

Required.

#### Failure modes

- `permission_denied`
- `stale_target`
- `validation_failed`
- `sync_failed`
- `policy_denied`

#### Observability

Audit approval decision, target, version, sync status.

#### Tests

- agent/runtime actor cannot approve;
- rejection reason required;
- stale target blocked;
- Bolt sync failure visible.

---

## Blocker Service

### `POST /tasks/{task_id}/blockers`

Creates a human-reported blocker.

Input:

```json
{
  "type": "missing_context",
  "severity": "blocking",
  "summary": "Need target branch",
  "details": "Agent cannot proceed without branch name",
  "resolver_ref": { "actor_id": "usr_123", "actor_type": "human" }
}
```

### `POST /blockers/{blocker_id}/resolution`

Resolves, rejects, or supersedes blocker.

Input:

```json
{
  "decision": "resolved",
  "resolution": "Target branch is feature/crew-mvp",
  "linked_object": { "type": "comment", "id": "uuid" }
}
```

#### Rules

- blocking blockers prevent task done;
- resolution requires rationale;
- automated blockers require trusted integration endpoint, not this user endpoint.

---

## Evidence Service

## Boundary Contract: EvidenceReference from Bolt/Wrench/Gear

```json
{
  "format": "crew.evidence_reference.v0.1",
  "task_id": "uuid",
  "run_ref_id": "uuid-or-null",
  "type": "log|diff|test_report|screenshot|artifact|decision_record|inspection_report|other",
  "summary": "string",
  "artifact_ref": {
    "provider": "gear|external|inline",
    "id": "string",
    "uri": "optional-safe-uri",
    "content_hash": "sha256-optional"
  },
  "produced_by": {
    "actor_id": "agent-or-runtime-id",
    "actor_type": "agent|runtime_service|system"
  },
  "produced_at": "timestamp"
}
```

### `POST /tasks/{task_id}/evidence`

Creates human-submitted evidence or trusted integration-submitted evidence depending auth context.

### `GET /evidence/{evidence_id}`

Returns evidence detail and artifact availability.

### `POST /evidence/{evidence_id}/review`

#### Owner layer

Rumble evidence review UX; Gear/Bolt artifacts remain external references.

#### Input

```json
{
  "decision": "accepted|rejected",
  "reason": "Sufficient test report and diff",
  "mark_task_done": true,
  "target_version_ack": "hash-or-version"
}
```

#### Output

Updated evidence, optional task transition result.

#### Auth

`evidence:review` and human actor requirement.

#### Idempotency

Required.

#### Failure modes

- `permission_denied`
- `stale_target`
- `validation_failed`
- `policy_denied`
- `artifact_unavailable`

#### Observability

Audit evidence decision, artifact ref/hash, reviewer.

#### Tests

- rejection reason required;
- accepted evidence cannot close task with open blocking blocker;
- unavailable artifact blocks acceptance unless explicit policy path exists.

---

## Agent/Skill Service

### `GET /workspaces/{workspace_id}/agent-profiles`

Returns visible agent profiles.

### `POST /workspaces/{workspace_id}/agent-profiles`

Creates local agent profile metadata.

Rules:

- no credentials;
- optional runtime ref;
- disabled profiles cannot receive assignments.

### `GET /workspaces/{workspace_id}/skill-cards`

Returns skill cards with input requirements, output expectations, required approvals, and compatible runtime refs.

### `POST /workspaces/{workspace_id}/skill-cards`

Creates local skill card.

### `PATCH /skill-cards/{skill_card_id}`

Updates/disabled/deprecates a skill card.

Rules:

- active cards require input/output requirements;
- disabling card does not mutate historical tasks.

### `POST /workspaces/{workspace_id}/integrations/cos-matic/sync-capabilities`

Requests capability metadata sync from Bolt.

Output:

```json
{
  "sync_status": "completed|failed|partial",
  "agent_profiles_upserted": 2,
  "skill_cards_upserted": 5,
  "runtime_refs_updated": 1,
  "errors": []
}
```

---

## Runtime Log Service

### `GET /runs/{run_ref_id}/logs`

#### Owner layer

Rumble sensitive-data boundary; raw log source remains runtime/Gear/external reference where possible.

#### Input

Query:

- `visibility=summary|redacted_raw|privileged_raw`.
- `reason` required for privileged raw access if policy requires.

#### Output

For summary/redacted:

```json
{
  "run_ref_id": "uuid",
  "visibility": "summary|redacted_raw",
  "summary": "safe text",
  "redaction_status": "redacted|pending|failed",
  "contains_sensitive_markers": false
}
```

For privileged raw, output may include a short-lived safe fetch reference or raw body depending deployment policy.

#### Auth

- `logs:summary:read` for summary.
- `logs:raw:read` plus workspace `raw_logs_enabled=true` for raw.

#### Idempotency

Read-only, but raw access always appends `runtime_log_accessed` event.

#### Failure modes

- `permission_denied`
- `policy_denied`
- `not_found`
- `artifact_unavailable`
- `redaction_failed`

#### Observability

Every privileged raw access records actor, run, log ID/reference, visibility, reason, redaction status. Log body is never copied into audit payload.

#### Tests

- raw logs disabled blocks owner too;
- raw access emits audit event;
- raw logs are not indexed/searched;
- scanner failure does not silently expose logs to unprivileged users.

---

## Timeline/Audit Service

### `GET /workspaces/{workspace_id}/timeline`

Query params:

- `task_id`;
- `event_type`;
- `source`;
- `actor_id`;
- `from`;
- `to`;
- `cursor`.

Returns paginated activity events with redaction markers.

### `GET /tasks/{task_id}/timeline`

Task-specific timeline.

### `POST /workspaces/{workspace_id}/audit-exports`

Creates audit export request.

Input:

```json
{
  "scope": {
    "task_ids": ["uuid"],
    "from": "timestamp",
    "to": "timestamp"
  },
  "format": "json|markdown|bundle",
  "include_redacted_markers": true
}
```

Rules:

- export respects permissions;
- sensitive artifacts may be omitted with redaction markers;
- generated export may be stored as Gear artifact if configured.

---

## Integration Service — Inbound Events From `cos-matic`

Inbound integration must be authenticated and idempotent. Events use source event IDs to avoid duplicate projections.

### `POST /integrations/cos-matic/events`

#### Owner layer

Rumble integration endpoint receiving Bolt projections.

#### Input

```json
{
  "format": "crew.cosmatic.event.v0.1",
  "source_event_id": "string",
  "event_type": "run_status_changed|gate_requested|blocker_reported|evidence_produced|run_failed|run_cancelled",
  "occurred_at": "timestamp",
  "workspace_id": "uuid",
  "task_id": "uuid",
  "run_ref_id": "uuid",
  "external_run_id": "string",
  "payload": {}
}
```

#### Output

```json
{
  "accepted": true,
  "projection_updated": true,
  "activity_event_id": "uuid"
}
```

#### Auth

Trusted integration authentication. No user session.

#### Idempotency

Required via `source_event_id`.

#### Failure modes

- `permission_denied`
- `validation_failed`
- `not_found`
- `conflict`

#### Observability

Track accepted/rejected events, projection latency, duplicate rate.

#### Tests

- duplicate event does not create duplicate timeline entries;
- untrusted event rejected;
- unknown run/task does not mutate unrelated objects;
- gate event creates approval request.

---

## Inbound Event Types

### `run_status_changed`

Payload:

```json
{
  "status": "queued|claimed|running|waiting_for_approval|succeeded|failed|cancelled|unknown",
  "runtime_ref": {},
  "message": "optional"
}
```

Projection rules:

- update `RunRef.status`;
- if status `running`, task may become `in_progress`;
- if status `succeeded`, task should become `in_review` when evidence/review is expected;
- never mark task `done` solely from run success.

### `gate_requested`

Creates `Approval` with type and target.

### `blocker_reported`

Creates `Blocker`, may set task `blocked`.

### `evidence_produced`

Creates `Evidence` in `submitted` state.

### `run_failed`

Updates `RunRef` to failed and creates failure context activity. Task may move to `blocked`, `ready`, or `failed` according to policy/human decision; default is needs recovery decision.

### `run_cancelled`

Updates `RunRef` to cancelled and records activity. Task status depends on whether task cancellation was requested or only run cancellation.

---

## Gear Calls

MVP should not require Gear to exist, but APIs should be compatible with it.

### Artifact lookup

Rumble may call Gear/external artifact service to check evidence availability and metadata.

Input:

- `artifact_ref`.

Output:

- availability;
- content hash;
- redaction/access flags;
- preview URL if safe.

Failure behavior:

- show artifact unavailable;
- do not delete evidence;
- block acceptance if policy requires accessible proof.

### Audit export storage

Generated audit exports may be stored as Gear artifact and referenced by `artifact_ref`.

---

## Wrench Calls

Wrench outputs may be evidence, not task authority.

Examples:

- inspection report;
- validation report;
- policy check result;
- test report generated by a tool.

Rumble stores review state; Wrench report content/provenance remains attached as evidence reference.

---

## Security and Privacy Requirements for APIs

- Never return runtime secrets.
- Redact raw logs by default.
- Treat task context as potentially sensitive.
- All approval/evidence decisions require human actor attribution.
- Integration endpoints require service authentication and replay protection.
- Artifact refs must not expose private signed URLs indefinitely.
- Audit exports must respect access control and redaction policy.

---

## Minimal API Acceptance Tests

### Task/run separation

Given `cos-matic` sends `run_status_changed=succeeded`, when Rumble ingests event, then task becomes `in_review` or remains awaiting evidence unless explicit low-risk auto-close policy passes.

### Human-only approvals

Given an actor with `actor_type=agent`, when it posts approval decision, then API returns `permission_denied`.

### Idempotent run request

Given same idempotency key, when client retries `POST /tasks/{task_id}/run-requests`, then only one `RunRef` exists.

### Stale approval target

Given approval target hash changed, when reviewer approves old target, then API returns `stale_target`.

### Evidence unavailable

Given evidence artifact lookup fails, when reviewer accepts evidence, then API blocks unless explicit policy path exists.

### Integration replay

Given duplicate `source_event_id`, when integration event is replayed, then no duplicate activity event is created.

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should `cos-matic` receive direct approval callbacks or poll Rumble for decisions? | High | Accepted direction: push idempotent + retry + visible `sync_failed`; polling optional later. |
| Should run requests be execution-capable in MVP or planning-only first? | High | Accepted: real execution allowed when workspace `execution_mode=trusted_execution`; otherwise disabled/planning-only. |
| Should Gear artifact lookup be required before evidence acceptance? | Medium | Accepted direction: Gear target; local Rumble storage allowed only as extractable fallback. |
| What auth mechanism secures integration events? | High | Defer to security spec; must include replay protection. |
| Should failed runs move task to `blocked`, `ready`, or `failed` by default? | Medium | Accepted: needs recovery decision, not terminal failed automatically. |
