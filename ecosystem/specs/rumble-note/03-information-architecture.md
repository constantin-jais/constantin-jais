# Information Architecture — rumble-note

Status: Drafting.

## Navigation Model

MVP navigation is intentionally small and local-first:

```text
Workspace
├─ Inbox
├─ Notebooks
│  └─ Documents
├─ Search
├─ Handoffs
├─ Sources
└─ Settings / Export
```

Primary navigation should optimize for capture, retrieval, and handoff rather than visual graph exploration.

## Primary Spaces

### Inbox

Fast capture area for unclassified blocks.

Purpose:

- capture thoughts without choosing final structure;
- later triage into notebook/document/block qualification;
- preserve offline-first speed.

Contains:

- recent captured blocks;
- incomplete source references;
- unqualified task/spec/session candidates.

### Notebooks

User-facing grouping of documents.

Purpose:

- organize work by project, theme, journal, learning topic, or source collection;
- avoid making workspace hierarchy too deep.

MVP rule:

- one level of notebooks;
- documents can contain nested blocks, not nested documents.

### Documents

Main writing surface composed of ordered blocks.

Purpose:

- write structured notes;
- preserve stable block IDs;
- expose local document context for search and handoff.

Document types:

- `note`
- `journal`
- `source_notes`
- `spec_draft`
- `learning_notes`
- `task_notes`

Document type is a retrieval and template hint, not a hard workflow boundary.

### Search

Local retrieval surface over blocks, documents, labels, source references, relationship types, and handoff state.

Purpose:

- find reusable context;
- build handoff selections;
- expose broken links, stale source references, and candidate blocks.

MVP search modes:

- text search;
- filter by block type;
- filter by label;
- filter by source/reference;
- filter by handoff state;
- filter by privacy state.

### Handoffs

Review and export surface for selected blocks.

Purpose:

- prepare deterministic packages;
- preview included content and metadata;
- enforce privacy review before export/submission;
- record package status and downstream response.

Package purposes in MVP:

- source context;
- spec context;
- task context;
- learning-session context;
- harness context;
- local export.

Durable memory promotion to `gear-memory` is post-MVP and must use a dedicated explicit workflow.

### Sources

Reference surface for provenance-bearing sources.

Purpose:

- list source references used by notes;
- show verification state;
- distinguish user-authored notes from imported or external content;
- avoid turning `rumble-note` into an ingestion engine.

MVP source states:

- unverified;
- verified;
- stale;
- failed;
- archived.

### Settings / Export

Workspace-level controls.

Purpose:

- configure local paths, privacy defaults, export formats, and indexing behavior;
- trigger backup/export;
- rebuild local index;
- inspect local audit/handoff history.

## Object Hierarchy

Canonical hierarchy:

```text
Workspace
└─ Notebook
   └─ Document
      └─ Block
         └─ Child Block
```

Cross-cutting objects:

```text
Reference        links blocks/documents/sources/handoffs
SourceReference  points to provenance-bearing source data
HandoffPackage   snapshots selected blocks for a purpose/target
LocalIndex       rebuildable projection over local truth
```

Rules:

- `Block` is the smallest addressable unit.
- `Document` owns block order.
- `Notebook` groups documents, but does not own source truth.
- `Reference` creates graph relationships without changing ownership.
- `HandoffPackage` snapshots selected content; it is not a live view.

## Search / Browse Model

### Browse

Browse starts from human structure:

1. workspace;
2. notebook;
3. document;
4. block outline.

### Search

Search starts from reusable context:

1. query text;
2. filters;
3. block result list;
4. document context preview;
5. selection into handoff package.

### Backlinks

Backlinks are shown as contextual lists, not as the primary navigation model.

Backlink entry should show:

- source block title or excerpt;
- relationship type;
- document/notebook context;
- source verification state if relevant;
- whether the link was included in any handoff package.

### Saved Views

Deferred from MVP unless needed for handoff package drafts.

## Settings Model

Workspace settings:

- local root path;
- default notebook/inbox;
- privacy defaults;
- export format defaults;
- index status and rebuild controls;
- optional telemetry/audit logging controls;
- future sync adapter settings.

Document settings:

- title;
- notebook;
- document type;
- archive state;
- default block privacy.

Block settings:

- type;
- labels;
- qualification;
- privacy;
- source references;
- relationship links.

Handoff settings:

- purpose;
- target;
- audience;
- privacy constraints;
- included metadata;
- redaction rules;
- execution policy note: planning/context only, no direct execution.

## Empty State Strategy

### Empty Workspace

Show:

- create first notebook;
- capture into inbox;
- import source reference from existing extracted content;
- open privacy/export settings.

### Empty Inbox

Show:

- quick capture prompt;
- recent documents;
- keyboard shortcut/help.

### Empty Notebook

Show:

- create document;
- move inbox blocks here;
- explain that notebooks are lightweight groupings.

### Empty Document

Show:

- first block placeholder;
- block type shortcuts;
- privacy hint.

### Empty Search

Show:

- suggestions to remove filters;
- option to rebuild index if stale;
- link to browse notebooks.

### Empty Handoffs

Show:

- select blocks from document or search;
- explain handoff purposes;
- privacy reminder.

### Empty Sources

Show:

- create manual source reference;
- connect/import output from `gear-loader` later;
- explain unverified vs verified source state.

## Boundary Notes

- No visual graph editor in MVP; backlinks are lists and filters.
- No broad ingestion UI in MVP; sources are references or imported outputs from Wrench.
- No autonomous memory view in MVP; memory candidates are post-MVP.
- No agent execution view in MVP; downstream systems own planning/execution.
