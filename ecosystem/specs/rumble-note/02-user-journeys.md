# User Journeys — rumble-note

Status: Drafting.

## Journey: Quick Capture to Structured Block

### Trigger

The user has a thought, observation, quote, question, or decision to preserve.

### Actor

Local Knowledge Owner.

### Preconditions

- A local workspace exists.
- User has write access to the target notebook or inbox.

### Happy Path

1. User opens quick capture or a document.
2. User writes the note as one or more blocks.
3. System assigns stable block IDs.
4. User optionally sets block type, labels, and source reference.
5. System saves locally and indexes the blocks.

### Alternate Paths

- User captures into an inbox without choosing a notebook.
- User creates nested blocks under an existing heading.
- User marks a block as private/no-handoff.

### Failure Paths

- Local storage unavailable.
- Block content exceeds configured size.
- Workspace index cannot update.

### Recovery Path

- Keep an unsynced local draft.
- Retry index update.
- Show a warning if search may be stale.

### Data Created or Updated

- `Document` or inbox entry.
- `Block` records.
- Optional `BlockLabel`, `Reference`, and local index entries.

### Events Emitted

- `note.block.created`
- `note.block.updated`
- `note.index.update_requested`

### Audit Requirements

- Local audit entry records creation timestamp, actor reference, document, and block IDs.

### Acceptance Criteria

- A block can be created offline.
- A stable block ID is generated immediately.
- The block appears in search after indexing succeeds.

## Journey: Create a Typed Backlink

### Trigger

The user identifies that one block supports, contradicts, expands, depends on, mentions, or derives from another block/source.

### Actor

Local Knowledge Owner or Spec / Product Author.

### Preconditions

- Source and target block or source reference exist.
- User can edit the source block.

### Happy Path

1. User selects a block.
2. User adds a reference to another block, document, or source.
3. User chooses a relationship type.
4. System creates the forward reference and computed backlink.
5. System displays the backlink on the target.

### Alternate Paths

- User creates an untyped mention first, then qualifies it later.
- User links to a not-yet-created placeholder block.
- User links to imported source content from `gear-loader`.

### Failure Paths

- Target ID cannot be resolved.
- Link would create an invalid self-reference.
- User lacks permission in a collaborative future workspace.

### Recovery Path

- Save unresolved reference as a warning state.
- Let user repair or remove broken links.

### Data Created or Updated

- `BlockLink` / `Reference`.
- Computed backlink index.
- Updated document metadata.

### Events Emitted

- `note.reference.created`
- `note.backlink.indexed`

### Audit Requirements

- Relationship type, source ID, target ID, actor, and timestamp are recorded locally.

### Acceptance Criteria

- Backlink is visible from the target block.
- Link type is stored and exportable.
- Deleting the source block does not silently erase prior handoff provenance.

## Journey: Search and Retrieve Context

### Trigger

The user needs to find prior notes relevant to a task, spec, source, or session.

### Actor

Any human role.

### Preconditions

- Workspace contains indexed blocks.

### Happy Path

1. User enters a query.
2. User filters by block type, label, notebook, source, relationship type, or handoff state.
3. System returns matching blocks with document context and key references.
4. User opens, selects, or adds blocks to a handoff package.

### Alternate Paths

- Index is stale; system falls back to slower local scan.
- User searches while offline; local index is used.
- User saves a search as a collection candidate.

### Failure Paths

- Index corrupted.
- Query syntax invalid.
- Too many results to render safely.

### Recovery Path

- Rebuild local index.
- Show query validation errors.
- Paginate or narrow results.

### Data Created or Updated

- Optional saved search or selection set.
- Search telemetry in local event log if enabled.

### Events Emitted

- `note.search.executed`
- `note.search.index_rebuild_requested`

### Audit Requirements

- No mandatory audit for ordinary local search.
- Handoff-related selection history is recorded when a package is created.

### Acceptance Criteria

- Search works offline.
- Results include block ID, document, type, and matching context.
- User can add selected results to a handoff package.

## Journey: Note to Source

### Trigger

The user wants a note block to become or reference a source with provenance.

### Actor

Local Knowledge Owner, Spec / Product Author, or Imported Source Provider.

### Preconditions

- The block exists.
- User has permission to create source references.

### Happy Path

1. User selects a block or imported content.
2. User chooses `Prepare as source` or `Link to source`.
3. User adds provenance: URL/file/path/title/author/date/checksum/extraction reference where available.
4. System creates a `SourceReference` and links it to selected blocks.
5. User can include the source reference in future handoffs.

### Alternate Paths

- Source metadata comes from `gear-loader`.
- User creates a manual source with incomplete metadata and warning state.
- Existing duplicate source is detected and reused.

### Failure Paths

- Required provenance fields missing for trusted-source status.
- Imported source checksum mismatch.
- User tries to overwrite source metadata without creating a revision.

### Recovery Path

- Save as `unverified` source reference.
- Request re-import from `gear-loader`.
- Create a new source revision.

### Data Created or Updated

- `SourceReference`.
- `Reference` from block to source.
- Optional provenance metadata.

### Events Emitted

- `note.source_reference.created`
- `note.source_reference.verified`
- `note.source_reference.marked_unverified`

### Audit Requirements

- Source provenance changes are auditable.
- Trusted/unverified state changes record actor and reason.

### Acceptance Criteria

- A note can reference a source without importing the whole source.
- Provenance is preserved in export and handoff.
- Unverified sources are clearly marked.

## Journey: Note to Spec

### Trigger

The user wants selected blocks to feed a product/spec drafting flow.

### Actor

Spec / Product Author.

### Preconditions

- Selected blocks exist.
- User has reviewed included private/sensitive blocks.

### Happy Path

1. User selects blocks from a document or search results.
2. User chooses `Prepare spec context`.
3. System creates a handoff package with purpose `spec_context`.
4. User classifies blocks as goal, persona insight, journey, rule, risk, open question, decision, or source evidence.
5. User reviews included blocks, sources, and exclusions.
6. User exports or sends the package to `rumble-canvas` or the harness.

### Alternate Paths

- User saves package as draft.
- System warns that a claim lacks source reference.
- User includes contradictory blocks intentionally and labels them as conflict.

### Failure Paths

- Package contains archived/deleted block.
- Downstream consumer rejects missing required fields.
- Handoff target unavailable.

### Recovery Path

- Repair package by replacing missing blocks.
- Export locally instead of sending.
- Record downstream refusal and reason.

### Data Created or Updated

- `HandoffPackage`.
- `HandoffItem` per selected block.
- Block `handoff_state`.

### Events Emitted

- `note.handoff.created`
- `note.handoff.validated`
- `note.handoff.exported`
- `note.handoff.submitted`
- `note.handoff.rejected`

### Audit Requirements

- Record included block IDs, revisions, package purpose, target, timestamp, and actor.

### Acceptance Criteria

- Package content is previewable before export/submission.
- Output includes block IDs and source references.
- Downstream submission never executes work directly.

## Journey: Note to Task

### Trigger

The user identifies an actionable item in notes.

### Actor

Local Knowledge Owner or Spec / Product Author.

### Preconditions

- A block exists that can be interpreted as a task candidate.

### Happy Path

1. User marks a block as `task_candidate`.
2. User adds intent, constraints, expected output, and optional due/priority metadata.
3. User links supporting context blocks.
4. User prepares a task handoff package.
5. Package is exported or submitted to a Bolt-facing planning flow.

### Alternate Paths

- User keeps the task candidate local without handoff.
- User links task candidate to a spec candidate.
- Downstream system returns a plan or refusal.

### Failure Paths

- Candidate lacks enough context.
- User attempts to execute directly from notes.
- Target task system unavailable.

### Recovery Path

- Request more context from the user.
- Save as draft handoff.
- Export local package for later submission.

### Data Created or Updated

- Block type/status update.
- Supporting `Reference` links.
- Optional `HandoffPackage`.

### Events Emitted

- `note.block.qualified`
- `note.handoff.created`
- `note.handoff.submitted`

### Audit Requirements

- Task handoff records source blocks and user confirmation.

### Acceptance Criteria

- Task candidate remains a note until explicitly handed off.
- Handoff target owns planning/execution lifecycle.

## Journey: Note to Learning Session

### Trigger

The user wants notes and sources to become a learning-session context.

### Actor

Learning Session Preparer.

### Preconditions

- Selected blocks exist.
- Source references exist for source-grounded claims or are explicitly marked missing.

### Happy Path

1. User selects relevant blocks.
2. User chooses `Prepare learning session`.
3. User classifies blocks as objective, source claim, question, example, activity idea, facilitator note, or participant-safe content.
4. System validates source references for source-grounded claims.
5. User exports or submits the package to the learning product/harness.

### Alternate Paths

- User creates a private facilitator-only package.
- User exports a participant-safe subset.
- User keeps missing-source blocks as ungrounded prompts.

### Failure Paths

- Source references missing for required grounded content.
- Package includes private notes in participant-safe section.
- Downstream session system rejects format.

### Recovery Path

- Move sensitive blocks to facilitator-only context.
- Add or repair source references.
- Export local package for manual review.

### Data Created or Updated

- Learning labels on blocks.
- `HandoffPackage` with audience flags.

### Events Emitted

- `note.learning_context.prepared`
- `note.handoff.validated`
- `note.handoff.submitted`

### Audit Requirements

- Record which blocks were marked participant-safe and by whom.

### Acceptance Criteria

- Package separates facilitator-only and participant-safe material.
- Source references survive export.

## Journey: Privacy Review and Export

### Trigger

The user wants to export notes, migrate workspace data, or send a handoff package.

### Actor

Local Knowledge Owner.

### Preconditions

- Workspace or package contains exportable data.

### Happy Path

1. User selects export scope: workspace, notebook, document, selected blocks, or handoff package.
2. System shows privacy review: private labels, source metadata, PII markers, hidden blocks, linked assets.
3. User excludes or redacts content.
4. System produces deterministic Markdown/JSON export.
5. Export is saved locally.

### Alternate Paths

- User exports only metadata/provenance.
- User exports a redacted handoff package.
- User exports for backup/restore.

### Failure Paths

- Linked asset missing.
- Export target path unavailable.
- Redaction would break required package references.

### Recovery Path

- Warn and continue with manifest of missing assets.
- Let user choose another target path.
- Require explicit confirmation for broken references.

### Data Created or Updated

- Export artifact.
- Optional local audit event.
- Handoff/export manifest.

### Events Emitted

- `note.export.previewed`
- `note.export.created`
- `note.export.failed`

### Audit Requirements

- Handoff exports record included block IDs and redactions.
- Full private backup export may remain unaudited if user disables local audit, but default should log it.

### Acceptance Criteria

- Export is readable without the app.
- User sees what private/sensitive data is included before export.
- Redactions are represented explicitly in the manifest.
