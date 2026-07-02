# Target Version V1 — Rumble / Portal / Bolt / Wrench / Gear

Status: Accepted  
Declared: 2026-07-02  
Machine contract: [`target-version.v1.json`](target-version.v1.json) validated by [`specs/harness/stack-target-version.v0.1.schema.json`](specs/harness/stack-target-version.v0.1.schema.json).

## Mission

Deliver one coherent sovereign stack where Rumble products consume Portal, Bolt, Wrench, and Gear through explicit contracts and leave reproducible evidence.

## Canonical rule

```text
Rumble exprime le produit.
Portal rend les clients cohérents.
Bolt planifie et orchestre.
Wrench inspecte et produit des preuves.
Gear extrait, stocke, transporte, package et gouverne les artefacts.
```

## Final stack

```text
RUMBLE — products / user-facing meaning
├─ rumble-canvas        product conception → specs → handoff
├─ rumble-cos           public education and ecosystem explanations
├─ rumble-crew          human/agent teamwork, approvals, evidence
├─ rumble-feed-mind     feed/watch curation and explainable rules
├─ rumble-lm            source-grounded learning and live facilitation
├─ rumble-note          local-first personal knowledge and context export
└─ rumble-ai-practices  professional AI-practice training

PORTAL — client platform / design system substrate
├─ portal-forge         DTCG tokens → CSS/Swift/Kotlin + WCAG
├─ portal-core          Rust UI contracts, i18n UI, a11y, bindings
├─ portal-apple         SwiftUI adapter
└─ portal-android       Jetpack Compose adapter

BOLT — orchestration / plans / gates
├─ bolt-cos-matic       deterministic planning, refusals, safe writes
└─ bolt-harness         public sandbox and evidence bench

WRENCH — inspection / validation / evidence
├─ wrench-inspect       structural, policy, spec, browser/a11y evidence
└─ wrench-db-inspect    Postgres/RLS/grants/migration/pgvector evidence

GEAR — runtime substrate / memory / artifacts / release
├─ gear-loader          canonical extraction and source candidates
├─ gear-memory          SourceRef, memory entries, event log, provenance
├─ gear-depot           ArtifactRef, manifests, policy, cache/proxy
└─ gear-cable           release plans, checksums, install floors, app-store adapters
```

## Milestones

| ID | Name | Goal | Acceptance |
| --- | --- | --- | --- |
| P0 | Control plane complete | Doctrine, names, maturity schemas, and target-version contracts are coherent. | Spec validation passes; `gear-loader` is canonical; target manifest validates. |
| P1 | Portal proof | Prove Portal tokens/core/adapters through one Rumble client fixture. | Versioned token bundle; Portal contracts consumed; one Rumble shell uses Portal. |
| P2 | Gear source path | Prove Gear Loader → Gear Memory source/provenance flow. | Loader candidate; SourceRef persisted; hostile-content evidence travels. |
| P3 | Wrench evidence | Prove inspection over specs, Portal surfaces, and Gear Loader outputs. | EvidenceReport schema; Portal checks; Loader evidence inspection. |
| P4 | Bolt gated planning | Prove Rumble handoff planning with evidence refs and refusals. | Planning bundle validates; unsafe evidence refuses; approval placeholder explicit. |
| P5 | First end-to-end Rumble slice | Ship one real product slice using Portal, Gear, Wrench, and Bolt boundaries. | UI consumes Portal; Gear source/artifact flow; Wrench report; Bolt handoff or explicit no-need. |
| P6 | Native and release proof | Prove native client and reproducible release path without product-logic duplication. | Apple/Android shell consumes Portal; Cable release plan links to Depot; release proof reproducible. |

## System acceptance

V1 is complete when:

1. at least one real Rumble product uses Portal for UI tokens and accessibility;
2. at least one source flow runs Gear Loader to Gear Memory with provenance;
3. at least one exported product artifact is represented by Gear Depot manifest data;
4. at least one release plan is connected through Gear Cable when distribution is needed;
5. Wrench evidence exists for the chosen product slice;
6. Bolt can validate or refuse a planning-only handoff using evidence refs;
7. Rumble Cos or an equivalent learning note explains the slice and links to evidence.

## Non-goals

- Do not merge all repositories into one monorepo as a default answer.
- Do not let Gear Depot absorb Portal UI semantics.
- Do not let Wrench own runtime ingestion or durable truth.
- Do not activate Bolt trusted execution before evidence and approval gates are proven.
- Do not duplicate product logic in SwiftUI or Compose shells.

## Verification

```bash
cd constantin-jais && bash ecosystem/specs/ci-validate-contracts.sh
cd portal-forge && cargo test
cd portal-core && cargo test
cd gear-loader && cargo test --workspace --all-targets
cd gear-memory && cargo test --workspace --all-targets
cd rumble-lm && cargo test --workspace --all-targets
```
