# ADR 0022 — Starred Repository Ideas Strengthen Existing Repositories First

Status: Accepted
Date: 2026-06-30

## Context

The curated GitHub stars audit surfaced several useful project-shaped ideas:

- evidence operations for API, browser, CI, and agent/LLM outputs;
- browser inspection and visual proof capture;
- evaluation suites for prompts, generated content, citations, and agent behavior;
- clean-room inspiration/license/sovereignty audits;
- reusable policy gates for agent runs;
- source cataloging and usage ledgers;
- compact agent-readable payload projections;
- release floor and target matrix planning.

Creating new repositories for each idea would fragment contracts, increase security surface, and turn inspiration into roadmap debt before product demand proves stable ownership.

## Decision

No new repository is created for these starred-repo-derived ideas at this stage.

They are integrated as hardening tracks inside existing repositories:

| Idea | Owner repository | Integration shape |
| --- | --- | --- |
| EvidenceOps | `wrench-inspect` | `evidence` inspection/reporting capability |
| Browser Lab | `wrench-inspect` | sandboxed `browser` evidence collector |
| Eval Lab | `wrench-inspect` | `eval` evidence collector for LLM/agent/content checks |
| Clean-room Auditor | `wrench-inspect` | `cleanroom` inspection mode for license, sovereignty, fit, and reuse boundaries |
| Policy Pack | `cos-matic` | policy gate definitions, checks, explanations, and refusal evidence |
| Source Vault | `gear-memory` | `source-catalog` over `SourceRef`, provenance, deletion/anonymization, and indexing boundaries |
| Usage Ledger | `gear-memory` | append-only technical usage events and aggregate projections without user profiling |
| Payload / Compact Contracts | `gear-depot` or shared Gear library | payload projections derived from canonical JSON/NDJSON artifacts; never canonical truth |
| Release Floor | `gear-cable` | target matrix, install floors, release plans, checksum/signature plans |

## Extraction Rule

A module may be extracted into a new repository only when all conditions are met:

1. it has multiple real consumers across the ecosystem;
2. it has a stable machine-readable contract;
3. keeping it in the parent repository would blur the parent responsibility;
4. the new repository has a clear Rumble/Portal/Bolt/Wrench/Gear ownership boundary;
5. license, sovereignty, secrets, PII, and hostile-content risks have dedicated checks.

## Consequences

- `wrench-inspect` becomes the first integration point for evidence, browser, eval, and clean-room capabilities.
- `cos-matic` remains the policy/gate owner instead of creating a parallel Bolt policy runtime.
- `gear-memory` keeps source and usage substrate responsibilities unless evidence proves they need extraction.
- `gear-depot` owns artifact policy and compact projections only when tied to artifact manifests; canonical schemas remain JSON/NDJSON.
- `gear-cable` absorbs release-floor concerns without creating a release-stack repository.
- Starred repositories remain benchmarks and inspiration, not backlog items.

## Non-Goals

- Do not add dependencies from the starred repositories through this ADR.
- Do not define final CLI names or schemas.
- Do not implement browser automation, LLM evals, or usage accounting yet.
- Do not duplicate the active Biscuit, Gear Memory, Gear Loader, Wrench DB Inspect, Bolt hardening, Portal client platform, or Rumble LM sessions.

## Acceptance Tests

- A new starred-repo-derived idea is first mapped to an existing owner repository or rejected as knowledge/later.
- A proposal for a new repository cites the extraction rule and demonstrates all five conditions.
- Wrench evidence/browser/eval/clean-room work shares one report model before any split.
- Compact payload projections can be regenerated from canonical JSON/NDJSON and are not treated as source of truth.
- Usage events do not contain raw secrets, prompt payloads, or behavioral profiling data by default.
