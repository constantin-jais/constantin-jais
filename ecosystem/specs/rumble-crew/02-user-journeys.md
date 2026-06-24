# User Journeys — rumble-crew

## Scope

This document defines MVP journeys for `rumble-crew`.

The first vertical slice is:

> create/assign task → request Bolt run → observe status → handle blocker/approval → review evidence → mark done or retry/cancel

`rumble-crew` owns the user-facing workflow and task governance. `cos-matic` owns orchestration, runtime execution, gates, and run evidence production.

---

## Journey: Assign a Task to an Agent

### Trigger

A human wants an agent to perform a bounded piece of work with visible status and evidence.

### Actor

Agent Supervisor, Workspace Owner, or delegated Human Contributor.

### Preconditions

- Actor is authenticated and has permission to create or assign tasks.
- Workspace exists.
- At least one `AgentProfile` and compatible `SkillCard` are available.
- Task title, goal, and expected output can be stated.
- `cos-matic` integration is configured if a run will be requested immediately.

### Happy Path

1. Actor opens the board.
2. Actor creates a task with:
   - title;
   - goal/outcome;
   - context;
   - constraints;
   - expected evidence;
   - risk level;
   - optional due date/priority.
3. Actor selects an `AgentProfile`.
4. System shows compatible `SkillCard` options and required permissions/approvals.
5. Actor selects a skill/capability and confirms bounded assignment.
6. System creates `Task` in `assigned` or `ready` state.
7. If required approvals are satisfied, actor requests a Bolt run.
8. System creates `RunRef` with status `queued` and sends a planning/execution request reference to `cos-matic` according to integration contract.
9. Board updates the task card with assignee, skill, status, and latest run state.
10. Timeline records assignment and run request.

### Alternate Paths

- Actor creates the task as human-assigned first, then later assigns an agent.
- Actor saves as draft because required context is missing.
- Actor assigns an agent but does not request a run yet.
- A skill card indicates that human approval is required before run start.

### Failure Paths

- Actor lacks permission to assign agents.
- No compatible skill card exists.
- Required context is missing.
- `cos-matic` is unavailable.
- The run request is rejected by Bolt policy.

### Recovery Path

- Show missing context or permission errors inline.
- Keep the task in `created` or `assigned` state.
- Allow actor to change assignee, add context, request approval, or retry run request.
- If Bolt rejects, store refusal reason and suggested fix in timeline.

### Data Created or Updated

- `Task`
- `TaskAssignment`
- `RunRef` if run requested
- `ActivityEvent`
- optional `Approval` if required before start

### Events Emitted

- `task_created`
- `task_assigned`
- `skill_card_selected`
- `bolt_run_requested`
- `bolt_run_request_failed` if applicable

### Audit Requirements

- Actor ID.
- Task ID.
- Agent profile ID.
- Skill card ID.
- Context snapshot or hash.
- Run request ID and target Bolt reference.
- Approval requirement if any.

### Acceptance Criteria

- Given valid task context and agent assignment permission, when actor assigns an agent, then the task records the selected `AgentProfile` and `SkillCard`.
- Given required context is missing, when actor requests a run, then the system blocks the request and lists missing fields.
- Given `cos-matic` rejects the request, then the task remains visible with failure reason and retry path.
- Given an approval is required before start, then a run cannot enter active execution until approval is granted.

---

## Journey: Agent Reports a Blocker

### Trigger

An agent or runtime cannot proceed because context, permission, approval, input, or external state is missing.

### Actor

Agent Identity via Bolt projection, Runtime Service Account via trusted integration, or Human Contributor manually reporting a blocker.

### Preconditions

- Task exists.
- Task is assigned, ready, in progress, or under review.
- Actor/source is authorized to report blockers for this task.
- If automated, the incoming event is linked to a known `RunRef`.

### Happy Path

1. `cos-matic` or a human submits blocker details:
   - blocker type;
   - summary;
   - required human action;
   - severity;
   - linked run/step if available.
2. System creates `Blocker` in `open` state.
3. System updates task status projection to `blocked` when blocker is active and blocking.
4. Board shows blocked badge and responsible resolver.
5. Timeline records `blocker_reported`.
6. Responsible human receives notification or board attention marker.
7. Human opens task detail and responds with clarification, approval, context, or cancellation.
8. System marks blocker `resolved` or `superseded` when condition is satisfied.
9. If applicable, actor requests rerun/resume through Bolt.

### Alternate Paths

- Blocker is non-blocking and task remains `in_progress` with warning.
- Multiple blockers exist on same task.
- Blocker is converted into an approval request.
- Human marks blocker invalid with rationale.

### Failure Paths

- Incoming blocker references unknown task/run.
- Runtime event is not trusted.
- Blocker lacks actionable description.
- Resolver lacks permission to provide required answer.

### Recovery Path

- Store unlinked event in integration error queue if safe.
- Request more detail from agent/runtime.
- Allow authorized human to edit blocker summary without changing original raw event.
- Escalate to Workspace Owner if no resolver is assigned.

### Data Created or Updated

- `Blocker`
- `Task.status_projection`
- `ActivityEvent`
- optional `Approval`
- optional `CommentThread`

### Events Emitted

- `blocker_reported`
- `task_marked_blocked`
- `blocker_resolved`
- `blocker_superseded`
- `blocker_rejected`

### Audit Requirements

- Reporter actor/source.
- Run reference if automated.
- Original blocker payload or safe hash.
- Human resolver and resolution rationale.
- Timestamp for open and resolution.

### Acceptance Criteria

- Given an authorized blocker event, when it is ingested, then the task shows blocked state and timeline entry.
- Given a blocker requires human input, when a human responds, then the response is recorded and the blocker can be resolved.
- Given an untrusted runtime event, then no task state changes and an integration error is recorded.
- Given all blocking blockers are resolved, then task status can return to previous actionable state or ready-for-rerun.

---

## Journey: Human Approves a Gate

### Trigger

A task or run requires explicit human approval before proceeding.

### Actor

Reviewer / Approver, Workspace Owner, or delegated Agent Supervisor when policy allows.

### Preconditions

- `Approval` exists in `requested` state.
- Approval targets a specific task, run, blocker, or evidence/review gate.
- Actor has permission to approve the target approval type.
- Approval request includes rationale, risk level, requested action, and expiry/timeout if applicable.

### Happy Path

1. Actor receives approval request from board, notification, or task detail.
2. Actor opens approval detail.
3. System displays:
   - requested decision;
   - task context;
   - run reference;
   - risk classification;
   - expected side effects;
   - evidence or prior logs if available.
4. Actor approves with optional conditions or comment.
5. System records `Approval` as `approved` with actor, timestamp, target version, and rationale/conditions.
6. Timeline records `approval_granted`.
7. If the approval unblocks Bolt execution, system sends approval decision to `cos-matic` or marks it available for polling.
8. Task/run projection moves out of `waiting_for_approval` when Bolt acknowledges or next run state arrives.

### Alternate Paths

- Actor rejects approval with reason.
- Actor requests changes or clarification instead of approving.
- Approval expires before decision.
- Approval requires second human for high-risk work.

### Failure Paths

- Actor lacks permission.
- Approval target is stale or superseded.
- Approval request lacks required risk/side-effect details.
- Bolt acknowledgement fails after approval is recorded.

### Recovery Path

- Show permission/staleness errors before allowing decision.
- Require actor to review latest target when stale.
- Keep approval recorded locally and retry synchronization with Bolt.
- If sync fails permanently, mark approval `sync_failed` and show manual recovery action.

### Data Created or Updated

- `Approval`
- `ActivityEvent`
- `RunRef.sync_status`
- optional `Blocker`

### Events Emitted

- `approval_requested`
- `approval_granted`
- `approval_rejected`
- `approval_expired`
- `approval_sync_failed`

### Audit Requirements

- Approver actor ID.
- Approval target and version.
- Decision and rationale.
- Risk level and conditions.
- Sync status with Bolt.

### Acceptance Criteria

- Given a valid approval request and authorized approver, when approval is granted, then decision is recorded and linked to exact target version.
- Given approval target is superseded, when actor attempts to approve, then system blocks or requires explicit acknowledgement.
- Given approval is rejected, then Bolt is not authorized to proceed and task shows rejection reason.
- Given approval sync fails after local record, then the UI shows degraded sync state rather than pretending execution resumed.

---

## Journey: Review Evidence and Complete Task

### Trigger

An agent or human submits evidence claiming the task outcome is complete or reviewable.

### Actor

Reviewer / Approver or Workspace Owner.

### Preconditions

- Task exists.
- Evidence is submitted and linked to task.
- Evidence has type, producer, timestamp, and artifact/log/report reference or inline content.
- Actor has review permission.

### Happy Path

1. Actor opens review queue or task detail.
2. System displays evidence bundle:
   - summary;
   - producer;
   - linked run/reference;
   - artifact references;
   - tests/checks/reports;
   - claimed outcome;
   - known risks or blockers.
3. Actor inspects evidence.
4. Actor accepts evidence as sufficient.
5. System marks evidence `accepted`.
6. If no blocking approval, blocker, or open review remains, actor marks task `done` or system offers the transition.
7. Timeline records `evidence_accepted` and `task_done`.
8. Board moves task to Done.

### Alternate Paths

- Actor rejects evidence with reason and requests changes.
- Actor accepts evidence but leaves task in review because another gate remains.
- Actor marks evidence partially sufficient and creates follow-up task.
- New evidence supersedes older evidence during review.

### Failure Paths

- Evidence artifact is unavailable.
- Evidence is not linked to current run or task.
- Evidence lacks provenance.
- Actor lacks permission.
- Task still has unresolved blockers.

### Recovery Path

- Show unavailable artifact state and allow retry.
- Request evidence resubmission.
- Reject evidence with actionable reason.
- Keep task in `in_review` or `blocked` until all requirements are satisfied.

### Data Created or Updated

- `Evidence.review_status`
- `Task.status`
- `ActivityEvent`
- optional `CommentThread`
- optional follow-up `Task`

### Events Emitted

- `evidence_submitted`
- `evidence_accepted`
- `evidence_rejected`
- `evidence_superseded`
- `task_marked_done`
- `changes_requested`

### Audit Requirements

- Evidence ID and version/reference.
- Reviewer ID.
- Decision and rationale.
- Task status transition.
- Artifact references and integrity metadata if available.

### Acceptance Criteria

- Given sufficient evidence and no blockers, when reviewer accepts evidence, then task can transition to `done`.
- Given evidence is rejected, then task remains actionable and rejection reason is visible.
- Given evidence artifact is unavailable, then reviewer cannot accept it as complete unless policy allows explicit waiver.
- Given newer evidence supersedes old evidence, then old evidence cannot silently close the task.

---

## Journey: Rerun After Failure or Rejected Evidence

### Trigger

A run fails, is cancelled, or produces evidence that is rejected.

### Actor

Agent Supervisor, Workspace Owner, or delegated Human Contributor.

### Preconditions

- Task exists.
- There is a failed/cancelled run or rejected/superseded evidence.
- Actor has permission to request rerun.
- Failure/rejection reason is visible.
- Required approvals are satisfied or requestable.

### Happy Path

1. Actor opens task detail.
2. System shows failed run or rejected evidence with reason.
3. Actor chooses “Request rerun”.
4. Actor optionally edits:
   - context;
   - constraints;
   - selected skill card;
   - expected evidence;
   - retry note.
5. System creates new `RunRef` linked to previous failed/superseded run.
6. System sends rerun request to `cos-matic`.
7. Timeline records `rerun_requested`.
8. Task status returns to `ready` or `in_progress` depending on Bolt acknowledgement and run state.

### Alternate Paths

- Actor cancels task instead of rerun.
- Actor reassigns task to a human.
- Actor changes agent profile or skill card before retry.
- Actor creates follow-up task and marks original failed.

### Failure Paths

- Actor lacks rerun permission.
- Failure reason requires human approval before retry.
- Retry limit is reached.
- Bolt rejects rerun request.
- Task was cancelled or done meanwhile.

### Recovery Path

- Show why rerun is blocked.
- Allow approval request if needed.
- Allow task cancellation or reassignment.
- Preserve rerun draft if Bolt is unavailable.

### Data Created or Updated

- `RunRef`
- `Task.status_projection`
- `ActivityEvent`
- optional `Approval`
- optional `TaskAssignment`

### Events Emitted

- `rerun_requested`
- `rerun_rejected`
- `task_reassigned`
- `task_cancelled`
- `task_marked_failed`

### Audit Requirements

- Actor ID.
- Previous run/evidence reference.
- Rerun reason.
- Changed context/constraints.
- New run reference.

### Acceptance Criteria

- Given a failed run and rerun permission, when actor requests rerun, then new run reference is created and linked to previous attempt.
- Given retry limit is reached, when actor requests rerun, then system blocks or requires approval.
- Given evidence was rejected, then rerun request includes rejection reason in context.
- Given task is cancelled, then no new run can be requested.

---

## Journey: Cancel or Fail a Task

### Trigger

A task should no longer proceed because scope changed, risk is unacceptable, repeated attempts failed, or work is no longer needed.

### Actor

Workspace Owner, Agent Supervisor, or delegated Human Contributor according to policy.

### Preconditions

- Task exists and is not already done/cancelled.
- Actor has permission to cancel/fail task.
- If a run is active, cancellation behavior with Bolt is known.

### Happy Path

1. Actor opens task detail.
2. Actor selects cancel or mark failed.
3. System asks for reason.
4. If active run exists, system sends cancel request to `cos-matic` or records pending cancellation.
5. System updates task status to `cancelled` or `failed` when allowed by policy.
6. Timeline records status change and linked run cancellation status.
7. Board moves task to cancelled/failed lane or archive depending on view configuration.

### Alternate Paths

- Actor cancels only current run but keeps task ready for reassignment.
- Actor marks task failed and creates follow-up task.
- Bolt cannot cancel active run immediately; task shows cancellation pending.

### Failure Paths

- Actor lacks permission.
- Task is already done.
- Active run cannot be cancelled.
- Cancellation sync with Bolt fails.

### Recovery Path

- Show permission/state error.
- Keep task in previous state if cancellation did not apply.
- Mark cancellation as pending when request is sent but not acknowledged.
- Allow owner escalation.

### Data Created or Updated

- `Task.status`
- `RunRef.cancel_status`
- `ActivityEvent`
- optional follow-up `Task`

### Events Emitted

- `task_cancel_requested`
- `run_cancel_requested`
- `run_cancel_acknowledged`
- `task_cancelled`
- `task_marked_failed`

### Audit Requirements

- Actor ID.
- Reason.
- Active run reference if any.
- Bolt cancellation acknowledgement or failure.

### Acceptance Criteria

- Given a task without active run and valid permission, when actor cancels, then task becomes `cancelled` with reason.
- Given active run exists, when actor cancels, then system records both task decision and Bolt cancellation status.
- Given task is done, cancellation is blocked unless reopening policy exists.
- Given cancellation sync fails, UI shows pending/failed sync state.

---

## Shared Capability Candidates Found

| Candidate | From journey | Proposed placement | Status |
| --- | --- | --- | --- |
| Agent task | Assign task / rerun / fail | Bolt owns run lifecycle; Rumble owns task UX/projection | Candidate |
| Approval/gate | Human approves gate | Bolt gate + Rumble approval UX | Candidate |
| Evidence review | Review evidence | Gear artifact/provenance + Rumble review UX | Candidate |
| Blocker | Agent reports blocker | Shared Rumble/Bolt seam | Candidate |
| Runtime reference | Assign/run/cancel | Bolt/Gear integration reference | Candidate |
| Activity timeline | All journeys | Gear event log + Rumble projection | Candidate |
| Skill card | Assign task | Bolt capability registry + Rumble projection | Discuss |
| Rerun request | Rerun after failure | Bolt run semantics + Rumble action | Candidate |
