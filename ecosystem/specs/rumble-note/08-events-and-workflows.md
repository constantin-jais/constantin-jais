# Events and Workflows — rumble-note

Status: Drafting.

## Event Principles

- Events are local-first and metadata-only by default.
- Events support audit, debugging, index rebuild, and handoff traceability.
- Sensitive content must not be logged unless explicitly required and marked.
- Event names use `note.<domain>.<verb>`.
- Index events are projections; source records remain authoritative.

## Event: note.workspace.created

### Producer

WorkspaceService.

### Consumers

Event log, settings UI, backup/export services.

### Payload

- workspace ID
- local root reference
- settings schema version
- actor reference

### Persistence

Persistent local event.

### Replay Behavior

Informational; not required to rebuild workspace.

### Audit Relevance

Medium.

## Event: note.block.created

### Producer

BlockService.

### Consumers

IndexService, event log, document editor, search.

### Payload

- block ID
- document ID
- parent block ID optional
- block type
- privacy
- revision
- actor reference

### Persistence

Persistent metadata event.

### Replay Behavior

Can help rebuild projections but block table remains source of truth.

### Audit Relevance

High for handoff-related blocks, medium otherwise.

## Event: note.block.updated

### Producer

BlockService.

### Consumers

IndexService, event log, handoff validation.

### Payload

- block ID
- document ID
- changed fields metadata
- new revision
- content hash
- actor reference

### Persistence

Persistent metadata event. Content diffs disabled by default.

### Replay Behavior

Projection update only.

### Audit Relevance

High when block is included in a handoff package.

## Event: note.block.moved

### Producer

BlockService.

### Consumers

Document editor, index service.

### Payload

- block ID
- from parent/sort
- to parent/sort
- document ID

### Persistence

Persistent metadata event.

### Replay Behavior

Projection update.

### Audit Relevance

Medium.

## Event: note.block.qualified

### Producer

BlockService.

### Consumers

SearchService, HandoffService, event log.

### Payload

- block ID
- previous qualification
- new qualification
- actor reference

### Persistence

Persistent metadata event.

### Replay Behavior

Projection update.

### Audit Relevance

High when qualification leads to handoff.

## Event: note.reference.created

### Producer

ReferenceService.

### Consumers

Backlink projection, SearchService, HandoffService.

### Payload

- reference ID
- source pointer
- target pointer
- relationship type
- actor reference

### Persistence

Persistent.

### Replay Behavior

Can rebuild backlink index.

### Audit Relevance

High for source/provenance links.

## Event: note.source_reference.created

### Producer

SourceReferenceService or approved Wrench import flow.

### Consumers

SearchService, HandoffService, Sources screen.

### Payload

- source reference ID
- source kind
- locator hash or redacted locator
- verification state
- canonical source ID optional

### Persistence

Persistent.

### Replay Behavior

Projection update.

### Audit Relevance

High.

## Event: note.handoff.created

### Producer

HandoffService.

### Consumers

Handoff screen, event log, PrivacyReviewService.

### Payload

- package ID
- purpose
- target optional
- included block IDs
- actor reference

### Persistence

Persistent.

### Replay Behavior

Not enough to rebuild package; package table is source of truth.

### Audit Relevance

High.

## Event: note.handoff.validated

### Producer

HandoffService / PrivacyReviewService.

### Consumers

Handoff screen, ExportService, downstream submission.

### Payload

- package ID
- validation status
- warning/error codes
- manifest hash
- actor reference

### Persistence

Persistent.

### Replay Behavior

Informational; validation can be rerun.

### Audit Relevance

High.

## Event: note.handoff.exported

### Producer

ExportService.

### Consumers

Event log, Handoff screen.

### Payload

- package ID
- export artifact reference
- format
- manifest hash
- actor reference

### Persistence

Persistent, with destination path optionally redacted.

### Replay Behavior

No replay; export can be regenerated if package is retained.

### Audit Relevance

High.

## Event: note.handoff.submitted

### Producer

HandoffService.

### Consumers

Event log, downstream status adapter.

### Payload

- package ID
- target
- package revision/hash
- execution policy
- actor reference

### Persistence

Persistent.

### Replay Behavior

Must not auto-resubmit on replay. Retry is explicit.

### Audit Relevance

Critical.

## Event: note.handoff.rejected

### Producer

Downstream adapter.

### Consumers

Handoff screen, event log.

### Payload

- package ID
- target
- refusal reason/code
- downstream reference optional

### Persistence

Persistent.

### Replay Behavior

Informational.

### Audit Relevance

High.

## Event: note.export.created

### Producer

ExportService.

### Consumers

Event log.

### Payload

- export ID
- scope type
- format
- manifest hash
- actor reference

### Persistence

Persistent depending on local audit settings; handoff exports always logged by default.

### Replay Behavior

No automatic re-export.

### Audit Relevance

High for handoff, medium for private backup.

## Event: note.index.rebuild_completed

### Producer

IndexService.

### Consumers

Search screen, Workspace Home.

### Payload

- workspace ID
- index kind
- status
- duration

### Persistence

Optional metadata event.

### Replay Behavior

None.

### Audit Relevance

Low.

---

# Workflows

## Workflow: Capture to Indexed Block

### Trigger

User creates a block in Inbox or Document Editor.

### Steps

1. BlockService validates target and input.
2. BlockService assigns stable block ID.
3. Block record is saved locally.
4. `note.block.created` is emitted.
5. IndexService updates or marks index stale.
6. UI confirms saved state.

### Gates

- writable workspace;
- valid parent/document;
- content size limit.

### Rollback

If block save fails, keep unsaved draft. If index fails, keep block and mark index stale.

### Retry

Retry save with idempotency key.

### Evidence

Block ID, revision, event log entry.

## Workflow: Create Backlink

### Trigger

User creates a typed reference from one block/source to another.

### Steps

1. ReferenceService validates source and target pointer.
2. Relationship type is checked.
3. Reference is persisted.
4. Backlink projection is updated.
5. UI displays forward link and backlink.

### Gates

- edit permission on source;
- valid relationship type;
- unresolved target explicitly allowed if target missing.

### Rollback

If projection update fails, keep reference and mark link index stale.

### Retry

Rebuild link index.

### Evidence

Reference ID and event.

## Workflow: Search to Handoff Draft

### Trigger

User searches and selects blocks for reuse.

### Steps

1. SearchService executes query locally.
2. User selects results.
3. HandoffService creates or updates draft package.
4. Blocks with `no_handoff` are excluded by default.
5. Draft opens in Handoff Builder.

### Gates

- readable blocks;
- at least one valid block.

### Rollback

Remove selection from draft or delete draft.

### Retry

Retry package creation with idempotency key.

### Evidence

Draft package ID and selected block IDs.

## Workflow: Handoff Privacy Validation

### Trigger

User validates a handoff package.

### Steps

1. HandoffService loads package items.
2. PrivacyReviewService checks privacy markers.
3. SourceReferenceService checks required source states.
4. HandoffService verifies block revisions/hashes.
5. Validation report is stored.
6. Package moves to `validated` or remains draft with errors.

### Gates

- purpose set;
- target set;
- no unresolved blocking privacy conflicts;
- source requirements satisfied or warning accepted where allowed.

### Rollback

Failed validation leaves package editable.

### Retry

User repairs and reruns validation.

### Evidence

Validation report, manifest hash, event log.

## Workflow: Local Export

### Trigger

User exports workspace/notebook/document/blocks/handoff.

### Steps

1. ExportService builds manifest.
2. PrivacyReviewService flags sensitive/private data.
3. User confirms or redacts.
4. ExportService writes bundle.
5. Manifest hash and export event are recorded.

### Gates

- writable destination;
- explicit confirmation for sensitive/private scope;
- redaction manifest for omitted content.

### Rollback

Partial export is removed or marked incomplete.

### Retry

User retries same manifest or chooses new destination.

### Evidence

Export manifest, artifact hash, event log entry.

## Workflow: Submit Handoff to Harness/Bolt

### Trigger

User submits a validated package to configured downstream target.

### Steps

1. HandoffService checks package status and manifest hash.
2. User confirms final package preview.
3. Downstream adapter submits package with `context_only` or `planning_only` policy.
4. Adapter records accepted/queued/rejected response.
5. Package status updates.

### Gates

- package validated;
- execution policy forbids direct execution;
- target configured;
- sensitive/private confirmation complete.

### Rollback

No automatic rollback of downstream receipt. If rejected, package can be repaired and resubmitted as new revision.

### Retry

Retry only with same package revision idempotency key. Never replay event to resubmit automatically.

### Evidence

Submission event, target response reference, package manifest.

## Workflow: Import Source Reference from Wrench Output

### Trigger

User chooses to import or reference Wrench Loader output.

### Steps

1. User selects source bundle or canonical source ID.
2. SourceReferenceService verifies metadata/checksum where possible.
3. User chooses import scope: reference only or selected content blocks.
4. SourceReference is created.
5. Optional imported blocks are marked as imported/source-derived.

### Gates

- explicit user selection;
- provenance metadata available or source marked unverified;
- no broad ingestion without scope.

### Rollback

Remove imported source reference and optionally imported blocks.

### Retry

Re-import with same canonical ID detects duplicate.

### Evidence

Source reference event, provenance metadata, checksum if available.

## Workflow: Rebuild Local Index

### Trigger

Index stale/corrupt or user requests rebuild.

### Steps

1. IndexService marks index `rebuilding`.
2. Reads local authoritative tables.
3. Rebuilds text/link/label/source/handoff projections.
4. Marks index `ready` or `failed`.

### Gates

- local store readable;
- enough disk space.

### Rollback

Keep prior index until new index completes where possible.

### Retry

User or system can retry.

### Evidence

Index status and rebuild event.
