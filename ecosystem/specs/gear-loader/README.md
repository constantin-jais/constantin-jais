# Gear Loader Specifications — historical `gear-loader` path

> Migration note: ADR-0023 supersedes the layer/name placement. The canonical repository is now `gear-loader` because ingestion is runtime-capable Gear substrate. This directory keeps the historical `gear-loader` schema path until contracts/fixtures are migrated without breaking validation.

`gear-loader` is the canonical ingestion/extraction brick. It transforms hostile or heterogeneous inputs into deterministic, auditable canonical source documents.

## Files

| File | Purpose |
| --- | --- |
| `00-canonical-ingestion-scope.md` | Scope, boundaries, contracts, security model, acceptance tests. |
| `gear-loader.v0.1.schema.json` | Historical JSON Schema bundle for Gear Loader extraction requests, canonical documents, Gear source candidates, and loader evidence reports. |
| `fixtures/` | Valid and invalid contract fixtures. |

## Boundary Reminder

Gear Loader extracts and normalizes. It does not decide product meaning, store durable memory, index for retrieval, poll feeds as product workflow, or orchestrate next actions. Wrench tools may inspect its evidence.

- Gear Memory owns durable `SourceRef`, `MemoryEntry`, retrieval, stale/delete/anonymize propagation.
- Rumbles own UX, curation, learning/session/note/spec/task semantics.
- Bolt owns sequencing, gates, schedules, and execution decisions.
