# Non-Functional Requirements — rumble-note

Status: Drafting.

## Offline Behavior

- Core capture, edit, search over local index, references, handoff draft, validation, and local export must work offline.
- Network absence must be shown as normal, not error, unless user attempts remote submission/verification.
- Remote targets are optional.

## Sync / Conflict Handling

MVP:

- no mandatory sync;
- local store is source of truth;
- schema reserves sync metadata only if low-cost.

Post-MVP sync requirements:

- opt-in;
- self-hostable;
- preserve block IDs;
- never silently merge conflicting block content;
- conflict UI shows both revisions;
- sensitive/no-handoff metadata must sync with content if sync is enabled;
- remote data residency must be explicit.

## Performance

MVP targets on a typical local machine:

- open existing workspace summary under 1 second for small workspaces;
- create block under 100 ms excluding disk stalls;
- search first results under 300 ms for small/medium workspace;
- rebuild index for 10k blocks under acceptable interactive delay with progress indicator;
- handoff validation for 100 blocks under 1 second where possible;
- export progress for large packages.

Performance rules:

- paginate search results;
- avoid loading full workspace content for home screen;
- avoid unbounded event log rendering;
- index is rebuildable and can be stale without blocking editing.

## Accessibility

- Keyboard navigation for capture, editor, search, and handoff builder.
- Screen-reader labels for block types, privacy state, validation errors, and source verification state.
- Do not rely on color only for privacy/source/error states.
- Focus management in side panels and modals.
- Export and validation errors must be textual and actionable.

## Observability

- Local event log for key lifecycle events.
- Metadata-only by default.
- Debug logs must redact content and credentials.
- Handoff/export operations produce manifest hashes.
- Index status visible to user.

## Portability / Self-Hosting

- Core truth stored locally.
- Export to Markdown/JSON or bundle format.
- No mandatory proprietary service.
- Downstream integrations must be optional and configurable.
- Prefer open-source local storage/index components.

## Backup / Restore

Backup must include:

- structured local store;
- assets;
- settings schema;
- handoff manifests;
- source references;
- tombstones required for audit.

Restore must:

- validate schema version;
- preserve IDs;
- rebuild indexes;
- warn about missing assets or broken external locators.

## Disaster Recovery

- Local store corruption should trigger repair mode.
- Index corruption should trigger rebuild, not data loss.
- Before schema migrations, create backup or rollback point.
- Partial exports/submissions must be marked incomplete or retried explicitly.

## Cost Constraints

- MVP should not require paid external services.
- Search/index should run locally.
- Optional remote targets may have costs, but core use remains free/self-hostable.

## Security

- Local-only by default.
- No hidden network calls for core operations.
- Handoff requires explicit confirmation.
- No direct execution policy.
- Credentials are not stored in notes/logs/exports.

## Privacy / RGPD

- Data minimization: no mandatory telemetry.
- Portability: readable export.
- Erasure: local delete/purge.
- Consent: explicit for handoff/import/future sync.
- Audit: metadata without content by default.

## Data Residency

MVP data residency is the local device. Any future sync/submission target must disclose where data goes and remain self-hostable where possible.

## Internationalization

MVP specs may be English; UI should avoid hard-coded text where possible. French/English product operation should be feasible later.

## Reliability

- Saving a block must not depend on index update.
- Export writes should be atomic where possible.
- Submission retries must be idempotent.
- App should recover from stale references and missing sources gracefully.

## Compatibility

- Exports should remain readable across versions.
- Package schema version required.
- Unknown block types should render as generic blocks with metadata preserved.

## Non-Goals for NFR MVP

- Real-time collaboration.
- Mobile offline sync.
- End-to-end encrypted multi-device sync.
- Semantic/embedding search.
- High-volume document ingestion.
