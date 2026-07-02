# ADR 0023 — Layer Classification by Client, Not by Verb

Status: Accepted
Date: 2026-07-02
Decision owner: Ecosystem Architecture
Related decision: D15 (decision-log)

## Context

Rumble, Wrench, and Gear layers have been described by verb (inspect, load, execute, store). This leads to ambiguity when tools have multiple audiences and responsibilities.

`wrench-loader` extracts and produces candidates for Gear Memory. If classified by verb alone, it becomes "a tool that executes extraction," but its actual purpose varies by client:

- From Canvas/Crew/LM perspective: a runtime dependency (product ingestion).
- From Rumble development perspective: a build/verification tool (hostile-content scanning, CI gates).
- From Bolt perspective: a planning artifact (evidence generation).

This ambiguity causes accidental product dependencies in build artifacts and blurs governance boundaries.

## Decision

Classify architectural layers and tools by **primary client and deployment boundary**, not by verb:

1. **Wrench** (factory-only): Tools that assist development, CI, security inspection, and governance. Never shipped in product binaries. Includes `wrench-loader`, `wrench-inspect`, `wrench-db-inspect`, and future audit tools.

2. **Gear** (runtime substrate): Shared services and contracts that ship with or are accessible to product runtime (Rumble clients, Bolt, agents). Includes `gear-memory`, `gear-depot`, `gear-cable`, and their contracts.

3. **Rumble** (product): User-facing workflows and data models (Canvas, Crew, LM, Note, COS, FeedMind). Owns UX, product state, and publication gates.

4. **Bolt** (orchestration): Planning, handoff evaluation, and execution coordination inside `cos-matic`. Consumes Wrench evidence and Gear references, owned by the Rumble ecosystem.

Rename `wrench-loader` to `gear-loader` in any product-facing APIs and cargo dependencies to reflect that extracted content is a Gear artifact candidate, not a Wrench-owned intermediate.

## Architecture objectives satisfied

| Objective                   | ADR consequence                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Clear governance boundaries | Wrench/Gear boundary is enforced by CI: no Wrench crates in product `Cargo.lock`.                                              |
| Unified security model      | Gear contracts own artifact integrity and source refs; Wrench owns hostile-content evidence that feeds Gear gates.             |
| Simplified onboarding       | New products know: "Use Gear for runtime persistence, Wrench for CI/security checks, Rumble for UX/business logic."            |
| Future platform elasticity  | If Wrench is decoupled from build, it can be a standalone external service; Gear remains the stable product-adjacent boundary. |

## Consequences

### Positive

- Product CI cannot accidentally depend on Wrench artifacts (cargo check fails if attempted).
- Canvas, Crew, LM, Note, and future Rumbles have a single source for content ingestion (`gear-loader` contract).
- Bolt can distinguish "evidence for planning" (Wrench output) from "durable artifact" (Gear output).
- Security gates are clearly owned: Wrench scans are advisory; Gear gates are mandatory.

### Negative / Costs

- Renaming `wrench-loader` → `gear-loader` requires crate migration and consumer updates.
- CI checks to enforce Wrench exclusion from product binaries are needed and must stay current as crates are added.
- Documentation must clarify that Wrench tools are not public APIs; breakage between releases is acceptable.

## Alternatives considered

### Verb-based classification only

Rejected. Leads to tool purpose ambiguity and accidental cross-layer dependencies.

### Strict per-layer repos with no shared contracts

Rejected. Would fragment the contract ownership for loader I/O, evidence, and artifact manifests.

## Required follow-up

- Rename `wrench-loader` crate to `gear-loader` and update all imports.
- Add CI check to block any `wrench-*` crate imports in `rumble-*`, `gear-*`, and product binaries.
- Update docs in `wrench-inspect` and `wrench-db-inspect` to clarify factory-only status.
- Publish updated layer diagram in `overview.md`.

## Acceptance criteria

- `cargo check` fails if any `rumble-*` or product crate imports `wrench-loader` or `wrench-*`.
- `gear-loader` contract is documented as the canonical ingestion entry point for all Rumble products.
- Wrench tools carry `factory_only = true` metadata in their Cargo.toml or CI metadata.
