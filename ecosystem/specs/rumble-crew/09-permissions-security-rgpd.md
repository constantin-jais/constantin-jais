# Permissions, Security, RGPD — rumble-crew

## Scope

This document defines MVP permissions, security, privacy, and RGPD requirements for `rumble-crew`.

It encodes the high-risk product decisions:

- real `cos-matic` execution can be requested from MVP;
- some tasks may auto-close after run success through explicit policy;
- raw runtime logs may be accessible to privileged users;
- local evidence storage is temporary/extractable when Gear is not available.

Security priority order:

1. Prevent unauthorized execution.
2. Prevent secrets/PII leakage from task context, logs, artifacts, and exports.
3. Preserve auditability of human decisions and runtime projections.
4. Keep Rumble out of credential/runtime ownership.

---

## Role Model

| Role | Security posture |
| --- | --- |
| Workspace Owner | High privilege. Can configure workspace, execution mode, policies, members, exports. |
| Human Contributor | Limited task creation/editing and own/assigned work. Cannot approve unless granted reviewer role. |
| Reviewer / Approver | Can decide approvals/evidence within scope. Human-only. |
| Agent Supervisor | Can assign agents/request execution if policy allows. Not automatically approver. |
| Agent Identity | Non-human actor. Can report/propose through projection. Cannot approve. |
| Runtime Service Account | Integration actor. Can sync events/evidence/log refs. Cannot approve or own tasks. |
| Observer / Auditor | Read-only, potentially export-capable if explicitly granted. |
| System | Derived state and audit enforcement only. Cannot make human decisions. |

---

## Permission Matrix

| Permission | Owner | Contributor | Reviewer | Agent Supervisor | Agent | Runtime Service | Observer | System |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `workspace:update` | Yes | No | No | No | No | No | No | No |
| `member:manage` | Yes | No | No | No | No | No | No | No |
| `task:create` | Yes | Yes | No | Yes | No | No | No | No |
| `task:update` | Yes | Own/assigned | No | Supervised | No | No | No | No |
| `task:assign` | Yes | Request/limited | No | Yes | No | No | No | No |
| `run:request` | Yes | Delegated only | No | Yes | No | No | No | No |
| `run:cancel` | Yes | Own if policy | No | Yes | No | No | No | No |
| `run:rerun` | Yes | Request/delegated | Request | Yes | No | No | No | No |
| `approval:decide` | Yes | No | Yes | If policy | No | No | No | No |
| `evidence:submit` | Yes | Yes | No | No | Via projection | Via integration | No | No |
| `evidence:review` | Yes | No | Yes | If policy | No | No | No | No |
| `blocker:report` | Yes | Yes | Yes | Yes | Via projection | Via integration | No | Yes |
| `blocker:resolve` | Yes | Own/assigned | Review blockers | Yes | No | No | No | Derived only |
| `logs:summary:read` | Yes | Scoped | Yes | Yes | No | No UI | If granted | No |
| `logs:raw:read` | Privileged only | No | Privileged only | Privileged only | No | No UI | Privileged auditor only | No |
| `audit:export` | Yes | No | If granted | No | No | No | If granted | No |
| `integration:manage` | Yes | No | No | If granted | No | No | No | No |
| `integration:event_ingest` | No | No | No | No | No | Yes | No | Yes |

---

## Execution Security

## Execution Mode

```text
execution_mode = disabled | planning_only | trusted_execution
```

### `trusted_execution` requirements

A workspace may request real execution only if all are true:

- `cos-matic` integration is configured and healthy enough for requests;
- integration authentication is configured;
- idempotency storage is active;
- activity event/audit logging is active;
- approval policy exists;
- RuntimeRef is available or explicit queue policy permits pending requests;
- kill switch exists for disabling new execution requests;
- raw credentials are not stored in Rumble.

### Kill Switch

Owners or platform operators must be able to set:

```text
execution_mode=disabled
```

Effects:

- blocks new run/rerun requests;
- does not delete existing run projections;
- active external runs require separate cancel request to `cos-matic`.

### Authorization Rules

- Rumble may request execution, never execute directly.
- Agent/runtime/system actors cannot request execution as accountable humans.
- High/critical risk tasks require policy-defined approval before execution.
- Drifted `SkillCard`/`AgentProfile` blocks or requires explicit confirmation.

---

## Auto-Close Security

Auto-close is allowed but not global.

```text
completion_mode = manual_review_required | auto_close_if_evidence_valid | auto_close_if_run_succeeded
```

### Default

`manual_review_required`.

### `auto_close_if_run_succeeded` requirements

All must be true:

- workspace `execution_mode='trusted_execution'`;
- task `risk_level='low'`;
- selected `SkillCard.auto_closable=true`;
- skill card allows `auto_close_if_run_succeeded`;
- run status is `succeeded` from trusted `cos-matic` event;
- no open blocking blocker;
- no pending approval;
- no stale target/version conflict;
- no task context change occurred after run request;
- completion audit event records policy and reason.

### `auto_close_if_evidence_valid` requirements

All above, plus evidence reference/hash/provenance or local verified artifact exists.

### Forbidden Auto-Close

- high/critical risk tasks;
- raw-log-only evidence;
- unknown/stale runtime state;
- rejected/superseded evidence;
- task with open blocker;
- task with active approval request.

---

## Runtime Logs Security

Raw runtime logs are high-risk sensitive data.

### Visibility Levels

```text
none
summary
redacted_raw
privileged_raw
```

### Default

- Board/timeline show summaries only.
- Search indexes summaries only.
- Raw logs are disabled unless workspace enables them.

### Privileged Raw Logs Requirements

- Workspace `raw_logs_enabled=true`.
- Workspace `execution_mode='trusted_execution'`.
- Actor has `logs:raw:read`.
- User confirms sensitive access.
- Access emits critical `runtime_log_accessed` activity event.
- Raw logs have TTL/retention policy.
- Raw logs are not included in normal audit exports.
- Raw logs are never indexed in full-text search.

### Secret Detection Baseline

Before display/export, apply best-effort detection/redaction for:

- bearer/API tokens;
- Authorization headers;
- cookies/session IDs;
- private keys;
- SSH keys;
- database DSNs;
- env var dumps;
- cloud credentials;
- OAuth refresh/access tokens;
- webhooks with secrets.

If scanner fails, default UI should require stronger confirmation or show summary only.

### Audit Event: `runtime_log_accessed`

Payload must include:

- actor;
- run_ref_id;
- log_id;
- visibility level;
- reason if required;
- timestamp;
- redaction status.

Do not include log body in audit payload.

---

## Evidence Security and Extraction

## Storage Policy

Target architecture: Gear owns durable artifact/provenance storage.

MVP fallback: Rumble may store evidence locally when no suitable Gear backend exists.

### Local Evidence Rules

- Must be marked `storage_backend='rumble_local'`.
- Must be `extractable=true`.
- Must have `content_hash`.
- Must have `migration_status`.
- Must support export to Gear-compatible bundle.
- Must be encrypted at rest in hosted/multi-user mode.
- Must not be used as permanent architecture decision.

### Extraction Criteria

Migrate evidence out of Rumble when:

- Gear artifact/provenance backend exists;
- evidence volume grows beyond MVP threshold;
- multiple Rumble products need evidence storage;
- retention/legal requirements exceed app-local storage maturity;
- search/provenance requirements need shared substrate.

### Acceptance Review

Evidence may be accepted only when:

- actor is human reviewer or valid auto-close system rule;
- artifact/reference is available or policy exception exists;
- provenance/hash is sufficient for task risk;
- evidence is not superseded;
- task target version is current.

---

## Integration Security With `cos-matic`

### Inbound Events

Inbound events from `cos-matic` require:

- service authentication;
- replay protection via `source_event_id`;
- timestamp freshness or replay window;
- workspace/task/run reference validation;
- schema validation;
- redaction validation for payload summaries.

### Outbound Requests

Outbound requests to `cos-matic` require:

- idempotency key;
- request payload hash;
- bounded task context;
- no raw secrets in payload;
- execution policy included;
- audit event before/after external call.

### Approval Sync

- Local human decision is immutable.
- External sync is retryable.
- Sync failure is visible as `sync_failed`.
- Reversal requires superseding approval, not mutation.

---

## Sensitive Data Classification

| Data | Classification | Notes |
| --- | --- | --- |
| Workspace/member display names | Personal data | RGPD subject rights apply. |
| Task title/goal/description/context | Potentially personal/confidential | Treat as confidential by default. |
| Comments | Potentially personal/confidential | May include user-provided PII. |
| Approval decisions | Personal/accountability data | Retain for audit. |
| Evidence summaries | Confidential | May reveal implementation/business info. |
| Evidence artifacts | Confidential/sensitive | Backend-dependent. |
| Raw runtime logs | Sensitive/high-risk | May contain secrets/PII. |
| RuntimeRef labels | Internal | No secrets. |
| Audit events | Accountability/security data | Append-only retention. |
| Integration payload hashes | Internal/security | No content by themselves. |

---

## RGPD Requirements

### Legal Basis

Depends on deployment context; likely contract/legitimate interest for collaboration/work audit. Must be documented by deployer.

### Data Minimization

- Do not collect raw logs by default.
- Do not copy large artifacts if references suffice.
- Do not store runtime credentials.
- Avoid indexing sensitive artifacts/logs.

### Access Rights

- Users can request export of personal profile/member data.
- Task/audit records may require retention for legitimate interest/security; deletion can be redaction/anonymization rather than physical deletion when audit integrity is required.

### Rectification

- Mutable profile/display-name fields can be updated.
- Audit decisions are not rewritten; corrections use superseding events.

### Erasure

Supported through:

- workspace/member removal;
- personal data redaction where compatible with audit;
- artifact/log deletion after retention;
- local evidence purge after Gear migration/retention.

### Portability

Exports should support JSON/bundle format with redaction markers.

### Retention

Recommended defaults:

| Data | Default retention |
| --- | --- |
| Activity events | Workspace retention; long-lived for audit. |
| Approval/evidence decisions | Same as audit retention. |
| Raw runtime logs | Short TTL, e.g. 7–30 days, configurable downward. |
| Local evidence blobs | Until migrated or workspace retention expires. |
| Idempotency keys | Short TTL, e.g. 24h–30d depending operation. |
| Integration event IDs | Enough to prevent replay duplication, e.g. 30–90d. |

### Data Residency

Default target: self-hostable and EU/local deployment compatible. Do not require US hyperscalers for core truth.

---

## Threat Model Notes

| Threat | Risk | Mitigation |
| --- | --- | --- |
| Unauthorized execution request | High | `execution_mode`, permissions, approvals, idempotency, audit. |
| Agent approves own gate | High | Human-only approval enforcement. |
| Raw logs leak secrets | Critical | Raw disabled by default, privileged access, scanner, audit, TTL, no indexing. |
| Evidence tampering | High | hashes, artifact refs, append-only review events. |
| Integration event replay | High | `source_event_id` unique constraint, auth, freshness. |
| Stale approval accepted | High | target version/hash required. |
| Auto-close hides bad output | High | low-risk only, skill opt-in, no blockers/approvals, audit. |
| Rumble becomes credential store | Critical | RuntimeRef contains only safe opaque refs. |
| Audit event mutation | High | append-only critical events, correction via superseding events. |
| Over-broad exports | High | permission checks, redaction markers, separate raw-log export. |

---

## Security Acceptance Tests

- Given `execution_mode=disabled`, run request returns `policy_denied`.
- Given workspace not trusted, execution request cannot set `allow_execution=true`.
- Given agent actor submits approval decision, API returns `permission_denied`.
- Given high-risk task with run succeeded, task remains review/approval required.
- Given low-risk auto-closable task and no blockers, trusted run success can auto-close with audit event.
- Given raw log access, `runtime_log_accessed` event is appended and log body is not copied into audit payload.
- Given raw logs disabled, raw log endpoint denies access even to owner.
- Given duplicate integration event, no duplicate state transition occurs.
- Given task context changed after run request, auto-close is blocked.
- Given local evidence exists, export/migration metadata is present.

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Exact integration authentication mechanism for `cos-matic` events | High | Open; must support replay protection and rotation. |
| Default raw log TTL | High | Proposed: 7 days for hosted/multi-user, configurable. |
| Whether completion auto-close can be enabled workspace-wide | Medium | Proposed: no; skill/task opt-in required. |
| Evidence migration threshold to Gear | Medium | Open; define after first implementation volume. |
| Whether strict append-only storage is DB-enforced or application-enforced | High | Proposed: DB-enforced for critical events when possible. |
