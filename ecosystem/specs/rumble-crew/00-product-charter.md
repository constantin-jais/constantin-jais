# Product Charter — rumble-crew

Status: Drafting.

## Mission

`rumble-crew` is the agentic teamwork workspace where humans and agents collaborate through tasks, statuses, blockers, approvals, skills, and execution evidence.

It makes agentic work visible, governable, and reviewable without becoming the orchestration brain or runtime.

## Target Users

- Humans supervising agentic work.
- Contributors delegating bounded tasks to agents.
- Reviewers approving risky actions and completion evidence.
- Operators exposing agent skills/capabilities safely.
- Auditors inspecting what happened, who acted, and why work was accepted or rejected.

## Jobs To Be Done

- Create a bounded task with goal, context, constraints, and expected evidence.
- Assign a task to a human or agent profile.
- See whether work is ready, running, blocked, waiting for approval, under review, done, failed, or cancelled.
- Understand which runtime/run produced a status or evidence item.
- Respond to blockers and clarification requests.
- Approve or reject start, scope, risk, or completion gates.
- Review evidence and decide done, changes requested, rerun, fail, or cancel.
- Export or inspect an auditable timeline of task decisions and evidence.

## Product Promise

`rumble-crew` gives teams one reliable workspace to supervise agentic work:

> every task has an owner, every run has a reference, every blocker has a resolver, every approval has a human decision, and every completion claim has evidence.

## Non-Goals

- Not a generic project management tool.
- Not a general Kanban replacement.
- Not the agent runtime.
- Not the orchestration planner.
- Not a tool registry or marketplace.
- Not a credential store.
- Not the canonical artifact/provenance store.
- Not a chat UI for unrestricted agent interaction.

## Product Boundaries

### `rumble-crew` owns

- User-facing task workspace.
- Boards, task details, review queues, and timelines.
- Human/agent assignment UX.
- Agent profile and skill card presentation.
- Approval interaction and decision records.
- Evidence review status.
- Blocker visibility and resolution workflow.
- Safe projections of Bolt run state.

### `rumble-crew` consumes

- Bolt / `cos-matic` run state, gates, failures, and evidence references.
- Gear artifact/provenance/event-log primitives when available.
- Wrench inspection reports when used as evidence.
- Shared Rumble workspace/comment/notification primitives if extracted later.

### `rumble-crew` refuses to own

- Execution planning.
- Runtime tool selection.
- Agent process lifecycle.
- Hidden retries and sequencing.
- Raw artifact storage/provenance.
- Secrets or runtime credentials.
- Cross-product shared identity as a whole.

## Boundary With `cos-matic`

| Concern | `rumble-crew` | `cos-matic` |
| --- | --- | --- |
| Task intent | Creates and displays. | Consumes as execution input. |
| Plan/execution | Requests and observes. | Plans, sequences, gates, executes. |
| Run state | Displays projection. | Owns canonical run lifecycle. |
| Approval | Captures human decision. | Enforces execution gate. |
| Evidence | Reviews and accepts/rejects. | Produces evidence references via execution/tools. |
| Runtime identity | Stores safe reference. | Owns runtime identity/credentials. |
| Retry | Requests rerun with reason. | Decides retry execution plan. |

Boundary rule:

> `rumble-crew` requests and governs work; `cos-matic` decides and executes how work runs.

## MVP Scope

### Included

- Workspace with members and roles.
- Board view for agentic tasks.
- Task detail with goal, context, constraints, assignment, blockers, approvals, evidence, and timeline.
- Task lifecycle with clear separation from run lifecycle.
- Agent profile and skill card cards.
- Real execution requests to `cos-matic` when workspace `execution_mode=trusted_execution`.
- Run references projected from `cos-matic`.
- Explicit completion policy:
  - `manual_review_required` by default;
  - `auto_close_if_evidence_valid` for low-risk trusted tasks;
  - `auto_close_if_run_succeeded` only for explicit low-risk auto-closable tasks.
- Privileged raw runtime logs for trusted workspaces only, audited and non-indexed.
- Four approval types:
  - `start`;
  - `scope`;
  - `risk`;
  - `completion`.
- Evidence records with review status:
  - `submitted`;
  - `accepted`;
  - `rejected`;
  - `superseded`.
- Blocker reporting and resolution.
- Rerun/fail/cancel flows.
- Activity timeline for audit.

### Excluded from MVP

- Advanced dependency graphs.
- Multi-level configurable workflow engine.
- Capacity planning.
- Sprint planning.
- Generic roadmap management.
- Marketplace for agents/tools.
- Full runtime observability console.
- Secret management.
- Automatic task decomposition beyond Bolt-provided plans.

## Canonical Execution and Completion Policy

### Execution mode

```text
disabled
planning_only
trusted_execution
```

MVP may use `trusted_execution`: `rumble-crew` can request real execution through `cos-matic`, but still never executes directly and never owns runtime credentials.

### Completion mode

```text
manual_review_required
auto_close_if_evidence_valid
auto_close_if_run_succeeded
```

Default is `manual_review_required`.

`auto_close_if_run_succeeded` is allowed only when all are true:

- task is low risk;
- skill card is explicitly `auto_closable=true`;
- workspace is trusted for execution;
- run success comes from trusted `cos-matic` projection;
- no open blocker;
- no pending approval;
- no stale task context;
- auto-close audit event is recorded.

## Canonical Lifecycle

### TaskStatus — product collaboration state

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

### RunStatus — execution state projected from Bolt

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

### ActorStatus — availability/visibility state

```text
available
busy
offline
restricted
unknown
```

Key rule:

> A run can succeed without the task being done unless an explicit completion policy safely auto-closes it. Default behavior remains review-first.

## Primary Views

### Board

Purpose: operational overview.

Shows:

- task cards;
- task status;
- assignee;
- latest run state;
- blocker badge;
- approval pending badge;
- evidence/review state.

### Timeline

Purpose: audit and collaboration history.

Shows:

- task creation;
- assignment changes;
- run requests and projections;
- blockers;
- comments;
- approvals;
- evidence submissions/reviews;
- rerun/fail/cancel decisions.

### Run Detail

Purpose: inspect one execution attempt without turning Rumble into the runtime console.

Shows:

- `RunRef`;
- runtime reference;
- summarized state;
- gate requests;
- evidence references;
- failure context;
- safe logs or linked artifacts when allowed.

## Dependencies on Bolt/Wrench/Gear

### Bolt / `cos-matic`

- Agent task run requests.
- Run lifecycle projections.
- Gate/approval synchronization.
- Execution failure context.
- Execution evidence references.

### Wrench

- Inspection reports as evidence.
- Validation/audit outputs attached to tasks.

### Gear

- Artifact storage and provenance.
- Event log / audit substrate candidate.
- Safe references to stored outputs.
- Possible workspace/source/artifact primitives.

## Success Metrics

- A user can assign an agentic task with expected evidence in under 2 minutes.
- Every active task visibly answers: who owns it, what is blocking it, and what evidence exists.
- No task can be marked done without accepted evidence or explicit completion approval.
- Users can distinguish task status from run status in UI and audit export.
- Failed runs have a visible recovery path: rerun, reassign, fail, or cancel.
- Human approval decisions are tied to exact target versions and appear in the timeline.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Becoming a generic PM tool | High | Limit MVP to agentic task supervision: blockers, approvals, evidence, run refs. |
| Reimplementing `cos-matic` | High | Treat runs as external projections; never plan/sequence execution in Rumble. |
| Unsafe real execution from MVP | High | Require `trusted_execution`, idempotency, audit, approval policy, and kill switch. |
| Unsafe auto-close | High | Allow only explicit low-risk auto-closable tasks with no blockers/approvals/stale context. |
| Raw runtime log leakage | Critical | Raw logs privileged-only, disabled by default, audited, TTL-limited, non-indexed. |
| Confusing agent and runtime identity | High | Model `AgentProfile`, `RuntimeRef`, and `ActorRef` separately. |
| Accepting unverifiable evidence | High | Evidence requires provenance/reference and human review status. |
| Overbuilding approval workflows | Medium | MVP supports only four approval types. |
| Leaking secrets through run detail | High | Store safe references only; no credentials/raw sensitive logs by default. |

## Post-MVP Scope

- Cross-workspace agent workload summaries.
- More advanced notification rules.
- Configurable approval policy templates.
- Task dependency visualization if needed by agentic work.
- Rich audit exports.
- Shared capability registry integration.
- Offline/local-first board mode if required by deployment target.
- More detailed run observability, still sourced from Bolt.

## Initial Spec Files

- `00-product-charter.md` — product boundary and MVP framing.
- `01-personas-and-roles.md` — humans, agents, runtime service accounts, system roles.
- `02-user-journeys.md` — assign, block, approve, review evidence, rerun/fail/cancel.
- `05-domain-model.md` — initial domain model and lifecycle decisions.

## Open Questions

Canonical open questions are maintained in `12-open-questions.md`.

Key remaining pre-implementation questions:

| Question | Impact | Current direction |
| --- | --- | --- |
| Exact `cos-matic` integration authentication | High | Service auth with rotation, replay protection, source event IDs, timestamp freshness. |
| Task context hashing/versioning | High | Define canonical serialization before implementation. |
| Gear evidence extraction format | High | Rumble local fallback must be extractable and hash-verified. |
| Raw log redaction baseline | High | Minimum scanner before privileged raw display/export. |
