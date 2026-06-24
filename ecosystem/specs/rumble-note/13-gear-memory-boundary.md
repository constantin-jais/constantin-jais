# Boundary — rumble-note and gear-memory

Status: Draft / architecture guardrail.

## Rule

`rumble-note` owns the personal thinking UX and block graph. `gear-memory` owns indexing, retrieval, context substrate, and reusable memory/search primitives.

## Ownership Split

| Concern | rumble-note | gear-memory | Wrench |
| --- | --- | --- | --- |
| Block editor UX | Owns | No | No |
| Document/notebook navigation | Owns | No | No |
| Block IDs and local graph | Owns product semantics | May index | No |
| Full-text/semantic index | Uses | Owns | No |
| Retrieval API for agents | Uses | Owns | No |
| Import/OCR/extraction | Calls | Stores/indexes output | Owns |
| Note → spec/session/task handoff | Owns UX/export | Stores context refs | May transform inputs |

## NoteContextExport v0.1

Purpose: deterministic export from personal notes to Canvas/LM/Crew/Gear without giving those products unrestricted note access.

```json
{
  "format": "note.context_export.v0.1",
  "source": {
    "product": "rumble-note",
    "workspace_id": "id",
    "export_id": "id",
    "created_by": "actor-id",
    "created_at": "timestamp"
  },
  "scope": {
    "document_ids": [],
    "block_ids": [],
    "target": "rumble-canvas | rumble-lm | rumble-crew | gear-memory"
  },
  "blocks": [
    {
      "block_id": "id",
      "type": "paragraph",
      "content": "text or markdown projection",
      "content_hash": "sha256:...",
      "privacy": "normal | private | no_handoff | sensitive"
    }
  ],
  "links": [],
  "source_refs": [],
  "privacy_policy": {
    "excluded_private_blocks": true,
    "requires_user_confirmation": true
  },
  "target_hints": {
    "canvas": { "as": "spec_context" },
    "lm": { "as": "source_set" },
    "crew": { "as": "task_context" }
  }
}
```

## Events

| Event | Producer | Consumer |
| --- | --- | --- |
| `note_context_export_created` | rumble-note | Gear / target Rumble |
| `note_context_export_submitted` | rumble-note | target Rumble |
| `note_context_index_requested` | rumble-note | gear-memory |
| `note_context_rejected_by_privacy` | rumble-note | UI/audit |

## Acceptance Rules

- Blocks marked `private`, `no_handoff`, or `sensitive` require explicit inclusion or are excluded by default.
- Export contains hashes/provenance, not implicit live access.
- Gear Memory may index exported context but does not own note UX or source document editing.
- Wrench handles import/extraction before content becomes notes/context.

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should NoteContextExport use the same artifact envelope as SpecPackage? | High | Open |
| Should Gear Memory index all local notes or only explicit exports? | High | Open |
| How are deleted/anonymized blocks propagated to indexes/exports? | High | Open |
