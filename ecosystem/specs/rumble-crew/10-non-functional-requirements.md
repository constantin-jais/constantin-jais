# Non-Functional Requirements — rumble-crew

## Scope

This document defines MVP non-functional requirements for `rumble-crew`.

The most sensitive requirements concern:

- real execution requests to `cos-matic` through `trusted_execution`;
- task auto-close policy;
- local evidence fallback and extraction toward Gear;
- privileged raw runtime logs;
- audit/event replay;
- degraded integration behavior.

---

## Security

### Requirements

- New execution requests require `workspace.execution_mode='trusted_execution'`.
- Rumble must never store runtime credentials, private keys, tokens, or execution secrets.
- `RuntimeRef` must contain safe opaque references only.
- Human approvals require `actor_type='human'`.
- Integration events from `cos-matic` require authentication, schema validation, replay protection, and target validation.
- Raw runtime logs are disabled by default.
- Raw runtime logs require privileged permission, explicit workspace enablement, audit event, TTL, and non-indexing.
- Auto-close requires explicit policy and cannot apply to high/critical risk tasks.

### Acceptance Targets

- 100% of mutating endpoints enforce permission checks.
- 100% of approval decisions have human actor attribution.
- 100% of privileged raw log reads append `runtime_log_accessed`.
- 0 known runtime credentials stored in Rumble-owned tables.

---

## Privacy / RGPD

### Requirements

- Task context, comments, evidence summaries, and logs are confidential by default.
- Raw logs are treated as sensitive/high-risk.
- Personal display names and actor references are exportable/redactable according to policy.
- Audit events are corrected through superseding events, not silent mutation.
- Evidence stored locally must have retention and migration metadata.
- Raw logs must have short TTL by default.
- Normal audit exports exclude raw log bodies unless explicit sensitive export is requested and authorized.

### Default Retention Targets

| Data | Target |
| --- | --- |
| Idempotency keys | 30 days max unless operational need differs. |
| Integration dedupe IDs | 30–90 days. |
| Raw runtime logs | 7 days default for hosted/multi-user; configurable downward/upward by owner policy. |
| Activity events | Workspace audit retention. |
| Approval/evidence decisions | Workspace audit retention. |
| Local evidence blobs | Until Gear migration or retention expiry. |

---

## Availability and Degraded Mode

### Requirements

- Board and task detail should remain readable with last known state when `cos-matic` is unavailable.
- If Bolt sync is stale, UI must show stale/unknown run status.
- Execution requests must fail safely when integration is unavailable unless queue policy explicitly permits pending requests.
- Approval decisions are recorded locally before external sync; sync failure is visible and retryable.
- Inbound integration event replay must be idempotent.

### Degraded Behaviors

| Condition | Required behavior |
| --- | --- |
| `cos-matic` unavailable | Show last known run state; block/queue new execution per policy. |
| Gear unavailable | Existing evidence refs show unavailable; local fallback only if configured. |
| Raw log scanner fails | Do not silently expose raw logs to unprivileged users. |
| Timeline partial load | Show partial timeline with explicit load error. |
| Approval sync failed | Keep local decision immutable; show `sync_failed`; retry. |

---

## Performance

### MVP Targets

| Operation | Target |
| --- | --- |
| Board load for 500 visible tasks | p95 < 1.5s server-side query, excluding network. |
| Task detail load | p95 < 800ms for metadata without large artifacts/logs. |
| Review queue load | p95 < 1s for 500 pending items. |
| Timeline page load | p95 < 1s for 100 events page. |
| Inbound integration event ingestion | p95 < 300ms excluding downstream artifact checks. |
| Run request local creation | p95 < 500ms excluding external `cos-matic` call. |

### Constraints

- Raw logs and evidence blobs are never loaded into board queries.
- Raw logs are not full-text indexed.
- Evidence artifact previews are lazy-loaded.
- Timeline is paginated.

---

## Scalability

### MVP Scale Assumptions

- Up to 50 active workspace members.
- Up to 5,000 tasks per workspace.
- Up to 50,000 activity events per workspace before archive/export pressure appears.
- Up to 10 runs per task in normal use.
- One active run per task by default.

### Requirements

- Index task status, run status, review queues, and timeline pagination keys.
- Use cursor pagination for timeline and large lists.
- Use summary/read models for board cards.
- Keep evidence/log blobs outside hot relational rows.

---

## Observability

### Requirements

Emit metrics/logs/traces for:

- run request count/result/latency;
- `cos-matic` integration availability;
- inbound event ingestion count/rejection/duplicates;
- approval sync failures;
- evidence artifact availability failures;
- raw log access count;
- auto-close success/block reason;
- task transition failures;
- permission denials;
- idempotency key conflicts.

### Critical Alerts

- Spike in `approval_sync_failed`.
- Repeated inbound event auth failures.
- Raw log access anomaly.
- Execution requests attempted while `execution_mode=disabled`.
- Auto-close blocked due to stale context repeatedly.

---

## Auditability

### Requirements

- Critical events are append-only where possible.
- Corrections use superseding events.
- Every task terminal transition records actor, reason/policy, and source.
- Auto-close terminal transitions record policy decision details.
- Runtime log access records metadata but never log body.
- Audit export includes redaction markers and omitted sensitive-data markers.

### Critical Events

- `approval_granted`
- `approval_rejected`
- `evidence_accepted`
- `evidence_rejected`
- `task_marked_done`
- `task_cancelled`
- `task_marked_failed`
- `bolt_run_requested`
- `runtime_log_accessed`
- `auto_close_applied`
- `auto_close_blocked`

---

## Accessibility

### Requirements

- Board must be navigable without drag/drop.
- Status/risk/approval state must not rely on color alone.
- Review decisions require clear labels and confirmations.
- Timeline events must have semantic grouping.
- Forms expose validation errors programmatically.
- Raw log views must support text wrapping, search within displayed content, and keyboard navigation without forcing full-page lock.

### Target

WCAG 2.2 AA for MVP UI where applicable.

---

## Offline / Local-First Behavior

### MVP Requirement

`rumble-crew` is not required to be fully local-first in MVP because trusted execution and integration sync are central.

### Required Offline/Degraded Behavior

- Last known board/task/timeline may be readable if cached.
- Mutations that affect execution, approvals, evidence review, or raw logs are disabled offline.
- Local drafts for task creation may be supported but must not auto-submit execution when connection returns without user confirmation.

---

## Portability / Self-Hosting

### Requirements

- Core truth must be self-hostable.
- No mandatory dependency on US hyperscalers.
- `cos-matic` integration endpoint must be configurable.
- Gear/Wrench integrations must be optional and replaceable by local/external adapters.
- Local evidence fallback must not prevent migration to Gear.

---

## Backup and Restore

### Requirements

Backup must include:

- relational task/workspace state;
- activity events;
- approvals/evidence review records;
- idempotency state if needed for operational continuity;
- local evidence blobs if used;
- runtime log metadata and raw log storage if retention requires.

Restore must preserve:

- IDs;
- event ordering;
- content hashes;
- migration status;
- audit integrity metadata where available.

### Restore Risk

After restore, integration sync with `cos-matic` may be stale. UI must show stale/unknown state until resynced.

---

## Disaster Recovery

### Requirements

- Run projections can be resynced from `cos-matic` when available.
- Local human decisions remain source of truth for Rumble audit even if sync failed.
- Failed or duplicate inbound events must not corrupt state.
- Recovery tooling should recompute board/read models from task tables and activity events.

---

## Cost Constraints

### Requirements

- Do not store raw logs indefinitely.
- Do not index raw logs.
- Keep large artifacts outside hot DB rows.
- Prefer references/hashes over copied blobs.
- Provide extraction path to Gear before evidence volume grows.

---

## Internationalization

MVP can use one UI language initially, but domain/event/API enums must remain stable and language-neutral.

User-facing labels should be localizable later.

---

## Acceptance Criteria

- Given `cos-matic` is down, board still displays last known task/run state with stale marker.
- Given raw logs are disabled, raw log access fails even for owner.
- Given raw logs are accessed, audit event is created and raw body is not copied into audit event.
- Given 500 visible tasks, board query meets MVP target without loading evidence/log blobs.
- Given local evidence storage is used, evidence has extraction metadata.
- Given auto-close applies, audit records policy inputs and reason.
- Given auto-close is blocked, UI/timeline can explain why.
