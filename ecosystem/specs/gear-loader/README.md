# Gear Loader Specifications

`gear-loader` is the canonical ingestion/extraction brick. It transforms hostile or heterogeneous inputs into deterministic, auditable canonical source documents.

## Files

| File                              | Purpose                                                                                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `00-canonical-ingestion-scope.md` | Scope, boundaries, contracts, security model, acceptance tests.                                                       |
| `gear-loader.v0.1.schema.json`    | JSON Schema bundle for extraction requests, canonical documents, Gear source candidates, and loader evidence reports. |
| `fixtures/`                       | Valid and invalid contract fixtures.                                                                                  |

## Boundary Reminder

Gear Loader extracts and normalizes. It does not decide product meaning, store durable memory, index for retrieval, poll feeds as product workflow, or orchestrate next actions.

- Gear Memory owns durable `SourceRef`, `MemoryEntry`, retrieval, stale/delete/anonymize propagation.
- Rumbles own UX, curation, learning/session/note/spec/task semantics.
- Bolt owns sequencing, gates, schedules, and execution decisions.
