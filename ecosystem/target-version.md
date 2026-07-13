# Target Version — accepted full target of the ecosystem stack

Version: 2.1.0 · Ratified: 2026-07-11 · Machine version: [`target-version.v1.json`](target-version.v1.json) (validated against [`specs/harness/stack-target-version.v0.2.schema.json`](specs/harness/stack-target-version.v0.2.schema.json) by the spec-contracts gate)
Ratified by: ADR 0028, ADR 0029, ADR 0032, ADR 0033, ADR 0037 and ADR 0038–0046.

This file is the human summary of the accepted target. When it disagrees with the ADRs, the ADRs win; when the machine file disagrees with this file, fix whichever drifted and note it in the decision log. Re-deciding any element below mid-wave requires an explicit stop (big-bang posture makes a moving target expensive).

Public repository names and maturity are governed by [`governance/repo-profiles.json`](governance/repo-profiles.json). Historical `rumble-*`, `portal-*`, `bolt-*`, `wrench-*`, and `gear-*` strings below are compatibility identifiers for versioned contracts, crates, fixtures and imported paths; they are not a public naming scheme for new repositories.

## Layer model (ADR 0033)

The prefix carries the **owning domain**; the **deployment class** (`product-linkable` | `factory-only` | `build-time`) is a CI-gated claim in `maturity/stack/*.json`, never a naming convention.

| Prefix     | Role                     | One-line definition                                                                                                                           |
| ---------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| functional product slugs | Products                 | User-facing workflows; owns UX, product state, domain models and publication gates                                                            |
| `portal-*` | Client platform          | Tokens, primitives, a11y, i18n UI, native bindings; also the agents' UI-production capability (tokens-only); never actor/tenant authorization |
| `bolt-*`   | Factory                  | Orchestration, planning, handoff evaluation, execution coordination + the factory's own proof surfaces                                        |
| `wrench-*` | Transverse factory tools | Inspection, audit, and evaluation labs serving ≥ 2 domains; never ship in products                                                            |
| `gear-*`   | Runtime substrate        | Linkable services/contracts: ingestion, memory, artifacts, distribution; one contract, two clients                                            |

## Elected stack (ADR 0032)

- **Application stack**: Dioxus 0.7.9 is the preferred shared shell across web/PWA, SSR/SSG, fullstack server functions, desktop, Android and iOS. Product-domain crates remain renderer-independent.
- **Web/PWA evidence**: patterns are bound to `libre-ai/proof-kit/labs/dioxus` evidence (Primitives ARIA, HttpOnly SameSite=Strict session, wasm ≤ 450 KiB gzip, e2e 4 engines, tracing ids-only, tokens-only colors). Canonical starter: `dioxus-app-template`.
- **Headless component library**: Dioxus Components (`dioxus-primitives`, git-pinned `bf007c15`, dual MIT/Apache-2.0) — unstyled WAI-ARIA primitives, appearance via Portal tokens only (ADR 0036). The Git pin is temporary until a verifiable release exists.
- **Static publication**: Dioxus SSG for ecosystem products; the Astro exception ended with the Website rebuild decision.
- **Desktop and mobile**: Dioxus WebView shells are the default convergence target. Portal owns adaptive components and native integration contracts. SwiftUI/Compose adapters remain escape hatches and evidence labs, not duplicate default UIs.
- **Support claims**: web, desktop, Android, iOS, fullstack and UI each require the matrix in [`specs/shared/dioxus-target-evidence.md`](specs/shared/dioxus-target-evidence.md). Until a target passes it, that target is `experimental`, not supported.
- **Data/backing**: Rust service GO; PostgreSQL/SQLx and OIDC/Biscuit conditional; Redis remains WAIT; paid provisioning remains a separate human operation.
- **Language boundary**: durable logic stays in Rust; JavaScript source is forbidden; TypeScript is limited to browser presentation, Playwright, generated clients, bounded Office host interop and tooling (ADR 0038/0039).
- **Hosted boundaries**: Clever Cloud/SQL/Cellar and Clever AI are named portable-adapter targets; GitHub is the canonical public forge. Provisioning remains separately approved (ADR 0043).

## Visual contract (ADR 0037)

- **Identity**: Libre IA Design System 2.0 on every active client surface.
- **Source**: versioned distribution `urn:libre-ai:design-system:2.0.0`, path `design-system/tokens/tokens.json`; compilation and WCAG evidence through `portal/forge`.
- **Palette**: black, white, neutral grays and Vert Libre `#22C55E` as the only accent; status meaning never depends on color alone.
- **Typography**: self-hosted Inter and Plus Jakarta Sans; no remote font request.
- **Distribution**: generated CSS/Swift/Kotlin plus SHA-256 manifest, vendored at build time with no runtime network dependency.
- **Exceptions**: raw benchmark outputs stay immutable; CLI-only repositories have no artificial visual layer.

## Ownership decisions

- **Public domains**: `libre-ai.fr` explains the portfolio, explicit product subdomains act, and `preuves.libre-ai.fr` verifies. Every product host remains inactive until its own public-alpha gate passes; DNS activation is a separate human operation (ADR 0046).
- **Session runtime**: `libre-ai/sessions` owns it; AI Practices is a content pack + scoring module (ADR 0029 + addendum — its local store is a frozen shim until convergence).
- **Identity/Workspace**: identity primitives → Gear (contract-first, extraction D11-gated); workspace container → shared product contract; Portal is excluded (ADR 0028 + amendments, closed permission vocabulary in `workspace-identity.v0.1`).

## Cross-cutting authority (ADR 0038–0044)

- Specialized document/provider/browser adapters implement Rust-owned contracts, are replaceable and fail closed. Hostile parsers run in killable, networkless processes.
- Clean-room adoption uses autonomous specifications and synthetic fixtures only; copying or transliterating private code, prompts, schemas or corpus is forbidden.
- Biscuit/Ed25519 is the canonical delegated authorization contract with mandatory organization, resource, action, purpose, expiry and revocation scope.
- Servers and supervisors unwind; hostile parser crashes become typed worker failures. Abort is limited to measured one-shot CLI/WASM artifacts.
- Compromises are explicit: GitHub forge, Clever hosted boundaries and specialized adapters. No direct model-provider fallback.

## Definition of done

A stack slice is complete when **one real product** traverses: Portal → Gear Loader → Gear Memory → Gear Depot → Gear Cable → Wrench evidence → Bolt planning-only handoff → product explanation. Flagship slice: **Sessions**.

## Wave posture (DA-8)

Big-bang: nothing is in service, blocking is acceptable, specific-over-target code gets broken and rebuilt. Two invariants survive the posture: every repo advances by green PRs under its gates, and this target stays frozen for the wave's duration.
