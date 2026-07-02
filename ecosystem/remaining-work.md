# Remaining Work Toward the Target Stack

This file persists the target backlog for the Rumble / Portal / Bolt / Wrench / Gear stack. It is intentionally strategic: product repos own detailed implementation plans, while this file tracks cross-layer completion.

## Target definition of done

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

## P0 — Control plane and naming

- Keep `overview.md`, `status.md`, `loop.md`, and shared decisions aligned on Rumble / Portal / Bolt / Wrench / Gear.
- Keep `gear-loader` as the canonical ingestion name in specs, fixtures, schemas, prompts, and product docs.
- Keep `rumble-lm-ui` as the Rumble LM local UI crate; shared UI/client-platform ownership remains Portal.
- Maintain the stack-wide maturity schema `stack.project_maturity.v0.1` and claims in `ecosystem/maturity/stack/`.
- Keep contract validation green after every rename or schema movement.

## P0b — Stack validation and local-only gates

- Maintain the accepted stack decision matrix: Rust service GO, Astro static publication GO, PostgreSQL/SQLx and Biscuit/OIDC conditional GO, DB security gate GO, Dioxus/PWA and RAG as local spikes, Redis/native shells waiting for proven need, paid provisioning NO-GO.
- Keep the implemented P0 agentic tools aligned with the spec: `project_status`, `stack_detect`, `stack_scorecard`, `dependency_audit`, and `local_smoke`.
- Keep later tools explicitly scoped: `db_security_check` only when PostgreSQL is active, `adr_generate` for accepted decisions, and `deploy_dry_run` without resource creation.
- Reject `setup_everything`, automatic cloud provisioning, real deploy automation, and SaaS integrations requiring API keys until a separate human-approved ADR exists.
- Use ADR-0024 (`specs/shared/adrs/0024-stack-validation-local-only.md`) as the accepted local-only stack validation authority.
- Use ADR-0025 (`specs/shared/adrs/0025-agentic-p0-tooling-backlog.md`) and `specs/harness/04-stack-validation-tooling.md` as the P0 tooling spec before implementation.
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

- Harden planning-only handoffs, structured refusals, idempotency, evidence refs, and audit events.
- Add human approval gates before trusted execution.
- Add harness scenarios for Portal build, Gear Loader hostile source, Wrench evidence refusal, Gear artifact proof, and Rumble handoff.
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
