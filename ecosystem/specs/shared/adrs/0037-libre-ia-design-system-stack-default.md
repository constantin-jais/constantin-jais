# ADR 0037 — Libre IA Design System 2.0 as the stack-wide visual contract

Status: Accepted
Date: 2026-07-10
Decision owner: Constantin Jais
Supersedes: product-local visual directions that conflict with the Libre IA palette
Related: ADR 0024 (Portal), ADR 0036 (Dioxus Components)

## Context

The completed Libre IA identity provides canonical brand assets, DTCG tokens,
typography, motion and component-state contracts. Existing products still carry
independent blue, amber, violet, red and shadow-based themes. Copying the new
CSS into each product would preserve that drift and bypass Portal.

## Decision

Libre IA Design System 2.0 is the default visual contract for every active and
future ecosystem client surface.

```text
Libre IA DTCG source
→ portal-forge compilation and WCAG report
→ Portal web/native artefacts
→ Rumble products and visible factory reports
```

Rules:

1. The only accent is Vert Libre (`#22C55E`). Product verdicts and statuses are
   expressed through icon, label, structure and copy, never a new accent.
2. Web surfaces use self-hosted Inter and Plus Jakarta Sans, Portal tokens and
   Dioxus Components for headless WAI-ARIA behaviour where appropriate.
3. Product-specific components and workflows remain owned by Rumble; their
   appearance consumes the shared semantic token contract.
4. `portal-forge` compiles and validates but does not become the authoring UI or
   runtime token host.
5. Every generated bundle carries the Design System version and SHA-256
   manifest. Runtime network retrieval is forbidden.
6. Raw benchmark outputs remain immutable evidence. Their public wrapper may
   adopt Libre IA without rewriting the compared artefacts.
7. CLI-only repositories receive no decorative UI. Any user-facing HTML report
   must consume the same Portal artefacts.

## Migration

Delivery is incremental under green per-repository gates even though the target
is global: foundation → template/lab/inspection → active Rumble clients → native
adapter proofs → future products by construction.

Compatibility bridges are temporary and must not retain fallback color
literals. A migrated surface has no unapproved hardcoded visual values outside
canonical token, font and asset files.

## Acceptance criteria

- all active client surfaces declare Design System 2.0 and its checksum;
- Portal Forge emits CSS, Swift and Kotlin from the canonical DTCG source;
- declared text pairs pass WCAG AA and visible focus passes on light and dark;
- no remote fonts, mandatory SaaS, gradient, glow or realistic shadow;
- 320/768/1440, keyboard and reduced-motion checks pass for product surfaces;
- previous product-local visual directions are removed or explicitly waived.
