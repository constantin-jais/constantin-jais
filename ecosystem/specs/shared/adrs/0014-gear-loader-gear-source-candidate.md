# ADR 0014 — Gear Loader Produces GearSourceCandidate, Not SourceRef

Status: Accepted
Date: 2026-06-30

## Context

Gear Loader extracts and normalizes source material. Gear Memory owns durable source references, lifecycle state, indexing, retrieval, deletion, anonymisation, stale propagation, and revocation.

If Loader creates durable `SourceRef` records directly, it becomes a memory store and duplicates Gear state.

## Decision

`gear-loader` produces `GearSourceCandidate v0.1`. Gear Memory accepts, rejects, persists, indexes, deletes, anonymizes, revokes, or marks stale by creating/updating its own `SourceRef` and `MemoryEntry` records.

Loader may run without Gear availability. In that case it returns canonical output and evidence only; it must not pretend a durable `SourceRef` exists.

## Consequences

- Wrench remains extraction/normalization tooling.
- Gear remains the source/memory lifecycle authority.
- Products can inspect extraction output before deciding whether to persist/index.

## Acceptance Tests

- Given successful extraction and Gear unavailable, Loader returns no `SourceRef` ID.
- Given a `GearSourceCandidate`, Gear can deterministically create a `SourceRef` with matching hash/provenance.
- Given Gear rejects a candidate due to policy, Loader does not retry as hidden storage.
