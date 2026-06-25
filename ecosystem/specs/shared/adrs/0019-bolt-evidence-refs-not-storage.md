# ADR 0019 — Bolt Uses Evidence References, Not Evidence Storage

Status: Accepted
Date: 2026-06-30

## Context

Bolt planning depends on Wrench reports and Gear references. If Bolt stores raw report bodies, source excerpts, artifacts, logs, embeddings, or provenance truth, it absorbs Wrench/Gear responsibilities and increases PII/secrets risk.

## Decision

Bolt P0 stores and emits `EvidenceRef` values only: kind, producer, ref ID, hash, state/status, provenance ref, and safe summary. Rich bodies remain in Wrench/Gear/product-owned storage according to their policies.

## Consequences

- Bolt can gate on evidence without becoming an evidence database.
- Logs and plan reports remain safe to inspect.
- Gear and Wrench stay authoritative for storage and inspection output.

## Acceptance Tests

- A `PlanReport` cites Wrench/Gear evidence by ref/hash/status.
- Raw source excerpts and report bodies are absent from Bolt audit events.
- Evidence with missing hash or unsafe status blocks planning.
