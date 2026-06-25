# ADR 0006 — Gear Memory Progressive Indexing

Status: Proposed
Date: 2026-06-30

## Context

Search needs differ by product. Full vector-first memory would be opaque, harder to audit, and more fragile for deletion/anonymisation. But full-text alone is insufficient for code graph and source graph needs.

## Decision

Gear Memory indexes progressively:

1. reference catalog: IDs, hashes, states, provenance;
2. full-text: deterministic offline search baseline;
3. graph: explicit typed edges with provenance;
4. tree-sitter `CodeMap`: parser-backed symbol graph, produced by Wrench and stored by Gear;
5. vector: optional acceleration only.

Vector indexes must never be the sole source of truth. Every vector hit must resolve to canonical references, state, hash, and provenance.

## Consequences

- Products can adopt Gear Memory incrementally.
- Offline/local-first operation works before vector infrastructure exists.
- Deleted/anonymized content can be dropped from all indexes with auditable tombstones.
- Vector backend choices can be benchmarked later without changing contracts.

## Acceptance Tests

- With vector disabled, full-text and graph retrieval still work offline.
- Deleted/anonymized entries are absent from full-text/vector payload search.
- Stale entries are clearly marked and not returned as current truth.
- `CodeMap` rebuild staleness is triggered by source revision or parser ref changes.
