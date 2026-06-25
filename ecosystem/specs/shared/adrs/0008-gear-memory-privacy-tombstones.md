# ADR 0008 — Gear Memory Privacy Tombstones

Status: Proposed
Date: 2026-06-30

## Context

Gear Memory is local-first/offline-first. Replicas may receive events out of order. Deletion, anonymisation, and revocation must not be undone by stale active records or older index rebuilds.

## Decision

Privacy-preserving state transitions win sync conflicts:

1. `anonymized` and `deleted` beat `active` and `stale` for searchable content.
2. `revoked` prevents normal retrieval/export until explicitly superseded by a valid later policy transition.
3. Tombstones are replayable events with timestamps, actor refs, target refs, and provenance refs.
4. Tombstones retain minimal audit references only when policy allows; raw content, chunks, embeddings, and source excerpts are removed.

## Consequences

- Offline replicas cannot resurrect deleted/anonymized searchable content through old events.
- Gear Memory can satisfy RGPD erasure/anonymisation expectations while preserving legal audit minima.
- Products keep retention-policy ownership; Gear enforces substrate state transitions.

## Acceptance Tests

- Replaying an old `active` event after a later deletion tombstone does not restore searchable payload.
- An anonymized source causes linked memory chunks and embeddings to be dropped or rebuilt from anonymized projection only.
- Event logs record the transition without raw PII or source excerpts.
