# Data Model — rumble-crew

## Scope

This document defines the MVP data model for `rumble-crew` after the product decisions:

- MVP may request real execution through `cos-matic`.
- Auto-close is supported only through explicit `completion_policy`.
- Evidence may be stored locally in Rumble only when no suitable Gear backend exists, and must be extractable.
- Skill cards may be local or synced from `cos-matic`.
- Current-state tables are mutable, while critical audit events are append-only.
- Raw runtime logs may be stored/displayed only as privileged sensitive data.
- Parallel runs are post-MVP unless an explicit policy enables them later.
- Failed runs require human recovery decision by default.

---

## Data Model Principles

1. Separate current state from audit history.
2. Keep runtime secrets out of Rumble tables.
3. Store safe references to external artifacts/runtimes whenever possible.
4. If local evidence storage is used, make extraction to Gear a first-class migration path.
5. Treat raw logs as sensitive, non-indexed, access-audited data.
6. Never infer human approval from agent/runtime/system actors.
7. Use optimistic concurrency on mutable business records.

---

## Enumerations

### `task_status`

```text
created, assigned, ready, in_progress, blocked, in_review, done, failed, cancelled
```

### `run_status`

```text
queued, claimed, running, waiting_for_approval, succeeded, failed, cancelled, unknown
```

### `execution_mode`

```text
disabled, planning_only, trusted_execution
```

### `completion_mode`

```text
manual_review_required,
auto_close_if_evidence_valid,
auto_close_if_run_succeeded
```

### `artifact_storage_backend`

```text
rumble_local, gear, external
```

### `log_visibility`

```text
none, summary, redacted_raw, privileged_raw
```

---

## Table: `workspaces`

### Columns

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable workspace ID. |
| `name` | text not null | Human-readable. |
| `slug` | text not null | Unique per account/profile. |
| `status` | text not null | `active`, `archived`. |
| `execution_mode` | text not null | Default `planning_only`; MVP can use `trusted_execution`. |
| `raw_logs_enabled` | boolean not null | Default false. Required for privileged raw logs. |
| `approval_policy` | jsonb not null | Four fixed types with simple rules. |
| `default_completion_mode` | text not null | Default `manual_review_required`. |
| `evidence_storage_policy` | jsonb not null | Backend preference + extraction settings. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |
| `archived_at` | timestamptz null | Archive. |
| `version` | bigint not null | Optimistic concurrency. |

### Indexes

- unique `(slug)` within account/profile scope.
- `(status)`.

### Constraints

- `execution_mode in ('disabled','planning_only','trusted_execution')`.
- `default_completion_mode in (...)`.
- `raw_logs_enabled=false` unless `execution_mode='trusted_execution'`.

### RLS/Auth Rules

- Owners can update settings.
- Non-owners read only allowed workspace summary.
- Archived workspace is read-only except export/restore.

### PII Classification

Workspace name may contain personal/client data: **internal/confidential**.

### Retention

Archived workspaces retained according to workspace policy; hard delete blocked while audit/evidence retention applies.

---

## Table: `workspace_members`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `workspace_id` | uuid fk | Parent. |
| `actor_id` | text not null | External/local actor ID. |
| `actor_type` | text not null | `human`, `agent`, `system`, `runtime_service`, `external`. |
| `display_name_snapshot` | text null | Audit readability. |
| `source` | text null | Identity source. |
| `roles` | text[] not null | Product roles. |
| `status` | text not null | `invited`, `active`, `suspended`, `removed`. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |

### Indexes

- `(workspace_id, actor_id)` unique for active/suspended/invited rows.
- `(workspace_id, status)`.

### Constraints

- At least one active human owner per workspace enforced transactionally.
- `runtime_service` and `agent` cannot have owner role.

### PII Classification

Actor display names: **personal data**.

---

## Table: `boards`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `workspace_id` | uuid fk | Parent. |
| `name` | text not null | Human label. |
| `view_mode` | text not null | `status_board`, `assignee_board`, `review_queue`, `blocked_queue`. |
| `filters` | jsonb null | Saved system filters. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |

MVP boards are views; task lifecycle state stays in `tasks`.

---

## Table: `tasks`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable task ID. |
| `workspace_id` | uuid fk | Parent. |
| `title` | text not null | May contain sensitive data. |
| `description` | text null | Context. |
| `goal` | text not null | Desired outcome. |
| `constraints` | jsonb null | Bounded execution constraints. |
| `expected_evidence` | jsonb null | Expected proof. |
| `status` | text not null | `task_status`. |
| `priority` | text null | Optional. |
| `risk_level` | text null | `low`, `medium`, `high`, `critical`. |
| `completion_mode` | text not null | Per-task mode; defaults from workspace/skill. |
| `auto_close_reason` | text null | Set when auto-closed. |
| `created_by_actor` | jsonb not null | ActorRef snapshot. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |
| `closed_at` | timestamptz null | Done/failed/cancelled time. |
| `closed_by_actor` | jsonb null | Human or system auto-close actor. |
| `version` | bigint not null | Optimistic concurrency. |

### Indexes

- `(workspace_id, status)`.
- `(workspace_id, risk_level)`.
- `(workspace_id, updated_at desc)`.
- Full-text search only over title/summary fields, not raw logs.

### Constraints

- `done` requires accepted evidence or valid auto-close event.
- `failed`/`cancelled` require reason via activity event.
- `auto_close_if_run_succeeded` allowed only for low-risk trusted skill/task policy.

### PII Classification

Task title/description/goal/context: **potentially confidential/personal**.

### Soft Delete / Archive

No hard delete in MVP once task has runs, evidence, approvals, or audit events. Use archive/redaction policy.

---

## Table: `task_assignments`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `task_id` | uuid fk | Parent task. |
| `assignee_type` | text not null | `human`, `agent_profile`, `role`. |
| `assignee_ref` | text not null | Member/profile/role reference. |
| `skill_card_id` | uuid fk null | Required for agent execution when configured. |
| `status` | text not null | `proposed`, `active`, `completed`, `revoked`, `superseded`. |
| `assigned_by_actor` | jsonb not null | ActorRef. |
| `assigned_at` | timestamptz not null | Audit. |
| `superseded_at` | timestamptz null | Audit. |

### Indexes

- `(task_id, status)`.
- Partial unique active assignment if MVP allows one active assignment.

---

## Table: `agent_profiles`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `workspace_id` | uuid fk | Parent. |
| `name` | text not null | Human label. |
| `description` | text null | Capability summary. |
| `status` | text not null | `active`, `disabled`, `deprecated`, `unknown`. |
| `actor_ref` | jsonb not null | Agent actor snapshot. |
| `runtime_ref_id` | uuid fk null | Default runtime. |
| `source` | text not null | `local`, `cos_matic`. |
| `source_id` | text null | External source ID. |
| `capabilities_hash` | text null | Drift detection. |
| `last_synced_at` | timestamptz null | Sync status. |
| `drift_status` | text null | `current`, `drifted`, `unknown`. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |

### Constraints

- Disabled/deprecated agents cannot receive new run requests.
- Drifted synced agents require confirmation or block execution per policy.

---

## Table: `runtime_refs`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Local safe reference. |
| `workspace_id` | uuid fk | Parent. |
| `provider` | text not null | MVP: `cos-matic`. |
| `external_runtime_id` | text null | Opaque. |
| `display_name` | text null | Safe label. |
| `status` | text not null | `available`, `unavailable`, `restricted`, `unknown`. |
| `capabilities_hash` | text null | Drift detection. |
| `last_seen_at` | timestamptz null | Sync. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |

### Constraints

- No secrets, tokens, keys, env vars, command credentials.
- Runtime unavailable blocks trusted execution unless queue policy explicitly permits.

---

## Table: `skill_cards`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `workspace_id` | uuid fk | Parent. |
| `name` | text not null | Label. |
| `description` | text not null | Capability summary. |
| `input_requirements` | jsonb not null | Required context. |
| `output_expectations` | jsonb not null | Expected evidence/output. |
| `risk_notes` | text null | Risks. |
| `required_permissions` | text[] null | Abstract permissions. |
| `approval_requirements` | text[] null | start/scope/risk/completion. |
| `compatible_runtime_refs` | uuid[] null | Safe refs. |
| `status` | text not null | `active`, `disabled`, `deprecated`. |
| `source` | text not null | `local`, `cos_matic`. |
| `source_id` | text null | External capability ID. |
| `capabilities_hash` | text null | Drift detection. |
| `last_synced_at` | timestamptz null | Sync. |
| `drift_status` | text null | `current`, `drifted`, `unknown`. |
| `auto_closable` | boolean not null | Default false. |
| `allowed_completion_modes` | text[] not null | Completion modes permitted. |
| `parallel_runs_policy` | text not null | MVP default `disabled`. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Audit. |

### Constraints

- Active skill cards require input/output declarations.
- `auto_closable=true` allowed only if output expectations and risk constraints are present.
- `auto_close_if_run_succeeded` may be allowed only for low-risk tasks and trusted execution.

---

## Table: `run_refs`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Local run ref. |
| `task_id` | uuid fk | Parent task. |
| `bolt_provider` | text not null | MVP: `cos-matic`. |
| `external_run_id` | text null | Opaque Bolt ID. |
| `runtime_ref_id` | uuid fk null | Runtime ref. |
| `status` | text not null | RunStatus. |
| `attempt_number` | integer not null | Monotonic per task. |
| `requested_by_actor` | jsonb not null | Human requester. |
| `request_payload_hash` | text null | Integrity. |
| `previous_run_ref_id` | uuid fk null | Rerun lineage. |
| `started_at` | timestamptz null | Projection. |
| `finished_at` | timestamptz null | Projection. |
| `sync_status` | text not null | `current`, `stale`, `sync_failed`, `unknown`. |
| `recovery_state` | text null | `none`, `needs_decision`, `rerun_requested`, `failed_accepted`, `cancelled`. |
| `created_at` | timestamptz not null | Audit. |
| `updated_at` | timestamptz not null | Projection update. |

### Indexes

- `(task_id, attempt_number)` unique.
- `(task_id, status)`.
- `(external_run_id)` where not null.

### Constraints

- One active run per task in MVP unless explicit post-MVP policy enables parallel runs.
- Failed run sets or implies `recovery_state='needs_decision'` by default.
- Historical run refs are not deleted.

---

## Table: `approvals`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `task_id` | uuid fk | Parent task. |
| `run_ref_id` | uuid fk null | Linked run. |
| `type` | text not null | `start`, `scope`, `risk`, `completion`. |
| `target_type` | text not null | task/run/blocker/evidence/rerun. |
| `target_id` | text not null | Target. |
| `target_version_hash` | text not null | Stale protection. |
| `status` | text not null | requested/approved/rejected/expired/superseded/sync_failed. |
| `risk_level` | text null | Risk. |
| `request_summary` | text not null | Human-readable. |
| `requested_by_actor` | jsonb not null | ActorRef. |
| `decided_by_actor` | jsonb null | Must be human for decisions. |
| `decision_reason` | text null | Required for rejection/high risk. |
| `conditions` | jsonb null | Conditions. |
| `expires_at` | timestamptz null | Optional. |
| `created_at` | timestamptz not null | Audit. |
| `decided_at` | timestamptz null | Audit. |
| `version` | bigint not null | Concurrency. |

### Constraints

- Approved/rejected requires `decided_by_actor.actor_type='human'`.
- Rejected requires reason.
- Expired/superseded approvals do not unblock work.
- Decision rows are immutable after decided except sync status through explicit event.

---

## Table: `blockers`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `task_id` | uuid fk | Parent task. |
| `run_ref_id` | uuid fk null | Linked run. |
| `type` | text not null | missing_context/approval_required/permission/tool_failure/runtime_unavailable/scope_ambiguity/external_dependency/other. |
| `severity` | text not null | `info`, `warning`, `blocking`. |
| `status` | text not null | `open`, `resolved`, `rejected`, `superseded`. |
| `summary` | text not null | Human-readable. |
| `details` | jsonb null | Safe details. |
| `reported_by_actor` | jsonb not null | ActorRef. |
| `resolver_ref` | jsonb null | Expected resolver. |
| `resolution` | text null | Required when resolved/rejected. |
| `created_at` | timestamptz not null | Audit. |
| `resolved_at` | timestamptz null | Audit. |

### Constraints

- Open blocking blockers prevent task done and auto-close.
- Resolution/rejection requires rationale.

---

## Table: `evidence`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `task_id` | uuid fk | Parent task. |
| `run_ref_id` | uuid fk null | Producing run. |
| `type` | text not null | log/diff/test_report/screenshot/artifact/decision_record/inspection_report/other. |
| `status` | text not null | submitted/accepted/rejected/superseded. |
| `summary` | text not null | Human-readable. |
| `artifact_ref` | jsonb null | Gear/external/local ref. |
| `storage_backend` | text not null | rumble_local/gear/external. |
| `content_hash` | text null | Integrity. |
| `provenance_ref` | jsonb null | Optional provenance pointer. |
| `extractable` | boolean not null | True for local evidence. |
| `migration_status` | text not null | `not_needed`, `pending`, `exported`, `verified`, `failed`. |
| `produced_by_actor` | jsonb not null | ActorRef. |
| `reviewed_by_actor` | jsonb null | Human reviewer or system auto-close actor. |
| `review_reason` | text null | Required for rejection. |
| `created_at` | timestamptz not null | Audit. |
| `reviewed_at` | timestamptz null | Audit. |
| `version` | bigint not null | Concurrency. |

### Constraints

- Rejected requires reason.
- Accepted evidence requires accessible artifact/provenance or explicit policy exception.
- Local evidence must be marked extractable and have migration status.
- Superseded evidence remains available for audit until retention expires.

---

## Table: `evidence_blobs_local`

Temporary local evidence storage when no suitable Gear backend exists.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Blob ID. |
| `evidence_id` | uuid fk unique | Parent evidence. |
| `workspace_id` | uuid fk | Partitioning/access. |
| `content_type` | text not null | MIME/safe type. |
| `byte_size` | bigint not null | Size. |
| `storage_path` | text null | Internal path/object key. |
| `encrypted` | boolean not null | Must be true in hosted/multi-user mode. |
| `content_hash` | text not null | Integrity. |
| `created_at` | timestamptz not null | Audit. |
| `expires_at` | timestamptz null | Retention/TTL. |
| `exported_artifact_ref` | jsonb null | Gear ref after extraction. |

### Constraints

- Not searched by default.
- Must support export to Gear-compatible bundle.
- Must not store runtime secrets intentionally.

---

## Table: `runtime_logs`

Sensitive raw or redacted logs linked to runs.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Stable ID. |
| `workspace_id` | uuid fk | Parent. |
| `run_ref_id` | uuid fk | Linked run. |
| `visibility` | text not null | none/summary/redacted_raw/privileged_raw. |
| `summary` | text null | Safe summary. |
| `raw_storage_backend` | text null | rumble_local/gear/external. |
| `raw_artifact_ref` | jsonb null | Raw log reference. |
| `redaction_status` | text not null | not_applicable/pending/redacted/failed. |
| `contains_sensitive_markers` | boolean not null | Scanner result. |
| `content_hash` | text null | Integrity. |
| `created_at` | timestamptz not null | Audit. |
| `expires_at` | timestamptz null | TTL strongly recommended. |

### Constraints

- Raw logs require workspace `raw_logs_enabled=true` and `execution_mode='trusted_execution'`.
- Raw logs are never full-text indexed.
- Access to privileged raw logs emits `runtime_log_accessed` critical audit event.
- Raw logs export requires explicit sensitive export permission.

---

## Table: `activity_events`

Append-only audit/timeline table.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Event ID. |
| `workspace_id` | uuid fk | Parent. |
| `task_id` | uuid fk null | Related task. |
| `event_type` | text not null | Canonical event name. |
| `actor` | jsonb not null | ActorRef. |
| `source` | text not null | rumble_crew/cos_matic/gear/wrench/system. |
| `target_type` | text null | Target. |
| `target_id` | text null | Target. |
| `payload` | jsonb null | Safe payload only. |
| `source_event_id` | text null | Integration idempotency. |
| `integrity_hash` | text null | Optional. |
| `redaction` | jsonb null | Redaction metadata. |
| `occurred_at` | timestamptz not null | Event time. |
| `received_at` | timestamptz not null | Ingestion time. |

### Indexes

- `(workspace_id, occurred_at desc)`.
- `(task_id, occurred_at desc)`.
- unique `(source, source_event_id)` where source_event_id is not null.
- `(event_type)`.

### Constraints

- Append-only for critical events.
- Corrections use superseding events.
- Raw logs/secrets not copied into payload.

---

## Table: `comments`

MVP may store threads/comments simply.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid pk | Comment ID. |
| `workspace_id` | uuid fk | Parent. |
| `target_type` | text not null | task/blocker/approval/evidence/run_ref. |
| `target_id` | text not null | Target. |
| `author_actor` | jsonb not null | ActorRef. |
| `body` | text not null | Comment. |
| `created_at` | timestamptz not null | Audit. |
| `edited_at` | timestamptz null | Optional edit window. |
| `deleted_at` | timestamptz null | Soft delete/redaction. |

---

## Table: `idempotency_keys`

| Column | Type | Notes |
| --- | --- | --- |
| `workspace_id` | uuid | Scope. |
| `actor_id` | text | Actor. |
| `key` | text | Client key. |
| `request_hash` | text | Prevent key reuse with different payload. |
| `response_ref` | jsonb | Existing result. |
| `created_at` | timestamptz | Audit. |
| `expires_at` | timestamptz | TTL. |

Primary key: `(workspace_id, actor_id, key)`.

---

## RLS / Authorization Summary

| Object | Read | Write |
| --- | --- | --- |
| Workspace | active members | owners/settings roles |
| Task | members with task visibility | creator/assignee/supervisor/owner by action |
| RunRef | task-visible members, redacted | integration/system for projections; humans for requests/cancel |
| Approval | target-visible members | human approvers only for decisions |
| Evidence | target-visible members | producers can submit; reviewers decide |
| Raw logs | privileged roles only | trusted integration/system only |
| ActivityEvent | target-visible members | system/integration/application only |
| Settings | owners/admin roles | owners only |

---

## Migration Strategy

1. Start with Rumble-owned tables and local evidence storage interface.
2. Keep `artifact_ref`, `storage_backend`, `provenance_ref`, `extractable`, and `migration_status` from day one.
3. When Gear backend matures, add Gear writer implementation.
4. Migrate `evidence_blobs_local` to Gear artifacts in batches.
5. Verify hashes, update `evidence.artifact_ref`, set `migration_status='verified'`.
6. Retain or purge local blobs according to retention policy.

---

## Acceptance Tests

- Given trusted execution disabled, run request cannot start execution.
- Given low-risk auto-closable task with trusted run success and no blockers, task can auto-close with audit event.
- Given high-risk task, run success never auto-closes without completion approval/review.
- Given local evidence exists, export/migration fields are populated.
- Given raw log is accessed, `runtime_log_accessed` event is appended.
- Given duplicate `source_event_id`, inbound event is idempotent.
- Given actor type agent, approval decision is rejected.
