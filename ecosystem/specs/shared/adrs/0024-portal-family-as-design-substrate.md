# ADR 0024 — Portal Family as Design Substrate and Factory Tool

Status: Accepted
Date: 2026-07-02
Decision owner: Ecosystem Architecture
Related decision: D14 (decision-log), Rumble Crew product
Related contract: `../contracts/portal-design-substrate.v0.1.md` (to be written)

## Context

`portal-forge`, `portal-core`, `portal-apple`, and `portal-android` were conceived as separate bridges and clients. As the ecosystem matures, they serve a dual purpose:

1. **Factory-side** (Rumble Crew, Bolt, operators): Authoring, orchestration, admin interfaces, and trusted-execution dashboards.
2. **Product-side** (end-user delivery): Native mobile, web, and embedded clients.

Treating them as a unified design substrate clarifies ownership: Crew delegates to `portal-forge` for workspace admin and job scheduling; end-users interact with product-specific thin shells (`portal-apple`/`portal-android`/web) that consume Gear contracts.

Additionally, operator roles (tokens, audit, secrets) must be isolated from participant personas. The rule "tokens only, no user data in portal cookies/storage" must be enforced at the substrate boundary.

## Decision

Adopt the **Portal family as a dual-client design substrate**:

- `portal-core`: Shared library for token handling, Biscuit verification, Gear contract interaction, and audit references. Internal-only API.
- `portal-forge`: Factory-side tool (admin dashboards, batch operations, workspace config, job lifecycle). Deployed to operators only.
- `portal-apple` / `portal-android`: Frozen at current state; no new features until RFP-driven demand. UniFFI bridge proven sufficient.
- Web shell (elected via E2E spike): Single implementation, replaces Astro exception. Dioxus or Leptos winner deployed as web client; loser deleted.

Rules:

1. **Tokens only in portal-core storage**: No participant/user data in localStorage, cookies, or session. Participant responses belong in Gear artifacts, not portal substrate.
2. **Operator/participant isolation**: `portal-forge` UI is strictly for operator roles (workspace admin, batch, audit). End-user clients (mobile/web) are minimal and read-only after job submission.
3. **CI check** (`wrench-inspect` or new `portal-inspect`): Verify that portal binaries do not contain product-specific data enums or participant schemas.
4. **Gear contracts as truth**: Portal clients are thin; all state lives in Gear (artifacts, source refs, responses, metadata).

## Architecture objectives satisfied

| Objective                     | ADR consequence                                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Product-operator separation   | Crew (factory) and participant (product) are separate personas; Portal substrates enforce this boundary.                      |
| Design reuse without coupling | Shared `portal-core` avoids token logic duplication across mobile/web/Tauri without bleeding product semantics.               |
| Frozen vs. Living             | Mobile bridges are frozen when proven; web iteration is fast. Tauri covers desktop without new native ports.                  |
| Audit and sovereignty         | Operator actions in `portal-forge` are Biscuit-signed and fully auditable; participant data never touches operator substrate. |

## Consequences

### Positive

- Crew and operator workflows have a dedicated, auditable UI layer.
- Participant-side clients are guaranteed lightweight and stateless (no accidental data hoarding).
- Mobile platforms are stable and low-risk; web can evolve rapidly.
- Sustainability: unfrozen portals (web/Tauri) have clear ownership; frozen ones (Apple/Android) require RFP to thaw.

### Negative / Costs

- Web shell decision (Dioxus vs. Leptos) requires E2E spike to avoid regret later.
- Mobile frozen state may frustrate feature requests; RFP process must be clear and lightweight.
- `portal-core` must be kept strictly minimal; product creep would blur the boundary.
- CI checks for "no participant data in portals" are ongoing maintenance.

## Alternatives considered

### Unify all portals into one agnostic framework

Rejected. Mobile constraints (native, offline-first, restricted storage) differ sharply from web; one size does not fit all.

### Keep portals as separate silos

Rejected. `portal-core` code is duplicated (tokens, Biscuit, Gear refs), and operator tooling is ad-hoc.

## Required follow-up

- Conduct E2E spike: Dioxus (in lm) vs. Leptos (in feed-mind). Winner becomes web shell; loser is deleted.
- Write `portal-design-substrate.v0.1.md` contract defining `portal-core` API and isolation rules.
- Add `portal-inspect` CI check to verify participant schemas are not compiled into portal binaries.
- Document RFP process for unfreezing mobile implementations.
- Ensure `portal-forge` is deployment-gated (operator-only, not product-facing).

## Acceptance criteria

- `portal-core` exports exactly: token validation, Biscuit verifier, Gear contract readers, audit refs, and nothing else.
- `portal-apple` and `portal-android` builds do not import product namespaces (e.g., `rumble_lm::activities`, `rumble_crew::tasks`).
- Web shell spike produces pass/fail evidence for Dioxus and Leptos E2E, with winner/loser decision recorded in decision-log.
- `portal-forge` requires operator token or trusted environment variable to authenticate.
