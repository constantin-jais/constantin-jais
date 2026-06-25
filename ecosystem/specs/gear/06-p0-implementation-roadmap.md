# Gear P0 Implementation Roadmap

Status: Draft / implementation guidance, not runtime code.

Purpose: define the first Rust-first implementation path for Gear without overbuilding a platform.

## 1. Implementation Goal

Build a local-first Gear Memory P0 that can:

- persist `SourceRef`, `MemoryEntry`, `EventLogEntry`, `CodeMap`, and `ProvenanceRecord`;
- validate JSON contracts and fixture compatibility;
- index active memory entries with deterministic full-text search;
- store explicit graph/code edges;
- propagate stale/deleted/anonymized/revoked lifecycle states;
- export/import canonical JSON/NDJSON for audit and replay;
- expose a small CLI/API consumed by Rumbles, Wrench, and Bolt.

Non-goal: vector search, sync service, cloud storage, workflow engine, product UI, agent brain.

## 2. Recommended Rust Crate Shape

Initial crate layout:

```text
gear-memory/
  Cargo.toml
  crates/
    gear-memory-core/      # domain structs, validation, lifecycle rules
    gear-memory-store/     # SQLite store implementation
    gear-memory-index/     # FTS, graph/code indexes
    gear-memory-cli/       # local CLI
  fixtures/
    memory/                # mirror or import ecosystem fixtures
```

Keep interfaces small and stable before optimizing internals.

## 3. Storage Baseline

Recommended P0 storage: SQLite local file.

Why:

- local-first and offline by default;
- widely inspectable;
- easy backup/export;
- FTS available;
- transaction semantics are enough for P0;
- no server dependency.

Initial tables:

| Table | Purpose |
| --- | --- |
| `source_refs` | source identity, hash, state, origin, URI/opaque locator |
| `memory_entries` | indexed snapshots rooted in sources |
| `provenance_records` | actor/operation/input/output/tool refs |
| `event_log_entries` | safe append-only substrate events |
| `graph_edges` | explicit typed source/memory/artifact/code relationships |
| `code_maps` | code map metadata and state |
| `code_symbols` | symbols from Wrench parser output |
| `code_edges` | symbol relationships |
| `tombstones` | deletion/anonymization/revocation replay state |

SQLite FTS can back full-text indexing. Vector search is deferred.

## 4. P0 API Surface

### Core operations

```text
source put <source-ref.json>
source state <source_id> <active|stale|deleted|anonymized|revoked>
memory put <memory-entry.json>
memory search --text "query" --state active
provenance append <provenance-record.json>
event append <event-log-entry.json>
code-map put <code-map.json>
export ndjson --out gear-memory-export.ndjson
import ndjson gear-memory-export.ndjson
validate <bundle.json>
```

### Library traits

Indicative Rust traits:

```rust
trait SourceStore {
    fn put_source(&self, source: SourceRef) -> Result<()>;
    fn get_source(&self, id: &SourceId) -> Result<Option<SourceRef>>;
    fn set_source_state(&self, id: &SourceId, state: SourceState) -> Result<StateTransition>;
}

trait MemoryIndex {
    fn put_entry(&self, entry: MemoryEntry) -> Result<()>;
    fn search(&self, query: SearchQuery) -> Result<Vec<SearchHit>>;
    fn drop_payload_for_source(&self, source_id: &SourceId) -> Result<()>;
}

trait ProvenanceLog {
    fn append_provenance(&self, record: ProvenanceRecord) -> Result<()>;
    fn append_event(&self, event: EventLogEntry) -> Result<()>;
}
```

Do not expose product-specific methods such as `rank_lesson_source`, `prioritize_task`, or `summarize_note`.

## 5. Lifecycle Propagation Algorithm

P0 rule:

```text
SourceRef state transition
→ write tombstone/state event
→ update linked MemoryEntry states
→ drop or rebuild searchable payloads
→ mark graph/code/vector partitions stale/deleted/anonymized/revoked
→ append ProvenanceRecord + EventLogEntry
```

Priority in conflicts:

```text
deleted/anonymized > revoked > stale > active
```

A stale active replica must never resurrect deleted or anonymized searchable content.

## 6. Index Strategy P0 → P2

### P0

- reference catalog;
- SQLite FTS full-text index;
- explicit graph edges;
- `CodeMap` storage and symbol lookup;
- lifecycle propagation;
- JSON/NDJSON export/import.

### P1

- Wrench parser integration for real `CodeMap` production;
- query filters by workspace/scope/state/origin;
- richer citation/source-span retrieval;
- sync replay tests;
- artifact-as-source integration with Gear Depot.

### P2

- vector index backend benchmark;
- compact prompt projection generator;
- remote sync transport;
- encrypted local store options;
- UI/debug viewer.

## 7. Dependency and Sovereignty Policy

Default dependencies should be permissive and self-hostable:

- Rust crates under MIT/Apache/BSD/ISC/MPL compatible licenses;
- SQLite via Rust bindings after license/security review;
- no mandatory hosted DB, US SaaS, or opaque vector store;
- no AGPL/GPL/SSPL direct dependency unless isolated by explicit ADR/waiver;
- no telemetry by default.

Before adopting vector/object search, benchmark local options against:

- determinism;
- deletion/anonymization behavior;
- offline operation;
- binary size/build complexity;
- license;
- Rust integration quality.

## 8. Acceptance Tests for First Implementation

### Contract compatibility

- Existing `gear-memory-minimal.valid.json` imports successfully.
- Existing invalid fixtures are refused with structured validation errors.
- Exported JSON validates against `gear-memory.v0.1.schema.json`.

### Search/index

- Active memory entry is searchable by full-text query.
- Deleted/anonymized entry is not searchable.
- Stale entry is returned only when stale results are explicitly allowed and marked stale.

### Provenance/audit

- Every source insert creates or links a provenance record.
- Every state transition emits an event log entry.
- Metadata with unsafe keys is rejected before persistence.

### Lifecycle

- `SourceRef deleted` drops linked FTS payloads.
- `SourceRef anonymized` drops original payloads and allows reindexing only anonymized projection.
- `SourceRef stale` marks memory/code graph refs stale.
- Tombstones win after replaying out-of-order events.

### CodeMap

- CodeMap symbols resolve to source refs and hashes.
- Source hash change marks dependent symbols/edges stale.
- Unsupported language fallback to file-level node is accepted.

## 9. First Vertical Slice

Recommended first slice:

```text
1. Parse and validate gear-memory-minimal.valid.json.
2. Insert SourceRef + MemoryEntry + ProvenanceRecord + EventLogEntry into SQLite.
3. Build FTS index for active MemoryEntry text projection.
4. Run a search returning source_id, memory_entry_id, state, hash, provenance_id.
5. Mark source deleted.
6. Verify search no longer returns payload.
7. Export NDJSON and replay into a fresh DB.
```

This proves the core promise without vector search, sync service, or UI.

## 10. What Not To Build First

Do not start with:

- vector search;
- agent memory policies;
- multi-user sync;
- UI explorer;
- remote service API;
- code parser implementation inside Gear;
- automatic note indexing;
- product-specific ranking.

Those can come later only after the reference/provenance/lifecycle substrate is boring and correct.

## 11. Open Implementation Questions

| Question | Default for P0 |
| --- | --- |
| SQLite vs embedded Rust KV store? | SQLite first for inspectability and FTS. |
| FTS vs Tantivy? | SQLite FTS first; benchmark Tantivy if quality/perf insufficient. |
| Graph engine? | SQL edge tables first. |
| Vector backend? | Defer; optional P2 benchmark. |
| Sync? | Export/import NDJSON first; no network sync P0. |
| Encryption at rest? | Defer to deployment/OS in P0; design hooks for future encrypted store. |
| Workspace/tenant model? | Store opaque scope refs only; shared identity/workspace decision remains open. |
