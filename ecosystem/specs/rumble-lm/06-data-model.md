# Data Model — rumble-lm

Status: Draft.

## Data Model Principles

- Store session truth in Rumble application tables.
- Reference shared identity/source/artifact primitives instead of owning them permanently.
- Snapshot policy-sensitive fields at submission/export time.
- Prefer archive/soft-delete for auditability; hard-delete only for retention/RGPD workflows.
- Keep generated content traceable to source set, response set, and generation metadata.

## Table: sessions

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk | Session ID |
| workspace_id | uuid | Tenant/workspace boundary |
| title | text | Required |
| objective | text | Required before Prepared |
| audience | text | Optional structured later |
| status | enum | Draft/Prepared/Live/Closed/Synthesized/Exported/Archived |
| facilitator_actor_id | uuid/text | Actor reference ID |
| active_source_set_id | uuid nullable | FK to source_sets |
| settings_json | jsonb | Visibility/access/export defaults |
| created_at | timestamptz | Audit |
| prepared_at | timestamptz nullable | Lifecycle |
| started_at | timestamptz nullable | Lifecycle |
| closed_at | timestamptz nullable | Lifecycle |
| archived_at | timestamptz nullable | Lifecycle |
| deleted_at | timestamptz nullable | Soft delete |

### Indexes

- `(workspace_id, status)`
- `(workspace_id, facilitator_actor_id)`
- `(created_at)`

### RLS/Auth Rules

- Admin may view metadata; content access depends on policy.
- Facilitator may manage sessions they own or are assigned to.
- Participants cannot query sessions directly except session participant view.

### PII Classification

Low to medium: title/objective may contain personal data if user enters it. Treat as workspace content.

## Table: source_sets

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| revision | integer | Monotonic per session |
| status | enum | Open/Processing/Ready/Locked/Stale |
| created_by | actor ref |  |
| created_at | timestamptz |  |
| locked_at | timestamptz nullable |  |

### Constraints

- Unique `(session_id, revision)`.
- Active source set referenced by `sessions.active_source_set_id`.

## Table: source_set_items

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| source_set_id | uuid fk |  |
| source_ref | text/uuid | Gear/Wrench source ID |
| source_revision | text/integer nullable | Pinned source revision |
| title_snapshot | text | For display/export stability |
| provenance_snapshot | jsonb | Minimal inspectable provenance |
| added_at | timestamptz |  |
| removed_at | timestamptz nullable | Soft removal |

### Indexes

- `(source_set_id)`
- `(source_ref)`

## Table: activities

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| type | enum | Quiz/Vote/Reflection/Discussion/SummaryCheckpoint |
| title | text |  |
| objective | text |  |
| prompt | text |  |
| status | enum | Draft/Validated/Published/Running/Closed/Archived |
| agenda_order | integer | Unique per session when active |
| duration_seconds | integer nullable |  |
| response_mode | jsonb | Schema/config for allowed response |
| visibility | jsonb | Activity-level visibility overrides |
| grounding_mode | enum | SourceGrounded/FacilitatorAuthored/Unsupported/Mixed |
| source_set_revision | integer nullable | Source grounding reference |
| generated_metadata | jsonb nullable | Tool/model/run metadata without secrets |
| created_by | actor ref |  |
| validated_by | actor ref nullable |  |
| created_at | timestamptz |  |
| updated_at | timestamptz |  |
| deleted_at | timestamptz nullable |  |

### Constraints

- Unique `(session_id, agenda_order)` for non-deleted activities.
- Published source-grounded activities require citation resolution enforced at service/domain layer.

### PII Classification

May contain personal data in prompts. Treat as session content.

## Table: activity_options

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| activity_id | uuid fk |  |
| label | text |  |
| value | text |  |
| is_correct | boolean nullable | Quiz only, optional |
| agenda_order | integer |  |
| metadata_json | jsonb |  |

## Table: activity_runs

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| activity_id | uuid fk |  |
| status | enum | Open/Paused/Closed |
| started_by | actor ref |  |
| closed_by | actor ref nullable |  |
| started_at | timestamptz |  |
| closed_at | timestamptz nullable |  |

### Constraints

- At most one `Open` run per session in MVP.

## Table: participants

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| actor_ref | text/uuid nullable | Null for guest if allowed |
| display_name | text nullable | PII |
| join_mode | enum | Guest/Auth/Invite |
| joined_at | timestamptz |  |
| last_seen_at | timestamptz nullable |  |
| left_at | timestamptz nullable |  |
| anonymized_at | timestamptz nullable |  |

### Indexes

- `(session_id)`
- `(actor_ref)` when not null.

### PII Classification

Personal data. Display names and actor references require retention and deletion controls.

## Table: responses

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk | Denormalized for policy queries |
| activity_id | uuid fk |  |
| activity_run_id | uuid fk |  |
| participant_id | uuid fk |  |
| content_json | jsonb | Response content |
| response_type | enum | Choice/Text/Rating/Rank/Composite |
| visibility_snapshot | jsonb | Captured at submission time |
| submitted_at | timestamptz |  |
| updated_at | timestamptz nullable | Only before close if allowed |
| deleted_at | timestamptz nullable | Privacy/delete workflow |
| anonymized_at | timestamptz nullable |  |

### Indexes

- `(activity_id, submitted_at)`
- `(participant_id)`
- `(session_id)`

### Constraints

- Service enforces open activity run at submission.
- Optional unique `(activity_run_id, participant_id)` when one response per activity is configured.

### PII Classification

High. Free-text responses may contain sensitive data. Avoid response content in logs.

## Table: citations

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| target_type | enum | Activity/ActivityOption/Summary/SummarySection |
| target_id | uuid |  |
| source_ref | text/uuid |  |
| source_revision | text/integer nullable |  |
| source_chunk_ref | text/uuid |  |
| quote | text | Source excerpt |
| location_json | jsonb | Page/offset/URL fragment/etc. |
| support_level | enum | Strong/Partial/Weak/Contradicted/NotReviewed |
| status | enum | Candidate/Validated/Rejected/Stale |
| validated_by | actor ref nullable |  |
| validated_at | timestamptz nullable |  |
| created_at | timestamptz |  |

### Indexes

- `(target_type, target_id)`
- `(session_id, status)`
- `(source_ref)`

### PII Classification

Depends on source content. Treat as content; may include personal data excerpts.

## Table: summaries

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| audience | enum | FacilitatorOnly/Participants/AdminAudit |
| status | enum | Draft/Validated/Published/Archived |
| revision | integer |  |
| content_json | jsonb | Structured sections |
| generated_metadata | jsonb nullable | No secrets |
| validated_by | actor ref nullable |  |
| generated_at | timestamptz nullable |  |
| validated_at | timestamptz nullable |  |
| published_at | timestamptz nullable |  |

### Constraints

- Unique `(session_id, audience, revision)`.

### PII Classification

Medium to high. May summarize participant content; enforce audience policy.

## Table: exports

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| session_id | uuid fk |  |
| format | enum | PDF/Markdown/HTML/JSON/Bundle |
| audience | enum | FacilitatorOnly/Participants/AdminAudit/MachineReadable |
| included_data_json | jsonb | Data classes included |
| artifact_ref | text/uuid | Gear artifact candidate |
| checksum | text nullable | Integrity |
| generated_by | actor ref |  |
| generated_at | timestamptz |  |
| revoked_at | timestamptz nullable |  |

### PII Classification

Matches included data. Export access and retention must be explicit.

## Table: audit_events

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid pk |  |
| workspace_id | uuid |  |
| session_id | uuid nullable |  |
| actor_ref | jsonb | Actor snapshot |
| event_name | text |  |
| target_type | text |  |
| target_id | text/uuid |  |
| metadata_json | jsonb | No secrets, no response content |
| created_at | timestamptz |  |

### Indexes

- `(workspace_id, created_at)`
- `(session_id, created_at)`
- `(event_name)`

## Retention Policy

- Sessions: archived by default, hard delete per workspace policy.
- Participants/responses: configurable retention; support anonymization.
- Audit events: retained longer than content where legally/policy appropriate, but must avoid sensitive content.
- Exports: revocable link/reference where possible; immutable artifact may require retention/deletion policy.

## Local-First / Sync Behavior

MVP is not full local-first. It may cache read-only session metadata or prepared content. Live participation requires network connectivity. Offline-first can be revisited once shared storage/sync primitives are decided.

## Migration Notes

- Use additive migrations for enum changes where possible.
- Do not hard-code activity types in ways that prevent new activity plugins later.
- Keep `generated_metadata` schema versioned.

## Backup / Restore Expectations

Backups must preserve sessions, activities, responses, citations, summaries, exports metadata, and audit events. Restore must not silently regenerate summaries or citations without marking revisions.
