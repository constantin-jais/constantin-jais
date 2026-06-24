# Events and Workflows — rumble-crew

## Scope

This document defines MVP events and workflows for `rumble-crew`.

Events must support:

- audit timeline;
- idempotent integration with `cos-matic`;
- task/run/approval/evidence traceability;
- recovery after sync failure;
- replay of derived projections where possible.

---

## Event Principles

1. Product events are not runtime execution commands.
2. Bolt events are projections into Rumble, not proof that task governance is complete.
3. Every event has actor/source attribution.
4. Mutating external events need idempotency keys or source event IDs.
5. Sensitive payloads are summarized or referenced, not copied blindly.
6. Event replay must not duplicate timeline entries or mutate immutable decisions.

---

## Event Envelope

```json
{
  "event_id": "uuid",
  "event_type": "task_created",
  "workspace_id": "uuid",
  "task_id": "uuid-or-null",
  "target_type": "task|run_ref|approval|blocker|evidence|workspace",
  "target_id": "uuid-or-string",
  "actor": {
    "actor_id": "string",
    "actor_type": "human|agent|system|runtime_service|external",
    "display_name": "optional",
    "source": "optional"
  },
  "source": "rumble_crew|cos_matic|gear|wrench|system",
  "payload": {},
  "occurred_at": "timestamp",
  "received_at": "timestamp",
  "source_event_id": "optional-string",
  "integrity_hash": "optional-string",
  "redaction": {
    "has_redactions": false,
    "reason": "optional"
  }
}
```

---

## Canonical Events

## Task Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `task_created` | Rumble | Board, timeline | High |
| `task_updated` | Rumble | Board, timeline | Medium |
| `task_assigned` | Rumble | Board, task detail, timeline | High |
| `task_ready` | Rumble/System | Board | Medium |
| `task_started` | Rumble/System from run projection | Board, timeline | High |
| `task_marked_blocked` | System | Board, review queue | High |
| `task_entered_review` | System | Board, review queue | High |
| `task_marked_done` | Rumble | Board, timeline, audit | High |
| `task_marked_failed` | Rumble | Board, timeline, audit | High |
| `task_cancelled` | Rumble | Board, timeline, audit | High |

### Rules

- `task_marked_done` requires accepted evidence or explicit completion approval.
- `task_cancelled` and `task_marked_failed` require human actor and reason.
- System-derived `task_entered_review` may follow `run_status_changed=succeeded` or `evidence_submitted`.

---

## Run Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `bolt_run_requested` | Rumble | RunRef, timeline | High |
| `bolt_run_request_failed` | Rumble/System | Task detail, timeline | High |
| `bolt_run_queued` | cos-matic | RunRef, board | Medium |
| `bolt_run_claimed` | cos-matic | RunRef | Medium |
| `bolt_run_started` | cos-matic | RunRef, task projection | High |
| `bolt_run_waiting_for_approval` | cos-matic | Approval service, board | High |
| `bolt_run_succeeded` | cos-matic | Evidence/review workflow | High |
| `bolt_run_failed` | cos-matic | Recovery workflow | High |
| `bolt_run_cancelled` | cos-matic | RunRef, task detail | High |
| `bolt_run_sync_failed` | System | Integration dashboard/timeline | High |

### Rules

- Bolt run events update `RunRef` projections.
- Run success does not directly emit `task_marked_done` unless explicit completion policy passes.
- Unknown/stale run state must be visible.
- Failed run defaults to recovery decision, not terminal task failure.

---

## Approval Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `approval_requested` | Rumble or cos-matic | Review queue, board | High |
| `approval_granted` | Rumble | Bolt sync, timeline | Critical |
| `approval_rejected` | Rumble | Bolt sync, timeline | Critical |
| `approval_expired` | System | Review queue, timeline | High |
| `approval_superseded` | System | Review queue | High |
| `approval_sync_failed` | System | Task detail, integration ops | High |

### Rules

- Only human actors can emit grant/reject decisions.
- Approval must target a specific version/hash/reference.
- Sync failure does not erase local human decision.

---

## Blocker Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `blocker_reported` | Rumble or cos-matic | Board, review queue | High |
| `blocker_resolved` | Rumble | Board, task detail | High |
| `blocker_rejected` | Rumble | Timeline | High |
| `blocker_superseded` | System/Rumble | Board, timeline | Medium |

### Rules

- Blocking open blockers prevent task done.
- Resolution requires rationale.
- Automated blockers require trusted source event ID.

---

## Evidence Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `evidence_submitted` | Rumble, cos-matic, Wrench | Review queue, task detail | High |
| `evidence_accepted` | Rumble | Task completion workflow | Critical |
| `evidence_rejected` | Rumble | Rerun/rework workflow | Critical |
| `evidence_superseded` | System/Rumble | Review queue, task detail | High |

### Rules

- Rejection requires reason.
- Evidence acceptance requires human actor.
- Superseded evidence stays in timeline.

---

## Agent/Skill Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `agent_profile_created` | Rumble | Agents & Skills | Medium |
| `agent_profile_disabled` | Rumble | Assignment validation | High |
| `skill_card_created` | Rumble | Assignment | Medium |
| `skill_card_updated` | Rumble/Bolt sync | Assignment validation | Medium |
| `skill_card_disabled` | Rumble | Assignment validation | High |
| `bolt_capabilities_synced` | Integration | Agents & Skills | Medium |

---

## Timeline Persistence

### Persistence

MVP stores timeline events in Rumble’s application store. Gear event log is a shared capability candidate.

### Replay Behavior

- Idempotent events can be replayed by `event_id` or `source_event_id`.
- Projection events recompute board/task derived state.
- Human decisions are immutable records; replay must not duplicate or reverse them.
- Redacted payloads remain redacted during export.

### Audit Relevance Levels

| Level | Meaning |
| --- | --- |
| Low | UI/navigation only; not required in audit. |
| Medium | Useful operational history. |
| High | Required to reconstruct task state. |
| Critical | Required for human accountability/compliance. |

---

# Workflows

## Workflow: Assign Agent and Request Run

### Trigger

Human creates or updates a task and assigns an agent profile/skill.

### Steps

1. Validate task title and goal.
2. Validate agent profile active.
3. Validate skill card active and compatible.
4. Create/activate `TaskAssignment`.
5. Emit `task_assigned`.
6. Check approval policy.
7. If approval needed, create `Approval` and emit `approval_requested`.
8. If no approval needed, create `RunRef`.
9. Send `crew.cosmatic.run_request.v0.1` to `cos-matic`.
10. Emit `bolt_run_requested`.
11. Ingest Bolt response/projection.

### Gates

- Permission: `task:assign`, `run:request`.
- Policy: start/scope/risk approval.
- Compatibility: skill/runtime available.

### Rollback

- If run request fails, keep task assignment and failed run request context.
- Do not delete task.

### Retry

- Retry run request using idempotency key or create explicit rerun after failure.

### Evidence

No completion evidence required at assignment time; expected evidence must be declared or waived by policy.

---

## Workflow: Agent Reports Blocker

### Trigger

`cos-matic` sends blocker event or human reports blocker.

### Steps

1. Authenticate source.
2. Validate task/run reference.
3. Deduplicate by source event ID if integration event.
4. Create `Blocker`.
5. Emit `blocker_reported`.
6. If severity blocking, update task projection to `blocked` and emit `task_marked_blocked`.
7. Notify/mark responsible resolver.
8. Human resolves/rejects/supersedes blocker.
9. Emit resolution event.
10. If all blockers cleared, recompute task actionable state.

### Gates

- Trusted integration or human permission.
- Resolution requires rationale.

### Rollback

Incorrect blocker is rejected/superseded, not deleted.

### Retry

Integration event replay is idempotent.

### Evidence

Resolution comment/approval/context becomes audit evidence for unblocking.

---

## Workflow: Human Approval Gate

### Trigger

Approval policy or Bolt gate requires human decision.

### Steps

1. Create `Approval` in requested state.
2. Emit `approval_requested`.
3. Show in review queue/task/run detail.
4. Human opens approval detail.
5. Validate permission and target version.
6. Human approves/rejects with reason/conditions.
7. Emit `approval_granted` or `approval_rejected`.
8. If execution-affecting, sync decision to `cos-matic`.
9. If sync fails, mark `approval_sync_failed`.
10. Bolt continues or stops based on decision.

### Gates

- Human actor required.
- Stale target protection.
- High-risk confirmation/separation if configured.

### Rollback

Approval decisions are not silently changed. A new superseding approval flow is required.

### Retry

Sync to Bolt can retry; local decision remains.

### Evidence

Approval decision is critical audit evidence.

---

## Workflow: Evidence Review and Completion

### Trigger

Evidence is submitted by human, Bolt, Wrench, or runtime integration.

### Steps

1. Create `Evidence` in submitted state.
2. Emit `evidence_submitted`.
3. Task enters `in_review` if completion evidence is expected.
4. Reviewer opens evidence.
5. System checks artifact availability/provenance where required.
6. Reviewer accepts or rejects.
7. Emit `evidence_accepted` or `evidence_rejected`.
8. If accepted and no blockers/approvals remain, task can be marked done.
9. Emit `task_marked_done` if completion occurs.
10. If rejected, task remains actionable and may trigger rerun workflow.

### Gates

- Human reviewer permission.
- Artifact/provenance availability if required.
- No open blocking blocker for completion.

### Rollback

Rejected/accepted evidence remains immutable; correction uses superseding evidence or explicit correction event.

### Retry

Artifact availability can be rechecked. Rerun can produce new evidence.

### Evidence

Accepted evidence and review decision are completion proof.

---

## Workflow: Rerun After Failure or Rejected Evidence

### Trigger

Run failed/cancelled or evidence rejected/superseded.

### Steps

1. User opens task recovery state.
2. System displays failure/rejection reason.
3. User chooses rerun.
4. Validate no active run.
5. Validate retry policy and approvals.
6. Create new `RunRef` linked to previous attempt.
7. Send rerun request to `cos-matic`.
8. Emit `rerun_requested` and `bolt_run_requested`.
9. Ingest new run projections.

### Gates

- Permission: `run:rerun`.
- Retry limit/policy.
- Approval if risk increased or repeated failure.

### Rollback

If Bolt rejects, keep rerun failure context.

### Retry

Idempotency key avoids duplicate reruns.

### Evidence

Rerun reason links previous failure/rejection to new attempt.

---

## Workflow: Cancel or Fail Task

### Trigger

Human decides work should stop or cannot complete.

### Steps

1. Human selects cancel/fail.
2. System requires reason.
3. If active run exists, send cancel request to `cos-matic`.
4. Record task terminal decision or pending cancellation state.
5. Emit `task_cancel_requested`, `run_cancel_requested`, `task_cancelled`, or `task_marked_failed` as applicable.
6. Board moves task to terminal lane/filter.

### Gates

- Human permission.
- Reason required.
- Active run cancellation sync when relevant.

### Rollback

Reopen is post-MVP or owner-only explicit policy.

### Retry

Cancel sync with Bolt can retry.

### Evidence

Reason and run cancel acknowledgement are audit evidence.

---

## Projection Rules

| Input | Projection |
| --- | --- |
| `task_created` | Task status `created`. |
| `task_assigned` | Task status `assigned` unless approvals/context make it `ready`. |
| Required context + approvals satisfied | Task status `ready`. |
| `bolt_run_started` | Task may become `in_progress`. |
| `blocker_reported` severity blocking | Task status `blocked`. |
| All blockers resolved + active run | Task may return `in_progress`. |
| `evidence_submitted` | Task may become `in_review`. |
| `bolt_run_succeeded` | Task may become `in_review`; it can become `done` only if explicit auto-close policy passes. |
| `evidence_accepted` + no blockers/approvals | Task can become `done`. |
| `bolt_run_failed` | Task needs recovery decision by default. |
| `task_cancelled` | Task terminal `cancelled`. |
| `task_marked_failed` | Task terminal `failed`. |

---

## Acceptance Criteria

- Given a duplicate integration event, replay does not duplicate timeline or change decision twice.
- Given a run succeeds and explicit low-risk auto-close policy passes, task can be marked done with audit event.
- Given a run succeeds without auto-close policy, task is not marked done without review/completion rule passing.
- Given a blocker is open and blocking, task cannot be done.
- Given approval sync fails, local approval and sync error both appear in timeline.
- Given evidence is rejected, task remains actionable and rerun path is visible.
- Given raw sensitive payload exists, event stores redacted summary/reference only.

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should event log be append-only at DB level in MVP? | High | Proposed: append-only for audit events, soft correction via superseding events. |
| Which projection is authoritative after conflict: latest Bolt event or human terminal decision? | High | Proposed: human terminal task decisions block further run projections from changing task status, but run timeline still records late events. |
| Should failed run auto-create blocker? | Medium | Accepted: no; create recovery item/attention state unless failure explicitly reports blocker. |
| How long are integration events retained? | High | Defer to data/security spec; proposed 30–90d for dedupe IDs. |
