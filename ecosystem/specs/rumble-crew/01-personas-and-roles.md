# Personas and Roles — rumble-crew

## Scope

This document defines the MVP personas and roles for `rumble-crew`.

`rumble-crew` is an agentic teamwork workspace. Its roles must support one core loop:

> assign work → observe execution → resolve blockers → approve gates → review evidence → close or retry

The product must distinguish:

- human collaboration roles;
- agent identities visible in the workspace;
- runtime/service identities used by `cos-matic` or other Bolt components;
- system actions used for audit, projections, and state synchronization.

---

## Personas

### Persona: Agent Supervisor

#### Goal

Coordinate agentic work safely without manually reconstructing task state from logs, chats, and execution tools.

#### Motivations

- Know which work is assigned, running, blocked, or waiting for review.
- Understand when a human decision is needed.
- Compare claimed progress with evidence.
- Avoid giving agents unbounded or ambiguous work.

#### Pain Points

- Execution state is scattered across terminals, CI, issue trackers, and chat.
- Agent failures often lack a clear recovery path.
- Approvals and blockers are not connected to the task they affect.
- It is unclear which runtime identity performed an action.

#### Success Condition

The supervisor can see every active agent task, approve or reject gates, inspect evidence, and decide done/retry/cancel from one workspace.

---

### Persona: Human Contributor

#### Goal

Collaborate with agents and other humans on concrete tasks while keeping ownership and accountability clear.

#### Motivations

- Delegate bounded work to agents.
- Add context or clarification when an agent is blocked.
- Take over tasks when automation is inappropriate.
- Keep personal workload visible to the team.

#### Pain Points

- Agents may ask for clarification outside the task context.
- Human and agent work are often represented in incompatible systems.
- Task status may say “in progress” without showing who or what is actually running.

#### Success Condition

The contributor can create, claim, comment on, and complete tasks while seeing agent work with the same collaboration vocabulary.

---

### Persona: Reviewer / Approver

#### Goal

Protect quality, safety, and scope by reviewing task outputs and granting explicit approvals where required.

#### Motivations

- Review evidence before work is considered complete.
- Approve risky actions before execution proceeds.
- Reject insufficient outputs with actionable reasons.
- Maintain an audit trail of decisions.

#### Pain Points

- Approvals are easy to lose in chat.
- Evidence is often incomplete, unverifiable, or detached from the task.
- Reviewers may accidentally approve the wrong run or stale output.

#### Success Condition

The reviewer can approve or reject the exact requested gate or evidence bundle tied to a task/run version.

---

### Persona: Auditor / Observer

#### Goal

Understand what happened, who acted, which runtime was used, and why a task ended in a given state.

#### Motivations

- Inspect decision and execution history.
- Verify that required human approvals happened.
- Trace evidence to artifacts, logs, test reports, or inspection reports.
- Detect boundary leaks between product UX and orchestration.

#### Pain Points

- Execution histories are incomplete or too technical.
- Human decisions and automated actions are mixed without clear attribution.
- Evidence retention and provenance are unclear.

#### Success Condition

The auditor can read a task timeline and reconstruct the full collaboration and execution story without requiring runtime access.

---

### Persona: Agent Operator

#### Goal

Expose available agents/capabilities to humans and route work through the correct Bolt runtime without making `rumble-crew` the orchestrator.

#### Motivations

- Make skills understandable to non-runtime users.
- Ensure task requests have enough context.
- Keep runtime identity, permissions, and evidence expectations explicit.
- Avoid direct, unsafe execution from the product UI.

#### Pain Points

- Users may assign work to an agent without knowing its limits.
- Runtime credentials and product user identity are often confused.
- Capability descriptions drift from what the runtime can actually do.

#### Success Condition

The operator can maintain clear `SkillCard`, `AgentProfile`, and `RuntimeRef` records that guide assignment while Bolt owns execution.

---

## Roles

### Role: Workspace Owner

#### Goal

Own workspace settings, membership, governance rules, and final accountability for agentic work.

#### Permissions

- Create, rename, archive, and configure a workspace.
- Invite/remove members.
- Assign roles.
- Configure board columns and approval policies.
- Create and edit all tasks.
- Assign tasks to humans or agent profiles.
- Accept or reject completion evidence.
- Cancel tasks.
- Export task history and audit data.

#### Visible Data

- All boards, tasks, blockers, approvals, evidence, comments, activity events, agent profiles, skill cards, and runtime references available to the workspace.

#### Editable Data

- Workspace settings.
- Member roles.
- Tasks and board metadata.
- Approval policies.
- Agent visibility and skill card metadata.

#### Allowed Actions

- `create_workspace`
- `update_workspace_settings`
- `invite_member`
- `change_member_role`
- `create_task`
- `assign_task`
- `request_agent_run`
- `approve_gate`
- `reject_gate`
- `accept_evidence`
- `reject_evidence`
- `cancel_task`
- `archive_task`
- `export_audit_log`

#### Forbidden Actions

- Bypass required audit logs.
- Directly execute runtime steps without Bolt.
- Mutate immutable evidence or run history.
- Approve using an agent identity.

#### Edge Cases

- The last active human owner cannot be removed.
- A workspace with execution history should be archived rather than hard-deleted unless retention policy permits deletion.
- Owner approval may be insufficient for high-risk gates if policy requires independent review.

#### Trust / Security Expectations

- Governance decisions are auditable.
- Destructive actions require confirmation.
- Runtime credentials are never exposed in product UI.

---

### Role: Human Contributor

#### Goal

Create, claim, progress, and complete human-visible work, alone or with agents.

#### Permissions

- Create tasks.
- Edit tasks they created or are assigned to, subject to workspace policy.
- Claim human tasks.
- Add comments and context.
- Report blockers.
- Submit evidence for human work.
- Request assignment to an agent if permitted.

#### Visible Data

- Boards and tasks visible to their workspace role.
- Task details, comments, blockers, approvals, and evidence for accessible tasks.
- Relevant skill cards and agent profiles.

#### Editable Data

- Own task updates.
- Comments.
- Blocker reports.
- Evidence submissions.

#### Allowed Actions

- `create_task`
- `claim_task`
- `update_task_context`
- `report_blocker`
- `resolve_own_blocker`
- `comment_on_task`
- `submit_evidence`
- `request_agent_assignment`

#### Forbidden Actions

- Approve their own completion if separation-of-duty is enabled.
- Edit runtime state directly.
- Delete evidence produced by another actor.
- Use agent/runtime identities as if they were personal identities.

#### Edge Cases

- A human may take over an agent-assigned task only if the task is not actively running or after cancellation.
- Concurrent edits must preserve both comments/activity events.
- Task reassignment should not erase previous accountability.

#### Trust / Security Expectations

- Human actions are attributed.
- Sensitive task context is access-controlled.
- Agent handoff requires explicit bounded context.

---

### Role: Reviewer / Approver

#### Goal

Review work, approve gates, and decide whether evidence satisfies the task outcome.

#### Permissions

- View tasks requiring review or approval.
- Approve or reject approval requests.
- Accept or reject evidence bundles.
- Request changes.
- Mark task as done when evidence is accepted, if policy permits.
- Add review comments and risk notes.

#### Visible Data

- Task context needed for review.
- Approval request details.
- Evidence and linked artifacts.
- Activity timeline.
- Relevant run summaries.

#### Editable Data

- Review decisions.
- Approval decisions.
- Evidence review status.
- Review comments.

#### Allowed Actions

- `approve_gate`
- `reject_gate`
- `accept_evidence`
- `reject_evidence`
- `request_changes`
- `mark_task_done`
- `flag_task_risk`

#### Forbidden Actions

- Approve stale or superseded runs without explicit acknowledgement.
- Mutate evidence contents.
- Approve as an agent or system actor.
- Override high-risk gates without required policy.

#### Edge Cases

- Reviewer cannot approve their own evidence when separation-of-duty is enabled.
- If a new run supersedes evidence during review, the reviewer must target the latest evidence or explicitly acknowledge older evidence.
- Rejected evidence must include a reason.

#### Trust / Security Expectations

- Approvals are tied to exact task/run/evidence versions.
- Rejections are auditable and actionable.
- Risk acceptance is explicit.

---

### Role: Agent Supervisor

#### Goal

Manage assignment and supervision of agentic tasks without owning runtime execution.

#### Permissions

- Assign tasks to agent profiles.
- Select applicable skill cards.
- Define task context and constraints.
- Request a Bolt run.
- Pause/cancel task requests if allowed.
- Respond to blockers and clarification requests.
- Request rerun after failure or rejected evidence.

#### Visible Data

- Assignable agents and skill cards.
- Task context.
- Run summaries and state projections.
- Blockers, approvals, evidence, and timeline.

#### Editable Data

- Assignment metadata.
- Task constraints.
- Human responses to blockers.
- Rerun requests.

#### Allowed Actions

- `assign_agent_profile`
- `select_skill_card`
- `set_task_constraints`
- `request_bolt_run`
- `respond_to_blocker`
- `request_rerun`
- `cancel_run_request`

#### Forbidden Actions

- Decide Bolt execution plan.
- Select hidden runtime tools directly.
- Modify run logs.
- Store or reveal runtime secrets.

#### Edge Cases

- Assignment may fail if the skill card requires unavailable permissions.
- A task can be assigned before execution context is ready, but cannot run until required context and approvals exist.
- Rerun should reference the failed/superseded run.

#### Trust / Security Expectations

- Assignment is bounded by capabilities and policy.
- Bolt remains the source of truth for run state.
- Every run request is auditable and idempotent.

---

### Role: Agent Identity

#### Goal

Represent an agent as a visible collaborator with declared skills, limits, and produced outputs.

#### Permissions

- Be assigned to tasks.
- Report status through Bolt projections.
- Report blockers or clarification needs.
- Submit evidence through a run.
- Suggest next actions.

#### Visible Data

- Only task context included in the assigned run or authorized capability scope.
- Its own task assignments and run summaries where exposed.

#### Editable Data

None directly in MVP. Agent outputs become proposed updates, blockers, comments, or evidence records through system/Bolt ingestion.

#### Allowed Actions

- `emit_status_update`
- `report_blocker`
- `submit_evidence`
- `suggest_rerun_reason`
- `request_clarification`

#### Forbidden Actions

- Approve gates.
- Accept evidence as complete.
- Change workspace membership or permissions.
- Directly mutate task state outside allowed projected events.
- Access context not explicitly provided.

#### Edge Cases

- An agent profile may represent a logical agent, while a run uses a separate runtime identity.
- Agent output may require human acceptance before changing task status.
- Agent status may be unknown if Bolt is unavailable.

#### Trust / Security Expectations

- Agent-generated updates are clearly marked.
- Agent identity is not equivalent to human accountability.
- Context boundaries are explicit.

---

### Role: Runtime Service Account

#### Goal

Represent a technical execution identity used by Bolt/runtime systems.

#### Permissions

- Emit run state updates through trusted integration.
- Attach evidence references.
- Attach logs or artifact references.
- Signal required approvals/gates.

#### Visible Data

- Operational context needed by the integration.
- No product UI visibility beyond projected references.

#### Editable Data

- Run projections.
- Evidence references.
- Activity events derived from trusted integration.

#### Allowed Actions

- `sync_run_status`
- `sync_gate_request`
- `sync_evidence_reference`
- `sync_failure_context`

#### Forbidden Actions

- Be treated as a human approver.
- Own tasks.
- Change task intent or human decisions.
- Expose secrets to the workspace.

#### Edge Cases

- One agent task may have multiple runtime attempts.
- Runtime identity may rotate; historical events must keep a stable snapshot.
- Integration outage must not corrupt task state.

#### Trust / Security Expectations

- Runtime events must be authenticated and tamper-evident where possible.
- Secrets are never stored in Rumble task records.
- RuntimeRef is a reference, not credential storage.

---

### Role: Observer / Auditor

#### Goal

Read task state and history without changing the work.

#### Permissions

- View accessible boards and task timelines.
- View evidence metadata and allowed artifacts.
- Export audit report if policy permits.

#### Visible Data

- Task status.
- Assignment history.
- Blockers.
- Approval decisions.
- Evidence review state.
- Activity events.

#### Editable Data

None.

#### Allowed Actions

- `view_board`
- `view_task_detail`
- `view_timeline`
- `view_evidence_metadata`
- `export_audit_report_if_allowed`

#### Forbidden Actions

- Edit tasks.
- Comment unless granted contributor role.
- Approve or reject.
- Request runs.

#### Edge Cases

- Some evidence artifacts may be redacted while metadata remains visible.
- Export may require owner approval for sensitive workspaces.

#### Trust / Security Expectations

- Read-only access cannot leak secrets or private runtime logs.
- Audit exports preserve provenance and redaction markers.

---

### Role: System

#### Goal

Maintain derived state, permissions, projections, auditability, and integration consistency.

#### Permissions

- Enforce role permissions.
- Record activity events.
- Compute derived task status.
- Ingest trusted Bolt events.
- Mark stale/superseded evidence.
- Detect blocked approval or review conditions.

#### Visible Data

Operational access only as required by deployment architecture.

#### Editable Data

- Derived statuses.
- Activity events.
- Synchronization metadata.
- Projection records.

#### Allowed Actions

- `record_activity_event`
- `compute_task_status`
- `ingest_bolt_event`
- `mark_evidence_superseded`
- `detect_stale_review`
- `enforce_permission`

#### Forbidden Actions

- Make human approvals.
- Invent evidence.
- Mutate immutable evidence contents.
- Execute orchestration logic.

#### Edge Cases

- If Bolt is unavailable, system must show stale/unknown state rather than fabricate progress.
- Replayed events must be idempotent.

#### Trust / Security Expectations

- System actions are deterministic and auditable.
- Derived state can be recomputed from events where possible.

---

## MVP Permission Matrix

| Action | Owner | Human Contributor | Reviewer / Approver | Agent Supervisor | Agent Identity | Runtime Service Account | Observer | System |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Create workspace | Yes | No | No | No | No | No | No | No |
| Manage members | Yes | No | No | No | No | No | No | No |
| Create task | Yes | Yes | No | Yes | No | No | No | No |
| Edit task context | Yes | Own/assigned | No | Assigned/supervised | Suggest only | No | No | No |
| Assign task to human | Yes | Limited by policy | No | Yes | No | No | No | No |
| Assign task to agent | Yes | Request only | No | Yes | No | No | No | No |
| Request Bolt run | Yes | If delegated | No | Yes | No | No | No | No |
| Report blocker | Yes | Yes | Yes | Yes | Via projection | Via integration | No | Yes |
| Resolve blocker | Yes | Own/assigned | If review blocker | Yes | No | No | No | Yes, derived only |
| Approve gate | Yes | No | Yes | If explicitly granted | No | No | No | No |
| Reject gate | Yes | No | Yes | If explicitly granted | No | No | No | No |
| Submit evidence | Yes | Yes | No | No | Via projection | Via integration | No | No |
| Accept evidence | Yes | No | Yes | If explicitly granted | No | No | No | No |
| Reject evidence | Yes | No | Yes | If explicitly granted | No | No | No | No |
| Request rerun | Yes | Request only | Request only | Yes | Suggest only | No | No | No |
| Cancel task/run request | Yes | Own if policy allows | No | Yes | No | No | No | No |
| View timeline | Yes | Yes | Yes | Yes | Scoped | No UI | Yes | Yes |
| Export audit | Yes | No | If granted | No | No | No | If granted | No |

---

## Shared Capability Candidates

| Candidate | Reason | Proposed placement |
| --- | --- | --- |
| Workspace membership | Needed by all collaborative Rumble products. | Shared Rumble + auth adapter. |
| ActorReference | Humans, agents, runtime accounts, and systems all need auditable attribution. | Shared identity/profile adapter; product keeps snapshots. |
| Activity event log | Task timeline and audit are central. | Gear event log with Rumble projection. |
| Comment/thread | Needed for task collaboration and reviews. | Shared Rumble. |
| Agent task | Core seam between Rumble UX and Bolt execution. | Bolt owns execution lifecycle; Rumble owns UX projection/request. |
| Approval/gate | Human decision UX plus Bolt gates. | Bolt for gate semantics; Rumble for interaction and audit projection. |
| Skill/capability card | Reusable description of assignable agent/tool capabilities. | Discuss: Bolt registry plus Rumble UX projection. |
| Evidence | Produced by tools/runs, reviewed in Rumble. | Gear artifact/provenance + Rumble review UX. |
| Runtime reference | Needed to avoid confusing agent profile and execution identity. | Bolt/Gear integration reference; Rumble stores safe snapshot. |

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should Agent Identity be a workspace member or only a referenced actor? | High | Proposed: referenced actor with optional scoped membership; cannot approve. |
| Should Agent Supervisor and Reviewer be separate in small teams? | Medium | Open; roles may be assigned to same human, but policy can require separation for high-risk gates. |
| Which approval policies are configurable in MVP vs hard-coded defaults? | High | Proposed: four approval types only. |
| How much runtime detail is visible to Human Contributor? | Medium | Open; default should be summarized, with privileged drill-down. |
