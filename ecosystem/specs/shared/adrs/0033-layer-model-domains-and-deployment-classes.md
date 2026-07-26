# ADR 0033 — Layer model: domain prefixes, deployment classes, family definitions

Status: Accepted
Date: 2026-07-03
Decision owner: Constantin (ecosystem architecture)
Related: supersedes ADR 0023 (the two colliding 0023 files were physically fused into `0023-layer-classification-and-portal-gear-loader-placement.md` on 2026-07-09, DA-3/DC-7 execution); arbitration DA-3/DA-4 in `ecosystem/architecture-alignment-2026-07.md`; ADR 0024 (Portal design substrate), ADR 0028 (identity ownership)

## Context

Two problems surfaced together. First, a numbering collision: two parallel sessions each authored "ADR 0023" on 2026-07-02 — one establishing classification by client (D15) and the gear-loader rename, the other adding Portal as a first-class layer _and also_ settling gear-loader placement. Their content overlaps; future sessions citing "ADR 0023" get one at random. Second, a definitional gap the alignment recon exposed: the classification rule conflated **domain ownership** with **deployment boundary**. Applied literally, the client test ("can this be linked in a product binary? no → wrench") would exile `bolt-harness` (the factory's own proof bench) to wrench — while existing practice already contradicts the literal rule in the other direction: `portal-forge` is a build-time tool that rightly carries the `portal-` prefix because its _domain_ is Portal.

## Decision

**1. The prefix carries the owning domain.** The families are defined as follows:

- **`rumble-*` — products.** User-facing workflows delivered natively on 6 targets (Web, iOS, Android, macOS, Linux, Windows). Owns UX, product state, domain models, and publication gates. Never owns orchestration, inspection evidence, or substrate.
- **`portal-*` — client platform / design substrate.** Tokens, UI primitives, accessibility and focus conventions, i18n UI, Rust-first bindings and platform adapters. Dual nature (ADR 0024): the products' design substrate AND the agents' UI-production capability (tokens-only rule). Never owns actor/tenant authorization (ADR 0028).
- **`bolt-*` — the factory.** Agent orchestration, planning, handoff evaluation, execution coordination — and the factory's own public proof surfaces (`bolt-harness`). Consumes Wrench evidence and Gear references; never ships in product binaries.
- **`wrench-*` — transverse factory tools.** Development, CI, inspection, security audit, and stack-evaluation tooling serving **two or more domains** (`wrench-inspect`, `wrench-db-inspect`, `wrench-dioxus-lab`). Never shipped in product binaries.
- **`gear-*` — runtime substrate.** Shared services and contracts linkable in product binaries (ingestion, memory, artifacts, distribution). One contract, two clients: product runtimes and agents.
- **Control plane (`constantin-jais/ecosystem`).** Governance: specs, shared contracts, decisions, maturity claims, branch policy. Owns truth, not code.

**2. The deployment class is a declared, CI-gated property — not a naming convention.** Every repo (or crate, for mixed repos like `gear-cable`) declares `deployment_class: product-linkable | factory-only | build-time` in its `maturity/stack/*.json` claim. CI gates enforce the property (e.g. the harness hygiene gate rejects `src/` and crates; linkable claims are backed by build targets such as wasm32 checks). The safety guarantee that the old naming rule tried to carry ("factory code never reaches a product binary") moves to an enforced claim — stronger than a prefix.

**3. `wrench-*` is reserved for transverse tools.** A factory tool serving a single domain keeps its domain prefix with `deployment_class: factory-only`. Test: "who breaks if this repo disappears?" — one family's development loop → that family's prefix; several → wrench.

**4. The client test decides the deployment class, not the prefix.** "Can this code be linked into a product binary?" → `product-linkable` (gear and portal runtime artifacts) vs `factory-only` / `build-time`.

**5. Documented naming exceptions.** `dioxus-app-template` keeps its neutral public name: the name is a public interface (cloned by third parties); its classification is transverse `build-time`.

**6. Applications ratified now.** `bolt-harness` stays `bolt-` (`factory-only`). `dioxus-lab` renames to `wrench-dioxus-lab` (transverse evaluation lab — its README already claims the name; GitHub repo, local directory, and `branch-policy.json` key follow). `gear-loader` stays `gear-` (`product-linkable`; its `wrench.*` contract prefixes remain intentional per its own ADR 0002). `portal-forge` stays `portal-` (`build-time`).

## Consequences

- Both ADR 0023 files are marked **Superseded by ADR 0033**; their content is merged here. Prose references to "ADR 0023" in the decision log remain historically valid.
- The sibling numbering collisions are repaired in the same PR: `0024-stack-validation-local-only` → **0034**, `0025-agentic-p0-tooling-backlog` → **0035**, with all references updated. (`0024-portal-family-as-design-substrate` and `0025-canvas-reference-ingestion-security` keep their numbers.)
- A **CI uniqueness gate** on ADR number prefixes (ignoring `Superseded` files) is added to the spec-contracts workflow, so the collision class cannot recur silently. The ADR 0003 gap in the shared series is accepted as historical (numbers are never reused).

> Historical note (2026-07-09, DC-7): the gate as built does **not** ignore `Superseded` files — it rejects duplicate numbers across **all** ADR files. Exempting superseded ADRs is what let two `0023` files coexist for a week, the very collision this ADR was written to repair, so DC-7 widened the gate when it executed the repair (`.github/workflows/spec-contracts.yml`, step "ADR number uniqueness"). DC-7 is dated after this ADR, is `Accepted` in the decision log, and is recorded as executed in `ecosystem/reviews/hygiene-audit-2026-07-09.md` ("gate unicité étendue à TOUS les fichiers ADR"). **DC-7 and the implementation prevail; the parenthesis above is stale prose, not a live rule.** Recorded rather than edited away: the decision log is a living register, so a superseded statement carries its status instead of disappearing.

- `maturity/stack/*.json` claims gain the `deployment_class` field as they are (re)generated (M7 of the alignment document).
