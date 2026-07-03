# ADR 0032 — Web shell framework: Dioxus 0.7.9 (ratifies the lab GO)

Status: Accepted
Date: 2026-07-03
Decision owner: Constantin (ecosystem architecture)
Related: supersedes ADR 0030 (Leptos); ratifies `wrench-dioxus-lab` ADR 0001; amends ADR 0027 (rumble-cos rebuild target); arbitration DA-1/DA-2 in `ecosystem/architecture-alignment-2026-07.md`

## Context

ADR 0030 elected Leptos on a native-delivery argument (portal/UniFFI owns native, so the web shell optimizes web only). On 2026-07-03 the local evaluation spike required by the stack matrix (ADR 0034, "Dioxus/PWA → SPIKE LOCAL") delivered its evidence: `wrench-dioxus-lab` ADR 0001 — a measured GO for Dioxus 0.7.9 fullstack (wasm 386 KiB gzip vs a 450 KiB budget, FCP 16–28 ms, 22 e2e specs across 4 engines, HttpOnly SameSite=Strict session proven end-to-end, a11y/token gates green, sovereignty and license audit clean, 10 upstream frictions logged with 3 PRs opened).

Independently, every interactive product repo's own ADR already targets Dioxus (`rumble-feed-mind` ADR 0002, `rumble-lm` ADR 0002, `rumble-ai-practices` ADR 0002); the forge holds a canonical starter (`dioxus-app-template`) proven by the same CI gates. The control plane was the only place still stating Leptos — the alignment document (2026-07-03) flagged this as the blocking contradiction.

## Decision

1. **Dioxus 0.7.9 fullstack** (with dioxus-cli 0.7.9) is the elected web/PWA shell for all interactive Rumble surfaces. **ADR 0030 is superseded.** The 0.8 series stays ignored until stable.
2. **The binding patterns are the lab's**: Dioxus Primitives (headless ARIA), Tailwind v4 compiled natively by `dx`, session in an `HttpOnly; SameSite=Strict` cookie never readable from JS, wasm ≤ 450 KiB gzip with the size-tuned release profile, e2e Playwright on 4 engines, `tracing` ids-only (zero PII/secret in logs), colors only via CSS variables / Portal tokens. `dioxus-app-template` is the canonical starter.
3. **Content sites**: `rumble-cos` rebuilds on the Dioxus SSG path (amends ADR 0027's "elected web shell" reference; arbitration DA-2a). The Astro exception ends. Because no public deployment exists yet (ask-cos.fr never went live), the rebuild is a clean replacement: the 221-item content corpus is the asset to migrate; the legacy redirect map is retained only as internal history (there is no SEO to protect). "Astro static publication GO" in the ADR 0034 matrix is narrowed accordingly: Astro remains permitted tooling outside forge products; forge products publish via Dioxus SSG.
4. **Desktop is re-opened**: ADR 0030's Tauri-2 choice was Leptos-coupled. Desktop is the next spike, demand-driven — no product asks today.
5. **Native (iOS/Android/macOS/Linux/Windows) is unchanged**: `portal-*` / UniFFI owns native delivery.
6. `rumble-lm`'s Dioxus UI is no longer "migration debt" (ADR 0030's framing); it aligns on the lab patterns as part of the flagship slice. `rumble-feed-mind`'s Leptos spike is retired (its evaluation remains available in git history as evidence).

## Consequences

- The stack matrix (`remaining-work.md` P0b, `status.md`) is updated in this PR; `target-version.md` / `target-version.v1.json` are created as the ratified target artifacts.
- Per-repo alignment chantiers are planned in the 2026-07 wave (lm UI alignment, feed-mind spike removal, cos rebuild).
- The upstream contribution workstream (lab FRICTION F-001…F-010) continues; the lab is the canonical evidence artifact and renames to `wrench-dioxus-lab` (ADR 0033, DA-5).
