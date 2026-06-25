# ADR 0017 — Bolt Planning-Only Lifecycle Before Execution Runtime

Status: Accepted
Date: 2026-06-30

## Context

Rumble products need implementation planning before any safe execution runtime exists. Allowing execution semantics into P0 would bypass evidence, approval, sovereignty, and authorization gates.

## Decision

Bolt P0 exposes only a planning lifecycle inside `cos-matic`:

```text
received → validating → refused | accepted_for_planning → planning → plan_ready | planning_failed
```

No P0 object may authorize implementation execution. A future execution runtime requires a separate ADR, human gate, delegated rights, attempt lineage, and runtime isolation model.

## Consequences

- Rumbles can ask for plans without gaining execution powers.
- `cos-matic` can harden validation/refusal before runtime complexity.
- Human approval remains a later explicit boundary.

## Acceptance Tests

- A planning request with `dry_run=true` can produce `PlanReport`.
- Any P0 request with `allow_execution=true` is refused.
- No fixture produces an execution run or requests runtime credentials.
