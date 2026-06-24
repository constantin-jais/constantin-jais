# Implementation Plan — rumble-crew MVP

## Scope

This plan turns the accepted `rumble-crew` MVP spec into implementable slices.

Primary implementation rule:

> Build the agentic supervision loop first: task → assignment → trusted run request → projection → approval/blocker/evidence → done/rerun/cancel.

Do not implement generic project management features or a runtime console.

---

## MVP Milestone 0 — Pre-implementation Decisions

Resolve before coding core flows:

1. `cos-matic` integration authentication:
   - service token/mTLS/signature choice;
   - rotation plan;
   - replay window;
   - `source_event_id` uniqueness rules.
2. Task context hash canonicalization:
   - stable JSON serialization;
   - included/excluded fields;
   - hash algorithm.
3. Raw log storage mode:
   - metadata in DB;
   - raw body in object/blob/external ref;
   - TTL default.
4. Local evidence export format toward Gear.
5. Critical `activity_events` append-only enforcement mechanism.

Deliverable: short ADR or implementation notes for each.

---

## MVP Milestone 1 — Core Data and Auth Foundation

### Build

- Workspace model with `execution_mode`, `approval_policy`, `raw_logs_enabled`.
- Workspace members and role checks.
- ActorRef snapshots.
- Task table and lifecycle transitions.
- ActivityEvent append-only write path.
- Idempotency key table.

### Acceptance

- Workspace owner/member permissions work.
- Agent/runtime/system actors cannot approve.
- Archived workspace is read-only.
- Critical activity events append and cannot be silently mutated.

### Tests

- Permission matrix tests.
- Actor type enforcement.
- Idempotency key reuse conflict.

---

## MVP Milestone 2 — Board and Task UX

### Build

- Board query/read model.
- Task create/edit/detail screens.
- Task assignment to human or agent profile.
- Comments or minimal task discussion.
- Status columns and attention badges.

### Acceptance

- Board shows task status and latest run status separately.
- Task detail shows goal, constraints, assignment, blockers, approvals, evidence, timeline.
- No raw logs/evidence blobs loaded in board query.

### Tests

- Board smoke.
- Task create validation.
- Task/run status separation.

---

## MVP Milestone 3 — Agents, Skills, RuntimeRef

### Build

- AgentProfile CRUD/projection.
- SkillCard CRUD/projection.
- RuntimeRef safe metadata.
- Capability sync placeholder from `cos-matic` if available.
- Drift fields: `source`, `source_id`, `capabilities_hash`, `last_synced_at`, `drift_status`.

### Acceptance

- Disabled skill/agent cannot receive new run request.
- Drifted skill warns or blocks according to policy.
- RuntimeRef stores no secrets.

### Tests

- Skill compatibility validation.
- RuntimeRef no-secret invariant.
- Drift warning UI.

---

## MVP Milestone 4 — Trusted Run Requests and `cos-matic` Projection

### Build

- `POST /tasks/{task_id}/run-requests`.
- `RunRef` creation.
- `crew.cosmatic.run_request.v0.1` outbound payload.
- Inbound `POST /integrations/cos-matic/events`.
- Event types:
  - run status changed;
  - gate requested;
  - blocker reported;
  - evidence produced;
  - run failed/cancelled.

### Acceptance

- `execution_mode=disabled` blocks execution.
- `planning_only` cannot send execution-capable request.
- `trusted_execution` can send execution-capable request when policy passes.
- Duplicate inbound event is idempotent.
- Unknown task/run event cannot mutate unrelated state.

### Tests

- Run request idempotency.
- Integration auth failure.
- Duplicate `source_event_id`.
- Failed run → recovery decision.

---

## MVP Milestone 5 — Approvals and Blockers

### Build

- Approval request/detail/decision.
- Approval sync to `cos-matic` with retry and `sync_failed`.
- Blocker create/resolve/reject/supersede.
- Review Queue sections for approvals and blockers.

### Acceptance

- Human-only approvals enforced.
- Stale target approval blocked.
- Open blocking blocker prevents done and auto-close.
- Approval sync failure visible and retryable.

### Tests

- Agent cannot approve.
- Runtime service cannot approve.
- Stale approval target blocked.
- Blocker prevents completion.

---

## MVP Milestone 6 — Evidence and Completion Policy

### Build

- Evidence create/detail/review.
- Local evidence fallback with extraction metadata.
- Evidence artifact availability check abstraction.
- Completion policy:
  - manual review;
  - auto-close if evidence valid;
  - auto-close if run succeeded.
- Auto-close audit events.

### Acceptance

- Run success default goes to review.
- Low-risk trusted auto-closable task can auto-close.
- High/critical risk task cannot auto-close.
- Local evidence has `storage_backend`, `content_hash`, `extractable`, `migration_status`.

### Tests

- Auto-close allowed scenario.
- Auto-close blocked reasons.
- Evidence unavailable cannot be accepted by default.
- Local evidence migration metadata.

---

## MVP Milestone 7 — Runtime Logs and Audit Exports

### Build

- RuntimeLog metadata.
- Summary/redacted/privileged raw access endpoint.
- Raw log access audit event.
- Raw log TTL metadata.
- Timeline and audit export with redaction markers.

### Acceptance

- Raw logs disabled blocks owner too.
- Privileged raw access requires permission and emits `runtime_log_accessed`.
- Raw log body is never copied into audit event.
- Normal audit export excludes raw bodies.
- Raw logs are not indexed.

### Tests

- Raw logs disabled.
- Raw access audited.
- Search does not find raw log body.
- Audit export excludes raw body.

---

## MVP Milestone 8 — Recovery, Cancel, Rerun

### Build

- Recovery queue for failed runs.
- Rerun request flow.
- Cancel run/task flow.
- Mark task failed with reason.
- Attempt lineage via `previous_run_ref_id`.

### Acceptance

- Failed run does not auto-fail task.
- Human chooses rerun/reassign/fail/cancel.
- Rerun creates new RunRef linked to previous attempt.
- Active run blocks duplicate run by default.

### Tests

- Failed run recovery decision.
- Rerun lineage.
- One active run invariant.
- Cancel sync visibility.

---

## MVP Milestone 9 — Hardening and Acceptance Sweep

### Build

- Observability metrics/alerts.
- Backup/restore basic validation.
- Read model recomputation.
- Security/RGPD review.
- NFR performance checks.

### Acceptance

- All minimum acceptance tests in `11-acceptance-tests.md` pass.
- Board query does not load blobs/logs.
- Restore marks run projections stale.
- No credentials stored in Rumble tables.

---

## Suggested Initial Issues

1. Define `cos-matic` auth and event signature/replay contract.
2. Define task context hash canonicalization.
3. Create database schema for workspaces/members/tasks/activity/idempotency.
4. Implement permission middleware and ActorRef snapshots.
5. Implement task create/detail/board read model.
6. Implement AgentProfile/SkillCard/RuntimeRef models.
7. Implement run request endpoint with `trusted_execution` gate.
8. Implement inbound `cos-matic` event ingestion with idempotency.
9. Implement approval request/decision/sync.
10. Implement blocker workflow.
11. Implement evidence records and local fallback interface.
12. Implement completion policy and auto-close audit.
13. Implement runtime log metadata and privileged access audit.
14. Implement review queue.
15. Implement failed-run recovery and rerun lineage.
16. Implement audit export with redaction markers.
17. Run acceptance test suite from `11-acceptance-tests.md`.

---

## Explicit Non-Goals for MVP Implementation

- Generic sprint/roadmap/capacity planning.
- Workflow builder.
- Marketplace/install flow.
- Full runtime console or arbitrary command execution.
- Raw log analytics/search.
- Parallel run writes without explicit post-MVP policy.
- Full local-first collaboration.

---

## Definition of Done

MVP is implementation-ready when:

- pre-implementation decisions are resolved;
- core data model has migrations/RLS/auth checks;
- Bolt integration contract has tests and replay protection;
- security tests for execution/raw logs/approvals pass;
- acceptance tests cover task → run → review/evidence → completion/recovery;
- audit exports and event timeline are inspectable;
- local evidence fallback can be extracted to Gear-compatible artifacts.
