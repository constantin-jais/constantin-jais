# Data Model — rumble-note

Status: Drafting.

## Storage Strategy

MVP uses a hybrid local-first model:

- human-readable Markdown exports for documents and packages;
- local structured store for IDs, block tree, links, source references, handoff manifests, audit events, and indexes;
- deterministic JSON manifests for handoff/export packages.

The structured store is the local source of truth for block identity and relationships. Markdown is an export/projection unless a later ADR chooses dual-write document storage.

## Global Rules

- All primary IDs are stable opaque strings.
- All user-authored records include `created_at`, `updated_at`, and optional `archived_at` / `deleted_at`.
- Destructive deletion uses soft delete first.
- Handoff packages snapshot block revisions or content hashes.
- Index tables are rebuildable and not authoritative.
- Sync metadata exists as reserved fields, but mandatory sync is post-MVP.

## Collection: workspaces

### Columns and Types

- `id`: string primary key
- `name`: string
- `root_path`: string
- `settings_json`: JSON
- `privacy_defaults_json`: JSON
- `created_at`: datetime
- `updated_at`: datetime
- `archived_at`: datetime nullable

### Primary Key

`id`

### Foreign Keys

None.

### Indexes

- unique `root_path`
- `archived_at`

### Constraints

- `name` non-empty.
- `root_path` non-empty and local.

### RLS/Auth Rules

MVP local single-owner. Future collaborative mode must introduce membership/role binding.

### Audit Fields

Creation/update/archive events in `event_log`.

### Retention Policy

Retained until user exports/deletes workspace.

### PII Classification

May contain local path and user-provided workspace name. Treat as personal metadata.

### Local-First / Sync Behavior

Workspace must open offline. Sync fields reserved but inactive.

### Migration Notes

Settings schema must be versioned.

## Collection: notebooks

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `title`: string
- `description`: text nullable
- `sort_order`: string/integer
- `visibility`: enum `normal`, `private`
- `created_at`, `updated_at`, `archived_at`

### Primary Key

`id`

### Foreign Keys

- `workspace_id -> workspaces.id`

### Indexes

- `workspace_id, sort_order`
- `workspace_id, title`

### Constraints

- `title` non-empty.
- notebook belongs to one workspace.

### RLS/Auth Rules

Local owner can read/write. Future: workspace membership required.

### Audit Fields

Create/update/archive events.

### Retention Policy

Archive before delete.

### PII Classification

User-authored metadata, may contain personal data.

### Local-First / Sync Behavior

Stored locally; conflicts resolved post-MVP by notebook revision metadata.

### Migration Notes

Keep hierarchy shallow for MVP.

## Collection: documents

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `notebook_id`: string nullable for inbox/system docs
- `title`: string
- `document_type`: enum
- `root_block_order_json`: JSON array of block IDs or sort keys
- `created_at`, `updated_at`, `archived_at`, `deleted_at`

### Primary Key

`id`

### Foreign Keys

- `workspace_id -> workspaces.id`
- `notebook_id -> notebooks.id`

### Indexes

- `workspace_id, notebook_id`
- `workspace_id, document_type`
- `updated_at`

### Constraints

- title non-empty except transient drafts.
- document belongs to one workspace.

### RLS/Auth Rules

Future: read/write by workspace role.

### Audit Fields

Events for create/update/archive/delete.

### Retention Policy

Soft delete first; purge only after user confirmation.

### PII Classification

Document title and content may contain PII.

### Local-First / Sync Behavior

Local authoritative. Future sync must preserve block IDs and ordering.

### Migration Notes

Document body is not a single blob; block table owns content.

## Collection: blocks

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `document_id`: string
- `parent_block_id`: string nullable
- `sort_key`: string
- `type`: enum `paragraph`, `heading`, `list_item`, `quote`, `code`, `source_ref`, `question`, `decision`, `task_candidate`, `spec_candidate`, `learning_candidate`, `context_fragment`
- `content`: text
- `content_format`: enum `plain_text`, `markdown`
- `labels_json`: JSON array
- `privacy`: enum `normal`, `private`, `no_handoff`, `sensitive`
- `qualification_json`: JSON nullable
- `revision`: integer
- `content_hash`: string
- `created_at`, `updated_at`, `archived_at`, `deleted_at`

### Primary Key

`id`

### Foreign Keys

- `workspace_id -> workspaces.id`
- `document_id -> documents.id`
- `parent_block_id -> blocks.id`

### Indexes

- `workspace_id, document_id, parent_block_id, sort_key`
- `workspace_id, type`
- `workspace_id, privacy`
- `workspace_id, updated_at`
- label index through derived index table or JSON index

### Constraints

- block belongs to one document.
- parent block belongs to same document.
- `sort_key` unique among siblings.
- `revision` increments on content or metadata changes relevant to handoff.

### RLS/Auth Rules

Future: inherit document/workspace permissions.

### Audit Fields

Block changes recorded as events; full content diffs optional and configurable for privacy.

### Retention Policy

Archive preferred. Hard delete creates tombstone if referenced by handoff.

### PII Classification

High risk: content may contain private notes, secrets, personal data, source excerpts.

### Local-First / Sync Behavior

Stable IDs across exports, moves, and future sync. Conflict resolution must not merge content silently.

### Migration Notes

Adding new block types must preserve existing exports and fallback rendering.

## Collection: block_tombstones

### Columns and Types

- `block_id`: string primary key
- `workspace_id`: string
- `last_document_id`: string nullable
- `reason`: enum `deleted`, `purged`, `redacted`
- `referenced_by_handoff_ids_json`: JSON array
- `deleted_at`: datetime

### Purpose

Keep prior handoff manifests resolvable without retaining deleted content.

### PII Classification

Avoid storing deleted content. IDs and references only.

## Collection: references

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `source_type`: enum `block`, `document`, `source`, `handoff`, `artifact`
- `source_id`: string
- `target_type`: enum `block`, `document`, `source`, `handoff`, `artifact`
- `target_id`: string
- `relationship_type`: enum `mentions`, `supports`, `contradicts`, `expands`, `depends_on`, `derived_from`, `duplicates`, `replaces`, `blocks`, `relates_to`
- `description`: text nullable
- `state`: enum `active`, `unresolved`, `archived`
- `created_at`, `updated_at`, `archived_at`

### Primary Key

`id`

### Foreign Keys

Typed polymorphic references; validate in domain service.

### Indexes

- `workspace_id, source_type, source_id`
- `workspace_id, target_type, target_id`
- `workspace_id, relationship_type`
- `workspace_id, state`

### Constraints

- relationship type required.
- source and target IDs non-empty.

### PII Classification

Description may contain personal data.

### Local-First / Sync Behavior

Broken references remain as `unresolved`.

## Collection: source_references

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `source_kind`: enum `url`, `file`, `note`, `transcript`, `document`, `dataset`, `external_id`
- `title`: string
- `locator`: string
- `provenance_json`: JSON
- `canonical_source_id`: string nullable
- `verification_state`: enum `unverified`, `verified`, `stale`, `failed`, `archived`
- `created_at`, `updated_at`, `archived_at`

### Indexes

- `workspace_id, source_kind`
- `workspace_id, verification_state`
- `canonical_source_id`

### Constraints

- title and locator required.
- trusted/verified state requires provenance evidence.

### RLS/Auth Rules

Local owner. Future: workspace role.

### PII Classification

May contain URLs, local file paths, author names, document titles.

### Local-First / Sync Behavior

Local wrapper around optional Wrench/Gear source IDs.

## Collection: handoff_packages

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `purpose`: enum `source_context`, `spec_context`, `task_context`, `learning_session_context`, `harness_context`, `export`
- `target`: enum `local_export`, `harness`, `rumble_canvas`, `rumble_lm`, `bolt_cos_matic`
- `status`: enum `draft`, `validated`, `exported`, `submitted`, `accepted`, `rejected`, `superseded`
- `summary`: text nullable
- `constraints_json`: JSON
- `validation_report_json`: JSON nullable
- `manifest_hash`: string nullable
- `created_at`, `updated_at`, `submitted_at`, `superseded_at`

### Indexes

- `workspace_id, status`
- `workspace_id, purpose`
- `workspace_id, target`
- `updated_at`

### Constraints

- purpose required.
- target required before validation/export/submission.
- submitted package immutable except status/response metadata.

### PII Classification

Package may contain sensitive summaries and references.

### Local-First / Sync Behavior

Can be exported offline. Remote submission optional.

## Collection: handoff_items

### Columns and Types

- `id`: string primary key
- `handoff_package_id`: string
- `source_type`: enum `block`, `source`, `document`
- `source_id`: string
- `revision`: integer nullable
- `content_hash`: string
- `included_content`: text nullable
- `included_metadata_json`: JSON
- `role_in_package`: enum
- `redaction_state`: enum `none`, `redacted`, `omitted_with_marker`
- `sort_order`: integer

### Foreign Keys

- `handoff_package_id -> handoff_packages.id`

### Indexes

- `handoff_package_id, sort_order`
- `source_type, source_id`

### Constraints

- redacted/omitted items require manifest marker.
- included content hash must match validation result.

### Retention Policy

Retain for audit unless package history is purged.

## Collection: exports

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `scope_type`: enum `workspace`, `notebook`, `document`, `blocks`, `handoff`
- `scope_id`: string nullable
- `format`: enum `markdown`, `json`, `markdown_json_bundle`
- `destination_ref`: string
- `manifest_hash`: string
- `created_at`

### PII Classification

May reveal local paths; audit log should allow redaction of destination path.

## Collection: event_log

### Columns and Types

- `id`: string primary key
- `workspace_id`: string
- `event_name`: string
- `actor_ref_json`: JSON
- `subject_type`: string
- `subject_id`: string
- `payload_json`: JSON
- `created_at`: datetime
- `privacy_level`: enum `metadata_only`, `includes_content`, `sensitive`

### Indexes

- `workspace_id, created_at`
- `workspace_id, event_name`
- `subject_type, subject_id`

### Constraints

- avoid full content in events by default.
- sensitive events must be marked.

### Retention Policy

Configurable local retention. Handoff audit events retained by default.

## Collection: local_indexes

### Columns and Types

- `workspace_id`: string
- `index_kind`: enum `text`, `links`, `labels`, `handoff`, `source`
- `status`: enum `ready`, `stale`, `rebuilding`, `failed`
- `last_built_at`: datetime nullable
- `error`: text nullable

### Purpose

Track rebuildable projections. Actual index implementation may use SQLite FTS or equivalent local open-source index.

### Constraints

- index loss must not lose source data.

## Authorization Rules

MVP is local single-owner:

- owner can read/write/export/delete all local data;
- downstream consumers can only read explicit handoff packages;
- imported source providers can only write through explicit import flow.

Future collaboration must introduce:

- workspace membership;
- role assignment;
- per-action permission checks;
- audit actor references.

## Backup / Restore Expectations

Backup must include:

- structured store;
- assets;
- export/handoff manifests;
- settings schema version.

Restore must preserve:

- workspace ID unless user chooses clone;
- block IDs;
- references;
- handoff package manifests;
- tombstones needed for audit.

## Migration Strategy

- Every schema has a version.
- Migrations are local and reversible where possible.
- Before destructive migrations, create backup or export manifest.
- Index migrations may rebuild from source truth.

## Deferred Data Decisions

- Exact local DB engine.
- Exact block ID format.
- Optional sync metadata format.
- Whether Markdown files become editable source of truth or remain export projection.
