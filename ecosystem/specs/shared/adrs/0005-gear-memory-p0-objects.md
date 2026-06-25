# ADR 0005 — Gear Memory P0 Objects

Status: Accepted
Date: 2026-06-30

## Context

Gear Memory must support all Rumbles and Bolt with stable references before implementation. The object set must be small enough for P0 and complete enough to avoid local reimplementation of source, memory, audit, code graph, and provenance primitives.

## Decision

Gear Memory P0 object set is:

1. `SourceRef` — stable source/input reference.
2. `MemoryEntry` — indexable snapshot rooted in a `SourceRef`.
3. `EventLogEntry` — append-only safe reference event.
4. `CodeMap` — reproducible source/code symbol and edge map.
5. `ProvenanceRecord` — actor/operation/input/output/tool reference chain.

`ArtifactRef` and artifact manifests remain owned by `gear-depot`. Gear Memory may index an artifact only by creating a `SourceRef` that points at that artifact as grounding input.

## Consequences

- `rumble-note`, `rumble-lm`, `rumble-canvas`, `rumble-feed-mind`, and `rumble-crew` can share the same reference/provenance substrate.
- `CodeMap` prevents each product or Bolt flow from inventing its own code graph.
- The object set avoids premature auth, product UX, or agent policy design.

## Acceptance Tests

- Every `MemoryEntry` references a `SourceRef`; it cannot be standalone truth.
- Every `CodeMap` symbol points back to a `SourceRef` and content hash.
- Every `EventLogEntry` and `ProvenanceRecord` uses references, not embedded raw source content.
