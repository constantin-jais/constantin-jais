# Ecosystem Status Cockpit

Status date: 2026-07-03
Purpose: one human/agent-readable cockpit for the Rumble / Portal / Bolt / Wrench / Gear stack.

This ecosystem is not prioritized as a startup portfolio. It is a personal process ecosystem for learning, trustworthy workflows, sovereign tooling, and high-quality agent-readable systems.

Build notes are written only when a concrete artifact creates useful public learning; see [`build-notes.md`](build-notes.md).

The process is the product:

```text
idea → specification → inspection → planning → controlled execution → evidence → memory → improvement
```

The accepted full target version lives in [`target-version.md`](target-version.md) / [`target-version.v1.json`](target-version.v1.json). The persisted cross-layer backlog lives in [`remaining-work.md`](remaining-work.md). Public repository cleanup is tracked in [`repos-inventory.md`](repos-inventory.md).

Rumble projects are dojos: they create real constraints and product-shaped pressure. Portal, Bolt, Wrench, and Gear are the reusable process core for clients, orchestration, inspection, and substrate work.

## Maturity vocabulary

Delivery maturity is now a harness contract too: see `specs/harness/03-rumble-delivery-maturity.md` and `specs/harness/rumble-delivery-maturity.v0.1.schema.json`.

Real current Rumble delivery claims live in `maturity/*.json`. Stack-layer claims for Portal/Bolt/Wrench/Gear live in `maturity/stack/*.json` and are validated by the same spec-contract workflow. Rumble claims are also checked with:

```bash
cosmatic maturity report ecosystem/maturity
```

| Status | Meaning |
| --- | --- |
| `speculative` | Idea or exploration, not stable yet. |
| `contract-first` | Contracts, domain model, specs, or fixtures exist; runtime is limited or absent. |
| `dojo` | Active experimentation surface that intentionally generates constraints for the stack. |
| `usable` | Locally usable for a real workflow with documented commands. |
| `trusted` | Tested, documented, gated, reproducible, and safe enough to rely on routinely. |
| `retired` | Archived, replaced, or intentionally stopped. |

Sub-statuses describe the current increment, not the whole project:

```text
P0 contract · P1 CLI proof · P2 local persistence · P3 inspection integrated
P4 orchestration integrated · P5 minimal UI · P6 reproducible release
```

Scale readiness is a separate attribute, never a maturity status:

| Scale-ready value | Meaning |
| --- | --- |
| `no` | Not ready for broader multi-user or production-like use. Missing hardening, observability, security, release, or operational proof. |
| `partially` | A bounded surface is usable beyond a stub, but important scale caveats remain documented. |
| `yes, with evidence` | Multi-user or production-like operation is backed by explicit evidence: tests/gates, observability, security hardening, deployment/release path, and documented limits. |

## Promotion criteria

### `speculative` → `contract-first`

- Problem statement exists.
- Intended users are identified.
- Boundaries and non-goals are written down.
- First contracts, specs, fixtures, or domain model are drafted.

### `contract-first` → `dojo`

- Contracts/specs are versioned or linked from the ecosystem cockpit.
- Fixtures, examples, or schemas exist.
- At least one local command, stub, or validation path exists.
- Current limitations are documented.
- The project creates useful constraints for Rumble/Portal/Bolt/Wrench/Gear instead of only describing ambition.

### `dojo` → `usable`

- A documented quickstart exists.
- CI passes for the relevant stack.
- At least one real local workflow works end-to-end.
- Outputs are understandable by a human.
- Known limitations are documented.
- No hidden mandatory secrets are required for basic use.

### `usable` → `trusted`

- CI + security gates pass.
- Domain fixtures, snapshots, or product smoke tests exist.
- Release or installation path is repeatable when the project distributes artifacts.
- Behavior and failure modes are documented.
- The project is used routinely without manual repair.
- Advisories and waivers are either resolved or explicitly time-bound with owner and removal plan.

### `trusted` → `scale-ready` attribute

`scale-ready` is not a maturity status. It can only be claimed when:

- deployment path is documented;
- observability exists;
- auth/security boundaries are explicit;
- persistence, backup, and retention are defined where relevant;
- multi-user or production constraints are tested;
- operational runbook exists;
- incident and rollback paths exist.

Rumble delivery levels describe long-term product maturity:

```text
R0 spec · R1 contract · R2 portable-core · R3 local-workflow · R4 service-api
R5 web-ui · R6 desktop · R7 mobile · R8 sync-offline · R9 reproducible-release · R10 commercializable
```

## Project cockpit

| Project | Layer | Learning role | Maturity | Current increment | Status / next quality step |
| --- | --- | --- | --- | --- | --- |
| `rumble-canvas` | Rumble | Specification, ambiguity, decisions, traceability, handoff. | `contract-first` | P0 contract | Public repo has hygiene + Rust quality gates. Next: full `SpecPackage` schema and Wrench completeness checks. |
| `rumble-feed-mind` | Rumble | Watch pipeline, feed curation, rules, BYOK, export/handoff. | `dojo` | P0 contract + P1 Rust proof | Dedicated `contracts.yml` proves fixture-based `CuratedItemExport`; `demo-curate-live` exists for manual feed checks. Next: adversarial log audit, advisory waiver removal, Wrench/Gear integration. |
| `rumble-lm` | Rumble | Pedagogy, citations, live sessions, grounding, aggregate analytics. | `contract-first` | P0 contract stub | Core/server stub validates boundaries. Next: `CitationValidation`, retention defaults, provider policy instantiation. |
| `rumble-note` | Rumble | Local-first PKM, private blocks, personal memory exports. | `contract-first` | P0 specs | Public placeholder repo is governed by hygiene checks; runtime not present locally. Next: minimal block model and `NoteContextExport` privacy contract. |
| `rumble-crew` | Rumble | Human/agent tasks, approvals, evidence, run recovery. | `contract-first` | P0 specs | Public placeholder repo is governed by hygiene checks. Next: `AgentTaskRequest` lifecycle and human approval policy. |
| `rumble-cos` | Rumble | Transmission, clarity, public explanation, documentation publishing. | `usable` | P5 minimal UI | Public Astro static site is usable, protected, and audit/check gates are green. Next: Dioxus SSG rebuild (ADR 0032 §3, DA-2a) — the 221-item corpus is the migration asset. |
| `portal-forge` | Portal | Design tokens, WCAG checks, cross-platform UI artifact generation. | `dojo` | P1 CLI/library proof | Token compiler emits CSS/Swift/Kotlin, semantic token types, and `portal.contrast_report.v0.1`; Rumble LM has a generated token fixture. Next: Portal Core a11y/theme + Wrench checks. |
| `portal-core` | Portal | Rust-first UI/client contracts, i18n UI, accessibility helpers, native bindings. | `contract-first` | P0 bridge proof | UniFFI-backed translation core exists. Next: theme/a11y contracts and generated binding fixtures consumed by Apple/Android. |
| `portal-apple` | Portal | SwiftUI adapter for Portal core/tokens. | `contract-first` | P0 native bridge proof | `swift test` verifies the core bridge. Next: integrate `portal-forge` Swift output and define Rumble shell fixture. |
| `portal-android` | Portal | Jetpack Compose adapter for Portal core/tokens. | `speculative` | P0 partial bridge | Kotlin bindings and native lib flow are sketched, but Gradle/Android SDK assembly is not fully verified. Next: committed wrapper + local SDK/NDK proof. |
| `bolt-harness` | Bolt | Public harness execution/governance surface. | `contract-first` | P0 hygiene | Public repo has `Harness hygiene` protection. Next: keep live sandbox fenced and evidence-producing. |
| `bolt-cos-matic` | Bolt | Deterministic orchestration, gates, plans, safe writes, evidence. | `usable` | P4 approval key registry + Wrench/Gear evidence proof | Renamed from `cos-matic`; local harness and tests pass, `handoff plan` can project Wrench EvidenceReport files, Gear ArtifactManifests, or registry-backed Ed25519 `bolt.human_approval.v0.1` contracts into hash-backed refs/gates; unknown/revoked/expired approval keys are refused. Next: Biscuit, audit, durable registry publication, and evidence gates before trusted execution. |
| `wrench-inspect` | Wrench | General critique, policy/design/spec inspection, evidence reports. | `speculative` | P0 placement | No local repo yet; capability is intentionally kept as a Wrench owner in shared registry. Next: evidence report model before repo split. |
| `wrench-db-inspect` | Wrench | Database security gates, RLS/grants/migration/pgvector evidence. | `dojo` | P1 CLI proof | Specialized DB inspector exists. Next: address clippy debt in the current codebase and decide integration as CI gate. |
| `gear-loader` | Gear | Runtime-capable ingestion, canonical extraction, hostile-content evidence. | `dojo` | P1 CLI proof | Reclassified from the former Wrench Loader placement; CLI/contracts/fixtures exist. Next: parser hardening for PDF/Office/feed/code under license/security/sandbox gates. |
| `gear-memory` | Gear | Source refs, memory entries, code maps, event log, provenance. | `contract-first` | P0 contract | Contracts/tests exist. Next: local persistence/indexing proof and Note/Loader integration. |
| `gear-depot` | Gear | Artifact manifests, supply-chain policy, provenance, safe metadata. | `contract-first` | P0 contract | Contracts/tests exist. Next: storage/cache policy and integration with spec/handoff artifacts. |
| `gear-cable` | Gear | Reproducible release, checksums, distribution wiring. | `contract-first` | P1 CLI/library proof | Release substrate skeleton and tests exist. Next: connect release plans to Depot manifests. |

## Current stack challenge decisions

References: [`specs/shared/adrs/0034-stack-validation-local-only.md`](specs/shared/adrs/0034-stack-validation-local-only.md), [`specs/shared/adrs/0035-agentic-p0-tooling-backlog.md`](specs/shared/adrs/0035-agentic-p0-tooling-backlog.md), [`specs/harness/04-stack-validation-tooling.md`](specs/harness/04-stack-validation-tooling.md).

| Stack / tool track | Decision | Next evidence |
| --- | --- | --- |
| Rust service: Tokio, Axum, SQLx-ready, tracing | GO | Local workspace skeleton or existing repo scorecard with fmt, clippy, tests, deny/audit. |
| PostgreSQL + SQLx | Conditional GO | Activate only when durable persistence is required; add migrations, local DB fixtures, and Wrench DB evidence. |
| OIDC/Keycloak + Biscuit | Conditional GO | Activate for organizational or multi-tenant rights; require allow/deny policy fixtures and no token/PII logging. |
| Redis / persisted queues | WAIT | Add only when critical jobs, fanout, or retry durability are proven by a product slice. |
| Dioxus/PWA + Portal | GO (ADR 0032) | Spike delivered: `wrench-dioxus-lab` ADR 0001 — wasm 386 KiB gzip, 4-engine e2e, HttpOnly session, a11y/token gates. Next: first product alignment (rumble-lm slice). |
| SwiftUI / Compose via Portal | WAIT | Promote only after PWA proof plus native product need, SDK verification, and Portal binding evidence. |
| RAG / pgvector / citation-gated generation | SPIKE LOCAL STRICT | Use fixtures first; prove citation validation, redaction, retention policy, and provider-free local checks. |
| Astro/MDX/Bun static publication | NARROWED (ADR 0032 §3) | Permitted outside ecosystem products; ecosystem products publish via Dioxus SSG — `rumble-cos` rebuilds accordingly (DA-2a). |
| DB security / RLS / grants / pgvector | GO as gate | Use sanitized SQL fixtures and `wrench-db-inspect` before protected branches or releases. |
| Agentic P0 tools | GO progressive | Harden and dogfood implemented P0 helpers: `project_status`, `stack_detect`, `stack_scorecard`, `dependency_audit`, `local_smoke`; keep dry-run/local-only defaults. |
| Paid infrastructure, provisioning, live providers | NO-GO | Remain recommendation/dry-run/config examples until explicit human approval. |

## Ownership and anti-duplication policy

- `constantin-jais/ecosystem/status.md` owns current cross-project status.
- `constantin-jais/ecosystem/overview.md` owns stable doctrine and layer boundaries.
- `constantin-jais/ecosystem/loop.md` owns the target self-improving process loop.
- `constantin-jais/ecosystem/specs/shared/` owns shared contracts, decisions, open questions, and reusable capability candidates.
- Repository READMEs own only local usage, local boundary, and local commands; they should link to ecosystem truth instead of copying it.
- ADRs in project repos own repo-local decisions only.

## Verification commands by project

| Project | Commands |
| --- | --- |
| `constantin-jais` | `bash ecosystem/specs/ci-validate-contracts.sh`; `python3 ecosystem/specs/validate_spec_schemas.py`; `python3 ecosystem/specs/harness/run_vertical_p0.py --output ecosystem/specs/harness/proofs/vertical-p0.proof.json`; `cosmatic maturity report ecosystem/maturity` |
| `bolt-cos-matic` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `bolt-harness` | `python3 scripts/harness_hygiene.py` when present; otherwise GitHub `Harness hygiene` workflow |
| `gear-cable` | `cargo test --workspace --all-targets` |
| `gear-depot` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `gear-memory` | `cargo test --workspace --all-targets` |
| `gear-loader` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `portal-forge` | `cargo test` |
| `portal-core` | `cargo test` |
| `portal-apple` | `./scripts/build-core.sh`; `swift test` |
| `portal-android` | `./scripts/build-core.sh`; `./gradlew :library:assemble` once Gradle wrapper + Android SDK/NDK are verified |
| `rumble-canvas` | `cargo fmt --all --check`; `cargo check --workspace --all-targets`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `rumble-cos` | `npm run check`; `npm run build`; `npm audit --audit-level=moderate`; `npm run test -- --project=chromium` |
| `rumble-crew` | GitHub `Repository hygiene` workflow |
| `rumble-feed-mind` | `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features -- -D warnings`; `cargo test --workspace`; `cargo run -p feedmind-cli -- demo-curate --opml examples/demo.opml --article examples/demo-article.json --rule examples/demo-rule.json --output out/curated.json`; `cargo run -p feedmind-cli -- validate-curated-export --file out/curated.json`; `diff -u examples/expected-curated-export.json out/curated.json` |
| `rumble-lm` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `rumble-note` | GitHub `Repository hygiene` workflow |
| `wrench-db-inspect` | `cargo test --workspace --all-targets`; prototype: `cd constantin-jais/ecosystem/prototypes/wrench-db-inspect && cargo test` |

## Current quality caveats

- `rumble-cos` uses an npm override (`yaml@2.9.0`) to keep `npm audit --audit-level=moderate` green without `npm audit fix --force`.
- `wrench-db-inspect` current codebase has known clippy warnings when run with `-D warnings`; tests are green.
- Rumble specs should not imply runtime maturity when only contracts/fixtures exist.
- Provider/BYOK, delegated auth, evidence storage, and retention policies must remain explicit before trusted status.
