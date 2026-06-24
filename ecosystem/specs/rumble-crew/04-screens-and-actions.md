# Screens and Actions — rumble-crew

## Scope

This document defines MVP screens and core actions for `rumble-crew`.

The screens must support:

- task creation and assignment;
- agent/run supervision;
- blocker handling;
- approval decisions;
- evidence review;
- rerun/fail/cancel recovery;
- timeline/audit inspection.

They must not implement generic project management or runtime orchestration.

---

## Screen: Board

### Purpose

Show the operational state of tasks and the next human action needed.

### Route / Entry Point

`/workspaces/:workspace_id/board`

### Allowed Roles

- Workspace Owner
- Human Contributor
- Reviewer / Approver
- Agent Supervisor
- Observer / Auditor, read-only

### Displayed Data

- Board columns.
- Task cards.
- Task status.
- Assignee and assignee type.
- Agent profile and skill card if applicable.
- Latest run status.
- Blocker count and severity.
- Pending approval count/type.
- Evidence review state.
- Risk level.
- Last activity timestamp.

### Actions by Role

| Action | Owner | Contributor | Reviewer | Agent Supervisor | Observer |
| --- | --- | --- | --- | --- | --- |
| Create task | Yes | Yes | No | Yes | No |
| Open task | Yes | Yes | Yes | Yes | Yes |
| Assign task | Yes | Limited | No | Yes | No |
| Request run | Yes | If delegated | No | Yes | No |
| Open approval | Yes | View if involved | Yes | Yes | View only |
| Open evidence review | Yes | View if involved | Yes | Yes | View only |
| Cancel task | Yes | Own if policy allows | No | Yes | No |
| Filter/search | Yes | Yes | Yes | Yes | Yes |

### Empty State

Explain the agentic task loop and provide “Create task” for authorized users.

### Loading State

Show skeleton columns and cards. Preserve current filters.

### Error State

Show board load error with retry. Do not hide cached/stale tasks if available.

### Offline State

Show last known board with stale marker if local cache exists. Disable run/approval sync actions.

### Permission Denied State

Show no task data unless workspace existence is allowed to be disclosed.

### Accessibility Notes

- Cards must be keyboard reachable.
- Status/risk cannot rely on color alone.
- Drag/drop must have accessible alternatives.

### Telemetry / Events

- `board_opened`
- `board_filter_changed`
- `task_card_opened`

### Service Calls

- `GET /workspaces/{workspace_id}/board`
- `GET /workspaces/{workspace_id}/tasks?filters=...`
- `POST /workspaces/{workspace_id}/tasks`
- `POST /tasks/{task_id}/assignments`
- `POST /tasks/{task_id}/run-requests`

### Acceptance Criteria

- Given tasks exist, board cards show task status and latest run status separately.
- Given a task has pending approval, board shows approval badge and review entry.
- Given Bolt sync is stale, board shows stale run state, not fabricated progress.
- Given observer role, board actions are read-only.

---

## Screen: Task Detail

### Purpose

Provide the canonical workspace page for one task: context, assignment, blockers, approvals, evidence, comments, timeline, and next action.

### Route / Entry Point

`/workspaces/:workspace_id/tasks/:task_id`

### Allowed Roles

- Workspace Owner
- Human Contributor with access
- Reviewer / Approver with access
- Agent Supervisor
- Observer / Auditor, read-only

### Displayed Data

- Task title, goal, description, constraints.
- Task status and risk level.
- Assignment history.
- Current assignee.
- Selected agent profile and skill card.
- Latest/current run summary.
- Blockers.
- Approval requests and decisions.
- Evidence bundle.
- Comments.
- Timeline slice.
- Primary next action.

### Actions by Role

| Action | Owner | Contributor | Reviewer | Agent Supervisor | Observer |
| --- | --- | --- | --- | --- | --- |
| Edit task context | Yes | Own/assigned | No | Yes | No |
| Assign/reassign | Yes | Request | No | Yes | No |
| Request run | Yes | If delegated | No | Yes | No |
| Report blocker | Yes | Yes | Yes | Yes | No |
| Resolve blocker | Yes | Own/assigned | Review blockers | Yes | No |
| Request approval | Yes | Yes | No | Yes | No |
| Approve/reject | Yes | No | Yes | If policy | No |
| Submit evidence | Yes | Yes | No | No | No |
| Review evidence | Yes | No | Yes | If policy | No |
| Request rerun | Yes | Request | Request | Yes | No |
| Mark failed/cancelled | Yes | Own if policy | No | Yes | No |
| Comment | Yes | Yes | Yes | Yes | No |

### Empty State

If task is newly created, prompt to add context and assign.

### Loading State

Load header first, then sections. Mark partial sections loading.

### Error State

Show section-level errors when possible. Preserve other loaded sections.

### Offline State

Allow reading cached data. Disable run requests, approvals, evidence acceptance, and cancellation sync.

### Permission Denied State

Show “You cannot access this task” without leaking sensitive details.

### Accessibility Notes

- Primary next action must be reachable by keyboard.
- Timeline events need semantic grouping.
- Approval/evidence decisions require clear labels and confirmation.

### Telemetry / Events

- `task_detail_opened`
- `task_primary_action_clicked`
- `task_section_opened`

### Service Calls

- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `POST /tasks/{task_id}/assignments`
- `POST /tasks/{task_id}/run-requests`
- `POST /tasks/{task_id}/blockers`
- `POST /tasks/{task_id}/approvals`
- `POST /tasks/{task_id}/evidence`
- `GET /tasks/{task_id}/timeline`

### Acceptance Criteria

- Given a task has latest run succeeded, task detail shows task `in_review` until evidence accepted.
- Given open blocking blocker exists, done action is disabled.
- Given a user lacks approval permission, approve/reject controls are hidden or disabled with reason.
- Given a task has multiple runs, current run and previous attempts are distinguishable.

---

## Screen: Create / Edit Task

### Purpose

Capture bounded task intent, expected evidence, risk, assignment, and constraints.

### Route / Entry Point

- Modal from board: `/workspaces/:workspace_id/board?action=create-task`
- Full route optional: `/workspaces/:workspace_id/tasks/new`

### Allowed Roles

- Workspace Owner
- Human Contributor
- Agent Supervisor

### Displayed Data

- Title.
- Goal/outcome.
- Description/context.
- Constraints.
- Expected evidence.
- Risk level.
- Assignee selector.
- Agent profile selector.
- Skill card selector.
- Required approvals preview.

### Actions by Role

| Action | Owner | Contributor | Agent Supervisor |
| --- | --- | --- | --- |
| Save draft task | Yes | Yes | Yes |
| Create task | Yes | Yes | Yes |
| Select agent profile | Yes | Request/if allowed | Yes |
| Select skill card | Yes | Request/if allowed | Yes |
| Request run immediately | Yes | If delegated | Yes |

### Empty State

No empty state; form starts blank with examples/placeholders.

### Loading State

Load agent/skill options progressively.

### Error State

Inline validation errors for required fields and compatibility.

### Offline State

May save local draft if supported; cannot request run.

### Permission Denied State

Hide entry point or show no create permission.

### Accessibility Notes

- Form labels and validation errors must be programmatically associated.
- Risk and approval preview must be text-readable.

### Telemetry / Events

- `task_create_opened`
- `task_create_submitted`
- `task_create_validation_failed`

### Service Calls

- `GET /workspaces/{workspace_id}/agent-profiles`
- `GET /workspaces/{workspace_id}/skill-cards`
- `POST /workspaces/{workspace_id}/tasks`
- `POST /tasks/{task_id}/assignments`
- `POST /tasks/{task_id}/run-requests`

### Acceptance Criteria

- Given title and goal are missing, create is blocked.
- Given agent assignment selected, compatible skill card is required if policy requires it.
- Given start approval is required, immediate run request creates/request approval instead of active run.
- Given Bolt unavailable, task can be created but run request is blocked or queued only if policy permits.

---

## Screen: Review Queue

### Purpose

Centralize items requiring human decision: approvals, evidence, blockers, failed runs.

### Route / Entry Point

`/workspaces/:workspace_id/review`

### Allowed Roles

- Workspace Owner
- Reviewer / Approver
- Agent Supervisor
- Human Contributor, limited to own/requested items
- Observer / Auditor, read-only if allowed

### Displayed Data

- Pending approvals.
- Submitted evidence.
- Blocking blockers requiring human input.
- Failed runs awaiting recovery decision.
- Risk level.
- Age/staleness.
- Target task and assignee.

### Actions by Role

| Action | Owner | Reviewer | Agent Supervisor | Contributor | Observer |
| --- | --- | --- | --- | --- | --- |
| Open review item | Yes | Yes | Yes | Limited | Yes |
| Approve/reject gate | Yes | Yes | If policy | No | No |
| Accept/reject evidence | Yes | Yes | If policy | No | No |
| Resolve blocker | Yes | If assigned | Yes | Own/assigned | No |
| Request rerun | Yes | Request | Yes | Request | No |
| Cancel/fail task | Yes | No | Yes | Limited | No |

### Empty State

“No human decisions needed.” Provide link back to board.

### Loading State

Show queue skeleton grouped by decision type.

### Error State

Show queue load error with retry. If partial, show loaded sections.

### Offline State

Read-only cached queue. Decisions disabled.

### Permission Denied State

Show no review access.

### Accessibility Notes

- Queue sections need headings.
- Risk/age sorting must be clear to screen readers.

### Telemetry / Events

- `review_queue_opened`
- `review_item_opened`
- `review_queue_filter_changed`

### Service Calls

- `GET /workspaces/{workspace_id}/review-queue`
- `POST /approvals/{approval_id}/decision`
- `POST /evidence/{evidence_id}/review`
- `POST /blockers/{blocker_id}/resolution`
- `POST /tasks/{task_id}/rerun-requests`

### Acceptance Criteria

- Given pending approval exists, it appears in Review Queue with task and target reference.
- Given evidence is submitted, it appears separately from approvals.
- Given user has no decision permission, item is visible read-only only if access policy allows.
- Given queue item is stale/superseded, decision controls require explicit refresh/acknowledgement.

---

## Screen: Approval Detail

### Purpose

Allow an authorized human to approve, reject, or request clarification for one gate.

### Route / Entry Point

`/workspaces/:workspace_id/approvals/:approval_id`

### Allowed Roles

- Workspace Owner
- Reviewer / Approver
- Agent Supervisor if policy permits
- Observer / Auditor read-only

### Displayed Data

- Approval type: start, scope, risk, completion.
- Request summary.
- Target task/run/evidence/blocker.
- Target version/staleness.
- Risk level.
- Requested by.
- Expected side effects.
- Conditions.
- Expiry.
- Related timeline events.

### Actions by Role

| Action | Owner | Reviewer | Agent Supervisor | Observer |
| --- | --- | --- | --- | --- |
| Approve | Yes | Yes | If policy | No |
| Reject | Yes | Yes | If policy | No |
| Request clarification | Yes | Yes | Yes | No |
| Open task/run | Yes | Yes | Yes | Yes |

### Empty State

Not applicable; missing approval shows 404/permission state.

### Loading State

Show approval summary skeleton.

### Error State

Show load/sync error. Decision controls disabled if target cannot be verified.

### Offline State

Read-only. Cannot approve/reject offline in MVP.

### Permission Denied State

Show “You cannot decide this approval.”

### Accessibility Notes

- Approve/reject are distinct buttons with confirmation for high/critical risk.
- Conditions field must be labelled.

### Telemetry / Events

- `approval_detail_opened`
- `approval_decision_submitted`
- `approval_decision_failed`

### Service Calls

- `GET /approvals/{approval_id}`
- `POST /approvals/{approval_id}/decision`
- `POST /approvals/{approval_id}/clarification-request`

### Acceptance Criteria

- Given approval target is superseded, approve is blocked or requires explicit acknowledgement.
- Given rejection, reason is required.
- Given high-risk approval, policy-required confirmation is enforced.
- Given approval sync to Bolt fails, approval shows `sync_failed` and task/run state does not pretend continuation.

---

## Screen: Evidence Review

### Purpose

Allow reviewers to inspect submitted evidence and accept/reject it against task expectations.

### Route / Entry Point

`/workspaces/:workspace_id/evidence/:evidence_id`

### Allowed Roles

- Workspace Owner
- Reviewer / Approver
- Agent Supervisor if policy permits
- Observer / Auditor read-only

### Displayed Data

- Evidence type.
- Summary.
- Producing actor.
- Linked task.
- Linked run.
- Artifact reference and availability.
- Content hash/integrity metadata if available.
- Expected evidence from task.
- Prior evidence and supersession status.
- Review history.

### Actions by Role

| Action | Owner | Reviewer | Agent Supervisor | Observer |
| --- | --- | --- | --- | --- |
| Accept evidence | Yes | Yes | If policy | No |
| Reject evidence | Yes | Yes | If policy | No |
| Request changes | Yes | Yes | Yes | No |
| Open artifact | Yes | Yes | Yes | If allowed |
| Mark task done | Yes | If policy | If policy | No |
| Request rerun | Yes | Request | Yes | No |

### Empty State

Not applicable; missing evidence shows 404/permission state.

### Loading State

Show metadata first, artifact preview second.

### Error State

If artifact unavailable, show metadata and block acceptance unless waiver/policy permits.

### Offline State

Read-only cached metadata. No acceptance/rejection.

### Permission Denied State

Show no access or redacted metadata depending on policy.

### Accessibility Notes

- Artifact preview must have text fallback/metadata.
- Accept/reject confirmations must be clear.

### Telemetry / Events

- `evidence_review_opened`
- `evidence_decision_submitted`
- `evidence_artifact_opened`

### Service Calls

- `GET /evidence/{evidence_id}`
- `POST /evidence/{evidence_id}/review`
- `POST /tasks/{task_id}/complete`
- `POST /tasks/{task_id}/rerun-requests`

### Acceptance Criteria

- Given evidence lacks provenance/reference, acceptance is blocked or requires explicit completion approval.
- Given evidence is rejected, reason is required and task remains actionable.
- Given evidence accepted and no blockers/approvals remain, task can transition to done.
- Given evidence is superseded, acceptance requires explicit acknowledgement or is blocked by policy.

---

## Screen: Run Detail

### Purpose

Inspect one Bolt run projection and its relationship to task state, approvals, evidence, and failure recovery.

### Route / Entry Point

`/workspaces/:workspace_id/runs/:run_ref_id`

### Allowed Roles

- Workspace Owner
- Agent Supervisor
- Reviewer / Approver with access
- Human Contributor with task access
- Observer / Auditor read-only if allowed

### Displayed Data

- Local `RunRef` ID.
- External Bolt run ID if visible.
- Provider: `cos-matic`.
- Runtime reference safe label.
- Run status.
- Sync status/staleness.
- Attempt number.
- Requested by.
- Request payload hash.
- Linked previous run.
- Gate requests.
- Evidence produced.
- Failure context.
- Safe log/artifact references.

### Actions by Role

| Action | Owner | Agent Supervisor | Reviewer | Contributor | Observer |
| --- | --- | --- | --- | --- | --- |
| Open linked task | Yes | Yes | Yes | Yes | Yes |
| Approve/reject gate | Yes | If policy | Yes | No | No |
| Request cancel | Yes | Yes | No | Own if policy | No |
| Request rerun | Yes | Yes | Request | Request | No |
| Open evidence | Yes | Yes | Yes | If allowed | If allowed |
| Retry sync | Yes | Yes | No | No | No |

### Empty State

If run ref missing, show not found/permission state.

### Loading State

Show run summary first; lazy-load evidence/log references.

### Error State

If Bolt sync fails, show last known run status and sync error.

### Offline State

Read-only cached projection.

### Permission Denied State

Show redacted run reference if task existence can be disclosed; otherwise no access.

### Accessibility Notes

- Status history must be screen-reader navigable.
- Failure context must be readable text, not only raw log blocks.

### Telemetry / Events

- `run_detail_opened`
- `run_cancel_requested`
- `run_sync_retry_requested`

### Service Calls

- `GET /runs/{run_ref_id}`
- `POST /runs/{run_ref_id}/cancel-request`
- `POST /runs/{run_ref_id}/sync-retry`
- `POST /tasks/{task_id}/rerun-requests`

### Acceptance Criteria

- Given run succeeded without eligible completion policy, screen does not mark task done automatically.
- Given run succeeded with eligible low-risk auto-close policy, screen shows done state and auto-close audit reason.
- Given run failed, failure context and recovery actions are visible to authorized users.
- Given runtime logs contain sensitive data, default view shows summaries/redacted refs; privileged raw access is available only when enabled and audited.
- Given Bolt is unavailable, screen shows stale state.

---

## Screen: Agents & Skills

### Purpose

Show available agent profiles and skill cards for safe assignment.

### Route / Entry Point

`/workspaces/:workspace_id/agents-skills`

### Allowed Roles

- Workspace Owner
- Agent Supervisor
- Human Contributor, read/select depending on policy
- Reviewer / Approver, read
- Observer / Auditor, read if allowed

### Displayed Data

- Agent profiles.
- Agent status.
- Runtime reference safe label.
- Compatible skill cards.
- Skill input requirements.
- Skill output expectations.
- Required approvals.
- Required permissions.
- Risk notes.
- Last synced timestamp if sourced from Bolt.

### Actions by Role

| Action | Owner | Agent Supervisor | Contributor | Reviewer | Observer |
| --- | --- | --- | --- | --- | --- |
| View agent profile | Yes | Yes | Yes | Yes | If allowed |
| View skill card | Yes | Yes | Yes | Yes | If allowed |
| Create local skill card | Yes | Yes | No | No | No |
| Disable skill card | Yes | Yes | No | No | No |
| Sync from Bolt | Yes | Yes | No | No | No |
| Start task from skill | Yes | Yes | Request/if allowed | No | No |

### Empty State

Prompt authorized users to add a local skill card or sync capabilities from `cos-matic`.

### Loading State

Show cards skeleton and integration sync status.

### Error State

Show sync failure without deleting existing local cards.

### Offline State

Read cached cards; cannot sync.

### Permission Denied State

Hide restricted skill details and runtime refs.

### Accessibility Notes

- Cards must have structured headings.
- Risk/approval requirements must be textual.

### Telemetry / Events

- `agents_skills_opened`
- `skill_card_opened`
- `agent_profile_opened`
- `bolt_capability_sync_requested`

### Service Calls

- `GET /workspaces/{workspace_id}/agent-profiles`
- `GET /workspaces/{workspace_id}/skill-cards`
- `POST /workspaces/{workspace_id}/skill-cards`
- `PATCH /skill-cards/{skill_card_id}`
- `POST /workspaces/{workspace_id}/integrations/cos-matic/sync-capabilities`

### Acceptance Criteria

- Given no skill cards exist, user sees clear setup path.
- Given skill card is disabled, it cannot be selected for new assignments.
- Given runtime ref is unavailable, related skill cards show warning before assignment.
- Given contributor lacks permission, start-task action is request-only or hidden.

---

## Screen: Timeline / Audit

### Purpose

Provide human-readable audit history across workspace, task, run, review, and evidence events.

### Route / Entry Point

- Workspace: `/workspaces/:workspace_id/timeline`
- Task slice: `/workspaces/:workspace_id/tasks/:task_id/timeline`

### Allowed Roles

- Workspace Owner
- Human Contributor with access
- Reviewer / Approver with access
- Agent Supervisor
- Observer / Auditor

### Displayed Data

- Activity events.
- Event type.
- Actor.
- Source: Rumble, `cos-matic`, Wrench, Gear, system.
- Target object.
- Timestamp.
- Safe payload summary.
- Integrity hash/reference if available.
- Redaction markers.

### Actions by Role

| Action | Owner | Contributor | Reviewer | Agent Supervisor | Observer |
| --- | --- | --- | --- | --- | --- |
| Filter timeline | Yes | Yes | Yes | Yes | Yes |
| Open event target | Yes | Yes | Yes | Yes | Yes |
| Export audit | Yes | No | If granted | No | If granted |
| Retry failed sync event | Yes | No | No | Yes | No |

### Empty State

“No activity yet.”

### Loading State

Show chronological skeleton.

### Error State

Show partial timeline with failed-page marker if pagination fails.

### Offline State

Show cached events with stale marker.

### Permission Denied State

Show no timeline access.

### Accessibility Notes

- Timeline must support chronological keyboard navigation.
- Event categories must not rely on color alone.

### Telemetry / Events

- `timeline_opened`
- `timeline_filter_changed`
- `audit_export_requested`

### Service Calls

- `GET /workspaces/{workspace_id}/timeline`
- `GET /tasks/{task_id}/timeline`
- `POST /workspaces/{workspace_id}/audit-exports`

### Acceptance Criteria

- Given task events exist, timeline shows actor, source, event type, and timestamp.
- Given event payload is redacted, redaction is explicit.
- Given export permission is absent, export action is unavailable.
- Given integration events are replayed, timeline does not duplicate idempotent events.

---

## Screen: Settings — Members, Policy, Integrations

### Purpose

Configure minimal workspace governance required for MVP.

### Route / Entry Point

`/workspaces/:workspace_id/settings`

### Allowed Roles

- Workspace Owner, full access
- Agent Supervisor, integration read/sync if granted
- Observer / Auditor, read-only if granted

### Displayed Data

- Members and roles.
- Approval policy:
  - start;
  - scope;
  - risk;
  - completion.
- Bolt integration status.
- Runtime refs.
- Audit/data retention summary.

### Actions by Role

| Action | Owner | Agent Supervisor | Observer |
| --- | --- | --- | --- |
| Invite/remove member | Yes | No | No |
| Change role | Yes | No | No |
| Update approval policy | Yes | No | No |
| View integration status | Yes | Yes | If granted |
| Register/update safe RuntimeRef | Yes | If granted | No |
| Request capability sync | Yes | Yes | No |
| Request audit export | Yes | No | If granted |

### Empty State

Settings has no global empty state; missing integration shows setup guidance.

### Loading State

Load settings sections independently.

### Error State

Show section-level errors and avoid applying partial policy changes silently.

### Offline State

Read-only cached settings.

### Permission Denied State

Show no settings access or read-only limited view.

### Accessibility Notes

- Role changes require confirmation.
- Policy toggles must have explicit labels and descriptions.

### Telemetry / Events

- `settings_opened`
- `member_role_changed`
- `approval_policy_updated`
- `integration_status_checked`

### Service Calls

- `GET /workspaces/{workspace_id}/settings`
- `POST /workspaces/{workspace_id}/members`
- `PATCH /workspace-members/{member_id}`
- `PATCH /workspaces/{workspace_id}/approval-policy`
- `GET /workspaces/{workspace_id}/integrations/cos-matic/status`
- `POST /workspaces/{workspace_id}/runtime-refs`

### Acceptance Criteria

- Given non-owner opens settings, restricted sections are hidden/read-only according to role.
- Given policy update fails, previous policy remains active.
- Given last owner removal is attempted, action is blocked.
- Given integration unavailable, status is visible without exposing secrets.

---

# Core Actions

## Action: Create Task

### Actor

Workspace Owner, Human Contributor, Agent Supervisor.

### Intent

Create a bounded unit of work with clear goal and expected evidence.

### Input

- title;
- goal;
- description/context;
- constraints;
- expected evidence;
- risk level;
- optional assignee/skill card.

### Preconditions

- Actor can create tasks.
- Workspace is active.

### Business Rules

- Title and goal are required.
- Expected evidence is strongly recommended; may be required by policy for agent-assigned tasks.
- Agent assignment requires compatible skill card if configured.

### Validation Rules

- Title non-empty and within length limit.
- Risk level valid.
- Referenced agent/skill exists and is active.

### Side Effects

- Creates `Task`.
- Optionally creates `TaskAssignment`.
- Records activity event.

### Events Emitted

- `task_created`
- `task_assigned` if applicable

### Audit Log

Actor, task ID, initial fields, assignment, timestamp.

### Permission Check

`task:create`.

### Idempotency

Client may provide idempotency key to avoid duplicate task creation.

### Rollback / Retry

If assignment fails after task creation, task remains created with warning and can be assigned later.

### Errors

- permission denied;
- validation failed;
- workspace archived;
- agent/skill unavailable.

### Acceptance Criteria

- Valid request creates task in `created` or `assigned` state.
- Invalid agent assignment does not create hidden run.

---

## Action: Request Bolt Run

### Actor

Workspace Owner, Agent Supervisor, delegated Human Contributor.

### Intent

Ask Bolt/`cos-matic` to execute or prepare execution for an agent-assigned task.

### Input

- task ID;
- assignment ID;
- selected skill card;
- context snapshot/hash;
- execution constraints;
- idempotency key.

### Preconditions

- Task exists and is assigned to agent profile.
- Required context is present.
- Required start/scope/risk approvals are satisfied or requestable.
- `cos-matic` integration is configured.

### Business Rules

- Rumble creates a request; Bolt owns planning/execution.
- If approval is required, create approval instead of active run unless already approved.
- Only one current active run per task in MVP.

### Validation Rules

- Task not done/cancelled.
- Skill card active.
- RuntimeRef available or queue policy permits unknown runtime.
- Actor has run request permission.

### Side Effects

- Creates `RunRef` or `Approval`.
- Sends request to `cos-matic` when allowed.
- Records activity event.

### Events Emitted

- `bolt_run_requested`
- `approval_requested` if gated
- `bolt_run_request_failed` if failed

### Audit Log

Actor, task, assignment, payload hash, Bolt target, response.

### Permission Check

`run:request`.

### Idempotency

Required. Repeated request with same key returns same `RunRef`/request result.

### Rollback / Retry

If Bolt call fails, preserve run request draft/failure context for retry.

### Errors

- missing context;
- approval required;
- active run exists;
- Bolt unavailable;
- Bolt rejected request.

### Acceptance Criteria

- Run request never executes through Rumble directly.
- If active run exists, duplicate run is blocked.
- If Bolt unavailable, task state remains honest and recoverable.

---

## Action: Decide Approval

### Actor

Workspace Owner, Reviewer / Approver, policy-authorized Agent Supervisor.

### Intent

Approve or reject a gate with human accountability.

### Input

- approval ID;
- decision: approve/reject;
- reason;
- optional conditions;
- target version acknowledgement.

### Preconditions

- Approval exists and is requested.
- Actor can decide this approval type.
- Target is not stale or actor acknowledges latest target.

### Business Rules

- Agent/runtime/system actors cannot approve.
- Rejection requires reason.
- High-risk approval requires policy confirmation.
- Execution-affecting approvals must sync to Bolt.

### Validation Rules

- Decision valid.
- Reason required for rejection and high-risk approval.
- Approval not expired/superseded.

### Side Effects

- Updates `Approval`.
- Records activity.
- Sends decision to Bolt if required.
- May unblock blocker/run projection after Bolt acknowledgement.

### Events Emitted

- `approval_granted`
- `approval_rejected`
- `approval_sync_failed`

### Audit Log

Approver, decision, target version, reason, conditions, sync status.

### Permission Check

`approval:decide`.

### Idempotency

Decision submission should be idempotent for same actor/decision/target version.

### Rollback / Retry

Local approval decision is immutable; sync to Bolt may retry. Reversal requires new superseding approval flow.

### Errors

- permission denied;
- stale target;
- approval expired;
- sync failed.

### Acceptance Criteria

- Human-only approval enforced.
- Stale target cannot be silently approved.
- Sync failure is visible.

---

## Action: Review Evidence

### Actor

Workspace Owner, Reviewer / Approver, policy-authorized Agent Supervisor.

### Intent

Accept or reject evidence against the task goal and expected evidence.

### Input

- evidence ID;
- decision: accept/reject;
- reason;
- optional “mark task done” flag.

### Preconditions

- Evidence exists and is submitted.
- Actor has review permission.
- Evidence target is not superseded unless acknowledged.

### Business Rules

- Rejection requires reason.
- Acceptance requires artifact/provenance availability unless policy allows exception.
- Task moves to done only if no blocking blockers/approvals remain.

### Validation Rules

- Decision valid.
- Evidence not already accepted/rejected unless idempotent repeat.
- Actor not prohibited by separation-of-duty policy.

### Side Effects

- Updates evidence review status.
- May update task status to `done` or leave in `in_review`.
- Records activity event.

### Events Emitted

- `evidence_accepted`
- `evidence_rejected`
- `task_marked_done` if applicable

### Audit Log

Reviewer, evidence ID, decision, reason, artifact reference/hash.

### Permission Check

`evidence:review`.

### Idempotency

Same decision for same evidence version returns same result.

### Rollback / Retry

Evidence review is not silently mutated. Correction requires superseding evidence or owner-controlled review correction event.

### Errors

- evidence unavailable;
- permission denied;
- blocker remains;
- stale/superseded evidence.

### Acceptance Criteria

- Run success alone does not mark task done.
- Rejected evidence keeps task actionable.
- Accepted evidence closes task only when completion rules pass.

---

## Action: Report / Resolve Blocker

### Actor

Human Contributor, Agent Supervisor, Reviewer, Workspace Owner, Agent/Runtime via trusted projection.

### Intent

Record a condition blocking progress and resolve it with accountable action.

### Input

For report:

- blocker type;
- severity;
- summary;
- details;
- resolver.

For resolution:

- resolution action;
- reason/comment;
- optional linked approval/evidence/run.

### Preconditions

- Task exists.
- Reporter/resolver authorized.

### Business Rules

- Blocking open blockers prevent task done.
- Automated blockers preserve source attribution.
- Resolution requires rationale.

### Validation Rules

- Summary required.
- Severity valid.
- Resolver valid if set.

### Side Effects

- Creates/updates `Blocker`.
- May update task status projection.
- Records activity.

### Events Emitted

- `blocker_reported`
- `task_marked_blocked`
- `blocker_resolved`
- `blocker_rejected`

### Audit Log

Reporter/resolver, blocker state, rationale, linked objects.

### Permission Check

`blocker:report` / `blocker:resolve`.

### Idempotency

Integration-reported blockers require source event ID to avoid duplicates.

### Rollback / Retry

Incorrect blocker can be rejected/superseded; original record remains.

### Errors

- invalid source;
- missing summary;
- permission denied;
- task closed.

### Acceptance Criteria

- Open blocking blocker prevents done.
- Resolved blocker appears in timeline.
- Untrusted runtime blocker does not change task state.

---

## Action: Request Rerun

### Actor

Workspace Owner, Agent Supervisor, delegated Human Contributor, Reviewer as request-only if policy.

### Intent

Start a new run attempt after failure, rejected evidence, or changed context.

### Input

- task ID;
- previous run/evidence reference;
- rerun reason;
- updated context/constraints;
- idempotency key.

### Preconditions

- Task not done/cancelled.
- Previous run failed/cancelled or evidence rejected/superseded, or explicit policy allows rerun.
- Actor has permission.
- Retry limits/approvals satisfied.

### Business Rules

- Rerun creates new `RunRef` linked to previous attempt.
- Rejected evidence reason should be included in rerun context.
- Active run blocks rerun unless cancelled/superseded.

### Validation Rules

- Reason required.
- Previous reference exists.
- Skill/agent still active or replacement selected.

### Side Effects

- Creates `RunRef`.
- Sends request to Bolt.
- Records activity.

### Events Emitted

- `rerun_requested`
- `bolt_run_requested`
- `rerun_rejected`

### Audit Log

Actor, previous attempt, reason, changed context, new run ref.

### Permission Check

`run:rerun`.

### Idempotency

Required idempotency key.

### Rollback / Retry

If Bolt unavailable, keep rerun draft/failure for retry.

### Errors

- retry limit reached;
- active run exists;
- permission denied;
- Bolt rejected request.

### Acceptance Criteria

- Rerun lineage is visible.
- Duplicate rerun requests are not created from retry.
- Rerun cannot occur after cancellation unless task is explicitly reopened by policy.

---

## Action: Cancel / Fail Task

### Actor

Workspace Owner, Agent Supervisor, delegated Human Contributor for own tasks if policy.

### Intent

Stop work or mark it unsuccessful with a reason.

### Input

- task ID;
- action: cancel/fail;
- reason;
- active run cancellation preference.

### Preconditions

- Task not done/cancelled.
- Actor has permission.

### Business Rules

- Reason required.
- Active run cancellation must be requested through Bolt.
- Cancellation does not delete evidence/history.

### Validation Rules

- Valid state transition.
- Actor authorized.
- Active run state known or acknowledged stale.

### Side Effects

- Updates task status.
- Sends cancel request to Bolt if active run exists.
- Records activity.

### Events Emitted

- `task_cancel_requested`
- `run_cancel_requested`
- `task_cancelled`
- `task_marked_failed`

### Audit Log

Actor, reason, previous status, active run reference, sync status.

### Permission Check

`task:cancel` / `task:fail`.

### Idempotency

Repeated cancel/fail for same task returns existing terminal state.

### Rollback / Retry

Reopening terminal tasks is post-MVP or owner-only explicit policy.

### Errors

- task already done/cancelled;
- permission denied;
- Bolt cancellation sync failed;
- invalid transition.

### Acceptance Criteria

- Terminal transition requires human reason.
- Active run cancellation status is visible.
- History remains inspectable.
