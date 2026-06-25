# ADR 0004 — Gear Memory Responsibility Boundary

Status: Accepted
Date: 2026-06-30

## Context

Rumble products and Bolt need shared memory, source graph, code graph, indexing, and provenance. If each Rumble implements these locally, deletion, stale propagation, citations, and audit behavior will diverge. If Gear Memory becomes an agent brain, it will absorb product and orchestration responsibilities.

## Decision

`gear-memory` owns reference, index, graph, retrieval, and provenance substrate. It does not own product meaning, agent goals, planning, ranking decisions, or next-action policy.

Gear Memory may answer:

- which sources and memory entries exist;
- how they are linked;
- whether they are active, stale, deleted, anonymized, or revoked;
- what hash/provenance supports them;
- which references match a retrieval query.

Gear Memory must not answer:

- what the user should do next;
- what an agent should decide;
- which product workflow state should change;
- whether generated claims are acceptable;
- which note/session/task/feed item is strategically important.

## Consequences

- Rumbles avoid reimplementing dangerous infrastructure.
- Bolt receives reliable context references but keeps orchestration decisions.
- Wrench keeps extraction, parsing, validation, and inspection logic.
- Gear Memory remains reusable without becoming a product or platform monolith.

## Acceptance Tests

- A retrieval response returns references, states, hashes, and provenance, not a recommended action.
- A product-specific ranking or workflow transition is rejected from Gear Memory scope.
- A Wrench-produced extraction can be stored/indexed without Gear owning the extraction rules.
