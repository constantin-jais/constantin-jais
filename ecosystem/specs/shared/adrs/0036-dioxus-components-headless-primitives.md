# ADR 0036 — Headless component library: Dioxus Components (dioxus-primitives)

Status: Accepted
Date: 2026-07-03
Decision owner: Constantin (ecosystem architecture)
Related: ADR 0032 (Dioxus 0.7.9 web shell — names "Dioxus Primitives (headless ARIA)" as a binding pattern); ADR 0024 (Portal family as design substrate); `wrench-dioxus-lab` ADR 0001 (proven usage); target-version 1.1.0

## Context

ADR 0032 ratified Dioxus 0.7.9 and listed "Dioxus Primitives (headless ARIA)" among the binding UI patterns, but never named the component library as an explicit stack element with a source, a version pin, and a styling contract. Every Rumble product that builds a UI now needs the same headless, accessible component set — reinventing buttons, dialogs, and menus per product is exactly the duplication the Portal doctrine exists to prevent.

`wrench-dioxus-lab` already proved the library in practice: `dioxus-primitives` from `DioxusLabs/components`, git-pinned by rev, consuming `Collapsible` with an ARIA `aria-expanded` lifecycle asserted end-to-end (lab ADR 0001; `Cargo.toml:12`). This ADR promotes that proven usage to a named stack element.

## Decision

1. **The standard headless component library is Dioxus Components (`dioxus-primitives`).** It provides unstyled, WAI-ARIA-compliant primitives (Accordion, AlertDialog, Avatar, Button, Checkbox, Collapsible, Dialog, Dropdown/Menu, Tabs, Toast, Tooltip, and the rest of the gallery at `dioxuslabs.github.io/dioxus-components/`). Products compose these primitives rather than hand-rolling accessible components.

2. **Source and pin.** Depend on it **git-pinned by rev**, matching the lab's proven pin `rev = "bf007c15d0cf4d04d3181cc46cf12325aa773955"` (`DioxusLabs/components`), with the `allow-git` exemption in each repo's `deny.toml` (the pattern in `dioxus-app-template/deny.toml`). The crates.io publication status is a **standing follow-up (lab friction F-006)**: verify whether a real (non-`0.0.0`-placeholder) release exists on crates.io; when it does, un-pin to a semver range and drop the git exemption. Until then, git-pin is the sovereign, reproducible default.

3. **Styling is tokens-only.** Primitives ship unstyled by design; all styling comes through Portal tokens (CSS variables / `portal-forge` output), never bundled component styles and never hardcoded literals. This is the same rule `wrench-inspect portal inspect` already enforces (ADR 0033 tokens-only). The library is the _behaviour + accessibility_ layer; Portal is the _appearance_ layer.

4. **Sovereignty.** Dual MIT/Apache-2.0 — permissive, self-hostable, on the forge floor (ADR 0034 / sovereign-stack). No AGPL/SSPL, no SaaS coupling.

5. **First application: `rumble-ai-benchmark`.** Per Constantin, the first Rumble product to apply the library is `rumble-ai-benchmark` — a bounded, already-shipped static benchmark site, chosen as the low-risk proving ground before the pattern reaches the larger products (`rumble-lm` UI alignment, `rumble-cos` rebuild). Its plan lives in `rumble-ai-benchmark/docs/plans/`.

## Consequences

- target-version bumps to **1.1.0**: the elected stack gains a named `component_library`.
- lm's UI-alignment plan and the cos rebuild plan already assume Primitives; they now cite this ADR as the authority.
- `rumble-ai-benchmark` enters the governed set for this work (it was previously out of scope as a finished artifact); it gets a maturity claim and a rebuild plan.
- The crates.io un-pin is tracked as a demand-driven follow-up, not a blocker.
