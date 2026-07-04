# Cold Backlog — triggered & deferred chantiers

Purpose: a single, thin index of the forge's big chantiers so nothing is lost between waves and a lighter model can pick up "what is ripe to execute now". This is **pointers, not plans**: each row names the chantier, its real state, the trigger/blocker that gates it, and a stable anchor (ADR/contract/spec). A detailed `forge.plan.v0.1` is written **at execution time against fresh state**, never stockpiled here (a fat plan rots as the code moves; a pointer does not).

Discipline (per the 2026-07-04 method arbitration):

- **Anchor to an ADR/contract, not to line numbers.** Volatile references are banned.
- **The trigger is the freshness gate.** Before executing a cold row, re-read `git log` + real state (agent-behavior §1); the row is a claim about the past.
- **Hot ≠ cold.** Hot chantiers live in `remaining-work.md` (the 2026-07 wave plan index). This file holds what is _deliberately deferred behind a trigger_, plus the cross-layer status snapshot so triage has one entry point.
- Prune rows when done or superseded.

State legend: **done** · **partial** · **stub** (specs/contracts only) · **not-started** · **cold** (deferred by design, trigger written).

## Triggered — deferred by design, trigger written

| Chantier                                             | Layer       | State       | Trigger to execute                                                                                                                   | Anchor                                                                        |
| ---------------------------------------------------- | ----------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| DNS-pinning SSRF transport (odysseus E10)            | gear/wrench | cold        | First gear-loader increment that enables `NetworkPolicy::SingleUrl`/`BoundedCrawl` (defaults `Disabled` today)                       | `odysseus-decomposition.md` E10; ADR 0015                                     |
| Untrusted-context envelope (odysseus E22)            | bolt/cross  | cold        | First forge surface that feeds untrusted text to a model                                                                             | `odysseus-decomposition.md` E22; ADR 0015                                     |
| Fail-closed + allowlist tool gating (odysseus E23)   | bolt        | cold        | cos-matic authorization increment (converges with M2)                                                                                | `odysseus-decomposition.md` E23; ADR 0028                                     |
| Blind-comparison eval method (odysseus E32)          | wrench      | cold        | A wrench-inspect **Eval Lab** exists (it does not — grep eval/blind/compare ∅)                                                       | `odysseus-decomposition.md` E32                                               |
| `rumble-mail` product                                | rumble      | cold        | Product ratification (M1 identity lock closed 2026-07-04)                                                                            | `odysseus-decomposition.md` product cards; `rumble-mail-cal-decomposition.md` |
| `rumble-cal` product                                 | rumble      | cold        | Product ratification; paired with rumble-mail (M1 identity lock closed 2026-07-04)                                                    | `odysseus-decomposition.md` product cards; `rumble-mail-cal-decomposition.md` |
| wrench-inspect Eval Lab                              | wrench      | not-started | An eval is demanded by ≥1 real consumer                                                                                              | codebase-memory E21, meilisearch workloads, odysseus E32                      |
| D10 — dedicated governance repo                      | control     | cold        | After DA-6 governance onboarding completes (all governed repos in `branch-policy.json`, required CI gates active); high blast radius | `architecture-alignment-2026-07.md` (D10); `plans/2026-07-governance-wave.md` |
| Native shells SwiftUI/Compose (portal-apple/android) | portal      | cold        | A product need + local SDK verification + a11y + release path proven (P6)                                                            | ADR 0033; remaining-work P6                                                   |
| cable → App Store / Play Store release adapter       | gear        | cold        | Native distribution becomes active                                                                                                   | remaining-work P6                                                             |

## Cross-layer locks & unlocks (hot-adjacent status snapshot)

Coverage note: **M5** (ratification artifacts) is **done** (target-version 1.1.0, 2026-07-03); **M6** (ingestion hardening) → gear-loader row in "Substrate & factory"; **M8** (governance onboarding) and **M9** (product proof) are partial and tracked in `remaining-work.md` / the product rows below. This table lists the locks not already covered elsewhere.

| M-item / chantier                                | State       | Blocker / next                                                                                                                                       | Anchor                                                |
| ------------------------------------------------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| M1 — workspace-identity contract + schema        | **done**    | Closed 2026-07-04: contract + schema Accepted; Rumble-Canvas #4 emits `tenant_id` and re-syncs its local schema                       | ADR 0028; `workspace-identity.v0.1`; Rumble-Canvas #4 |
| M2 — Biscuit real chain (mint↔verify)            | partial     | cos-matic verify still stub; wire against lm-minted keys after first slice                                                                           | ADR 0029/0036; `delegated-authorization-biscuit.v0.1` |
| M3/M4 — first gear-loader / gear-memory consumer | stub        | lm ingestion/provenance increment                                                                                                                    | remaining-work P2; lm ADR-0003                        |
| M10 — observability (tracing, zero PII)          | not-started | lm `println!` → tracing; ai-practices idem                                                                                                           | alignment M10; axis #1                                |
| M11 — backup automation + RTO/RPO                | partial     | manual snapshots only; weekly job + quantify D13                                                                                                     | alignment M11                                         |
| M12 — dioxus-lab → template sync protocol        | stub        | script or checklist the manual sync                                                                                                                  | alignment M12                                         |
| FORGE_ADMIN_TOKEN PAT                            | not-started | governance drift-check 401s until set                                                                                                                | ADR 0031                                              |
| M7 — maturity/stack coverage + cockpit           | partial     | generate missing `deployment_class` claims                                                                                                           | alignment M7                                          |

## Product verticals (Rumble)

| Product                                    | State      | Next / blocker                                                                          | Anchor                      |
| ------------------------------------------ | ---------- | --------------------------------------------------------------------------------------- | --------------------------- |
| rumble-lm — session runtime + DoD slice    | partial    | runtime fixture-only; **chosen first vertical** (2026-07-04)                            | ADR 0029; remaining-work 2a |
| rumble-ai-practices — corpus + convergence | partial    | corpus 30q DoD, media-bias audit, drop frozen shim at lm convergence                    | remaining-work 3            |
| rumble-canvas — MVP multi-user             | partial    | UI absent; unblocked by M1 (now done)                                                   | remaining-work 2c           |
| rumble-cos — Dioxus SSG rebuild            | partial    | **verified never deployed** (DA-2 §205); clean rebuild, corpus+redirects are the assets | ADR 0032 §3; DA-2a          |
| rumble-feed-mind — RustSec waivers         | partial ⏰ | **4 waivers expire 2026-09-30** (hard external deadline); Leptos skeleton to purge (C7) | remaining-work 2d; ADR 0032 |
| rumble-crew — human/agent tasks            | stub       | specs only (0 LOC); stays contract-first until fixtures ship                            | remaining-work; ADR 0028    |
| rumble-note — local-first PKM              | stub       | specs only (0 LOC); stays contract-first until fixtures ship                            | remaining-work              |

## Substrate & factory

| Chantier                                    | State   | Next / blocker                                                                                      | Anchor                      |
| ------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------- | --------------------------- |
| gear-memory — Stage 0 + RGPD ops            | stub    | erasure/anonymization ops absent (schema has states, zero ops)                                      | remaining-work P2; D12      |
| gear-loader — parser hardening + fetch      | partial | code↔fixture drift; URL fetch absent (lands E10)                                                    | remaining-work P2; ADR 0015 |
| gear-depot — manifests/retention/signatures | stub    | contract-first until a real consumer                                                                | remaining-work P2           |
| gear-cable — release E2E                    | partial | zero real consumer; confine `ASC_PRIVATE_KEY`                                                       | remaining-work P2           |
| bolt-cos-matic — real Biscuit + engine tag  | partial | gates **verified evidence-derived** (not hardcoded, VERIF 2026-07-04); Biscuit verify demand-driven | ADR 0017/0018/0019; D3      |
| bolt-harness — fixtures wired for real      | partial | appear in cockpit §3.2; wire fixtures                                                               | remaining-work P4           |
| wrench-inspect — evidence checks            | partial | implement token/contrast/a11y/RGPD/sovereignty/Portal checks (versioned, 14 tests green)            | remaining-work P3           |
| wrench-db-inspect — extraction + CI gate    | partial | ADR-0004 Accept; strict CI gate profile                                                             | remaining-work P3; D9       |
| portal-forge / portal-core                  | partial | token coverage; theme/a11y/i18n/focus/binding contracts                                             | remaining-work P1           |
