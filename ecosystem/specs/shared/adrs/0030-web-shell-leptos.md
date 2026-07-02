# ADR 0030 — Web shell framework: Leptos

Status: Accepted
Date: 2026-07-02
Decision owner: Constantin (ecosystem architecture)
Related: D7 (decision-log); supersedes the "Rust core + Dioxus UI by default" decisions of 2026-06-30; ADR 0024 (Portal design substrate); ADR 0027 (rumble-cos rebuild)

## Context

The doctrine required interactive Rumble products to converge on a single Rust UI framework, but the choice (Dioxus vs Leptos) was left to an E2E spike. Two symmetric spikes were run:

- **Dioxus 0.7** in `rumble-lm` (`crates/ui/examples/spike_web.rs`): 3 mocked screens, 8 tests, **wasm32 build proven** in-workspace. Documented in `rumble-lm/docs/spikes/dioxus-web-shell.md`.
- **Leptos 0.7** in `rumble-feed-mind` (`apps/web-rs/src/spike/`): the same 3 screens, 12 tests, native SSR proven; wasm32 blocked on a workspace `uuid` feature-config gap (not a Leptos limitation). Documented in `rumble-feed-mind/docs/spikes/leptos-web-shell.md`.

Neither agent ran the other framework, so the per-framework verdicts were biased toward what each measured. The deciding input was **not** the spikes' self-verdicts but a prior architectural fact.

## The deciding question

**How are native targets (iOS, Android, macOS, Linux, Windows) delivered?**

Answer (Constantin, 2026-07-02): **native goes through `portal-*`** — a shared Rust core exposed to native shells (SwiftUI, Jetpack Compose) via UniFFI, plus `portal-forge` design tokens. The web framework is therefore **not** responsible for native rendering.

This collapses the choice: the web shell only needs to be the best **web** shell, not a cross-platform renderer.

## Decision

1. **The web shell is Leptos.** Interactive Rumble products render their web/PWA surface with Leptos.
2. **Native targets go through `portal-*`** (Rust core + UniFFI + SwiftUI/Compose), not through the web framework's renderer.
3. **Desktop is the Leptos web shell wrapped in Tauri 2** — not a separate renderer.
4. **`rumble-cos` (content site) benefits directly**: Leptos's first-class SSR serves the D6 rebuild (SEO, static-first performance) better than a client-centric renderer.

### Why Leptos, given native is portal's job

- **Fine-grained signals** (DOM-node reactivity) suit live-participation UIs (lm sessions, polls) better than component-tree re-render.
- **First-class SSR** is built-in, not bolted-on — decisive for the cos rebuild and for SEO-bearing surfaces.
- **Rust cohesion**: cargo + clippy + fmt, zero Node.js in the shell.
- Dioxus's main advantage (one renderer → web + desktop + native mobile) is **irrelevant here** because portal owns native and Tauri owns desktop.

### Accepted trade-offs

- Leptos 0.7 is pre-1.0 with recent API renames (`create_signal → signal()`); pin `0.7.x`, plan a migration checkpoint on 0.8.
- Smaller community and thinner docs than Dioxus.
- The wasm32 build must be unblocked (workspace `uuid` feature config) — a one-time setup task, tracked as a follow-up.

## Consequences

- **Dioxus is retired as the web shell.** `rumble-lm/crates/ui` (Dioxus) becomes migration debt: its web surface moves to Leptos at lm's next UI increment. The Dioxus spike doc is superseded (kept as historical evidence).
- **feed-mind's Leptos skeleton (`apps/web-rs`) becomes the reference** web shell pattern.
- **The doctrine changes** from "Rust core + Dioxus UI by default" to "Rust core; web shell = Leptos; native = portal; desktop = Tauri." The 2026-06-30 Dioxus-default decisions are superseded by D7.
- Follow-ups: unblock wasm32 config; migrate lm's Dioxus web UI to Leptos; align feed-mind's legacy Next.js surface toward the Leptos shell; sequence cos rebuild (D6) on this shell.

## Non-goals

- This does not mandate rewriting non-web code. Domain/core logic stays framework-agnostic Rust.
- This does not choose a native mobile framework beyond "via portal/UniFFI" — that stays per-product and demand-driven (D14).
