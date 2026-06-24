# Services and APIs — rumble-note

Status: Drafting.

## Service Boundary Doctrine

`rumble-note` owns local note UX, block operations, references, search, export, and handoff package creation. It may call other ecosystem services but must not absorb their responsibility.

## Rumble App Services

## Service: WorkspaceService

### Owner Layer

Rumble / `rumble-note`.

### Input

Workspace path, workspace ID, settings updates.

### Output

Workspace summary, settings, health status.

### Auth

Local owner in MVP.

### Idempotency

Opening workspace is idempotent. Creating workspace with same path should return existing or ask user to import/repair.

### Failure Modes

- path unavailable;
- schema migration required;
- corrupted local store;
- insufficient file permissions.

### Observability

Local event: `note.workspace.opened`, repair events, migration events.

### Tests

- creates workspace;
- opens existing workspace offline;
- refuses invalid root path;
- repair path preserves data.

## Service: DocumentService

### Owner Layer

Rumble / `rumble-note`.

### Input

Notebook ID, document ID, title, document type.

### Output

Document metadata and block tree references.

### Auth

User must have workspace write access for mutations.

### Idempotency

Document creation uses client idempotency key.

### Failure Modes

- notebook missing;
- duplicate transient create;
- invalid document type;
- storage failure.

### Observability

Document create/update/archive/delete events.

### Tests

- document creation;
- archive preserves blocks;
- move between notebooks;
- cannot silently delete handoff references.

## Service: BlockService

### Owner Layer

Rumble / `rumble-note`.

### Input

Block content, type, parent, sort key, labels, privacy, qualification.

### Output

Block record, revision, content hash.

### Auth

Write access to document/workspace.

### Idempotency

Create/update operations use revision and optional idempotency key.

### Failure Modes

- invalid parent;
- stale revision;
- content too large;
- invalid block type;
- storage failure.

### Observability

Block events with metadata-only payload by default.

### Tests

- stable ID across edits/moves;
- revision increments;
- parent same-document invariant;
- no-handoff privacy rules.

## Service: ReferenceService

### Owner Layer

Rumble / `rumble-note`.

### Input

Typed source pointer, typed target pointer, relationship type, description.

### Output

Reference record and backlink projection status.

### Auth

Write access to source object; future visibility check on target.

### Idempotency

Duplicate source-target-type collapses unless annotated duplicate explicitly allowed.

### Failure Modes

- target unresolved;
- invalid relationship type;
- self-reference not allowed;
- index update failure.

### Observability

Reference and backlink events.

### Tests

- creates backlink;
- unresolved links are visible;
- deleting source does not erase historical handoff manifest.

## Service: SearchService

### Owner Layer

Rumble / `rumble-note`; underlying index may later become Gear substrate.

### Input

Query text, filters, pagination cursor.

### Output

Block search results with snippets, document context, source/reference indicators.

### Auth

Only local readable content. Future collaborative mode filters by visibility.

### Idempotency

Search is read-only.

### Failure Modes

- invalid query;
- stale/corrupt index;
- too many results;
- fallback local scan timeout.

### Observability

Search event may be metadata-only and locally configurable.

### Tests

- offline search;
- filter by type/label/source/privacy;
- stale index fallback;
- pagination.

## Service: SourceReferenceService

### Owner Layer

Rumble wrapper; canonical extraction/provenance may come from Wrench/Gear.

### Input

Source metadata, provenance, canonical source ID optional.

### Output

SourceReference record and verification state.

### Auth

User confirmation required for import or mutation.

### Idempotency

Duplicate canonical source ID or locator detection should return existing candidate.

### Failure Modes

- incomplete provenance;
- checksum mismatch;
- duplicate source conflict;
- import target unavailable.

### Observability

Source reference create/update/verify/stale events.

### Tests

- create unverified source;
- imported source preserves provenance;
- stale state visible in handoff.

## Service: HandoffService

### Owner Layer

Rumble / `rumble-note` creates packages. Downstream target owns consumption.

### Input

Selected block IDs, package purpose, target, constraints, redaction rules.

### Output

HandoffPackage, validation report, export bundle, submission status.

### Auth

User must read included blocks and confirm sensitive/private inclusion.

### Idempotency

Package creation/submission use package revision IDs and idempotency keys.

### Failure Modes

- missing target;
- private/no-handoff conflict;
- stale block revision;
- deleted block;
- missing provenance;
- target unavailable;
- downstream refusal.

### Observability

Handoff lifecycle events with package IDs and validation results.

### Tests

- deterministic manifest;
- privacy review blocks submission;
- no direct execution;
- exported package readable without app.

## Service: ExportService

### Owner Layer

Rumble / `rumble-note`.

### Input

Export scope, format, destination, redaction choices.

### Output

Export artifact, manifest hash.

### Auth

Export permission for scope.

### Idempotency

Same manifest hash can be re-exported; overwrites require explicit confirmation.

### Failure Modes

- invalid path;
- partial write;
- missing asset;
- redaction breaks required manifest.

### Observability

Export preview/create/fail events.

### Tests

- workspace export;
- handoff export;
- redaction manifest;
- no hidden remote dependency.

## Domain Services

## Service: PrivacyReviewService

### Owner Layer

Rumble / `rumble-note`.

### Input

Blocks, sources, package/export scope.

### Output

Warnings, blocking errors, suggested redactions.

### Auth

Local only.

### Idempotency

Pure validation for same inputs.

### Failure Modes

- unknown privacy marker;
- missing source state;
- stale package item.

### Observability

Validation result in package/export manifest.

### Tests

- private block warning;
- no-handoff block blocking by default;
- redaction marker required.

## Service: IndexService

### Owner Layer

Rumble MVP; Gear candidate if reused.

### Input

Workspace content events or rebuild request.

### Output

Index status and queryable projections.

### Auth

Local owner.

### Idempotency

Rebuild from source truth is repeatable.

### Failure Modes

- index corruption;
- disk full;
- unsupported query/index migration.

### Observability

Index stale/rebuild/fail events.

### Tests

- rebuild from blocks/references;
- failure does not corrupt source data.

## Bolt Calls

## API: SubmitPlanningContext

### Owner Layer

`rumble-note` caller, Bolt/`cos-matic` callee.

### Input

Validated `HandoffPackage` with target `bolt_cos_matic`, purpose `task_context` or `harness_context`, execution policy `planning_only`.

### Output

Accepted/queued/rejected status, plan reference, gate/refusal details.

### Auth

Configured local credential or local harness trust boundary. Never include secrets in logs.

### Idempotency

Package revision ID is idempotency key.

### Failure Modes

- target unavailable;
- package rejected;
- policy violation;
- auth failure.

### Observability

Record submission status and downstream response reference.

### Tests

- direct execution not allowed;
- rejection captured;
- retry does not duplicate request.

## Wrench Calls

## API: ImportCanonicalSource

### Owner Layer

Wrench Loader owns extraction. `rumble-note` consumes selected output.

### Input

User-approved Wrench output reference or canonical source bundle.

### Output

`SourceReference` plus optional imported source blocks.

### Auth

User approval required. Import scope explicit.

### Idempotency

Canonical source ID/checksum prevents duplicate imports.

### Failure Modes

- partial extraction;
- checksum mismatch;
- unsupported source kind;
- missing provenance.

### Observability

Import events and source verification state.

### Tests

- partial import marked unverified/stale;
- imported content distinguishable from user notes.

## Gear Calls

## API: ResolveSourceProvenance

### Owner Layer

Gear Memory/Gear provenance substrate candidate.

### Input

Canonical source ID or provenance locator.

### Output

Verified provenance metadata or failure/stale status.

### Auth

Local/self-hosted trust boundary. No remote dependency required for existing local notes.

### Idempotency

Read-only.

### Failure Modes

- source not found;
- stale checksum;
- unavailable substrate.

### Observability

Verification result recorded on SourceReference.

### Tests

- source remains usable if Gear unavailable;
- verification state visible in handoff.

## API: SubmitMemoryCandidate

### Owner Layer

Post-MVP only. Gear Memory owns durable memory lifecycle.

### Input

Explicitly promoted package or block set.

### Output

Accepted/rejected memory entry reference.

### Auth

Explicit user confirmation.

### Idempotency

Content hash + package ID.

### Failure Modes

- user has not confirmed;
- missing provenance;
- Gear unavailable;
- candidate rejected.

### Observability

Promotion events and downstream response.

### Tests

Deferred until post-MVP.

## External Integrations

None required for MVP. Optional downstream targets must be disabled by default and self-hostable.

## API Contract Candidates

### Handoff Package JSON

Minimum fields:

- `schema_version`
- `package_id`
- `workspace_id`
- `purpose`
- `target`
- `execution_policy`
- `created_at`
- `items[]`
- `sources[]`
- `references[]`
- `redactions[]`
- `validation_report`
- `manifest_hash`

### Execution Policy

MVP allowed value:

- `context_only`
- `planning_only`

Forbidden in `rumble-note` MVP:

- `execute`
- `auto_run`
