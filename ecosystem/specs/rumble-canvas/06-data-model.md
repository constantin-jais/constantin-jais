# Data Model — rumble-canvas

Status: Draft / MVP package+handoff slice.

## Principles

- Structured fields are canonical; Markdown is projection/export.
- Approved revisions and packages are immutable.
- Actor attribution is required for edits, approvals, waivers, packages, and handoffs.
- Handoff payloads are planning-only and hashable.
- Derived reports can be recomputed; package readiness snapshots are persisted for audit.

## Tables / Collections

### actors

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk | Local/shared actor reference. |
| actor_type | enum | human, agent, system, service. |
| display_name | text nullable | Snapshot. |
| source | text nullable | Local profile, Bolt, integration. |
| created_at | timestamptz | Audit. |

### spec_workspaces

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk | Stable workspace ID. |
| name | text | Required. |
| slug | text | Unique per owner/account. |
| status | enum | draft, in_review, approved, handoff_requested, archived. |
| owner_actor_id | text | FK/reference to actors. |
| settings_json | jsonb | Review/export settings. |
| created_at / updated_at / archived_at | timestamptz | Audit. |

Indexes: `(slug)`, `(owner_actor_id, status)`.

### workspace_memberships

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| actor_id | text |  |
| status | enum | invited, active, suspended, removed. |
| created_at / updated_at | timestamptz | Audit. |

Unique: `(workspace_id, actor_id)`.

### role_assignments

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| actor_id | text |  |
| role | enum | owner, editor, reviewer, viewer, agent, system. |
| granted_by | text | Actor ref. |
| created_at / revoked_at | timestamptz | Audit. |

### spec_sections

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| key | text | product-charter, roles, journeys, etc. |
| title | text |  |
| status | enum | empty, draft, ready_for_review, changes_requested, approved, waived. |
| current_revision_id | text nullable |  |
| approved_revision_id | text nullable |  |
| required_for_package | boolean |  |
| waiver_id | text nullable | If waived. |
| created_at / updated_at | timestamptz | Audit. |

### spec_section_revisions

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk | Immutable. |
| section_id | text |  |
| revision_number | integer | Monotonic per section. |
| content_format | enum | dual. |
| structured_content_json | jsonb | Canonical machine contract. |
| markdown_content | text nullable | Human projection/prose. |
| content_hash | text | Hash of canonical structured content. |
| created_by | text | Actor ref. |
| created_at | timestamptz | Audit. |

Unique: `(section_id, revision_number)`.

### traceability_links

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| source_type / source_id | text | Typed reference. |
| target_type / target_id | text | Typed reference. |
| relation_type | enum | justifies, implements, requires, tests, produces, extracts_to_candidate, included_in. |
| rationale | text nullable |  |
| confidence | enum | manual, agent_suggested, system_inferred. |
| status | enum | active, stale, rejected. |
| created_by / created_at | text/timestamptz | Audit. |

Indexes: `(workspace_id, source_type, source_id)`, `(workspace_id, target_type, target_id)`.

### waivers

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| target_type / target_id | text | Risk, question, section, validation gate. |
| severity | enum | low, medium, high, critical. |
| status | enum | proposed, accepted, rejected, expired, revoked. |
| rationale | text | Required. |
| approved_by_owner | text nullable | Human actor. |
| approved_by_reviewer | text nullable | Required for high/critical. |
| expires_at | timestamptz nullable |  |
| created_by / created_at | text/timestamptz | Audit. |

### decision_records / open_questions / risk_flags / capability_candidates

Store as structured JSON-backed domain tables with:

- `id`, `workspace_id`, `status`, `severity/impact` where relevant;
- `structured_content_json`;
- actor/timestamp audit fields;
- optional `waiver_id`;
- traceability links to related objects.

### spec_packages

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| version | text |  |
| status | enum | draft, approved, exported, handoff_submitted, handoff_failed. |
| package_hash | text | Canonical package hash. |
| readiness_snapshot_json | jsonb | Persisted evidence at approval time. |
| artifact_reference_id | text nullable | Gear candidate. |
| approved_by / approved_at | text/timestamptz | Audit. |

### spec_package_items

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| package_id | text |  |
| section_id | text |  |
| revision_id | text | Immutable included revision. |
| required | boolean |  |

### implementation_handoffs

| Column | Type | Notes |
| --- | --- | --- |
| id | text pk |  |
| workspace_id | text |  |
| package_id | text | Approved package. |
| status | enum | draft, validated, submitted, acknowledged, failed, cancelled. |
| payload_format | text | `canvas.bolt_handoff.v0.1`. |
| payload_json | jsonb | Canonical payload. |
| payload_hash | text | Hash used for idempotency. |
| bolt_reference | text nullable | Returned by cos-matic. |
| created_by / created_at | text/timestamptz | Audit. |

### activity_events

Append-only audit stream:

- `id`, `workspace_id`, `actor_id`, `event_type`, `target_type`, `target_id`, `payload_json`, `created_at`.

## RLS / Auth Rules

- Owner manages workspace and final package approval.
- Editor edits draft content.
- Reviewer reviews sections and high/critical waivers.
- Agent suggestions never mutate accepted truth without human acceptance.
- System can compute derived status and append system events.

## PII Classification

- Most content is user-authored and may contain PII.
- Logs must never include full section content or secrets.
- Handoff payloads must be reviewed for PII before leaving local/self-hosted boundary.

## Migration Notes

- Schema must version `structured_content_json` by object kind.
- Package hashes must be stable across migrations; keep canonicalization rules versioned.
