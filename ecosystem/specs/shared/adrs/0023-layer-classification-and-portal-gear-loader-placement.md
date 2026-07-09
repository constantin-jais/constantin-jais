# ADR 0023 — Layer Classification by Client + Portal Layer and Gear Loader Placement (fused)

Status: Superseded by ADR 0033 (2026-07-03)
Date: 2026-07-02 (both parts) · Fused: 2026-07-09 (DA-3 execution, ratified as DC-7 in `ecosystem/reviews/hygiene-audit-2026-07-09.md`)
Decision owner: Ecosystem Architecture

> **Fusion note (2026-07-09).** Two ADRs were accidentally created under the number 0023 on 2026-07-02; both overlapped on the `wrench-loader` → `gear-loader` placement and both were later superseded by ADR 0033 (consolidated layer model). Per arbitration DA-3, this file fuses them verbatim as Part A and Part B; the original files are removed and the ADR-uniqueness CI gate now rejects duplicate numbers across **all** ADR files, superseded included. Nothing below is rewritten.

---

## Part A — Layer Classification by Client, Not by Verb

Status (original): Superseded by ADR 0033 (2026-07-03) — the client test survives as the deployment-class criterion.
Related decision: D15 (decision-log)

### Context

Rumble, Wrench, and Gear layers have been described by verb (inspect, load, execute, store). This leads to ambiguity when tools have multiple audiences and responsibilities.

`wrench-loader` extracts and produces candidates for Gear Memory. If classified by verb alone, it becomes "a tool that executes extraction," but its actual purpose varies by client:

- From Canvas/Crew/LM perspective: a runtime dependency (product ingestion).
- From Rumble development perspective: a build/verification tool (hostile-content scanning, CI gates).
- From Bolt perspective: a planning artifact (evidence generation).

This ambiguity causes accidental product dependencies in build artifacts and blurs governance boundaries.

### Decision

Classify architectural layers and tools by **primary client and deployment boundary**, not by verb:

1. **Wrench** (factory-only): Tools that assist development, CI, security inspection, and governance. Never shipped in product binaries. Includes `wrench-loader`, `wrench-inspect`, `wrench-db-inspect`, and future audit tools.
2. **Gear** (runtime substrate): Shared services and contracts that ship with or are accessible to product runtime (Rumble clients, Bolt, agents). Includes `gear-memory`, `gear-depot`, `gear-cable`, and their contracts.
3. **Rumble** (product): User-facing workflows and data models (Canvas, Crew, LM, Note, COS, FeedMind). Owns UX, product state, and publication gates.
4. **Bolt** (orchestration): Planning, handoff evaluation, and execution coordination inside `cos-matic`. Consumes Wrench evidence and Gear references, owned by the Rumble ecosystem.

Rename `wrench-loader` to `gear-loader` in any product-facing APIs and cargo dependencies to reflect that extracted content is a Gear artifact candidate, not a Wrench-owned intermediate.

### Architecture objectives satisfied

| Objective                   | ADR consequence                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Clear governance boundaries | Wrench/Gear boundary is enforced by CI: no Wrench crates in product `Cargo.lock`.                                              |
| Unified security model      | Gear contracts own artifact integrity and source refs; Wrench owns hostile-content evidence that feeds Gear gates.             |
| Simplified onboarding       | New products know: "Use Gear for runtime persistence, Wrench for CI/security checks, Rumble for UX/business logic."            |
| Future platform elasticity  | If Wrench is decoupled from build, it can be a standalone external service; Gear remains the stable product-adjacent boundary. |

### Consequences

Positive:

- Product CI cannot accidentally depend on Wrench artifacts (cargo check fails if attempted).
- Canvas, Crew, LM, Note, and future Rumbles have a single source for content ingestion (`gear-loader` contract).
- Bolt can distinguish "evidence for planning" (Wrench output) from "durable artifact" (Gear output).
- Security gates are clearly owned: Wrench scans are advisory; Gear gates are mandatory.

Negative / Costs:

- Renaming `wrench-loader` → `gear-loader` requires crate migration and consumer updates.
- CI checks to enforce Wrench exclusion from product binaries are needed and must stay current as crates are added.
- Documentation must clarify that Wrench tools are not public APIs; breakage between releases is acceptable.

### Alternatives considered

- Verb-based classification only — rejected: leads to tool purpose ambiguity and accidental cross-layer dependencies.
- Strict per-layer repos with no shared contracts — rejected: would fragment the contract ownership for loader I/O, evidence, and artifact manifests.

### Required follow-up

- Rename `wrench-loader` crate to `gear-loader` and update all imports.
- Add CI check to block any `wrench-*` crate imports in `rumble-*`, `gear-*`, and product binaries.
- Update docs in `wrench-inspect` and `wrench-db-inspect` to clarify factory-only status.
- Publish updated layer diagram in `overview.md`.

### Acceptance criteria

- `cargo check` fails if any `rumble-*` or product crate imports `wrench-loader` or `wrench-*`.
- `gear-loader` contract is documented as the canonical ingestion entry point for all Rumble products.
- Wrench tools carry `factory_only = true` metadata in their Cargo.toml or CI metadata.

---

## Part B — Portal client platform and Gear Loader placement

Status (original): Superseded by ADR 0033 (2026-07-03) — the Portal layer definition and gear-loader placement it established are carried forward unchanged.
Supersedes: ADR-0012/0013/0014/0015/0016 naming and layer placement for `gear-loader`; keeps their contract intent as historical context.

### Context

The ecosystem originally used four layers: Rumble, Bolt, Wrench, and Gear. Two pressure points made the model incomplete:

1. Rumble products need a shared way to ship coherent clients across web, desktop, iOS, and Android without duplicating tokens, accessibility rules, i18n UI, or native bindings.
2. The former `wrench-loader` placement was not only an offline inspection tool. Its capability can be linked or called by product runtimes and agent workflows as canonical ingestion substrate.

### Decision

Add **Portal** as a first-class client-platform layer:

```text
Portal — Client Platform
```

Portal owns:

- design tokens and generated UI artifacts;
- accessibility and focus conventions;
- i18n for shared UI primitives;
- Rust-first bindings and platform adapters;
- SwiftUI, Compose, web/PWA, and desktop shell conventions.

Portal does not own:

- product workflows or domain screens — Rumble owns those;
- orchestration, planning, or execution gates — Bolt owns those;
- inspection evidence — Wrench owns that;
- release packaging, artifact provenance, cache, registry, or distribution governance — Gear Cable and Gear Depot own those.

Classify the former `wrench-loader` capability as **Gear Loader**:

```text
gear-loader = runtime-capable ingestion substrate
```

Gear Loader owns canonical extraction, normalization, parser policy, hostile-content evidence, and `GearSourceCandidate` handoff. Gear Memory owns durable `SourceRef` lifecycle. Wrench tools may inspect loader outputs and evidence, but Wrench does not own product-linkable parser runtime.

### Boundary rules

- Portal produces coherent client surfaces; Gear governs delivery artifacts.
- Portal-generated CSS/Swift/Kotlin files are client artifacts; Gear Cable may package them and Gear Depot may verify/cache/distribute them.
- Rumble products consume Portal primitives and own product-specific components.
- `presto-ui` in `rumble-lm` has been renamed to `rumble-lm-ui`; it is product-local UI, not shared design-system ownership.
- Dioxus/PWA is the fast default path for interactive Rumble products. SwiftUI/Compose are first-class native paths when product demand and local verification justify them.

### Consequences

- The ecosystem map becomes Rumble / Portal / Bolt / Wrench / Gear.
- Portal repositories (`portal-forge`, `portal-core`, `portal-apple`, `portal-android`) are intentional target-shape repos, not accidental product repos.
- Gear Depot must not absorb Portal because Depot owns artifact trust, not UI semantics.
- Historical `wrench-loader` specs remain migration references until schemas/paths are renamed to Gear Loader.
