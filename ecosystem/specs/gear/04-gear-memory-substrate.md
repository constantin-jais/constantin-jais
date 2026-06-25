# Gear Memory Substrate Charter

Status: Draft / P0 scope decision.

Purpose: define what `gear-memory` must own to serve every Rumble product and Bolt without becoming an agent brain, a product UI, or a hidden decision engine.

## 1. Responsibility Charter

`gear-memory` is the local-first substrate for reliable references. It stores, indexes, links, retrieves, and records provenance for source and memory material.

It must provide:

- stable references to source material through `SourceRef`;
- indexable snapshots through `MemoryEntry`;
- append-only safe audit references through `EventLogEntry`;
- source/code/document relationship maps through `CodeMap` and graph edges;
- provenance chains through `ProvenanceRecord`;
- deletion, anonymisation, revocation, and stale-state propagation;
- deterministic export/import of its contracts for offline and self-hosted use.

It must not provide:

- agent goals, planning, scoring, prioritisation, or next-action decisions;
- product semantics such as note meaning, learning state, task workflow, feed ranking, or spec approval;
- ingestion/extraction logic owned by Wrench;
- artifact distribution, registry, or release trust state owned by Gear Depot/Cable;
- identity provider or full authorization system.

Boundary rule:

> Gear Memory can answer “what references exist, how are they linked, are they current, and where did they come from?” It cannot answer “what should we do next?”

## 2. P0 Object Model

### 2.1 SourceRef

Owner: `gear-memory`.

Role: durable reference to input or grounding material: file, URL, feed item, note block export, transcript, document, dataset, or prior artifact reused as source.

Required capabilities:

- stable `source_id` independent from display title;
- source type and origin product/tool;
- optional URI or opaque local locator;
- canonical content hash for materialized content;
- lifecycle state: `active | stale | deleted | anonymized`;
- provenance link;
- policy-safe metadata only.

Non-goal: source parsing, enrichment, ranking, or product-specific meaning.

### 2.2 MemoryEntry

Owner: `gear-memory`.

Role: indexed snapshot of a `SourceRef` for retrieval.

Required capabilities:

- links to exactly one source reference as its root identity;
- canonical indexed-content hash;
- index state: `pending | indexed | stale | deleted | anonymized`;
- chunk/index mechanics in metadata;
- no product semantics in index metadata;
- searchable payload removable independently from retained audit references.

Non-goal: note block model, session knowledge model, or agent memory policy.

### 2.3 EventLogEntry

Owner: Gear shared shape, implemented first with `gear-memory`.

Role: append-only event reference for source and index transitions.

Required capabilities:

- safe reference-only payloads;
- actor attribution snapshot;
- target reference;
- provenance reference;
- metadata key rejection for secret-like fields;
- deterministic event type naming, while product event semantics remain product-owned.

Non-goal: business workflow engine or full audit product.

### 2.4 CodeMap

Owner: `gear-memory` for storage/indexing; Wrench owns parsing and validation.

Role: reproducible map of code artifacts and symbols that can be searched, linked, and cited by Bolt/Rumbles.

P0 shape:

```json
{
  "code_map_id": "cm_01",
  "root_source_ref": "src_repo_01",
  "scope": {
    "repo_ref": "optional",
    "revision": "git:commit-or-tree-hash",
    "paths": ["src/", "crates/"]
  },
  "parser_refs": ["tree-sitter:rust@version"],
  "symbols": [
    {
      "symbol_id": "sym_01",
      "kind": "function | type | module | trait | interface | route | table | test | config",
      "name": "qualified.name",
      "source_ref": "src_file_01",
      "range": { "start_line": 1, "end_line": 10 },
      "content_hash": "sha256:..."
    }
  ],
  "edges": [
    {
      "from": "sym_01",
      "to": "sym_02",
      "kind": "defines | calls | imports | tests | configures | documents | generated_from"
    }
  ],
  "state": "active | stale | deleted",
  "created_at": "2026-06-30T00:00:00Z"
}
```

Rules:

- `CodeMap` is a map/index, not the source of code truth.
- All symbols must point back to `SourceRef` and content hashes.
- Parser output is reproducible from declared parser refs and source revision.
- Ambiguous or unsupported languages may fall back to file-level nodes.
- `CodeMap` must become `stale` when the repository revision, parser version, or source state changes.

### 2.5 ProvenanceRecord

Owner: Gear shared shape, stored by Gear Memory for source/memory/index operations.

Role: reference-only chain of actor, operation, inputs, outputs, tool refs, timestamp, and safe metadata.

Required operations for Gear Memory P0:

- `created`, `imported`, `indexed`, `linked`, `stale_marked`, `deleted`, `anonymized`, `revoked`.

Non-goal: deciding whether an operation is allowed; authorization adapters and product policies decide, Gear records/enforces resulting substrate transitions.

## 3. Minimal Index Strategy

Gear Memory indexes progressively. Each layer must remain useful without the next one.

### Stage 0 — Reference catalog

- Store `SourceRef`, `MemoryEntry`, `ProvenanceRecord`, and `EventLogEntry`.
- Lookup by ID, hash, origin, state, timestamp, and provenance.
- Required before any text/vector/graph index.

### Stage 1 — Full-text index

- Deterministic local full-text search over indexed snapshots.
- Supports exact phrase, term, path/title/metadata filters, state filters.
- Deleted/anonymized entries are physically removed from searchable content.
- Preferred as the P0 retrieval baseline because it is auditable and cheap offline.

### Stage 2 — Graph index

- Stores explicit edges: cites, derived_from, duplicates, supersedes, blocks, tests, documents, generated_from, belongs_to.
- Edges are references only and must carry provenance.
- No inferred product meaning unless a producer records a typed edge.

### Stage 3 — Tree-sitter symbol index / CodeMap

- Wrench produces parser output; Gear Memory stores reproducible `CodeMap` snapshots.
- Uses tree-sitter language coverage when available, file-level fallback otherwise.
- Enables code graph, symbol lookup, test/source links, and stale propagation after code changes.

### Stage 4 — Vector index

- Optional enhancement, never sole source of truth.
- Embedding model reference, dimensions, chunking strategy, and created timestamp are mandatory.
- Vector hits must return source IDs, hashes, and provenance; never opaque answers.
- Local/self-hostable vector backends are preferred; benchmark native options before adoption.

Default retrieval order for agents:

1. filter by workspace/scope/state/rights;
2. search full-text and graph/symbol references;
3. optionally expand with vector similarity;
4. return references, excerpts only when permitted, hashes, and provenance;
5. let Bolt/Rumble decide what to do with the retrieved context.

## 4. Deletion, Anonymisation, Stale Propagation, Revocation

### 4.1 State semantics

| State | Meaning | Required substrate behavior |
| --- | --- | --- |
| `active` | current and retrievable | indexes may return it if access allows |
| `stale` | source/index changed or superseded | retrieval marks it non-current; agents must not treat it as truth without refresh |
| `deleted` | content must no longer be searchable | remove payloads/chunks/embeddings; retain minimal legal/audit refs if policy allows |
| `anonymized` | personal data removed or irreversibly transformed | remove or replace identifying fields and reindex only anonymized projection |
| `revoked` | trust/access withdrawn | stop normal retrieval/export; keep provenance of revocation |

### 4.2 Propagation rules

- `SourceRef deleted/anonymized` → all linked `MemoryEntry` content indexes are dropped or anonymized.
- `SourceRef stale` → linked `MemoryEntry`, `CodeMap`, graph edges, and derived vector chunks become stale unless regenerated from current content.
- `ArtifactRef revoked` when reused as `SourceRef` → corresponding source and memory entries become revoked or stale according to product policy, but the original artifact hash remains immutable in Depot.
- Parser or embedding model version changed → affected `CodeMap` or vector index partitions become stale until rebuilt.
- Propagation emits `EventLogEntry` and `ProvenanceRecord` without raw content.

### 4.3 RGPD deletion/anonymisation guardrails

- Logs/debug metadata must never contain raw PII, source excerpts, secrets, tokens, or credentials.
- Metadata writers reject secret-like keys before persistence; debug redaction is only a fallback.
- Audit records should retain IDs, state transitions, timestamps, actor refs, and policy refs, not raw data.
- Exported bundles must include deletion/anonymisation/revocation state so offline replicas can apply tombstones in order.
- Conflict resolution must prefer privacy-preserving transitions over resurrecting searchable content.

## 5. Boundary with Rumble Note

`rumble-note` owns personal knowledge product semantics:

- block editor, notebook/document UX, backlinks visible to the user;
- local block IDs and block graph meaning;
- privacy choices for private/sensitive/no-handoff blocks;
- NoteContextExport creation, target hints, and user confirmation;
- note-to-spec/session/task handoff UX.

`gear-memory` owns substrate behavior:

- indexing explicit note exports or allowed local note projections;
- retrieval API returning references/provenance, not unrestricted note access;
- stale/deleted/anonymized propagation from note source refs;
- graph edges that are typed references, not product meaning;
- deterministic export/import of memory references and indexes.

P0 decision:

> Gear Memory indexes only explicit exports or explicitly granted local projections. It must not silently index all local notes by default.

This keeps Rumble Note as the user-facing knowledge product and Gear Memory as reusable infrastructure.

## 6. Agent-Readable Formats

Preferred formats:

- canonical JSON for contracts, schemas, fixtures, and validation;
- Markdown for human-readable projections with stable front matter where needed;
- NDJSON for append-only event/provenance export streams;
- SQLite-compatible local storage for offline structured querying when implementation begins;
- compact tabular/TOON-like projections may be used for prompt payloads only when they are generated from canonical contracts and round-trip tested.

Rules:

- Canonical format must be explicit, typed, versioned, and hashable.
- Compact prompt formats are projections, never authoritative storage.
- Every returned retrieval item must include ID, state, hash, and provenance reference.
- No magic implicit graph expansion: expansions must list edge types and traversal depth.
- No hidden mutable state: index build inputs, parser refs, embedding refs, and timestamps must be recorded.

## 7. Inspiration Synthesis / Stack Posture

The stack audit points to these usable design inputs, without cloning external product scope:

| Audit input | Gear Memory implication | Boundary guardrail |
| --- | --- | --- |
| Egonex-AI/Understand-Anything | motivates code maps and explorable source/document graphs | store maps and references only; no explainer brain |
| xberg-io/tree-sitter-language-pack | provides a plausible parser coverage direction for symbols | Wrench parses; Gear stores reproducible `CodeMap` snapshots |
| unum-cloud/USearch | candidate class for fast vector/object search | optional index; never canonical truth |
| tursodatabase/agentfs | reinforces local-first filesystem snapshots and replayable state | no hosted lock-in; no hidden mutable state |
| toon-format/toon | useful compact agent-readable projection | projection only; canonical JSON/NDJSON remains authoritative |
| agenticnotetaking/arscontexta | validates owned markdown/context memory workflows | explicit exports and human-auditable files; no silent note indexing |

Licensing and sovereignty posture:

- MIT/Apache/MPL references may inform implementation decisions after dependency audit;
- unknown-license inputs require quarantine until verified;
- AGPL/GPL/SSPL-style copyleft blockers must not become direct dependencies for this substrate;
- hosted-only services are not acceptable for core truth.

## 8. Security and RGPD Risks

| Risk | Impact | Required mitigation |
| --- | --- | --- |
| Raw PII in logs/index metadata | RGPD breach, hard-to-delete replicas | metadata key rejection, no raw excerpts in events, privacy tests |
| Vector index retaining deleted content | deletion/anonymisation failure | partition-level tombstones, rebuild/drop tests, state filters before retrieval |
| Stale code/source returned as current | wrong agent or product action | explicit stale state, retrieval warnings, freshness acceptance tests |
| Graph edge overreach | Gear infers product meaning | edges are producer-declared references with provenance; no decision logic |
| Silent note indexing | user trust breach | explicit export/grant only for P0; privacy-by-default tests |
| Secret/token capture in provenance | credential leak | reject secret-like metadata keys; never store raw tokens; audit debug output |
| Offline replica resurrects deleted content | RGPD conflict failure | tombstone ordering, privacy-preserving conflict resolution, sync replay tests |
| Opaque compact formats | unverifiable agent behavior | canonical JSON source of truth; projection round-trip tests |
| Auth scope creep | incomplete insecure auth design | reference Biscuit rights/revocation refs only; do not design full auth here |

## 9. Acceptance Tests

### Contract validation

- Given a `SourceRef` without `source_id`, `origin_product`, or `provenance_id`, validation fails.
- Given a hash not matching `sha256:<64 hex chars>`, validation fails.
- Given metadata containing `secret`, `token`, `password`, `credential`, or `api_key` keys, persistence fails.
- Given a timestamp without explicit offset, validation fails.

### Indexing and retrieval

- Given an active source and memory entry, full-text retrieval returns ID, state, hash, and provenance.
- Given an entry marked `deleted`, full-text, vector, graph, and symbol retrieval do not return searchable payload.
- Given an entry marked `stale`, retrieval may return its reference only with stale warning and must not rank it as current truth.
- Given vector search is disabled or unavailable, full-text and graph retrieval still work offline.

### CodeMap

- Given the same source revision and parser refs, `CodeMap` generation is reproducible.
- Given an unsupported language, the map falls back to file-level nodes and records parser limitation metadata.
- Given a source file hash changes, dependent symbols and edges become stale.

### Deletion/anonymisation/revocation

- Given `SourceRef.state=anonymized`, linked memory chunks and embeddings are dropped or rebuilt from anonymized projection only.
- Given an offline replica receives tombstones after older active events, deletion/anonymisation wins.
- Given an artifact reused as source is revoked, derived memory entries stop normal retrieval and record provenance of the revocation path.

### Rumble Note boundary

- Given a private/no-handoff/sensitive block without explicit inclusion, Gear Memory does not index it.
- Given a `NoteContextExport`, Gear Memory indexes only exported blocks and stores source refs/provenance.
- Given a note block is deleted after export, related memory entries become deleted or stale according to the propagated source state.

### Agent-readable export

- Given an export stream, it can be replayed locally to reconstruct references, states, and provenance without network access.
- Given a compact prompt projection, it round-trips to canonical references and does not become authoritative storage.

## 10. ADR / Decision Work

Created or modified decision records:

1. `../shared/adrs/0004-gear-memory-responsibility-boundary.md` — Gear Memory owns reference/index/provenance substrate, not agent memory policy.
2. `../shared/adrs/0005-gear-memory-p0-objects.md` — P0 object set is `SourceRef`, `MemoryEntry`, `EventLogEntry`, `CodeMap`, `ProvenanceRecord`.
3. `../shared/adrs/0006-gear-memory-progressive-indexing.md` — progressive indexes use reference/full-text first, graph/tree-sitter next, vector optional.
4. `../shared/adrs/0007-gear-memory-agent-readable-formats.md` — compact formats are projections; canonical JSON/NDJSON remains authoritative.
5. `../shared/adrs/0008-gear-memory-privacy-tombstones.md` — privacy-preserving tombstones win sync conflicts.
6. `../shared/decision-log.md` — accepted P0 decisions and proposed follow-ups recorded.
7. `../rumble-note/13-gear-memory-boundary.md` — Note indexing open questions closed for P0.
