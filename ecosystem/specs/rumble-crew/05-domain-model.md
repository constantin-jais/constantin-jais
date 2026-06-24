# Domain Model — rumble-crew

## Scope

This document defines the MVP domain model for `rumble-crew`.

The model must support:

- human/agent collaboration around tasks;
- explicit separation between task state, run state, and actor availability;
- agent assignment through visible profiles and skill cards;
- blockers, approvals, evidence, reviews, and reruns;
- safe integration with `cos-matic` without reimplementing orchestration.

---

## Boundary With `cos-matic`

| Concern | `rumble-crew` owns | `cos-matic` owns |
| --- | --- | --- |
| User-facing task | Creates, displays, assigns, reviews, closes. | Consumes task intent as execution input if requested. |
| Run planning/execution | Displays projections and sends bounded requests. | Plans, sequences, gates, executes, retries internally. |
| Agent selection | Shows `AgentProfile` and `SkillCard` metadata. | Chooses actual tools/steps/runtime details as allowed. |
| Runtime identity | Stores safe `RuntimeRef` snapshots. | Owns runtime/service identity and execution credentials. |
| Approval UX | Captures human decisions and syncs them. | Enforces gates and waits/continues execution. |
| Evidence UX | Presents, reviews, accepts/rejects evidence. | Produces execution evidence via tools/runs. |
| Logs/artifacts | Shows summaries/references. | Produces references; Gear may store artifacts/provenance. |
| Retry/rerun | Requests rerun with rationale/context. | Decides execution plan for the new attempt. |

Boundary rule:

> `rumble-crew` requests and governs work; `cos-matic` decides and executes how work runs.

---

## Aggregate Overview

```text
Workspace
├── WorkspaceMember
├── Board
│   └── BoardColumn
├── Task
│   ├── TaskAssignment
│   ├── RunRef
│   ├── Blocker
│   ├── Approval
│   ├── Evidence
│   ├── CommentThread
│   └── ActivityEvent
├── AgentProfile
├── RuntimeRef
├── SkillCard
└── AuditExport
```

## State Separation

### TaskStatus

Product/collaboration state owned by `rumble-crew`.

```text
created
assigned
ready
in_progress
blocked
in_review
done
failed
cancelled
```

### RunStatus

Execution state projected from Bolt / `cos-matic`.

```text
queued
claimed
running
waiting_for_approval
succeeded
failed
cancelled
unknown
```

### ActorStatus

Availability/visibility state for humans or agents.

```text
available
busy
offline
restricted
unknown
```

Invariants:

- `TaskStatus` must not be treated as the source of truth for runtime execution.
- `RunStatus` must not directly close a task without product review rules.
- `ActorStatus` is advisory and must not imply permission.
- A task can be `blocked` because of a blocker even if the last run is `failed`, `waiting_for_approval`, or `unknown`.

---

## Entity: Workspace

### Definition

A collaboration space containing boards, tasks, members, agent profiles, skill cards, and task governance settings.

### Owner

`rumble-crew` for product semantics. Shared Rumble workspace primitive is a candidate.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `name` | string | Yes | Human-readable. |
| `slug` | string | Yes | Unique in account/local profile. |
| `status` | enum | Yes | `active`, `archived`. |
| `approval_policy` | json | Yes | MVP supports start, scope, risk, completion approvals. |
| `created_at` | timestamp | Yes | Audit. |
| `updated_at` | timestamp | Yes | Audit. |

### Relationships

- Has many `WorkspaceMember`.
- Has many `Board`.
- Has many `Task`.
- Has many `AgentProfile`.
- Has many `SkillCard`.

### Invariants

- A workspace must have at least one active human owner.
- Archived workspaces are read-only except export/restore actions.
- Approval policy changes do not mutate past approvals.

### Events

- `workspace_created`
- `workspace_updated`
- `workspace_archived`

### Shared Capability Candidates

- Workspace / project space.
- Permission/audit policy.

---

## Entity: WorkspaceMember

### Definition

A human or scoped non-human actor with access to a workspace.

### Owner

`rumble-crew` MVP, shared auth/profile adapter later.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `actor_ref` | ActorRef | Yes | Human, agent, system, runtime-service, external. |
| `roles` | string[] | Yes | Product roles. |
| `status` | enum | Yes | `invited`, `active`, `suspended`, `removed`. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Runtime service accounts cannot be human approvers.
- Agent identities cannot own workspaces.
- Removed/suspended members cannot act.

### Events

- `workspace_member_invited`
- `workspace_member_activated`
- `workspace_member_suspended`
- `workspace_member_removed`

---

## Value Object: ActorRef

### Definition

A safe attribution snapshot for a human, agent, system, runtime service, or external actor.

### Owner

Shared identity/profile candidate. `rumble-crew` stores snapshots for audit.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `actor_id` | string/UUID | Yes | Stable local/external identifier. |
| `actor_type` | enum | Yes | `human`, `agent`, `system`, `runtime_service`, `external`. |
| `display_name` | string | No | Snapshot. |
| `source` | string | No | Local profile, workspace member, Bolt agent, integration, etc. |

### Invariants

- Every approval, blocker, evidence submission, review, and status transition has actor attribution.
- Agent/runtime actors cannot satisfy human approval requirements.
- Actor snapshots remain readable even if identity provider changes.

---

## Entity: Board

### Definition

A workspace view over tasks, usually grouped by task status, assignment, or review state.

### Owner

`rumble-crew` UX.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Example: Agent Work. |
| `view_mode` | enum | Yes | `status_board`, `assignee_board`, `review_queue`, `blocked_queue`. |
| `filters` | json | No | Saved filters. |
| `created_at` | timestamp | Yes | Audit. |

### Relationships

- Has many `BoardColumn`.
- Displays many `Task` through query/filter.

### Invariants

- Board is a view, not the source of task lifecycle truth.
- Moving a card must call task transition rules, not only change column.

### Events

- `board_created`
- `board_updated`
- `board_view_changed`

---

## Entity: BoardColumn

### Definition

A visual grouping for tasks on a board.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `board_id` | UUID | Yes | Parent board. |
| `name` | string | Yes | Human label. |
| `task_status_filter` | TaskStatus[] | No | Statuses represented. |
| `sort_order` | integer | Yes | UI ordering. |

### Invariants

- Columns cannot create unsupported task states.
- Done/cancelled columns should not allow direct edits except reopen policy if later added.

---

## Entity: Task

### Definition

A bounded unit of human/agent work with product-visible goal, assignment, blockers, approvals, evidence, and lifecycle.

### Owner

`rumble-crew`.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `title` | string | Yes | Human-readable. |
| `description` | text | No | Context and intent. |
| `goal` | text | Yes | Desired outcome. |
| `expected_evidence` | json/text | No | What proof should be submitted. |
| `status` | TaskStatus | Yes | Collaboration/product state. |
| `priority` | enum | No | `low`, `normal`, `high`, `urgent`. |
| `risk_level` | enum | No | `low`, `medium`, `high`, `critical`. |
| `created_by` | ActorRef | Yes | Creator. |
| `created_at` | timestamp | Yes | Audit. |
| `updated_at` | timestamp | Yes | Audit. |
| `archived_at` | timestamp | No | Archive. |

### Relationships

- Has zero or more `TaskAssignment`.
- Has zero or more `RunRef`.
- Has zero or more `Blocker`.
- Has zero or more `Approval`.
- Has zero or more `Evidence`.
- Has one or more `ActivityEvent`.
- May have `CommentThread`.

### Lifecycle States

| State | Meaning |
| --- | --- |
| `created` | Task exists but is not assigned. |
| `assigned` | Human or agent has been selected. |
| `ready` | Required context and start approvals are present. |
| `in_progress` | Work is actively underway or latest run is active. |
| `blocked` | A blocking blocker or approval prevents progress. |
| `in_review` | Evidence/output awaits review. |
| `done` | Required evidence accepted and task closed. |
| `failed` | Work cannot complete in current form or allowed attempts exhausted. |
| `cancelled` | Work intentionally stopped. |

### State Transitions

```text
created → assigned
assigned → ready
ready → in_progress
in_progress → blocked
blocked → ready
blocked → in_progress
in_progress → in_review
in_review → done
in_review → ready        # changes requested / rerun
in_progress → failed
ready → cancelled
assigned → cancelled
blocked → cancelled
failed → ready           # explicit rerun/reopen policy
```

### Invariants

- `done` requires accepted evidence or explicit completion approval.
- `cancelled` requires human actor and reason.
- `failed` requires reason and current/last run or review context.
- A task with active blocking blockers cannot move to `done`.
- A task can have multiple runs, but only one current active run unless policy later allows parallel attempts.
- Direct board movement must respect lifecycle rules.

### Events

- `task_created`
- `task_assigned`
- `task_ready`
- `task_started`
- `task_marked_blocked`
- `task_entered_review`
- `task_marked_done`
- `task_marked_failed`
- `task_cancelled`

### Shared Capability Candidates

- Agent task.
- Activity/event log.
- Comment/thread.

---

## Entity: TaskAssignment

### Definition

The assignment of a task to a human, agent profile, or team role.

### Owner

`rumble-crew`.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `task_id` | UUID | Yes | Parent task. |
| `assignee_type` | enum | Yes | `human`, `agent_profile`, `role`. |
| `assignee_ref` | string/UUID | Yes | Member ID, AgentProfile ID, or role. |
| `skill_card_id` | UUID | No | Required for agent assignment when applicable. |
| `status` | enum | Yes | `proposed`, `active`, `completed`, `revoked`, `superseded`. |
| `assigned_by` | ActorRef | Yes | Actor. |
| `assigned_at` | timestamp | Yes | Audit. |

### Invariants

- Agent assignment should reference a compatible `SkillCard`.
- Reassignment does not delete prior assignments.
- Revoked/superseded assignments cannot receive new run requests.

### Events

- `task_assigned`
- `task_reassigned`
- `task_assignment_revoked`

---

## Entity: AgentProfile

### Definition

A user-facing representation of an agent/capability endpoint available for assignment.

### Owner

`rumble-crew` projection. Source of capability truth may be Bolt or a shared registry.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Human-readable. |
| `description` | text | No | What it is good for. |
| `status` | enum | Yes | `active`, `disabled`, `deprecated`, `unknown`. |
| `actor_ref` | ActorRef | Yes | Agent actor snapshot. |
| `runtime_ref_id` | UUID | No | Default runtime reference. |
| `visible_to_roles` | string[] | No | Access control. |

### Relationships

- Has many compatible `SkillCard`.
- May have one default `RuntimeRef`.

### Invariants

- Disabled/deprecated agents cannot receive new assignments unless overridden by owner policy.
- Agent profile is not a credential store.
- Agent profile is not the same as runtime identity.

### Events

- `agent_profile_created`
- `agent_profile_updated`
- `agent_profile_disabled`

### Shared Capability Candidates

- Agent profile.
- Runtime identity projection.

---

## Entity: RuntimeRef

### Definition

A safe reference to the runtime/service identity or execution environment used by Bolt.

### Owner

Bolt owns runtime semantics and credentials. `rumble-crew` stores a safe reference/snapshot.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Local reference ID. |
| `provider` | string | Yes | Example: `cos-matic`. |
| `external_runtime_id` | string | No | Opaque runtime ID. |
| `display_name` | string | No | Safe label. |
| `status` | enum | Yes | `available`, `unavailable`, `restricted`, `unknown`. |
| `capabilities_hash` | string | No | Optional drift detection. |
| `last_seen_at` | timestamp | No | Sync status. |

### Invariants

- Must not store secrets, tokens, private keys, or raw credentials.
- RuntimeRef changes do not mutate historical run records.
- Unknown/unavailable runtime blocks new run requests unless policy permits queued requests.

### Events

- `runtime_ref_registered`
- `runtime_ref_updated`
- `runtime_ref_unavailable`

### Shared Capability Candidates

- Runtime identity/reference.
- Permission/audit policy.

---

## Entity: SkillCard

### Definition

A visible capability card describing what kind of work an agent/runtime can accept, what inputs it needs, what evidence it produces, and what approvals/risks apply.

### Owner

`rumble-crew` owns presentation and workspace selection. Bolt may own canonical capability metadata later.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Human-readable. |
| `description` | text | Yes | Capability summary. |
| `input_requirements` | json/text | Yes | Required context. |
| `output_expectations` | json/text | Yes | Expected outputs/evidence. |
| `risk_notes` | text | No | Risks/constraints. |
| `required_permissions` | string[] | No | Abstract permission labels. |
| `approval_requirements` | string[] | No | `start`, `scope`, `risk`, `completion`. |
| `compatible_runtime_refs` | UUID[] | No | Safe references. |
| `status` | enum | Yes | `active`, `disabled`, `deprecated`. |

### Invariants

- Active skill cards must declare input requirements and output expectations.
- Skill card does not execute work directly.
- Skill card compatibility must be checked before agent assignment/run request.

### Events

- `skill_card_created`
- `skill_card_updated`
- `skill_card_disabled`
- `skill_card_selected`

### Shared Capability Candidates

- Skill/capability card.

---

## Entity: RunRef

### Definition

A local projection/reference to a Bolt run or attempt associated with a task.

### Owner

Bolt / `cos-matic` owns run lifecycle. `rumble-crew` owns local projection and UX state.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Local run reference ID. |
| `task_id` | UUID | Yes | Parent task. |
| `bolt_provider` | string | Yes | MVP: `cos-matic`. |
| `external_run_id` | string | No | Opaque Bolt run ID. |
| `runtime_ref_id` | UUID | No | Runtime reference. |
| `status` | RunStatus | Yes | Projected run state. |
| `attempt_number` | integer | Yes | Monotonic per task. |
| `requested_by` | ActorRef | Yes | Human actor requesting. |
| `request_payload_hash` | string | No | Bounded context integrity. |
| `previous_run_ref_id` | UUID | No | For rerun lineage. |
| `started_at` | timestamp | No | From Bolt or projection. |
| `finished_at` | timestamp | No | From Bolt or projection. |
| `sync_status` | enum | Yes | `current`, `stale`, `sync_failed`, `unknown`. |

### Lifecycle States

| State | Meaning |
| --- | --- |
| `queued` | Run request accepted/queued. |
| `claimed` | Runtime claimed work. |
| `running` | Execution underway. |
| `waiting_for_approval` | Bolt gate requires human decision. |
| `succeeded` | Bolt reports successful run. |
| `failed` | Bolt reports failed run. |
| `cancelled` | Run cancelled. |
| `unknown` | Status unavailable/stale. |

### Invariants

- Run state is a projection from Bolt, not authoritative task completion.
- `succeeded` may move task to `in_review`, not automatically `done` unless policy explicitly allows.
- Reruns create new `RunRef` records and link prior attempts.
- Historical run refs are immutable except sync/projection metadata.

### Events

- `bolt_run_requested`
- `bolt_run_queued`
- `bolt_run_claimed`
- `bolt_run_started`
- `bolt_run_waiting_for_approval`
- `bolt_run_succeeded`
- `bolt_run_failed`
- `bolt_run_cancelled`
- `bolt_run_sync_failed`

### Shared Capability Candidates

- Agent task/run seam.
- Activity/event log.

---

## Entity: Blocker

### Definition

A condition preventing or warning against progress on a task or run.

### Owner

`rumble-crew` for collaboration UX. Some blockers originate from Bolt.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `task_id` | UUID | Yes | Parent task. |
| `run_ref_id` | UUID | No | Linked run if applicable. |
| `type` | enum | Yes | `missing_context`, `approval_required`, `permission`, `tool_failure`, `runtime_unavailable`, `scope_ambiguity`, `external_dependency`, `other`. |
| `severity` | enum | Yes | `info`, `warning`, `blocking`. |
| `status` | enum | Yes | `open`, `resolved`, `rejected`, `superseded`. |
| `summary` | string | Yes | Human-readable. |
| `details` | text/json | No | Additional context. |
| `reported_by` | ActorRef | Yes | Reporter. |
| `resolver_ref` | ActorRef | No | Expected resolver. |
| `resolution` | text | No | Required when resolved/rejected. |
| `created_at` | timestamp | Yes | Audit. |
| `resolved_at` | timestamp | No | Audit. |

### Invariants

- Blocking open blockers prevent `done`.
- Resolving/rejecting a blocker requires human/system-authorized actor and rationale.
- Automated blocker payloads should preserve original source or safe hash.

### Events

- `blocker_reported`
- `task_marked_blocked`
- `blocker_resolved`
- `blocker_rejected`
- `blocker_superseded`

### Shared Capability Candidates

- Blocker as Rumble/Bolt seam primitive.

---

## Entity: Approval

### Definition

A human decision required before a start, scope, risk, or completion gate can proceed.

### Owner

Rumble owns UX/decision record. Bolt owns gate enforcement when approval affects execution.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `task_id` | UUID | Yes | Parent task. |
| `run_ref_id` | UUID | No | Linked run if applicable. |
| `type` | enum | Yes | `start`, `scope`, `risk`, `completion`. |
| `target_type` | string | Yes | `task`, `run`, `blocker`, `evidence`, `rerun`. |
| `target_id` | UUID/string | Yes | Target object. |
| `status` | enum | Yes | `requested`, `approved`, `rejected`, `expired`, `superseded`, `sync_failed`. |
| `risk_level` | enum | No | `low`, `medium`, `high`, `critical`. |
| `request_summary` | text | Yes | What is being asked. |
| `requested_by` | ActorRef | Yes | Requester/source. |
| `decided_by` | ActorRef | No | Human approver/rejecter. |
| `decision_reason` | text | No | Required for rejection/high-risk approval. |
| `conditions` | text/json | No | Approval constraints. |
| `expires_at` | timestamp | No | Optional timeout. |
| `created_at` | timestamp | Yes | Audit. |
| `decided_at` | timestamp | No | Audit. |

### Invariants

- Only human actors with approval permission can approve/reject.
- Approval target version must be explicit enough to prevent stale approvals.
- Approved execution gates must sync to Bolt before assuming execution can continue.
- Expired/superseded approvals cannot unblock work.

### Events

- `approval_requested`
- `approval_granted`
- `approval_rejected`
- `approval_expired`
- `approval_superseded`
- `approval_sync_failed`

### Shared Capability Candidates

- Approval/gate.
- Waiver/risk acceptance later if needed.

---

## Entity: Evidence

### Definition

A proof item or proof bundle submitted for task progress, review, or completion.

### Owner

`rumble-crew` owns review UX and status. Gear may own artifact/provenance storage. Bolt/Wrench may produce evidence.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `task_id` | UUID | Yes | Parent task. |
| `run_ref_id` | UUID | No | Producing run if applicable. |
| `type` | enum | Yes | `log`, `diff`, `test_report`, `screenshot`, `artifact`, `decision_record`, `inspection_report`, `other`. |
| `status` | enum | Yes | `submitted`, `accepted`, `rejected`, `superseded`. |
| `summary` | text | Yes | Human-readable. |
| `artifact_ref` | string/json | No | Gear/external reference. |
| `content_hash` | string | No | Integrity if available. |
| `produced_by` | ActorRef | Yes | Human/agent/runtime. |
| `reviewed_by` | ActorRef | No | Human reviewer. |
| `review_reason` | text | No | Required for rejection. |
| `created_at` | timestamp | Yes | Audit. |
| `reviewed_at` | timestamp | No | Audit. |

### Invariants

- Accepted evidence must be reviewable and tied to task objective.
- Rejected evidence requires reason.
- Superseded evidence remains in history.
- Evidence artifact unavailability must be visible; it cannot silently count as accepted proof.

### Events

- `evidence_submitted`
- `evidence_accepted`
- `evidence_rejected`
- `evidence_superseded`

### Shared Capability Candidates

- Artifact.
- Evidence/provenance.
- Inspector reports.

---

## Entity: CommentThread and Comment

### Definition

A discussion attached to a task, blocker, approval, evidence item, or run reference.

### Owner

Shared Rumble candidate. `rumble-crew` uses it for task collaboration.

### Fields: CommentThread

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `target_type` | string | Yes | `task`, `blocker`, `approval`, `evidence`, `run_ref`. |
| `target_id` | UUID | Yes | Target object. |
| `status` | enum | Yes | `open`, `resolved`. |

### Fields: Comment

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `thread_id` | UUID | Yes | Parent thread. |
| `author` | ActorRef | Yes | Author. |
| `body` | text | Yes | Content. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Comments are append-only after an edit window if editing is supported.
- Resolving a thread requires attribution.
- Agent comments must be marked as agent-generated/projection-sourced.

### Events

- `comment_thread_created`
- `comment_created`
- `comment_thread_resolved`

---

## Entity: ActivityEvent

### Definition

An immutable-ish timeline event describing what happened to a task/workspace object.

### Owner

Gear event log candidate with Rumble projection.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `task_id` | UUID | No | Related task. |
| `event_type` | string | Yes | Event name. |
| `actor` | ActorRef | Yes | Actor/source. |
| `target_type` | string | No | Target object type. |
| `target_id` | UUID/string | No | Target ID. |
| `payload` | json | No | Safe event data. |
| `occurred_at` | timestamp | Yes | Event time. |
| `source` | enum/string | Yes | `rumble_crew`, `cos_matic`, `gear`, `wrench`, `system`. |
| `integrity_hash` | string | No | Optional tamper evidence. |

### Invariants

- User-visible timeline derives from activity events.
- Sensitive runtime logs should be referenced/redacted, not copied blindly.
- Replayed integration events must be idempotent.

### Events

Activity events are themselves persisted records. Meta-events are not required in MVP.

### Shared Capability Candidates

- Activity/event log.
- Audit/provenance.

---

## Entity: AuditExport

### Definition

A generated export of selected task/workspace history for review, compliance, or handoff.

### Owner

`rumble-crew` UX; Gear artifact candidate for storage.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `scope` | json | Yes | Task IDs/date range/filters. |
| `format` | enum | Yes | `json`, `markdown`, `pdf`, `bundle`. |
| `status` | enum | Yes | `requested`, `generated`, `failed`, `expired`. |
| `artifact_ref` | string/json | No | Gear/external artifact reference. |
| `requested_by` | ActorRef | Yes | Human requester. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Export must respect permissions/redaction.
- Export must identify omitted/redacted evidence.
- Export should include enough provenance to be inspectable.

### Events

- `audit_export_requested`
- `audit_export_generated`
- `audit_export_failed`

---

## Initial Domain Decisions

### Decision 1: Separate TaskStatus, RunStatus, and ActorStatus

Status: Accepted for MVP.

Reason:

- A product task is not the same as a runtime run.
- An agent is not “running”; a run is running.
- A human or agent status is advisory availability, not task progress.

### Decision 2: `RunRef` is a projection, not orchestration state

Status: Accepted for MVP.

Reason:

- Prevents `rumble-crew` from becoming the execution brain.
- Keeps `cos-matic` authoritative for run/gate/execution lifecycle.
- Allows degraded UI when Bolt is unavailable.

### Decision 3: `SkillCard` is descriptive in MVP

Status: Accepted for MVP.

Reason:

- Users need to understand capabilities before assignment.
- Execution compatibility belongs to Bolt/runtime integrations.
- A marketplace or dynamic tool registry would over-expand MVP scope.

### Decision 4: Completion policy controls whether run success can close tasks

Status: Accepted for MVP.

Reason:

- Default behavior is review-first: run success moves toward review, not automatic completion.
- Product requires a path for low-risk auto-close to keep agentic work fluid.
- Auto-close is allowed only through explicit `completion_mode` and low-risk `SkillCard.auto_closable=true` policy.
- High/critical risk tasks, open blockers, pending approvals, stale context, and untrusted run projections block auto-close.

### Decision 5: Approval types are limited in MVP

Status: Accepted for MVP.

Reason:

- Four approval types cover immediate needs: `start`, `scope`, `risk`, `completion`.
- Simple rules by risk level provide enough control without a workflow builder.
- Avoids building a general workflow engine.

### Decision 6: Real execution is allowed in MVP only through trusted Bolt integration

Status: Accepted for MVP.

Reason:

- `rumble-crew` should be operationally useful from MVP.
- Rumble may request execution from `cos-matic`, but must not execute directly.
- Execution requires `execution_mode=trusted_execution`, audit, idempotency, approval policy, RuntimeRef, and kill switch.

### Decision 7: Evidence storage is local only as an extractable fallback

Status: Accepted for MVP.

Reason:

- Gear is the target owner for artifact/provenance storage.
- If no suitable Gear backend exists, Rumble can temporarily store evidence locally.
- Local evidence must include storage backend, hash, provenance/ref fields, `extractable=true`, and migration status.

### Decision 8: Raw runtime logs are allowed as privileged sensitive records

Status: Accepted with security constraints.

Reason:

- Raw logs are useful for debugging trusted executions.
- They are high-risk for secrets and PII.
- MVP allows them only for trusted workspaces, privileged actors, audited access, TTL-limited retention, no full-text indexing, and redaction/scanner safeguards.

### Decision 9: Parallel runs are post-MVP policy, not default

Status: Accepted for MVP.

Reason:

- Default remains one active `RunRef` per task.
- Future policies may allow compare-output, split-subtask, or redundant-verification parallelism.

### Decision 10: Failed run requires human recovery decision by default

Status: Accepted for MVP.

Reason:

- A run failure is not always task failure.
- Human should choose rerun, reassign, fail, or cancel.

---

## Shared Capability Candidates

| Candidate | Needed by | Proposed owner | Status | Notes |
| --- | --- | --- | --- | --- |
| Agent task | `rumble-crew`, later Canvas/Note/LM | Bolt + Rumble UX projection | Discuss | Bolt owns execution; Rumble owns task UX. |
| Approval/gate | Crew, Canvas, LM | Bolt gate + Rumble approval UX | Candidate | Needs shared semantics for stale targets. |
| Evidence | All Rumbles | Gear artifact/provenance + Rumble review | Candidate | Evidence review is product UX; storage/provenance likely Gear. |
| Skill/capability card | Crew, Canvas, Note | Discuss: Bolt registry + Rumble projection | Discuss | Avoid marketplace in MVP. |
| RuntimeRef | Crew primarily | Bolt/Gear integration | Candidate | Safe snapshot only; no secrets. |
| Blocker | Crew, Canvas handoff flows | Shared Rumble/Bolt seam | Candidate | Could represent human-required interruptions. |
| ActivityEvent | All Rumbles | Gear event log | Candidate | Backbone for audit/timeline. |
| CommentThread | Crew, Canvas, LM | Shared Rumble | Candidate | Reusable collaboration primitive. |

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should `Task` and `AgentTask` be separate entities? | High | Accepted: one `Task` with assignment/run refs; avoid duplicate work models. |
| Should `RunRef` support parallel attempts in MVP? | Medium | Accepted: no by default; post-MVP explicit policy only. |
| Should approval sync be push, poll, or both with `cos-matic`? | High | Accepted direction: push idempotent + retry + visible `sync_failed`; polling can be added later. |
| Where is canonical evidence stored? | High | Accepted: Gear target; Rumble local only extractable fallback until Gear maturity. |
| Is `SkillCard` canonical in Bolt or authored in Rumble? | High | Accepted: local or `cos_matic` sourced with sync/drift fields. |
| Which task fields are PII/sensitive by default? | High | Defer to data/security spec. |
