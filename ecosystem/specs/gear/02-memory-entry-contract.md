# Memory Entry and Event Log Contracts

Status: Draft / P0 substrate contract.

## MemoryEntry

Owner: `gear-memory`.

Purpose: represent content that can be indexed and retrieved without absorbing
Rumble product semantics.

```json
{
  "memory_entry_id": "mem_01",
  "source_ref": "src_01",
  "content_hash": "sha256:...",
  "index_state": "pending | indexed | stale | deleted | anonymized",
  "index_metadata": {
    "schema_version": "memory-entry.v0.1",
    "chunk_count": 0,
    "embedding_model_ref": "optional",
    "indexed_at": "optional"
  },
  "created_at": "2026-06-30T00:00:00Z"
}
```

Rules:

- `memory_entry_id` and `source_ref` must be non-empty.
- `source_ref` is required. Memory entries do not own source identity.
- `content_hash` is required, must use canonical bytes for the indexed content
  snapshot, and must be formatted as `sha256:<64 hex chars>`.
- `created_at` must be RFC3339 / ISO 8601 with an explicit offset.
- `index_state=stale` means source content or deletion/anonymization state has
  changed and retrieval must avoid treating the entry as current truth.
- `index_state=deleted` or `anonymized` must remove searchable content from
  retrieval indexes while preserving minimal audit references when policy allows.
- `index_metadata` may describe index mechanics, not product meaning.

## EventLogEntry

Owner: Gear shared shape; first modeled alongside `gear-memory` because memory
index state transitions need auditability.

```json
{
  "event_id": "evt_01",
  "event_type": "source.created | memory.indexed | artifact.revoked",
  "actor_ref": "actor_01",
  "target_ref": "src_01",
  "provenance_id": "prov_01",
  "metadata": {},
  "created_at": "2026-06-30T00:00:00Z"
}
```

Rules:

- `event_id`, `event_type`, `actor_ref`, `target_ref`, and `provenance_id` must
  be non-empty.
- `created_at` must be RFC3339 / ISO 8601 with an explicit offset.
- Event payloads contain references and small metadata only.
- No raw note content, response content, source excerpts, access tokens, API
  keys, or credentials are allowed in `metadata`.
- Metadata validation must reject secret-like keys before indexing or event
  persistence.
- Product event names may be projected into this shape, but product workflows
  remain product-owned.

## Local-First and Deletion Propagation

Gear Memory must support local-first operation: indexing and retrieval can work
against local stores without requiring a network service. Sync may replicate
references and index state, but it must preserve deletion/anonymization order.

Propagation rule:

```text
SourceRef state changed to deleted/anonymized
-> related MemoryEntry state becomes deleted/anonymized
-> retrieval indexes drop searchable content
-> EventLogEntry records the transition without raw content
```

This is infrastructure behavior, not product retention policy. Rumble products
choose the retention policy; Gear enforces the substrate transition.
