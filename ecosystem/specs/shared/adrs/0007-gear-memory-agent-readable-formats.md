# ADR 0007 — Gear Memory Agent-Readable Formats

Status: Proposed
Date: 2026-06-30

## Context

Agents need compact context, but compact prompt formats can become opaque and unverifiable if treated as storage truth. Gear Memory must remain auditable, reproducible, and exportable.

## Decision

Canonical Gear Memory contracts use versioned JSON schemas and NDJSON event/provenance streams. Markdown may be used for human-readable projections. TOON-like or compact tabular formats may be used only as generated prompt projections.

Rules:

- canonical JSON/NDJSON is authoritative;
- projections must include IDs, states, hashes, and provenance refs;
- projections must be reproducible from canonical records;
- round-trip tests are required before a compact format is accepted;
- no hidden graph expansion or implicit state is allowed.

## Consequences

- Agents receive efficient payloads without losing auditability.
- Debugging and replay use canonical records, not prompt text.
- Prompt projection changes do not mutate stored truth.

## Acceptance Tests

- A compact projection can be traced back to canonical record IDs and hashes.
- A projection cannot introduce a source or edge absent from canonical records.
- Export/replay from JSON/NDJSON works without network access.
