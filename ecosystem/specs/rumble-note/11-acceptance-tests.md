# Acceptance Tests — rumble-note

Status: Drafting.

## Capture and Blocks

### Scenario: Create a block offline

Given a local workspace is open offline
When the user creates a block in the inbox
Then the block is saved locally
And the block has a stable ID
And the absence of network is not an error.

### Scenario: Move block preserves ID

Given a block exists in the inbox
When the user moves it to a document
Then the block ID remains unchanged
And references to the block remain valid.

### Scenario: Block revision increments

Given a block exists with revision 1
When the user changes its content
Then the block revision becomes 2
And the content hash changes.

### Scenario: Invalid parent is rejected

Given two documents exist
When the user tries to set a block parent from another document
Then the operation is rejected
And no partial move is saved.

## References and Backlinks

### Scenario: Create typed backlink

Given two blocks exist
When the user creates a `supports` reference from block A to block B
Then block A shows the forward reference
And block B shows a backlink from block A
And the relationship type is exportable.

### Scenario: Broken target remains visible

Given a reference targets a block
When the target block is deleted or unavailable
Then the reference becomes `unresolved`
And the user can repair or remove it.

## Search

### Scenario: Search by text offline

Given blocks are indexed locally
And the workspace is offline
When the user searches text
Then matching blocks are displayed
And each result includes block ID, type, document, and snippet.

### Scenario: Search filters by type and privacy

Given blocks with different types and privacy states exist
When the user filters by `decision` and `sensitive`
Then only matching blocks are shown.

### Scenario: Corrupt index can rebuild

Given the local index is corrupt
When the user requests index rebuild
Then the index is rebuilt from local source data
And note content is not lost.

## Source References

### Scenario: Create unverified source reference

Given the user has a source URL or file path
When the user creates a source reference without full provenance
Then the source is saved as `unverified`
And handoff previews show the unverified state.

### Scenario: Import Wrench source with provenance

Given a user-approved Wrench output bundle
When the user imports the source reference
Then provenance metadata is preserved
And imported content is distinguishable from user-authored notes.

## Handoff

### Scenario: Create handoff draft from selected blocks

Given the user selected blocks in search
When the user creates a handoff package with purpose `spec_context`
Then a draft package is created
And package items reference selected block IDs and revisions.

### Scenario: no_handoff block excluded by default

Given one selected block is marked `no_handoff`
When the user creates a handoff package
Then the block is excluded or blocking warning is shown
And inclusion requires explicit override reason.

### Scenario: Sensitive block requires confirmation

Given a package includes a `sensitive` block
When the user validates the package
Then validation shows a privacy warning
And submission/export is blocked until the user confirms or redacts.

### Scenario: Handoff validation detects stale revision

Given a handoff package includes block revision 1
And the block is edited to revision 2
When the user validates the package
Then validation reports stale package item
And the user must update, pin, or omit the item.

### Scenario: Export deterministic package

Given a validated handoff package
When the user exports it locally
Then the export contains a manifest
And included items, sources, references, redactions, schema version, and manifest hash are present.

### Scenario: Handoff cannot execute directly

Given a validated handoff package targets Bolt or the harness
When the user submits it
Then the execution policy is `context_only` or `planning_only`
And no direct execution authorization is included.

### Scenario: Downstream rejection is recorded

Given a submitted handoff package
When the downstream target rejects it
Then package status becomes `rejected`
And refusal reason is visible to the user.

## Export and Privacy

### Scenario: Workspace export is readable without app

Given a workspace with documents and blocks
When the Local Knowledge Owner exports the workspace
Then the export includes readable Markdown/JSON
And block IDs and references are preserved.

### Scenario: Redaction manifest is explicit

Given the user redacts a block during export
When the export is created
Then the manifest records the redaction
And omitted content is not silently removed.

### Scenario: Export path failure is recoverable

Given an invalid destination path
When the user exports
Then the export fails safely
And no partial artifact is presented as complete.

## Permissions

### Scenario: Harness consumer reads package only

Given a handoff package was submitted
When the Harness Consumer receives it
Then it can read only included package content
And cannot access the full workspace.

### Scenario: Imported source provider cannot rewrite notes

Given an import flow is active
When the source provider returns metadata
Then it may create/update source references only through the approved import scope
And cannot mutate user-authored notes.

## Audit

### Scenario: Handoff audit event includes manifest hash

Given a package is exported or submitted
When the audit event is recorded
Then it includes package ID, purpose, target, actor, timestamp, and manifest hash
And does not include full note content by default.

### Scenario: Delete block referenced by handoff creates tombstone

Given a block was included in a prior handoff
When the user hard-deletes the block
Then content is removed
And a tombstone preserves the block ID and handoff reference.

## Migration / Backup

### Scenario: Backup preserves IDs

Given a workspace backup exists
When the user restores it
Then workspace data is available
And block IDs, references, and handoff manifests are preserved.

### Scenario: Schema migration backs up first

Given a local schema migration is required
When the app runs the migration
Then backup or rollback point is created first
And migration failure leaves the prior data recoverable.

## Security / RGPD

### Scenario: No hidden network calls for core capture

Given network monitoring is enabled
When the user captures, edits, searches, and exports locally
Then no network call is required for core operations.

### Scenario: Credentials are not logged

Given a downstream target is configured
When a submission fails
Then logs/events do not contain credentials or tokens.

### Scenario: User can purge local content

Given the user chooses to purge a document
When confirmation is complete
Then content is removed according to retention rules
And any required tombstones contain no deleted content.
