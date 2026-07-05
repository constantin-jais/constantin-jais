# Target Version — accepted full target of the ecosystem stack

Version: 1.1.0 · Ratified: 2026-07-03 · Machine version: [`target-version.v1.json`](target-version.v1.json) (validated against [`specs/harness/stack-target-version.v0.1.schema.json`](specs/harness/stack-target-version.v0.1.schema.json) by the spec-contracts gate)
Ratified by: ADR 0032, ADR 0033, ADR 0028 (amended), ADR 0029 (with addendum), and the DA-1..DA-12 arbitration recorded in [`architecture-alignment-2026-07.md`](architecture-alignment-2026-07.md).

This file is the human summary of the accepted target. When it disagrees with the ADRs, the ADRs win; when the machine file disagrees with this file, fix whichever drifted and note it in the decision log. Re-deciding any element below mid-wave requires an explicit stop (big-bang posture makes a moving target expensive).

## Layer model (ADR 0033)

The prefix carries the **owning domain**; the **deployment class** (`product-linkable` | `factory-only` | `build-time`) is a CI-gated claim in `maturity/stack/*.json`, never a naming convention.

| Prefix     | Role                     | One-line definition                                                                                                                           |
| ---------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `rumble-*` | Products                 | User-facing workflows, delivered natively on 6 targets; owns UX, product state, publication gates                                             |
| `portal-*` | Client platform          | Tokens, primitives, a11y, i18n UI, native bindings; also the agents' UI-production capability (tokens-only); never actor/tenant authorization |
| `bolt-*`   | Factory                  | Orchestration, planning, handoff evaluation, execution coordination + the factory's own proof surfaces                                        |
| `wrench-*` | Transverse factory tools | Inspection, audit, and evaluation labs serving ≥ 2 domains; never ship in products                                                            |
| `gear-*`   | Runtime substrate        | Linkable services/contracts: ingestion, memory, artifacts, distribution; one contract, two clients                                            |

## Elected stack (ADR 0032)

- **Web/PWA shell**: Dioxus 0.7.9 fullstack — patterns bound to the `wrench-dioxus-lab` evidence (Primitives ARIA, Tailwind v4 via dx, HttpOnly SameSite=Strict session, wasm ≤ 450 KiB gzip, e2e 4 engines, tracing ids-only, tokens-only colors). Canonical starter: `dioxus-app-template`.
- **Headless component library**: Dioxus Components (`dioxus-primitives`, git-pinned `bf007c15`, dual MIT/Apache-2.0) — unstyled WAI-ARIA primitives, appearance via Portal tokens only (ADR 0036). First application: `rumble-ai-practices`. crates.io un-pin is a demand-driven follow-up (F-006).
- **Static publication**: Dioxus SSG for ecosystem products; the Astro exception ended with the cos rebuild decision (DA-2a).
- **Native**: `portal-*` + UniFFI (SwiftUI / Compose); apple frozen at the proven-bridge tag, android frozen pending verifiable CI.
- **Desktop**: re-opened; next spike, demand-driven.
- **Data/backing**: Rust service GO; PostgreSQL/SQLx and OIDC/Biscuit conditional; Redis and native mobile shells WAIT; paid provisioning NO-GO (ADR 0034 discipline unchanged).

## Ownership decisions

- **Session runtime**: `rumble-lm` owns it; ai-practices is a content pack + scoring module (ADR 0029 + addendum — its local store is a frozen shim until convergence).
- **Identity/Workspace**: identity primitives → Gear (contract-first, extraction D11-gated); workspace container → shared Rumble contract; `portal-core` excluded (ADR 0028 + amendments, closed permission vocabulary in `workspace-identity.v0.1`).

## Definition of done (unchanged)

A stack slice is complete when **one real Rumble product** traverses: Portal → Gear Loader → Gear Memory → Gear Depot → Gear Cable → Wrench evidence → Bolt planning-only handoff → Cos explanation. Flagship slice of the 2026-07 wave: **rumble-lm**.

## Wave posture (DA-8)

Big-bang: nothing is in service, blocking is acceptable, specific-over-target code gets broken and rebuilt. Two invariants survive the posture: every repo advances by green PRs under its gates, and this target stays frozen for the wave's duration.
