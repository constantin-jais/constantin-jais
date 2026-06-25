# ADR 0021 — Starred Repositories Are Bolt Design Benchmarks, Not Backlog

Status: Accepted
Date: 2026-06-30

## Context

Starred repositories can inform Bolt planning, workflow, prompt, and gate design. Treating them as backlog would create scope creep and clone-by-inspiration risk.

## Decision

For Bolt/cos-matic, starred repositories are used only as design pressure:

- compare deterministic planning and safe-write behavior;
- identify run/gate/refusal patterns;
- benchmark UX concepts for Rumble Crew without moving them into Bolt;
- detect license, SaaS, or automation risks.

No starred project becomes a dependency or feature request without a separate dependency/license/security ADR.

## Consequences

- Bolt contracts remain ecosystem-owned.
- Product UX inspirations stay in Rumble, not Bolt P0.
- License/sovereignty review happens before adoption.

## Acceptance Tests

- A plan may cite a benchmark rationale but not require an unreviewed starred dependency.
- Workflow-builder or agent-team UI ideas are rejected from Bolt P0 scope.
