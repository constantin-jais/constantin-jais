# Domain Model — rumble-note

Status: Drafting.

## Domain Thesis

`rumble-note` is centered on stable addressable blocks and explicit handoff. The domain model must remain small enough to avoid becoming a full ingestion engine, memory substrate, or orchestrator.

Core lifecycle:

```text
capture -> structure -> link -> qualify -> retrieve -> handoff/export
```

## Aggregate Boundaries

- `Workspace` owns local settings, notebooks, documents, indexes, and export policy.
- `Document` owns ordered block structure.
- `Block` owns content, type, local metadata, and qualification state.
- `Reference` links blocks/documents/sources/artifacts but does not own target content.
- `HandoffPackage` snapshots selected block revisions for a declared target and purpose.
- `SourceReference` points to provenance-bearing source data, likely shared with Gear/Wrench primitives later.

## Entity: Workspace

### Definition

Local root for a user's notes, indexes, assets, configuration, and handoff/export history.

### Owner

`rumble-note` for product experience; shared Rumble/Gear ownership remains open for broader workspace primitive.

### Fields

- `id`
- `name`
- `root_path`
- `settings`
- `privacy_defaults`
- `created_at`
- `updated_at`

### Lifecycle States

- `active`
- `archived`
- `repair_required`

### Relationships

- Contains notebooks, documents, local indexes, assets, and handoff manifests.

### Invariants

- Workspace has one local root path.
- Workspace can operate without network access.
- Workspace export must not require remote services.

### State Transitions

- `active -> archived`
- `active -> repair_required`
- `repair_required -> active`

### Deletion / Archive Rules

- Archive preserves data and disables default editing.
- Deletion requires explicit confirmation and should support backup/export first.

### Emitted Events

- `note.workspace.created`
- `note.workspace.archived`
- `note.workspace.repair_requested`

### Shared Capability Candidates

- Workspace / project space.
- Permission/audit policy.
- Activity/event log.

## Entity: Notebook

### Definition

User-facing grouping of documents inside a workspace.

### Owner

`rumble-note` MVP; candidate shared Rumble information-architecture primitive only if repeated.

### Fields

- `id`
- `workspace_id`
- `title`
- `description`
- `sort_order`
- `visibility`
- `created_at`
- `updated_at`

### Lifecycle States

- `active`
- `archived`

### Relationships

- Belongs to workspace.
- Contains documents.

### Invariants

- Notebook title is unique within its parent workspace unless explicitly allowed by settings.
- Archiving a notebook does not delete contained documents.

### State Transitions

- `active -> archived`
- `archived -> active`

### Deletion / Archive Rules

- Deletion requires handling contained documents: move, archive, or delete with confirmation.

### Emitted Events

- `note.notebook.created`
- `note.notebook.updated`
- `note.notebook.archived`

### Shared Capability Candidates

- Workspace/project organization.

## Entity: Document

### Definition

Ordered, editable collection of blocks.

### Owner

`rumble-note`.

### Fields

- `id`
- `workspace_id`
- `notebook_id`
- `title`
- `root_block_ids`
- `document_type` (`note`, `journal`, `source_notes`, `spec_draft`, `learning_notes`, `task_notes`)
- `created_at`
- `updated_at`
- `archived_at`

### Lifecycle States

- `draft`
- `active`
- `archived`
- `deleted_pending_purge`

### Relationships

- Belongs to notebook and workspace.
- Contains ordered root blocks.
- May be referenced by other documents or handoff packages.

### Invariants

- A document contains at least one root block after creation, unless it is an empty draft.
- Block ordering is deterministic.
- Document delete cannot silently remove historical handoff snapshots.

### State Transitions

- `draft -> active`
- `active -> archived`
- `archived -> active`
- `archived -> deleted_pending_purge`

### Deletion / Archive Rules

- Archive is preferred over delete.
- Hard delete removes local content but leaves redacted tombstones for prior handoff manifests if needed.

### Emitted Events

- `note.document.created`
- `note.document.updated`
- `note.document.archived`
- `note.document.deleted`

### Shared Capability Candidates

- Artifact, if a document becomes an exported artifact.

## Entity: Block

### Definition

Smallest stable addressable unit of user-authored or imported note content.

### Owner

`rumble-note`.

### Minimal Fields

- `id`: stable unique block ID.
- `workspace_id`
- `document_id`
- `parent_block_id`: optional.
- `sort_key`: deterministic order among siblings.
- `type`: `BlockType`.
- `content`: human-readable body.
- `content_format`: `plain_text`, `markdown`, or later structured format.
- `labels`: user-defined labels.
- `privacy`: `normal`, `private`, `no_handoff`, `sensitive`.
- `qualification`: optional `BlockQualification`.
- `source_reference_ids`: optional list.
- `created_at`
- `updated_at`
- `archived_at`
- `deleted_at`

### Minimal Block Types

- `paragraph`
- `heading`
- `list_item`
- `quote`
- `code`
- `source_ref`
- `question`
- `decision`
- `task_candidate`
- `spec_candidate`
- `learning_candidate`
- `context_fragment`

### Lifecycle States

- `draft`
- `active`
- `archived`
- `deleted_pending_purge`

### Relationships

- Belongs to one document.
- May have parent/child blocks.
- May reference other blocks, documents, sources, artifacts, or handoff packages.
- May be included in many handoff packages by revision snapshot.

### Invariants

- Block IDs are stable across edits, moves, local exports, and handoffs.
- A block has one owning document at a time.
- Moving a block preserves its ID.
- Handoff packages reference block revision snapshots, not mutable live content only.
- Blocks marked `no_handoff` cannot be included in a handoff unless the user explicitly overrides with audit reason.

### State Transitions

- `draft -> active`
- `active -> archived`
- `archived -> active`
- `archived -> deleted_pending_purge`

### Deletion / Archive Rules

- Archive keeps links resolvable.
- Hard delete creates a tombstone if prior handoffs referenced the block.
- Deleting a parent block requires explicit choice for children: archive subtree, promote children, or delete subtree.

### Emitted Events

- `note.block.created`
- `note.block.updated`
- `note.block.moved`
- `note.block.qualified`
- `note.block.archived`
- `note.block.deleted`

### Shared Capability Candidates

- Traceability link.
- Activity/event log.
- Memory-entry candidate when promoted to Gear Memory.

## Value Object: BlockQualification

### Definition

User-assigned meaning that helps retrieval and handoff without turning the block into a downstream artifact automatically.

### Owner

`rumble-note`.

### Fields

- `kind`: `observation`, `claim`, `question`, `decision`, `risk`, `assumption`, `task_candidate`, `spec_candidate`, `learning_candidate`, `source_candidate`, `context_fragment`.
- `post_mvp_kind`: `memory_candidate`, only when durable memory promotion is specified.
- `confidence`: `low`, `medium`, `high`, optional.
- `status`: `candidate`, `reviewed`, `rejected`, `handed_off`.
- `reason`: optional.

### Invariants

- Qualification does not imply downstream acceptance.
- A block may have multiple labels but should have at most one primary qualification kind in MVP.

### Shared Capability Candidates

- Decision record if product decisions become shared.
- Agent task if task candidates are handed off.
- Memory-entry if memory candidates are handed off.

## Entity: Reference

### Definition

Typed relationship from one object to another.

### Owner

`rumble-note` for note-level links; shared traceability/provenance primitives may be extracted later.

### Fields

- `id`
- `workspace_id`
- `source_ref`: typed pointer to block/document/source/artifact/handoff.
- `target_ref`: typed pointer to block/document/source/artifact/handoff.
- `relationship_type`
- `description`
- `created_at`
- `created_by`

### Relationship Types

- `mentions`
- `supports`
- `contradicts`
- `expands`
- `depends_on`
- `derived_from`
- `duplicates`
- `replaces`
- `blocks`
- `relates_to`

### Lifecycle States

- `active`
- `unresolved`
- `archived`

### Relationships

- Links two typed references.
- Backlinks are computed/indexed projections of references.

### Invariants

- References must preserve source and target IDs even if target becomes archived.
- Broken references are visible as `unresolved` rather than silently removed.
- Relationship type is required for non-mention links.

### State Transitions

- `active -> unresolved`
- `unresolved -> active`
- `active -> archived`

### Deletion / Archive Rules

- Deleting a reference removes the current link but not historical handoff snapshots.

### Emitted Events

- `note.reference.created`
- `note.reference.updated`
- `note.reference.unresolved`
- `note.reference.archived`

### Shared Capability Candidates

- Traceability link.
- Source/provenance link.

## Entity: SourceReference

### Definition

A reference to a provenance-bearing source, without requiring `rumble-note` to own extraction or canonical storage.

### Owner

`rumble-note` for local reference UX; `wrench-loader` and `gear-memory` likely own canonical extraction/provenance/source substrate.

### Fields

- `id`
- `workspace_id`
- `source_kind`: `url`, `file`, `note`, `transcript`, `document`, `dataset`, `external_id`.
- `title`
- `locator`: path, URL, source ID, or canonical reference.
- `provenance`
- `verification_state`: `unverified`, `verified`, `stale`, `failed`.
- `created_at`
- `updated_at`

### Lifecycle States

- `active`
- `stale`
- `archived`

### Relationships

- May be linked from blocks.
- May originate from `wrench-loader` output.
- May map to Gear source/provenance primitives.

### Invariants

- Imported source metadata is distinguishable from user-authored notes.
- Verification state must be visible in handoff exports.
- Missing provenance prevents trusted-source status but not local note-taking.

### State Transitions

- `unverified -> verified`
- `verified -> stale`
- `stale -> verified`
- `active -> archived`

### Deletion / Archive Rules

- Archive preferred if blocks reference the source.
- Hard delete leaves unresolved source references unless user also removes links.

### Emitted Events

- `note.source_reference.created`
- `note.source_reference.verified`
- `note.source_reference.marked_stale`
- `note.source_reference.archived`

### Shared Capability Candidates

- Source.
- Provenance.
- Import pipeline.

## Entity: HandoffPackage

### Definition

Deterministic package of selected block revisions and metadata prepared for a declared purpose and target.

### Owner

`rumble-note` creates packages; downstream owner depends on target: `rumble-canvas`, Bolt/`cos-matic`, `rumble-lm`, `gear-memory`, or local export.

### Fields

- `id`
- `workspace_id`
- `purpose`: `source_context`, `spec_context`, `task_context`, `learning_session_context`, `harness_context`, `export`.
- `target`: `local_export`, `harness`, `rumble_canvas`, `rumble_lm`, `bolt_cos_matic`.
- `post_mvp_purpose`: `memory_candidate`, only when durable memory submission is specified.
- `post_mvp_target`: `gear_memory`, only through an explicit promotion workflow.
- `status`: `draft`, `validated`, `exported`, `submitted`, `accepted`, `rejected`, `superseded`.
- `items`: list of `HandoffItem`.
- `constraints`: privacy, execution policy, audience, source requirements.
- `summary`: user-authored brief.
- `created_at`
- `updated_at`
- `submitted_at`

### Lifecycle States

- `draft`
- `validated`
- `exported`
- `submitted`
- `accepted`
- `rejected`
- `superseded`

### Relationships

- Contains snapshots of selected blocks.
- References sources and relationships included in the package.
- May link to downstream returned artifact/status.

### Invariants

- Handoff is explicit and user-confirmed.
- Package includes immutable block revision snapshots or content hashes.
- Package purpose and target are required.
- Handoff cannot authorize execution directly; planning/execution remains downstream.
- Blocks marked `private`, `sensitive`, or `no_handoff` require visible review and/or explicit override.

### State Transitions

- `draft -> validated`
- `validated -> exported`
- `validated -> submitted`
- `submitted -> accepted`
- `submitted -> rejected`
- `accepted -> superseded`
- `rejected -> draft` for repair

### Deletion / Archive Rules

- Handoff manifests should be retained locally for audit unless user purges history.
- Purging a handoff does not delete source blocks.

### Emitted Events

- `note.handoff.created`
- `note.handoff.validated`
- `note.handoff.exported`
- `note.handoff.submitted`
- `note.handoff.accepted`
- `note.handoff.rejected`
- `note.handoff.superseded`

### Shared Capability Candidates

- Spec package.
- Implementation handoff.
- Artifact.
- Activity/event log.
- Permission/audit policy.

## Value Object: HandoffItem

### Definition

Snapshot of one included block or source in a handoff package.

### Fields

- `item_id`
- `source_ref`: block/source/document reference.
- `revision_id` or `content_hash`.
- `included_content`
- `included_metadata`
- `role_in_package`: `context`, `evidence`, `question`, `decision`, `risk`, `task`, `objective`, `private_facilitator_note`, `participant_safe_material`.
- `redaction_state`: `none`, `redacted`, `omitted_with_marker`.

### Invariants

- Package item content must match the recorded revision/hash at validation time.
- Redactions must be explicit.

## Entity: LocalIndex

### Definition

Local searchable projection over blocks, links, labels, sources, and handoff states.

### Owner

`rumble-note` UX; underlying index substrate may become Gear-owned if reused.

### Fields

- `workspace_id`
- `index_kind`: `text`, `links`, `labels`, `handoff`, `source`.
- `status`: `ready`, `stale`, `rebuilding`, `failed`.
- `last_built_at`

### Lifecycle States

- `ready`
- `stale`
- `rebuilding`
- `failed`

### Relationships

- Derived from workspace content.

### Invariants

- Index is rebuildable from local truth.
- Index failure must not corrupt source notes.

### Emitted Events

- `note.index.marked_stale`
- `note.index.rebuild_started`
- `note.index.rebuild_completed`
- `note.index.rebuild_failed`

### Shared Capability Candidates

- Gear search/index substrate.

## Open Model Questions

| Question | Impact | Recommendation |
| --- | --- | --- |
| Should workspace be shared Rumble or Gear-level? | High | Use product-local `Workspace` now, design IDs/settings so it can map to shared primitive later. |
| Should `SourceReference` be a local object or Gear source pointer? | High | Keep local wrapper with optional Gear/Wrench canonical IDs. |
| Should block content be Markdown-only or structured dual-format? | Medium | Use Markdown/human text for MVP, preserve metadata in structured sidecar/export. |
| Should sync be built into MVP? | High | No mandatory sync; define local-first storage so optional sync adapter can be added later. |
| Should embeddings/semantic search exist? | Medium | Not MVP; start with deterministic local text/link/type search. |

## Shared Bricks Identified

| Brick | Needed by `rumble-note` | Candidate Owner | Notes |
| --- | --- | --- | --- |
| Workspace / project space | Local root and future collaboration | Shared Rumble vs Gear | Keep local MVP isolated. |
| Source | Source references and provenance | Gear Memory + Wrench Loader | Local wrapper needed. |
| Provenance | Trusted source and handoff evidence | Gear | Required for note-to-source and learning flows. |
| Import pipeline | Bring extracted content into notes | Wrench Loader | `rumble-note` consumes, does not own. |
| Activity/event log | Local audit and handoff history | Gear candidate | MVP can use local event log. |
| Traceability link | Block-to-source/spec/task/session links | Shared Rumble/Gear candidate | Needed beyond Canvas. |
| Spec package / artifact | Exported handoff package | Gear artifact + Rumble UX | Package format should be deterministic. |
| Agent task | Task candidate handoff | Bolt/`cos-matic` | Note creates candidate; Bolt owns lifecycle. |
| Memory-entry | Durable memory candidate | Gear Memory | Post-MVP; user must explicitly promote through a dedicated workflow. |
| Visual graph/canvas | Explore block relationships | `rumble-canvas` | Note exposes graph data, does not own visual canvas. |

## MVP Domain Cut

Include in MVP:

- `Workspace`
- `Notebook`
- `Document`
- `Block`
- `Reference`
- `SourceReference`
- `HandoffPackage`
- `HandoffItem`
- `LocalIndex`

Defer:

- multi-user collaboration;
- mandatory sync;
- plugin system;
- semantic/embedding search;
- large ingestion pipelines;
- autonomous memory recall;
- visual graph editor.
