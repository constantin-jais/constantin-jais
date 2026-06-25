# Permissions, Security, RGPD — rumble-note

Status: Drafting.

## Security Posture

`rumble-note` handles private local notes. The main risk is accidental or silent disclosure through export, handoff, logs, source imports, or future sync. MVP must prefer explicit user confirmation, local-only defaults, minimal logging, and deterministic manifests.

## Roles

- Local Knowledge Owner
- Spec / Product Author
- Learning Session Preparer
- Harness Consumer
- Imported Source Provider

MVP is single-owner local. System-facing roles only access explicit package/import boundaries.

## Permission Matrix

| Action | Local Owner | Spec Author | Learning Preparer | Harness Consumer | Imported Source Provider |
| --- | --- | --- | --- | --- | --- |
| Create/edit blocks | Yes | Yes | Yes | No | No |
| Read full workspace | Yes | Yes if same local owner | Yes if same local owner | No | No |
| Create references | Yes | Yes | Yes | No | Import flow only |
| Create source references | Yes | Yes | Yes | No | With user approval |
| Create handoff draft | Yes | Yes | Yes | No | No |
| Validate handoff | Yes | Yes | Yes | No | No |
| Submit handoff | Yes | Yes if permitted | Yes if permitted | No | No |
| Consume submitted package | No | No | No | Explicit package only | No |
| Import canonical source | Yes | Yes | Yes | No | Provides selected source only |
| Export full workspace | Yes | No by default future role | No by default future role | No | No |
| Delete/purge workspace | Yes | No | No | No | No |

## Sensitive Data

Potential sensitive data includes:

- personal notes;
- unpublished product strategy;
- source excerpts;
- local file paths;
- URLs with tokens or private identifiers;
- names/emails in notes or sources;
- secrets accidentally pasted into blocks;
- downstream credentials for harness/Bolt/Wrench/Gear targets.

## Privacy Labels

Block privacy states:

- `normal`: eligible for handoff/export after review.
- `private`: visible locally, warning before handoff/export.
- `sensitive`: blocking warning before handoff/export, requires explicit confirmation.
- `no_handoff`: excluded from handoff by default; override requires reason.

## Handoff Protection Rules

- No handoff without explicit user action.
- Handoff preview must list included blocks, source references, redactions, and privacy warnings.
- `no_handoff` blocks are excluded by default.
- Sensitive/private blocks require confirmation.
- Handoff package must declare `context_only` or `planning_only`; no direct execution policy.
- Downstream consumers receive only included package content, not workspace access.

## Export Rules

- Export preview required for handoff and non-trivial scope.
- Redactions must be explicit in manifest.
- Export is readable without the app.
- Destination paths in audit logs may be redacted.
- Full workspace export requires Local Knowledge Owner.

## Data Retention

Default retention:

- notes retained until user archives/deletes;
- handoff manifests retained for audit unless purged;
- event log metadata retained locally with configurable retention;
- content diffs disabled by default;
- tombstones retained only for referenced deleted blocks.

Deletion:

- archive first;
- soft delete before purge;
- purge removes content but may keep minimal tombstone if needed for handoff audit;
- user must be warned if purge breaks references.

## Consent

Explicit consent required for:

- submitting package to downstream target;
- including private/sensitive/no-handoff blocks;
- importing source output from another tool;
- future sync enablement;
- future memory promotion to Gear Memory.

## Data Residency

MVP data resides on user's local machine. Remote targets are optional and must be self-hostable. No mandatory US hyperscaler dependency.

## Audit

Audit events must capture:

- who/what actor initiated action;
- action name;
- subject IDs;
- timestamp;
- package/export manifest hash for handoffs;
- downstream target/status for submissions.

Avoid storing full note content in audit by default.

## Threat Model Notes

### Threat: Silent Workspace Exfiltration

Risk: downstream consumer or integration reads more than selected blocks.

Controls:

- package-based access only;
- no workspace token in handoff;
- manifest lists exact included IDs/content.

### Threat: Accidental Sensitive Handoff

Risk: user includes private notes in package.

Controls:

- privacy labels;
- review screen;
- explicit override reason;
- redaction manifest.

### Threat: Ingestion Scope Creep

Risk: broad importer pulls private files unexpectedly.

Controls:

- no broad ingestion in core;
- Wrench import requires explicit selected scope;
- imported content marked distinct from authored notes.

### Threat: Log Leakage

Risk: note content or secrets written to logs/events.

Controls:

- metadata-only events by default;
- sensitive event classification;
- destination path redaction option;
- no downstream credentials in logs.

### Threat: Broken Provenance

Risk: source-grounded handoff lacks reliable source metadata.

Controls:

- source verification state;
- unverified sources visibly marked;
- validation warnings/errors by package purpose.

### Threat: Future Sync Conflict or Leakage

Risk: local notes sync to unwanted destination or merge incorrectly.

Controls:

- sync post-MVP;
- opt-in only;
- conflict records not silent merges;
- encryption/auth design required before implementation.

## RGPD Considerations

### Lawful Basis

Local personal tool controlled by user. If collaborative/hosted mode appears later, lawful basis and processor/controller roles must be specified.

### Data Subject Rights

MVP local user can:

- inspect data through app/export;
- export data in readable format;
- delete/purge local data;
- redact package exports.

### Data Minimization

- collect no mandatory telemetry;
- log metadata, not content;
- expose only selected package content to downstream systems.

### Portability

Markdown/JSON export required.

### Right to Erasure

Support local deletion/purge with caveat that tombstones may preserve IDs for audit without content.

### Privacy by Default

- local-only operation;
- no remote sync by default;
- no auto-handoff;
- no auto-memory-promotion;
- no broad ingestion.

## Secrets Handling

- Never store downstream API tokens in note blocks intentionally.
- If credentials are configured, store via OS/local secure storage where available.
- Never include tokens in export/handoff/logs.
- Warn when URL locators appear to contain token-like query parameters.

## Future Biscuit Delegation Mapping

MVP Note is single-owner local, so it does not need broad collaborative delegated authorization yet. Future collaborative modes must use the shared contract `../shared/contracts/delegated-authorization-biscuit.v0.1.md` instead of workspace-local custom tokens.

| Future Note operation | Shared Biscuit action | Required scope facts | Product-local checks |
| --- | --- | --- | --- |
| Read selected note/source package | `source:read` | `organization`, `workspace`, `resource("note_package", package_id)` or `source_ref` | Explicit package manifest; no full workspace access; privacy labels enforced. |
| Attach imported source | `source:attach` | `organization`, `workspace`, optional `source_ref` | User approval; import scope selected; provenance retained. |
| Create handoff/export | `export:create` or `handoff:prepare` | `organization`, `workspace`, `resource("note_package", package_id)` | Preview completed; private/sensitive/no-handoff overrides have reasons. |
| Submit handoff | `handoff:submit` | `organization`, `workspace`, `resource("handoff", handoff_id)`, payload hash attenuation | Planning/context-only policy; downstream target receives package only. |
| Manage collaborators | `member:manage` | `organization`, `workspace`, `actor($id, "human")` | Future owner/collaborator policy; no silent sync expansion. |

Note must never issue a token that grants general workspace read access to downstream harness consumers. Delegation is package/manifest-scoped.

## Open Security Questions

- Exact secure storage mechanism for downstream credentials.
- Whether local database should support encryption at rest in MVP.
- How to detect PII/secrets locally without adding opaque AI processing.
- Future collaborative auth model.
