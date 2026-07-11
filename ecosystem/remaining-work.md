# Remaining Work Toward the Target Stack

This file persists the target backlog for the Rumble / Portal / Bolt / Wrench / Gear stack. It is intentionally strategic: product repos own detailed implementation plans, while this file tracks cross-layer completion.

## Target definition of done

> **MET on 2026-07-09 by `rumble-lm`** (first full traversal, every link CI-gated):
> Portal tokens wrench-verified in CI · gear-loader real ingestion (contract-validated, hostile-content hardened) · SourceRefs in gear-memory (provenance + irreversible anonymization, pinned git dep) · depot-conformant ArtifactManifest emitted in CI (real sha256) · cable→depot E2E proven byte-identical (gear-cable #11/#12/#13, gear-depot #9) · Wrench evidence gate (lm #66) · planning-only Bolt handoff dry-run-validated by cos-matic, 10/10 gates (lm #69) · explained publicly in the cos corpus (`projets/corpus-dod-traversal`, fact-checked #27).

A stack slice is complete when one real Rumble product:

```text
Rumble product
→ uses Portal for web/native UI primitives and tokens
→ consumes Gear Loader for canonical ingestion when sources are needed
→ stores source refs/provenance in Gear Memory
→ exports at least one ArtifactRef/ArtifactManifest through Gear Depot
→ can be packaged through Gear Cable when distribution is needed
→ passes Wrench inspection evidence, plus Wrench DB Inspect if SQL-backed
→ can emit a planning-only Bolt handoff with evidence refs
→ is explained publicly or privately through Rumble Cos / learning notes
```

## 2026-07 wave — plan index (Phase C)

Plans authored against the frozen `target-version` 1.0.0, adversarially verified, planning-only until merged. Dependency-ordered. Status column updated by the 2026-07-09 hygiene audit (`ecosystem/reviews/hygiene-audit-2026-07-09.md`):

| Rank | Chantier                                                                    | Plan (repo-relative)                                                                                    | Status (2026-07-09)                                                                                                                |
| ---- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1a   | lm session API contract freeze (first increment of the runtime plan)        | `rumble-lm/docs/plans/2026-07-lm-session-runtime.md`                                                    | Delivered (I1, #45)                                                                                                                |
| 1b   | Governance full onboarding + maturity/stack + root hygiene                  | `constantin-jais/ecosystem/plans/2026-07-governance-wave.md`                                            | Partial — root hygiene done via DC-5 (2 deletions pending a manual `!`), 23 repos in policy                                        |
| 1b   | wrench-inspect hygiene (LICENSE, injectable dates, Bolt path)               | `wrench-inspect/docs/plans/2026-07-wrench-inspect-hygiene.md`                                           | **Completed** (I1-I3)                                                                                                              |
| 1b   | gear-loader hardening (find_any fix, structural validation)                 | `gear-loader/docs/plans/2026-07-gear-loader-hardening.md`                                               | I1 delivered (#4); I2 validation + I3 hardening remaining                                                                          |
| 1b   | portal-core hardening + theme/a11y contracts                                | `portal-core/docs/plans/2026-07-portal-core-hardening-and-thicken.md`                                   | I1 delivered (#2); I2-I4 remaining                                                                                                 |
| 2a   | lm session runtime                                                          | `rumble-lm/docs/plans/2026-07-lm-session-runtime.md`                                                    | **Completed** (I1-I2, I4-I6 merged; I3 superseded by the inline biscuit-auth v6 implementation — statuses reconciled in lm#71)     |
| 2a   | lm UI lab alignment + DoD slice (proof spine)                               | `rumble-lm/docs/plans/2026-07-lm-ui-lab-alignment-and-dod-slice.md`                                     | I3-I4 delivered by the DoD-chain wave (#65/#68, #66/#69); I1 (Dioxus Primitives) + I2 (tracing gate) in flight (W16)               |
| 2b   | cos rebuild on Dioxus SSG (+ cos-matic dogfooding pilot)                    | `rumble-libre-ia/docs/plans/2026-07-cos-rebuild-dioxus-ssg.md`                                               | I1-I8 delivered (#29/#30/#31; I7-bis gate fix in flight); I9-I11 + I12-prep in flight (W15); I13-I14 gated on the Clever Cloud account change     |
| 2c   | canvas MVP on workspace-identity (D11 implementation #1)                    | `rumble-canvas/docs/plans/2026-07-canvas-mvp-workspace-identity.md`                                     | **Completed** (I1-I4; #14/#15 + #16 rewired wrench checks to the real `handoff inspect` CLI and made the CI gate non-decorative)   |
| 2d   | feed-mind cleanup + RustSec waivers (external deadline 2026-09-30)          | `rumble-feed-mind/docs/plans/2026-07-feed-mind-cleanup-and-waivers.md`                                  | **Completed** (I1-I7); stripe waivers confirmed still CI-required; reviews 2026-08-31                                              |
| 3    | ai-practices convergence prep (frozen shim, scoring module)                 | `rumble-ai-practices/docs/plans/2026-07-ai-practices-convergence-prep.md`                               | In flight (W16, arbitrated 2026-07-10): prototypes #9/#10 proven green then merged; convergence-prep I1-I6 execution approved      |
| 3    | cos-matic real Biscuit + engine tag                                         | `bolt-cos-matic/docs/plans/2026-07-cos-matic-biscuit-and-tag.md`                                        | Not started; crypto majors landed green; octocrab migration increment added (#75 red)                                              |
| 4    | cable↔depot E2E                                                             | `gear-cable/docs/plans/2026-07-cable-depot-e2e.md` + `gear-depot/docs/plans/2026-07-depot-cable-e2e.md` | **Completed 2026-07-09** — cable I1/I2/I3 (#11/#12/#13) + depot ingest/verify/mirror (#9); manifest contract-aligned byte-for-byte |
| 4    | harness fixtures wired for real                                             | `bolt-harness/docs/plans/2026-07-harness-fixtures-alignment.md`                                         | On hold — overlapping local security-doctrine WIP awaits DC-10                                                                     |
| 5    | wrench-db-inspect strict gates + DB security manifest + RLS/grants/pgvector | `wrench-db-inspect/docs/plans/2026-07-wrench-db-inspect-gates.md`                                       | **New plan** (created 2026-07-09, P3 backlog)                                                                                      |

## P0 — Control plane and naming

- Keep `overview.md`, `status.md`, `loop.md`, and shared decisions aligned on Rumble / Portal / Bolt / Wrench / Gear.
- Keep `gear-loader` as the canonical ingestion name in specs, fixtures, schemas, prompts, and product docs.
- Keep `rumble-lm-ui` as the Rumble LM local UI crate; shared UI/client-platform ownership remains Portal.
- Maintain the stack-wide maturity schema `stack.project_maturity.v0.1` and claims in `ecosystem/maturity/stack/`.
- Keep contract validation green after every rename or schema movement.

## P0b — Stack validation and local-only gates

- Maintain the ratified stack decision matrix (ADR 0032, `target-version.v1.json`): Rust service GO, Dioxus 0.7.9 fullstack/PWA GO (web shell — evidence: `wrench-dioxus-lab`), Dioxus SSG for ecosystem content sites (Astro narrowed to non-ecosystem tooling), PostgreSQL/SQLx and Biscuit/OIDC conditional GO, DB security gate GO, RAG and Dioxus desktop as local spikes, Redis/native shells waiting for proven need, paid provisioning NO-GO.
- Keep the implemented P0 agentic tools aligned with the spec: `project_status`, `stack_detect`, `stack_scorecard`, `dependency_audit`, and `local_smoke`.
- Keep later tools explicitly scoped: `db_security_check` only when PostgreSQL is active, `adr_generate` for accepted decisions, and `deploy_dry_run` without resource creation.
- Reject `setup_everything`, automatic cloud provisioning, real deploy automation, and SaaS integrations requiring API keys until a separate human-approved ADR exists.
- Use ADR-0034 (`specs/shared/adrs/0034-stack-validation-local-only.md`) as the accepted local-only stack validation authority.
- Use ADR-0035 (`specs/shared/adrs/0035-agentic-p0-tooling-backlog.md`) and `specs/harness/04-stack-validation-tooling.md` as the P0 tooling spec before implementation.
- Prepare narrower ADR candidates only when a concrete product slice needs them: stack authority, web boundary, sovereign provider policy, OIDC/Biscuit auth, Portal boundary, RAG citation gate, DB security, and agentic tooling boundaries.
- Run stack-specific `pi -p` sessions only after the local validation target and expected evidence are stated.

## P1 — Portal proof

- `portal-forge`: expand remaining DTCG token support, wrappers, output parity, and keep the Rumble LM token fixture green.
- `portal-core`: define theme, a11y, i18n UI, focus, and binding contracts beyond the current translation bridge.
- `portal-apple`: integrate generated Swift tokens and prove a minimal Rumble shell.
- `portal-android`: commit Gradle wrapper, verify Android SDK/NDK build, integrate generated Kotlin tokens.
- Wrench Inspect: add no-hardcoded-style, token usage, contrast-report, and accessibility evidence checks.

## P2 — Gear source and artifact substrate

- `gear-loader`: harden PDF/Office/HTML/feed/code parsers, fail-closed policy, sandboxing, and hostile-content evidence.
- `gear-memory`: implement GearSourceCandidate → SourceRef ingestion, persistence, indexing, deletion/anonymization, and stale propagation.
- `gear-depot`: finalize ArtifactManifest policy, retention/revocation, signatures/checksums, and report/export artifacts.
- `gear-cable`: connect release plans to Depot manifests and prove at least one reproducible release path.

## P3 — Wrench evidence layer

- `wrench-inspect`: stabilize EvidenceReport, spec completeness, traceability, waiver, privacy/RGPD, sovereignty, browser, and Portal checks.
- `wrench-db-inspect`: resolve clippy debt, add strict CI gate profile, DB security manifest, RLS/grants/migration/pgvector checks.
- Keep Wrench as evidence/validation only; no durable truth and no product-linkable ingestion runtime.

## P4 — Bolt integration

- Planning-only handoffs now derive `wrench_report_passed`, artifact integrity, and human approval checkpoint gates from Wrench evidence refs, local EvidenceReport files, Gear ArtifactManifests, registry-backed `bolt.human_approval.v0.1` contracts, and execution policy; continue hardening structured refusals, idempotency, broader evidence refs, and audit events.
- Promote the local approval key registry contract toward durable publication/audit, then complete Biscuit rights, revocation propagation, and evidence gates before any trusted execution path.
- Add harness scenarios for Portal build, Gear Loader hostile source, and Rumble handoff; Wrench evidence refusal plus Wrench→Gear artifact planning proof have initial fixtures.
- Keep Bolt out of product UX, storage, parser runtime, and artifact registry responsibilities.

## P5 — First product slice

Recommended first candidates:

1. `rumble-ai-practices`: content-governed training product with Rust core + Portal PWA.
2. `rumble-lm`: source-grounded session product with CitationValidation, retention defaults, Gear Loader/Memory, and Portal client.

Acceptance for the first slice:

- Rust core invariants tested.
- Portal tokens/components used; no hardcoded shared styles.
- Gear Loader/Memory used for source flow where applicable.
- Gear Depot artifact/export exists.
- Wrench evidence report exists.
- Bolt planning-only handoff exists or is explicitly not needed.
- Local verification commands are documented and green.

## P6 — Native platform paths

- Use Dioxus/PWA as the fast default path when it is sufficient.
- Promote SwiftUI/Compose through Portal only when a product need, local SDK verification, accessibility checks, and release path are proven.
- Use Gear Cable for App Store / future Play Store release adapter boundaries.
- Do not duplicate product logic in native shells; product core stays Rust-first.
