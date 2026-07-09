# ADR 0012 — Wrench Loader Canonical JSON

Status: Accepted
Date: 2026-06-30

> Historical note (2026-07-09, DC-7): `wrench-loader` was renamed `gear-loader` (ADR 0023 fused / ADR 0033 layer model). Tool-name references below are kept as written; the contract decisions remain in force for `gear-loader`.

## Context

Rumble products need HTML, Markdown, PDF, Office, feed, URL, code, and text ingestion. If each product normalizes content locally, citations, source spans, PII handling, prompt-injection evidence, and hashes will diverge.

Markdown alone is not enough because source spans, chunks, security findings, and provenance need structured fields.

## Decision

`wrench-loader` emits `CanonicalSourceDocument v0.1` as structured JSON. Markdown and plain text are projections. Canonical document hashes are computed over stable canonical JSON bytes.

## Consequences

- Rumbles consume one deterministic extraction shape.
- Gear Memory receives source candidates with hashes and provenance without owning extraction.
- Citation maps can trace chunks back to blocks and source spans.
- Markdown remains useful for humans/agents but is not authoritative storage.

## Acceptance Tests

- Given HTML or Markdown input, output includes structured blocks, chunks, projections, security fields, quality fields, and provenance.
- Given a projection changes while structured content does not, canonical authority remains the JSON contract.
- Given a chunk, it traces back to block IDs and source span data when available.
