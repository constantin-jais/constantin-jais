# ADR-0023 — Portal client platform and Gear Loader placement

- Status: Accepted
- Date: 2026-07-02
- Supersedes: ADR-0012/0013/0014/0015/0016 naming and layer placement for `gear-loader`; keeps their contract intent as historical context.

## Context

The ecosystem originally used four layers: Rumble, Bolt, Wrench, and Gear. Two pressure points made the model incomplete:

1. Rumble products need a shared way to ship coherent clients across web, desktop, iOS, and Android without duplicating tokens, accessibility rules, i18n UI, or native bindings.
2. The former `wrench-loader` placement was not only an offline inspection tool. Its capability can be linked or called by product runtimes and agent workflows as canonical ingestion substrate.

## Decision

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

## Boundary rules

- Portal produces coherent client surfaces; Gear governs delivery artifacts.
- Portal-generated CSS/Swift/Kotlin files are client artifacts; Gear Cable may package them and Gear Depot may verify/cache/distribute them.
- Rumble products consume Portal primitives and own product-specific components.
- `presto-ui` in `rumble-lm` has been renamed to `rumble-lm-ui`; it is product-local UI, not shared design-system ownership.
- Dioxus/PWA is the fast default path for interactive Rumble products. SwiftUI/Compose are first-class native paths when product demand and local verification justify them.

## Consequences

- The ecosystem map becomes Rumble / Portal / Bolt / Wrench / Gear.
- Portal repositories (`portal-forge`, `portal-core`, `portal-apple`, `portal-android`) are intentional target-shape repos, not accidental product repos.
- Gear Depot must not absorb Portal because Depot owns artifact trust, not UI semantics.
- Historical `wrench-loader` specs remain migration references until schemas/paths are renamed to Gear Loader.
