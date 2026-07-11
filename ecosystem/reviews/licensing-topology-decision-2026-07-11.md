# Licensing and repository topology decision study — 2026-07-11

Status: Proposed  
Scope: public Libre IA ecosystem only; personal repositories are excluded and intentionally not inventoried.  
Decision axes, in order: Security > Quality > Performance > Completeness.  
Legal note: this is an engineering and governance recommendation, not legal advice.

## 1. Executive recommendation

Adopt two coordinated decisions:

1. **License standard:** `MIT OR Apache-2.0` for software, `CC-BY-4.0` for original public editorial/training content, and explicit per-asset licensing for media. Add DCO 1.1, SPDX/REUSE metadata, provenance gates, and a trademark exclusion.
2. **Topology:** selective consolidation by change boundary, not a mega-monorepo and not the 23-repository status quo.

Target after migration: about **13 active public repositories**, plus archived historical/spec artifacts. The target preserves distinct Rumble products while consolidating small same-domain repositories whose changes already need to be atomic.

Do not relicense or move code until rights/provenance are inventoried. Existing MIT grants remain valid for published revisions.

## 2. Evidence snapshot

Observed on the default branches of 23 original public repositories:

- 21 repositories contain runtime source; `rumble-note` and `rumble-crew` contain specifications only.
- About 65.7 kLOC Rust and 105 kLOC total code/configuration, excluding Markdown/MDX and lockfiles.
- Only two internal Git dependencies exist: `rumble-lm` pins `gear-loader` and `gear-memory` by commit.
- `portal-core` is about 128 LOC; the four Portal repositories total about 2.6 kLOC but require cross-repository scripts and CI.
- `wrench-dioxus-lab` and `dioxus-app-template` contain 21 byte-identical files (about 160 KB), including most application source.
- The control plane still contains an extracted `wrench-db-inspect` prototype of about 2.4 kLOC Rust alongside the dedicated repository.
- Feed parsing exists in both `gear-loader` and `rumble-feed-mind`, despite ADR 0016 assigning deterministic parsing to Gear Loader.
- `rumble-ai-practices` contains its own API/session/store/UI runtime although ADR 0029 assigns the session runtime to `rumble-lm`.
- `rumble-ai-practices` documents a provenance model, but none of the 33 inspected content files currently declares `provenance` or `license` metadata.
- `rumble-cos` contains 223 content files and 48 media files without file-level licence/provenance metadata.

Interpretation: repository count currently overstates executable modularity and understates synchronization cost.

## 3. Licensing scenarios

Scoring is directional, from 1 (weak) to 5 (strong). Weighted score uses adoption 20%, enterprise clarity 20%, patent protection 15%, commercial defensibility 10%, migration simplicity 15%, doctrine fit 20%.

| Scenario | Adoption | Enterprise | Patents | Commercial defence | Migration | Doctrine | Weighted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L0 — MIT software + split content only | 5 | 4 | 1 | 1 | 5 | 4 | 72/100 |
| **L1 — MIT OR Apache-2.0 + CC BY + asset ledger** | **5** | **5** | **4** | 1 | **4** | **5** | **86/100** |
| L2 — Apache-2.0 only + CC BY | 4 | 5 | 5 | 1 | 3 | 5 | 82/100 |
| L3 — permissive infrastructure + MPL-2.0 products | 3 | 4 | 4 | 3 | 2 | 4 | 68/100 |
| L4 — GPL/commercial dual licensing | 2 | 2 | 4 | 5 | 1 | 1 | 45/100 |

### Recommendation: L1

`MIT OR Apache-2.0` is the least disruptive standard for the Rust-heavy ecosystem:

- preserves the existing permissive posture;
- adds an explicit patent grant for recipients choosing Apache-2.0;
- matches common Rust ecosystem practice;
- remains enterprise-friendly and self-hostable;
- avoids the contribution and adoption friction of strong copyleft.

It does **not** create a commercial moat. Monetization should rely on training, support, integration, trusted releases, hosted operation where appropriate, and brand—not on restricting the public core.

MPL-2.0 remains acceptable for a future component that has a demonstrated need for file-level reciprocity. It should not be introduced portfolio-wide: it does not close the SaaS loophole and previously published MIT revisions remain usable.

AGPL, SSPL/BUSL and proprietary default licensing are rejected for this ecosystem. `BSL-1.0` in SPDX means the permissive Boost Software License; Business Source License is normally `BUSL-1.1` and must not be conflated with it.

## 4. Target licence matrix

| Asset class | Target licence | Repositories / paths | Notes |
| --- | --- | --- | --- |
| Rust/TS/JS/Python/Swift/Kotlin code | `MIT OR Apache-2.0` | all active software | Cargo/package metadata and source headers must agree |
| JSON schemas and machine contracts | `MIT OR Apache-2.0` | control plane and contract fixtures | optimized for implementation reuse |
| Technical README/ADR tightly coupled to code | same as software | software repositories | avoids unnecessary file-level complexity |
| Original essays, courses and public pedagogy | `CC-BY-4.0` | `rumble-cos` content | open reuse with attribution |
| Training corpus, questions and explanations | `CC-BY-4.0` | `rumble-ai-practices/content` | source citation is separate from redistribution rights |
| Benchmark prompt, rubric and methodology | `CC-BY-4.0` | `rumble-ai-benchmark` documents | generated outputs need an additional provenance notice |
| Images, audio, video, fonts | per asset | all `media/`, `public/`, `assets/` trees | no default relicensing without a rights record |
| Logos and family names | rights reserved via `TRADEMARKS.md` | ecosystem-wide | OSS licence must not imply trademark permission |

If commercial exclusivity is desired for a future course, create a clearly separated content collection under its own terms before publication. Do not silently change the licence of existing CC/MIT material.

## 5. Governance required by Option A

### 5.1 Licence layout

Use SPDX/REUSE-compatible files:

```text
LICENSES/
  Apache-2.0.txt
  MIT.txt
  CC-BY-4.0.txt
LICENSE          # concise licensing map, not concatenated full licences
REUSE.toml       # path-level annotations where headers are impractical
DCO.txt
TRADEMARKS.md
CONTRIBUTING.md
```

For software packages:

```toml
license = "MIT OR Apache-2.0"
```

`wrench-inspect` is the immediate correction: replace the concatenated MIT+Apache file with an explicit `OR` declaration and separate canonical licence texts.

### 5.2 Contributions

Adopt **DCO 1.1**, with `Signed-off-by` required for future non-bot commits. Use a small repository-owned CI check rather than depending on a proprietary DCO service.

DCO is recommended over a CLA because the current north star is open collaboration, not proprietary relicensing. If commercial dual licensing later becomes a real objective, contributor consent or an appropriate CLA will be required before accepting affected contributions.

### 5.3 Provenance

Every publishable content/media record should minimally carry:

```yaml
rights:
  origin: original | derived | third-party | generated
  rights_holder: stable-id
  license_spdx: CC-BY-4.0
  source_url: optional
  source_accessed_at: optional
  ai_assistance: none | draft | rewrite | review | generation
  review_status: draft | approved | blocked | retired
```

Required gates:

- fail if a public media asset lacks a licence/rights entry;
- fail if a third-party source is treated as redistributable merely because it is cited;
- fail if generated output claims exclusive human authorship without a provenance notice;
- never store reviewer PII, prompts containing secrets, or private source excerpts in public provenance.

## 6. Repository topology scenarios

Weighted score uses security/isolation 25%, quality/coherence 20%, maintenance 20%, integration completeness 15%, reversibility 10%, discoverability 10%.

| Scenario | Security | Quality | Maintenance | Integration | Reversibility | Discovery | Weighted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T0 — keep 23 repositories | 5 | 3 | 1 | 2 | 5 | 2 | 61/100 |
| T1 — one monorepo per family | 3 | 4 | 5 | 5 | 2 | 4 | 78/100 |
| **T2 — selective consolidation by change boundary** | **4** | **5** | **4** | **5** | **4** | **4** | **87/100** |
| T3 — one ecosystem mega-monorepo | 2 | 3 | 3 | 5 | 1 | 2 | 55/100 |

### Recommendation: T2

A repository boundary is justified when at least one is true:

1. it has an independent user/release lifecycle;
2. it isolates a materially different security or licence boundary;
3. it is consumed independently by external users;
4. it has multiple real consumers and a stable machine contract;
5. separate CI proves the artifact as an external consumer would use it.

A separate repository is not justified by a future target platform, a placeholder README, or a deployment class alone. Deployment class can be declared per crate in a workspace, as ADR 0033 already permits.

## 7. Proposed disposition matrix

| Current repository | Decision | Target | Rationale / gate |
| --- | --- | --- | --- |
| `constantin-jais` | KEEP, slim | control plane | remove extracted prototype code; retain governance, schemas and small governance tools |
| `bolt-cos-matic` | KEEP | unchanged | substantial independent engine and release lifecycle |
| `bolt-harness` | KEEP conditionally | external proof consumer | separate CI is valuable only while it installs/tests Bolt as an external consumer |
| `portal-core` | CONSOLIDATE | `portal` workspace | too small to justify independent governance |
| `portal-forge` | CONSOLIDATE | `portal` workspace | atomic tokens/core/adapters changes; deployment class remains per crate |
| `portal-apple` | CONSOLIDATE/FREEZE | `portal/adapters/apple` | preserve proof without an active repository |
| `portal-android` | CONSOLIDATE/FREEZE | `portal/adapters/android` | preserve proof without an active repository |
| `wrench-inspect` | CONSOLIDATE | `wrench` workspace | common evidence model and factory-only lifecycle |
| `wrench-db-inspect` | CONSOLIDATE | `wrench/crates/db-inspect` | keep a distinct CLI/crate, not necessarily a distinct repository |
| `wrench-dioxus-lab` | RETIRE after extraction | evidence under `dioxus-app-template/docs/evidence` | source is largely duplicated with the canonical template |
| `dioxus-app-template` | KEEP | unchanged | external-facing clone/template lifecycle justifies independence |
| `gear-loader` | CONSOLIDATE after consumer migration | `gear-context/crates/loader` | source ingestion and memory are consumed together by the flagship |
| `gear-memory` | CONSOLIDATE | `gear-context/crates/memory` | shared SourceRef/provenance path; keep security boundaries at crate level |
| `gear-depot` | CONSOLIDATE after E2E | `gear-supply/crates/depot` | intended atomic contract with Cable |
| `gear-cable` | CONSOLIDATE after E2E | `gear-supply/crates/cable` | release plan → manifest is one value stream |
| `rumble-lm` | KEEP and absorb runtime | unchanged | flagship product/session runtime owner |
| `rumble-ai-practices` | SLIM, do not archive | content/audit/scoring pack | move API/session/store/web runtime to LM; retain differentiated corpus value |
| `rumble-feed-mind` | KEEP, remove parser duplication | unchanged | independent product; consume Gear Loader for deterministic feed parsing |
| `rumble-canvas` | KEEP | unchanged | proven product-to-Bolt handoff and independent workflow |
| `rumble-cos` | KEEP, path-level licences | unchanged | independent publishing product and substantial corpus |
| `rumble-note` | ARCHIVE until runtime demand | specs remain in control plane | public placeholder duplicates the specification source of truth |
| `rumble-crew` | ARCHIVE until runtime demand | specs remain in control plane | public placeholder duplicates the specification source of truth |
| `rumble-ai-benchmark` | ARCHIVE as completed artifact | Pages/read-only artifact | no ongoing runtime role; preserve reproducibility and public demo |

Expected active topology after completion: control plane (1), Portal (1), Bolt (2), Wrench (1), Gear (2), template (1), active Rumble products/packs (5) = **13 active repositories**.

## 8. Important code moves

### 8.1 AI Practices → LM

Keep in AI Practices:

- corpus and source catalogue;
- domain types specific to professional AI practice;
- content validation, bias/media audit and pedagogical scoring;
- CLI for validating/auditing the pack;
- schemas and approved fixtures.

Move or delete in favour of LM:

- session store and TTL lifecycle;
- general session API;
- cohort/presence runtime;
- generic web/session shell;
- durable storage adapters for sessions.

Acceptance gate: LM freezes a pack-consumption/session contract and AI Practices runs the same pack against LM fixtures before deleting its shim.

### 8.2 Feed Mind → Gear Loader

Move deterministic RSS/Atom/JSON Feed parsing and normalization to Gear Loader. Keep in Feed Mind:

- subscriptions and polling intent;
- curation/ranking/rules and explanations;
- user workflow and exports;
- scheduling requests to Bolt;
- product-specific storage.

Acceptance gate: golden feed fixtures produce byte-equivalent canonical items before Feed Mind removes its parser.

### 8.3 Control plane → dedicated owners

Delete the deprecated Wrench DB prototype after verifying all unique fixtures/behaviour exist in the dedicated Wrench target. The control plane should retain contracts and historical decisions, not executable product/tool implementations.

## 9. Migration sequence

1. **Rights freeze:** inventory copyright/media rights; stop adding unclassified assets.
2. **Licensing foundation:** fix `wrench-inspect`; add `LICENSES/`, REUSE map, DCO, trademark and provenance schemas/templates.
3. **Obvious duplication:** remove the control-plane prototype; converge Feed parsing; freeze AI Practices runtime growth.
4. **Archive no-runtime/done repositories:** preserve README pointers and verify Pages before archiving.
5. **Portal consolidation:** import four histories into a new workspace and prove all platform CI before archiving old repos.
6. **Wrench consolidation:** share the evidence crate, retain two binaries, move lab evidence to the template.
7. **Gear context consolidation:** migrate LM's pinned Git dependencies in one compatibility window.
8. **Gear supply consolidation:** first prove Cable→Depot E2E, then merge; do not merge two unintegrated aspirations merely for symmetry.
9. **AI Practices convergence:** consume LM's frozen contract, then remove the provisional runtime.
10. **Final governance:** update cockpit, branch policies, badges, Cargo repository URLs, security policies and archive notices.

For history-preserving moves, use `git filter-repo --to-subdirectory-filter` and merge unrelated histories. Prefix colliding tags before import. Keep old repositories archived with migration pointers because GitHub issues, PRs, stars and release URLs do not migrate automatically.

## 10. Decision matrix

| ID | Decision | Recommendation | Blocking evidence before execution |
| --- | --- | --- | --- |
| LIC-1 | software standard | `MIT OR Apache-2.0` | rights inventory confirms the maintainer can offer both options |
| LIC-2 | public original content | `CC-BY-4.0` | content owner and third-party excerpts separated |
| LIC-3 | media | explicit per-asset terms | complete asset ledger; unknown rights block publication |
| GOV-1 | contribution policy | DCO 1.1, no CLA now | sign-off CI tested on PR fixtures |
| GOV-2 | provenance | SPDX/REUSE + content rights schema | all public assets classified |
| TOP-1 | topology strategy | selective consolidation T2 | migration plans and rollback tags per repository |
| TOP-2 | Portal | merge four repos | polyglot CI green in target workspace |
| TOP-3 | Wrench | merge Inspect + DB; retire Lab after evidence move | both CLIs and common report fixtures green |
| TOP-4 | Gear Context | merge Loader + Memory | LM consumes both from compatibility branch |
| TOP-5 | Gear Supply | merge Depot + Cable only after E2E | release plan produces a verified Depot manifest |
| TOP-6 | AI Practices | retain pack, move runtime to LM | frozen LM pack/session contract passes |
| TOP-7 | spec-only repos | archive until executable demand | canonical specs linked from archive README |
| TOP-8 | completed benchmark | archive read-only | Pages/demo and reproducibility verified |

## 11. Explicit non-decisions

- No mega-monorepo.
- No new shared-contract repository before two real consumers and a stable contract.
- No AGPL/SSPL/BUSL adoption.
- No history rewrite as part of topology work without a separate privacy/security decision.
- No deletion of old repositories; archive after migration and evidence checks.
- No relicensing of third-party media or generated output without verified rights.
