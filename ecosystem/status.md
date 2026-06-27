# Ecosystem Status Cockpit

Status date: 2026-06-30  
Purpose: one human/agent-readable cockpit for the Rumble / Bolt / Wrench / Gear stack.

This ecosystem is not prioritized as a startup portfolio. It is a personal process forge for learning, reliable workflows, sovereign tooling, and high-quality agent-readable systems.

The process is the product:

```text
idea → specification → inspection → planning → controlled execution → evidence → memory → improvement
```

Rumble projects are dojos: they create real constraints and product-shaped pressure. Bolt, Wrench, and Gear are the reusable process core.

## Maturity vocabulary

Delivery maturity is now a harness contract too: see `specs/harness/03-rumble-delivery-maturity.md` and `specs/harness/rumble-delivery-maturity.v0.1.schema.json`.

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

Rumble delivery levels describe long-term product maturity:

```text
R0 spec · R1 contract · R2 portable-core · R3 local-workflow · R4 service-api
R5 web-ui · R6 desktop · R7 mobile · R8 sync-offline · R9 reproducible-release · R10 commercializable
```

## Project cockpit

| Project | Layer | Learning role | Maturity | Current increment | Status / next quality step |
| --- | --- | --- | --- | --- | --- |
| `rumble-canvas` | Rumble | Specification, ambiguity, decisions, traceability, handoff. | `contract-first` | P0 contract | Canonical first harness package path exists in specs/fixtures. Next: full `SpecPackage` schema and Wrench completeness checks. |
| `rumble-feed-mind` | Rumble | Watch pipeline, feed curation, rules, BYOK, export/handoff. | `dojo` | P0 contract + P1 Rust proof | Ready for scoped implementation planning. Next: runtime tests for `CuratedItemExport`, logging classification, advisory waiver removal. |
| `rumble-lm` | Rumble | Pedagogy, citations, live sessions, grounding, aggregate analytics. | `contract-first` | P0 contract stub | Core/server stub validates boundaries. Next: `CitationValidation`, retention defaults, provider policy instantiation. |
| `rumble-note` | Rumble | Local-first PKM, private blocks, personal memory exports. | `contract-first` | P0 specs | Specs exist, runtime not present locally. Next: minimal block model and `NoteContextExport` privacy contract. |
| `rumble-crew` | Rumble | Human/agent tasks, approvals, evidence, run recovery. | `contract-first` | P0 specs | Specs exist, runtime not present locally. Next: `AgentTaskRequest` lifecycle and human approval policy. |
| `rumble-cos` | Rumble | Transmission, clarity, public explanation, documentation publishing. | `usable` | P5 minimal UI | Astro static site is usable. Next: fix Playwright browser install/mobile selector expectations and document ecosystem learnings. |
| `cos-matic` | Bolt | Deterministic orchestration, gates, plans, safe writes, evidence. | `usable` | P4 orchestration integrated | Local harness and tests pass. Next: keep planning/refusal/evidence gates hardened before runtime expansion. |
| `wrench-loader` | Wrench | Ingestion reliability, canonical extraction, hostile-content evidence. | `dojo` | P1 CLI proof | CLI/contracts/fixtures exist. Next: parser hardening for PDF/Office/feed/code under license/security gates. |
| `wrench-inspect` | Wrench | General critique, policy/design/spec inspection, evidence reports. | `speculative` | P0 placement | No local repo yet; capability is intentionally kept as a Wrench owner in shared registry. Next: evidence report model before repo split. |
| `wrench-db-inspect` | Wrench | Database security gates, RLS/grants/migration/pgvector evidence. | `dojo` | P1 CLI proof | Specialized DB inspector exists. Next: address clippy debt in prototype and decide integration as CI gate. |
| `gear-memory` | Gear | Source refs, memory entries, code maps, event log, provenance. | `contract-first` | P0 contract | Contracts/tests exist. Next: local persistence/indexing proof and Note/Loader integration. |
| `gear-depot` | Gear | Artifact manifests, supply-chain policy, provenance, safe metadata. | `contract-first` | P0 contract | Contracts/tests exist. Next: storage/cache policy and integration with spec/handoff artifacts. |
| `gear-cable` | Gear | Reproducible release, checksums, distribution wiring. | `contract-first` | P1 CLI/library proof | Release substrate skeleton and tests exist. Next: connect release plans to Depot manifests. |

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
| `constantin-jais` | `bash ecosystem/specs/ci-validate-contracts.sh`; `python3 ecosystem/specs/validate_spec_schemas.py`; `python3 ecosystem/specs/harness/run_vertical_p0.py --output ecosystem/specs/harness/proofs/vertical-p0.proof.json` |
| `cos-matic` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `gear-cable` | `cargo test --workspace --all-targets` |
| `gear-depot` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `gear-memory` | `cargo test --workspace --all-targets` |
| `rumble-cos` | `bun run check`; `bun run test` after Playwright browsers are installed |
| `rumble-feed-mind` | `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features -- -D warnings`; `cargo test --workspace` |
| `rumble-lm` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |
| `wrench-db-inspect` | `cargo test --workspace --all-targets`; prototype: `cd constantin-jais/ecosystem/prototypes/wrench-db-inspect && cargo test` |
| `wrench-loader` | `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test --workspace --all-targets` |

## Current quality caveats

- `rumble-cos` Playwright e2e is not green in the local environment: Firefox/WebKit browsers need installation, and some mobile tests select hidden desktop controls.
- `wrench-db-inspect` prototype in `constantin-jais` has known clippy warnings when run with `-D warnings`; tests are green.
- Rumble specs should not imply runtime maturity when only contracts/fixtures exist.
- Provider/BYOK, delegated auth, evidence storage, and retention policies must remain explicit before trusted status.
