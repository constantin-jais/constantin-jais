# Screens and Actions — rumble-note

Status: Drafting.

## MVP Screens

1. Workspace Home
2. Inbox / Quick Capture
3. Notebook Documents
4. Document Editor
5. Block Inspector
6. Search
7. Sources
8. Handoff Builder
9. Export / Privacy Review
10. Settings

## Screen: Workspace Home

### Purpose

Give the user a local overview and fast entry into capture, documents, search, and handoffs.

### Route / Entry Point

`/workspace/:workspace_id`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Workspace name and local status.
- Recent documents.
- Inbox count.
- Draft handoffs.
- Stale sources or broken references summary.
- Index status.

### Actions by Role

All human roles:

- open inbox;
- create document;
- open search;
- open draft handoff;
- open source list;
- open settings.

Local Knowledge Owner only:

- archive workspace;
- export workspace;
- rebuild index.

### Empty State

Show first-run actions: create notebook, capture into inbox, create document, configure privacy defaults.

### Loading State

Show local workspace loading and index status separately.

### Error State

If workspace metadata cannot load, show repair option and local path.

### Offline State

Normal state. Network absence must not block workspace use.

### Permission Denied State

MVP is local single-owner. Future collaborative mode should show read-only or inaccessible workspace state.

### Accessibility Notes

All primary actions must be keyboard reachable. Recent documents list must expose document title and updated time to screen readers.

### Telemetry / Events

- `note.workspace.opened`
- `note.index.rebuild_requested`

### Service Calls

- Load workspace summary.
- Load recent documents.
- Load handoff drafts.
- Load index health.

### Acceptance Criteria

- User can reach capture, search, and handoffs in one action.
- Workspace remains usable offline.
- Stale index does not block document opening.

## Screen: Inbox / Quick Capture

### Purpose

Capture blocks quickly without forcing structure upfront.

### Route / Entry Point

`/workspace/:workspace_id/inbox`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Capture input.
- Untriaged blocks.
- Suggested block types.
- Privacy default indicator.

### Actions by Role

All human roles:

- create block;
- edit block;
- set block type;
- add label;
- move block to document;
- mark `no_handoff`;
- create source reference from block.

### Empty State

Show capture prompt and examples: thought, quote, question, decision, task candidate.

### Loading State

Render existing local blocks first; index status may load later.

### Error State

If save fails, keep local draft in memory and show retry.

### Offline State

Normal state.

### Permission Denied State

Future collaborative mode: show read-only captured blocks if no write permission.

### Accessibility Notes

Capture input supports keyboard-only creation and block type shortcuts.

### Telemetry / Events

- `note.block.created`
- `note.block.updated`
- `note.block.moved`

### Service Calls

- Create block.
- Update block.
- Move block.
- Update local index.

### Acceptance Criteria

- User can create a block offline.
- Block receives stable ID immediately.
- User can move captured block into a document without changing ID.

## Screen: Notebook Documents

### Purpose

Browse and manage documents inside a notebook.

### Route / Entry Point

`/workspace/:workspace_id/notebooks/:notebook_id`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Notebook title and description.
- Document list.
- Document types.
- Last updated timestamps.
- Archive status.

### Actions by Role

All human roles:

- create document;
- open document;
- rename document;
- archive document;
- move document to another notebook.

Local Knowledge Owner:

- rename notebook;
- archive notebook;
- export notebook.

### Empty State

Show create document and move inbox blocks here.

### Loading State

Show notebook metadata first, then documents.

### Error State

If notebook missing, show unresolved state and link to workspace home.

### Offline State

Normal state.

### Permission Denied State

Future collaborative mode: hide destructive actions if read-only.

### Accessibility Notes

Document list supports keyboard navigation and announces archived state.

### Telemetry / Events

- `note.notebook.opened`
- `note.document.created`
- `note.document.archived`

### Service Calls

- Load notebook.
- List documents.
- Create/update/archive document.

### Acceptance Criteria

- User can create a document in a notebook.
- Archiving a document does not delete its blocks or handoff history.

## Screen: Document Editor

### Purpose

Write and structure notes as stable addressable blocks.

### Route / Entry Point

`/workspace/:workspace_id/documents/:document_id`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Document title and metadata.
- Ordered block tree.
- Block type indicators.
- Inline references/backlinks count.
- Privacy indicators.
- Handoff inclusion markers.

### Actions by Role

All human roles:

- create block;
- edit block;
- delete/archive block;
- move block;
- nest/unnest block;
- change block type;
- add label;
- add reference;
- open block inspector;
- select blocks for handoff.

Spec / Product Author:

- qualify block as spec candidate, decision, risk, open question, or task candidate.

Learning Session Preparer:

- qualify block as objective, source claim, question, example, activity idea, facilitator note, or participant-safe material.

### Empty State

Show first block placeholder and common block shortcuts.

### Loading State

Show document shell and progressively load block tree from local storage.

### Error State

If document cannot load, show repair/reindex options and link to notebook.

### Offline State

Normal state.

### Permission Denied State

Future collaborative mode: read-only view with disabled editing controls.

### Accessibility Notes

Block navigation must be keyboard accessible. Nested structure must expose heading/outline semantics.

### Telemetry / Events

- `note.document.opened`
- `note.block.created`
- `note.block.updated`
- `note.reference.created`
- `note.block.qualified`

### Service Calls

- Load document and blocks.
- Create/update/move/archive blocks.
- Create references.
- Update index.

### Acceptance Criteria

- Moving a block preserves its ID.
- Block edits update local index.
- Blocks marked `no_handoff` are visibly excluded from selection by default.

## Screen: Block Inspector

### Purpose

Inspect and edit metadata for one selected block.

### Route / Entry Point

Side panel from Document Editor or Search.

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Block ID.
- Type.
- Labels.
- Qualification.
- Privacy state.
- Source references.
- Forward references.
- Backlinks.
- Handoff history.

### Actions by Role

All human roles:

- copy block ID;
- change type;
- change labels;
- change privacy state;
- add/remove reference;
- link source;
- add to handoff draft.

Local Knowledge Owner:

- override `no_handoff` for a package with reason;
- archive block;
- hard-delete block when allowed.

### Empty State

No block selected: explain that inspector shows metadata, links, and handoff status.

### Loading State

Show block metadata first, then backlinks/handoff history.

### Error State

If backlinks fail to load, show stale-index warning and rebuild option.

### Offline State

Normal state.

### Permission Denied State

Future collaborative mode: metadata read-only if user cannot edit block.

### Accessibility Notes

Inspector must not trap keyboard focus. Relationship type controls require text labels.

### Telemetry / Events

- `note.block.inspected`
- `note.block.qualified`
- `note.reference.created`

### Service Calls

- Load block metadata.
- Load references/backlinks.
- Update block metadata.
- Add block to handoff draft.

### Acceptance Criteria

- User can see where a block is referenced.
- User can distinguish private/no-handoff blocks.
- Handoff history references package IDs and statuses.

## Screen: Search

### Purpose

Retrieve blocks and assemble context.

### Route / Entry Point

`/workspace/:workspace_id/search`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Query input.
- Filters.
- Result list by block.
- Document context snippets.
- Source/reference indicators.
- Add-to-handoff controls.

### Actions by Role

All human roles:

- run search;
- apply filters;
- open result;
- inspect block;
- select result;
- add selected blocks to handoff draft;
- rebuild index if stale.

### Empty State

Show filter suggestions and browse fallback.

### Loading State

Show query progress and local index status.

### Error State

Invalid query: show validation message. Corrupt index: show rebuild action.

### Offline State

Normal state using local index or local scan fallback.

### Permission Denied State

Future collaborative mode: omit inaccessible results.

### Accessibility Notes

Result count and filter changes should be announced to assistive tech.

### Telemetry / Events

- `note.search.executed`
- `note.search.result_selected`
- `note.index.rebuild_requested`

### Service Calls

- Search index.
- Load block snippets.
- Add selected blocks to handoff.

### Acceptance Criteria

- Search works offline.
- Results include block ID, type, document, and snippet.
- User can create or update a handoff draft from selected results.

## Screen: Sources

### Purpose

Manage provenance-bearing source references without owning ingestion pipelines.

### Route / Entry Point

`/workspace/:workspace_id/sources`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer
- Imported Source Provider through import flow only

### Displayed Data

- Source references.
- Source kind.
- Title/locator.
- Verification state.
- Linked block count.
- Imported/canonical metadata where available.

### Actions by Role

Human roles:

- create manual source reference;
- edit local source metadata;
- mark source stale;
- archive source reference;
- open linked blocks;
- add source to handoff context.

Imported Source Provider:

- provide source metadata through explicit user-approved import;
- update canonical extraction metadata.

### Empty State

Show create manual source and explain future/imported Wrench outputs.

### Loading State

Show source list first; linked block counts may load later.

### Error State

If source metadata invalid, mark source unverified and show repair action.

### Offline State

Manual and existing sources remain usable. Remote verification is unavailable.

### Permission Denied State

Future collaborative mode: source mutation disabled without write access.

### Accessibility Notes

Verification state must not rely on color only.

### Telemetry / Events

- `note.source_reference.created`
- `note.source_reference.updated`
- `note.source_reference.marked_stale`

### Service Calls

- List source references.
- Create/update/archive source reference.
- Resolve linked blocks.

### Acceptance Criteria

- User can create an unverified source reference.
- Imported metadata is distinguishable from user-authored notes.
- Source verification state appears in handoff previews.

## Screen: Handoff Builder

### Purpose

Prepare selected blocks as deterministic context package for a declared purpose and target.

### Route / Entry Point

`/workspace/:workspace_id/handoffs/:handoff_id`

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer
- Harness Consumer as downstream read-only consumer of submitted package

### Displayed Data

- Package purpose.
- Target.
- Included blocks and revisions/hashes.
- Included source references.
- Relationship graph as list.
- Privacy warnings.
- Missing provenance warnings.
- Redaction controls.
- Validation status.

### Actions by Role

Human roles:

- set package purpose;
- set target;
- add/remove blocks;
- assign role in package;
- redact item;
- validate package;
- export package;
- submit package to allowed downstream target;
- duplicate package;
- supersede package.

Local Knowledge Owner:

- override sensitive/no-handoff inclusion with reason;
- purge local package history.

Harness Consumer:

- read submitted package only;
- return status/refusal/artifact metadata through downstream integration.

### Empty State

Explain that handoff starts from block selection in editor/search or manual add.

### Loading State

Show package metadata, then included items and validation results.

### Error State

Show invalid package reasons: missing purpose, missing target, deleted block, privacy conflict, broken source reference.

### Offline State

Draft, validation, and local export work offline. Remote submission is unavailable.

### Permission Denied State

Future collaborative mode: user can view but not submit if lacking approval rights.

### Accessibility Notes

Validation errors must be listed textually and linked to affected items.

### Telemetry / Events

- `note.handoff.created`
- `note.handoff.validated`
- `note.handoff.exported`
- `note.handoff.submitted`
- `note.handoff.rejected`

### Service Calls

- Load/update handoff package.
- Validate handoff package.
- Export deterministic package.
- Submit to downstream target when configured.

### Acceptance Criteria

- User sees all included content before export/submission.
- Package purpose and target are required.
- `private`, `sensitive`, and `no_handoff` blocks require explicit review.
- Handoff cannot directly authorize execution.

## Screen: Export / Privacy Review

### Purpose

Preview, redact, and export workspace, notebook, document, selected blocks, or handoff package.

### Route / Entry Point

`/workspace/:workspace_id/export` or modal from Handoff Builder.

### Allowed Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer

### Displayed Data

- Export scope.
- Export format.
- Included blocks/assets/sources.
- Private/sensitive markers.
- PII markers when present.
- Redaction manifest.
- Destination path.

### Actions by Role

All human roles:

- choose scope;
- choose format;
- preview export;
- redact item;
- create export.

Local Knowledge Owner:

- export full workspace;
- export backup;
- purge export manifest.

### Empty State

Prompt user to choose export scope.

### Loading State

Show manifest generation progress.

### Error State

Missing asset, invalid path, permission error, or broken reference warning.

### Offline State

Normal for local export.

### Permission Denied State

Future collaborative mode: full workspace export disabled without owner permission.

### Accessibility Notes

Redacted and omitted items must be announced in the preview.

### Telemetry / Events

- `note.export.previewed`
- `note.export.created`
- `note.export.failed`

### Service Calls

- Build export manifest.
- Validate privacy constraints.
- Write export artifact.

### Acceptance Criteria

- Export is readable without the app.
- User can see private/sensitive data before export.
- Redaction manifest is included.

## Screen: Settings

### Purpose

Configure local workspace behavior, privacy defaults, indexing, and future integration endpoints.

### Route / Entry Point

`/workspace/:workspace_id/settings`

### Allowed Roles

- Local Knowledge Owner

### Displayed Data

- Workspace local path.
- Privacy defaults.
- Index status.
- Export defaults.
- Audit/event log settings.
- Optional downstream target configuration.

### Actions by Role

Local Knowledge Owner:

- update workspace name;
- update privacy defaults;
- update export defaults;
- rebuild index;
- inspect local audit log;
- configure downstream targets;
- archive workspace.

### Empty State

Not applicable; settings always show current defaults.

### Loading State

Show settings sections independently.

### Error State

If settings cannot save, show failed fields and preserve unsaved changes.

### Offline State

Normal state except remote target validation.

### Permission Denied State

Future collaborative mode: non-owner sees read-only settings subset.

### Accessibility Notes

Settings sections must have headings and explicit field descriptions.

### Telemetry / Events

- `note.settings.updated`
- `note.index.rebuild_requested`

### Service Calls

- Load workspace settings.
- Update workspace settings.
- Rebuild local index.

### Acceptance Criteria

- Privacy defaults are visible and editable.
- Index can be rebuilt without modifying source notes.
- Remote target config is optional.

---

# Core Actions

## Action: Create Block

### Actor

Any human role with write access.

### Intent

Capture or add a new addressable note fragment.

### Input

- document or inbox target;
- parent block optional;
- content;
- block type optional;
- privacy optional.

### Preconditions

- Workspace is writable.
- Target document or inbox exists.

### Business Rules

- Assign stable block ID immediately.
- Default privacy comes from workspace/document settings.
- New block starts as `draft` or `active` depending on capture mode.

### Validation Rules

- Content must not exceed configured block size.
- Parent block must belong to same document.

### Side Effects

- Document updated timestamp changes.
- Local index marked stale or updated.

### Events Emitted

- `note.block.created`

### Audit Log

Record actor, workspace, document, block ID, timestamp.

### Permission Check

User must have write access to target workspace/document.

### Idempotency

Client-supplied idempotency key prevents duplicate block creation on retry.

### Rollback / Retry

If index update fails, keep block and mark index stale.

### Errors

- workspace not writable;
- invalid parent;
- content too large;
- storage failure.

### Acceptance Criteria

- Block exists with stable ID after successful save.
- Failure does not create partial duplicate blocks.

## Action: Create Reference

### Actor

Any human role with write access to source object.

### Intent

Connect a block/document/source to another object with relationship meaning.

### Input

- source reference;
- target reference;
- relationship type;
- optional description.

### Preconditions

- Source exists.
- Target exists or is explicitly allowed as unresolved placeholder.

### Business Rules

- Non-mention relationships require a type.
- Backlink is a computed projection.
- Broken target is marked unresolved, not silently removed.

### Validation Rules

- Prevent invalid self-reference unless relationship type explicitly allows it.
- Relationship type must be in allowed enum.

### Side Effects

- Link index updated.
- Target backlink list updates.

### Events Emitted

- `note.reference.created`
- `note.backlink.indexed`

### Audit Log

Record source, target, relationship type, actor, timestamp.

### Permission Check

User must edit source object. Future collaborative mode may require target visibility.

### Idempotency

Duplicate source-target-type references are collapsed unless user explicitly creates another annotated link.

### Rollback / Retry

If backlink projection fails, keep reference and mark link index stale.

### Errors

- invalid target;
- invalid relationship type;
- permission denied;
- storage failure.

### Acceptance Criteria

- Forward reference and backlink are visible.
- Link is exportable with relationship type.

## Action: Qualify Block

### Actor

Any human role with write access.

### Intent

Assign reusable meaning to a block for retrieval and handoff.

### Input

- block ID;
- qualification kind;
- optional confidence;
- optional reason.

### Preconditions

- Block exists and is editable.

### Business Rules

- Qualification does not imply downstream acceptance.
- MVP supports at most one primary qualification kind per block.

### Validation Rules

- Qualification kind must be allowed.
- Reason may be required for rejection or override states.

### Side Effects

- Block metadata updated.
- Search index updated.

### Events Emitted

- `note.block.qualified`

### Audit Log

Record previous and new qualification.

### Permission Check

User must edit block metadata.

### Idempotency

Setting same qualification twice is a no-op.

### Rollback / Retry

Metadata update is atomic with block revision update.

### Errors

- block missing;
- invalid qualification;
- permission denied.

### Acceptance Criteria

- Qualified block appears in type/qualification filters.

## Action: Create Handoff Package

### Actor

Any human role with write access.

### Intent

Create a draft package from selected blocks.

### Input

- selected block IDs;
- purpose;
- target optional at draft stage;
- summary optional.

### Preconditions

- Selected blocks exist.

### Business Rules

- Package starts as `draft`.
- Package records block IDs and current revisions/hashes.
- `no_handoff` blocks are excluded by default.

### Validation Rules

- At least one included item is required.
- Purpose must be allowed.

### Side Effects

- Handoff draft created.
- Included blocks record handoff draft marker.

### Events Emitted

- `note.handoff.created`

### Audit Log

Record package ID, included block IDs, actor, timestamp.

### Permission Check

User must be able to read selected blocks and create package in workspace.

### Idempotency

Retry with same idempotency key returns same draft package.

### Rollback / Retry

If marker update fails, package remains draft and validation reports stale markers.

### Errors

- no valid blocks;
- private/no-handoff conflict;
- storage failure.

### Acceptance Criteria

- Draft package opens in Handoff Builder.
- Included items show current block revisions/hashes.

## Action: Validate Handoff Package

### Actor

Human role preparing handoff.

### Intent

Check package completeness, privacy, provenance, and target constraints before export/submission.

### Input

- handoff package ID.

### Preconditions

- Package exists in draft or repaired state.

### Business Rules

- Purpose and target are required before submission/export.
- Sensitive/private/no-handoff blocks require review.
- Missing source provenance creates warning or blocking error depending on purpose.
- Validation cannot authorize execution.

### Validation Rules

- Included block revisions/hashes must match current or intentionally pinned content.
- Deleted blocks must be replaced, omitted, or represented as tombstones.

### Side Effects

- Package status becomes `validated` if checks pass.
- Validation report is stored.

### Events Emitted

- `note.handoff.validated`

### Audit Log

Record validation result, warnings, blocking errors, actor, timestamp.

### Permission Check

User must edit package.

### Idempotency

Repeated validation with unchanged package returns same result.

### Rollback / Retry

Failed validation keeps package draft with repair instructions.

### Errors

- missing target;
- privacy conflict;
- source provenance required;
- stale block revision;
- broken reference.

### Acceptance Criteria

- User sees actionable validation errors.
- Validated package has deterministic manifest.

## Action: Export Handoff Package

### Actor

Human role preparing handoff.

### Intent

Write deterministic local package for humans and agents.

### Input

- handoff package ID;
- export format;
- destination path;
- redaction choices.

### Preconditions

- Package is validated.
- Destination path is writable.

### Business Rules

- Export includes manifest, included items, source references, redaction markers, and package metadata.
- Export does not require network access.

### Validation Rules

- Export format must be supported.
- Redaction must not silently remove required fields without manifest marker.

### Side Effects

- Export artifact written locally.
- Package status becomes `exported`.

### Events Emitted

- `note.handoff.exported`

### Audit Log

Record package ID, export path or artifact reference, format, actor, timestamp.

### Permission Check

User must export package and write destination.

### Idempotency

Same package revision and destination can overwrite only with explicit confirmation or versioned filename.

### Rollback / Retry

Failed export removes partial file or marks it incomplete.

### Errors

- destination unavailable;
- permission denied;
- unsupported format;
- partial write failure.

### Acceptance Criteria

- Export can be read without `rumble-note`.
- Manifest lists included/redacted/omitted items.

## Action: Submit Handoff Package

### Actor

Human role preparing handoff.

### Intent

Send a validated package to an allowed downstream target.

### Input

- handoff package ID;
- target;
- submission metadata.

### Preconditions

- Package is validated.
- Target is configured and reachable unless queued for later.

### Business Rules

- Submission is context/planning only.
- `rumble-note` never authorizes direct execution.
- Downstream response is recorded as status/artifact/refusal metadata.

### Validation Rules

- Target must match package purpose.
- User must confirm included sensitive/private content.

### Side Effects

- Package status becomes `submitted` or queued.
- Downstream response may create linked artifact/status record.

### Events Emitted

- `note.handoff.submitted`
- `note.handoff.accepted`
- `note.handoff.rejected`

### Audit Log

Record package ID, target, actor, timestamp, and downstream response reference.

### Permission Check

User must have permission to submit to target.

### Idempotency

Submission uses package revision ID to avoid duplicate downstream requests.

### Rollback / Retry

If target unavailable, package remains validated and can be retried. If target rejects, package moves to rejected with reason.

### Errors

- target unavailable;
- target rejects package;
- policy violation;
- privacy confirmation missing.

### Acceptance Criteria

- User receives accepted/rejected/queued status.
- No downstream execution is authorized by this action.
