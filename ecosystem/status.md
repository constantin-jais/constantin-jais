# Libre AI ecosystem status

Status date: 2026-07-11

This cockpit reports the public topology and migration state. Canonical repository metadata lives in [`governance/repo-profiles.json`](governance/repo-profiles.json); architecture decisions live in [`target-version.md`](target-version.md) and [`specs/shared/decision-log.md`](specs/shared/decision-log.md).

## Current topology

| Repository | Domain | Maturity | Current evidence |
| --- | --- | --- | --- |
| `website` | institutional | `usable` | Dioxus publication, CI and browser smoke |
| `sessions` | product | `contract-first` | contracts and guarded Rust workspace |
| `feed-radar` | product | `dojo` | executable curation pipeline and contracts |
| `spec-studio` | product | `contract-first` | specification and handoff contracts |
| `agent-board` | product | `specification` | product charter and roadmap; no availability claim |
| `notebook` | product | `specification` | product charter and roadmap; no availability claim |
| `ai-practices` | product | `dojo` | executable training surface under active hardening |
| `benchmarks` | evidence | `recurring` | published versioned comparison evidence |
| `dioxus-app-template` | distribution | `usable` | deterministic Portal mirror and deployed Pages smoke |
| `portal` | infrastructure | `consolidated` | four full histories, adapters and canonical template |
| `bolt` | infrastructure | `consolidated` | engine and harness histories with boundary gates |
| `wrench` | infrastructure | `consolidated` | inspectors and evidence lab histories |
| `gear` | infrastructure | `consolidated` | isolated Context and Supply workspaces |

`consolidated` describes repository topology, not production readiness.

## Migration state

- The 13 public target repositories have canonical URLs, repository profiles, branch policy, accessible cards and green protected checks.
- Four superseded Portal repositories are archived after history and CI continuity checks.
- Nine superseded Bolt, Wrench and Gear source repositories remain in migration freeze until release and Pages continuity is proven from their consolidated targets. They must not receive feature work.
- The control plane remains in its current namespace until GitHub Support removes inaccessible pull-request refs from the rewritten history.
- Public distributable metadata uses a versioned Design System URN and an immutable `portal/forge` builder revision; no private repository URL is published.
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
