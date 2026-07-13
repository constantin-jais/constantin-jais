# Libre AI ecosystem status

Status date: 2026-07-12

This cockpit reports the public topology and migration state. Canonical repository metadata lives in [`governance/repo-profiles.json`](governance/repo-profiles.json); architecture decisions live in [`target-version.md`](target-version.md) and [`specs/shared/decision-log.md`](specs/shared/decision-log.md).

## Current topology

| Repository | Domain | Maturity | Current evidence |
| --- | --- | --- | --- |
| `website` | institutional | `usable` | v3 catalogue exposes three public journeys and honest per-product states; Website and every launch CTA have separate publication gates |
| `sessions` | product | `contract-first` | contracts plus locally replayed Proof Kit, DB, artifact and Agent Factory evidence; complete user session still absent |
| `feed-radar` | product | `dojo` | executable curation pipeline and read-only Dioxus proof with pinned Client Kit provenance across Chromium, Firefox and WebKit |
| `spec-studio` | product | `contract-first` | specification, explicit handoff contracts and protected Rust supply-chain gate |
| `agent-board` | product | `contract-first` | tested `MissionRecord v1` and local fail-closed transition engine; no board, persistence or hosted runtime claim |
| `notebook` | product | `specification` | product charter and roadmap; no availability claim |
| `boussole-politique` | autonomous civic product | `contract-first` | local-first boundary, Rust contracts and deterministic M1 sensitivity evidence with a conditional verdict |
| `ai-practices` | product dojo | `dojo` | executable training surface, governed `activity.v1` drafts, PostgreSQL test proof and checksummed Proof Kit DB gate; no approved activity |
| `benchmarks` | evidence | `recurring` | published versioned comparison evidence |
| `dioxus-app-template` | generated distribution | `usable` | deterministic Client Kit mirror and deployed Pages smoke |
| `client-kit` | infrastructure | `consolidated` | four imported histories, adapters, Forge and canonical template |
| `agent-factory` | infrastructure | `consolidated` | engine/harness boundaries, Engine alpha.6 and an inactive PostgreSQL anti-replay candidate |
| `proof-kit` | infrastructure | `consolidated` | healthy Pages, DB Inspect alpha.7 and unsigned macOS bundle install/launch/removal evidence |
| `context-kit` | infrastructure | `consolidated` | extracted context history, isolated workspace and supply-chain CI |
| `artifact-supply` | infrastructure | `consolidated` | extracted supply history, isolated workspace and supply-chain CI |

Policy remains private and is not part of the seven-product public catalogue. Benchmarks is a separate evidence program, not an eighth product. `consolidated` describes repository topology, not production readiness.

ADR 0046 makes `libre-ai.fr` canonical and reserves seven explicit application hosts plus `preuves.libre-ai.fr`. All eight remain `discovery` with DNS and public URLs inactive. `libre-ia.fr` becomes a defensive redirect source only; no DNS or deployment operation follows from the documentation change.

Dioxus is the preferred application stack across web, fullstack, desktop and mobile. Web/SSG has deployed route and asset evidence. Proof Kit now builds an unsigned macOS `.app`; a bounded arm64 probe copies it to a fresh temporary installation, launches one visible WebView window, terminates it and removes it. Developer ID signing, notarization, distinct-version upgrade/rollback, lifecycle and accessibility remain unproven, so desktop, Android and iOS stay experimental under [`specs/shared/dioxus-target-evidence.md`](specs/shared/dioxus-target-evidence.md).

## Migration state

- Fifteen active public repository profiles are governed. The former Gear compatibility repository was deleted after verified recovery bundles and a zero-consumer scan; it is no longer queried by branch policy.
- Client Kit, Agent Factory and Proof Kit are the canonical renamed repositories; their imported histories, redirects, protected checks and active consumers are verified.
- The Gear split is complete: consumers use Context Kit or Artifact Supply, and the compatibility repository was deleted after a zero-consumer scan and verified final bundle.
- Agent Factory Engine alpha.6 and Proof Kit DB Inspect alpha.7 provide installable multi-platform releases with checksums, SBOM, provenance and attestations. DB Inspect alpha.7 corrects stale tool-version metadata in alpha.4–alpha.6; historical assets remain immutable.
- Proof Kit Pages now builds under its actual `/proof-kit/` project path and deploy-smokes root, JavaScript, CSS, fonts, WASM and the linked `blog/1/` deep route. The retired `/wrench/` asset path is absent from the deployed HTML.
- A fresh 2026-07-12 mirror audit found zero changed pre-rewrite commits reachable from public branches or tags, but 152 remain reachable from 69 GitHub pull-request refs. A Support escalation has been submitted; its human case reference is still pending. The control plane remains in its current namespace until GitHub confirms cleanup and a fresh mirror audit passes.
- Public distributable metadata uses a versioned Design System URN and immutable canonical builder revisions; no private repository URL is published.
- Twenty active Rust lockfile workspaces pass license/source inspection. A 19-repository Git/GitHub audit attributes all human contributions and PRs to `constantin-jais`; Agent Board now pilots prospective DCO and REUSE 3.3 without changing its MIT license. Data/content and monorepo rollout still require class-specific annotations.
- Feed Radar removed `RUSTSEC-2026-0173` by updating `validator_derive` to 0.20.1. A three-commit Biscuit patch is locally upstream-ready, removes `proc-macro-error2`, and passes Biscuit, Agent Factory and Sessions tests, but is unpublished. Agent Factory and Sessions retain the build-time waiver until an official release is adopted. Both removed `RUSTSEC-2023-0071` from their locked graphs by selecting the local AWS-LC backend instead of RustCrypto RSA; Agent Factory GitHub authentication remains token-based and Sessions preserves its OIDC RS256 verification tests.
- Agent Factory includes an optional, default-disabled SQLx 0.9 PostgreSQL replay store: static parameterized queries, forced RLS, reversible migration and exactly one success across 32 concurrent claims. Filesystem remains the only active backend and multi-host operation remains prohibited.
- Boussole M1 remains conditional: 95 strong-link core candidates span two legislatures, but the 84 adopted/11 rejected distribution, missing thematic taxonomy and partially reviewed source links prohibit canonical selection and PWA claims.
- Automated dependency updates are reviewed separately from migration work and are never merged without their repository gates.

## Maturity vocabulary

| Status | Meaning |
| --- | --- |
| `specification` | Intent, boundaries and roadmap exist; no usable runtime is claimed. |
| `contract-first` | Versioned contracts, fixtures or domain model exist; runtime is limited or absent. |
| `dojo` | Executable experimentation surface that intentionally generates stack constraints. |
| `usable` | A documented real workflow runs locally; operational maturity is not implied. |
| `consolidated` | Historical repositories were assembled behind one canonical boundary. |
| `trusted` | Tests, security, documentation, provenance and repeatable release evidence support routine reliance. |
| `retired` | Archived, replaced or intentionally stopped. |

Scale readiness is a separate evidence attribute. A repository never moves from `trusted` to `scale-ready` through wording alone.

## Promotion criteria

Promotion requires all evidence relevant to the target level:

1. documented boundaries and non-goals;
2. versioned contracts or fixtures where applicable;
3. protected CI and security gates;
4. a reproducible build or release path for distributed artifacts;
5. explicit failure modes and operational limits;
6. privacy, sovereignty and license checks;
7. an update to the repository profile and decision log.

## Verification

```sh
python3 ecosystem/governance/validate_repo_profiles.py
python3 -m unittest discover ecosystem/governance -v
python3 ecosystem/governance/ecosystem_policy.py check
sh ecosystem/specs/ci-validate-contracts.sh
```

The priority order remains **Security > Quality > Performance > Completeness**.
