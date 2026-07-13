# Libre AI ecosystem control plane

[![Spec contracts](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml)

This repository governs the public Libre AI portfolio: product boundaries, shared contracts, maturity evidence, repository profiles, and branch policy. It is not a product runtime and does not make a design or implementation repository public.

## Public portfolio

Maturity is evidence-based, not aspirational. `contract-first` and `specification` do not mean that a product is available to end users.

| Surface | Role | Responsibility | Maturity |
| --- | --- | --- | --- |
| [Libre AI Website](https://github.com/libre-ai/website) | gateway | Understand, choose, use and verify the portfolio | `usable` |
| [Feed Radar](https://github.com/libre-ai/feed-radar) | product | Explainable feed selection and portable curation | `dojo` |
| [Notebook](https://github.com/libre-ai/notebook) | product | Private local knowledge and controlled context export | `specification` |
| [AI Practices](https://github.com/libre-ai/ai-practices) | product | Professional AI-practice training | `dojo` |
| [Sessions](https://github.com/libre-ai/sessions) | product | Source-grounded collective learning and facilitation | `contract-first` |
| [Boussole Politique](https://github.com/libre-ai/boussole-politique) | product | Private civic comparison against sourced public votes | `contract-first` |
| [Spec Studio](https://github.com/libre-ai/spec-studio) | product | Product decisions, specifications and bounded handoffs | `contract-first` |
| [Agent Board](https://github.com/libre-ai/agent-board) | product | Human governance of agentic missions | `specification` |
| [Benchmarks](https://github.com/libre-ai/benchmarks) | evidence | Versioned comparison evidence | `recurring` |
| [Dioxus App Template](https://github.com/libre-ai/dioxus-app-template) | distribution | Generated Client Kit template mirror | `usable` |

## Infrastructure

The infrastructure repositories are independently testable and communicate through explicit handoffs. They are not public product brands.

| Repository | Owns | Does not own |
| --- | --- | --- |
| [Client Kit](https://github.com/libre-ai/client-kit) | Client primitives, adapters, token compilation and templates | Product workflows or artifact distribution |
| [Agent Factory](https://github.com/libre-ai/agent-factory) | Bounded planning, orchestration and execution gates | Product UX, storage or inspection truth |
| [Proof Kit](https://github.com/libre-ai/proof-kit) | Reproducible non-formal inspection evidence | Runtime ownership or product decisions |
| [Context Kit](https://github.com/libre-ai/context-kit) | Ingestion, source references, local memory and context provenance | Product semantics or artifact distribution |
| [Artifact Supply](https://github.com/libre-ai/artifact-supply) | Manifests, packaging, provenance and deterministic distribution | Release decisions or source ingestion |

## Governance entry points

- [`ecosystem/product-portfolio.md`](ecosystem/product-portfolio.md) — challenged vision, boundaries and proof ladder for the seven products.
- [`ecosystem/governance/repo-profiles.json`](ecosystem/governance/repo-profiles.json) — public names, canonical URLs, maturity and required checks for all 15 active public repositories.
- [`ecosystem/governance/branch-policy.json`](ecosystem/governance/branch-policy.json) — branch rules and required checks for the governed repositories.
- [`ecosystem/status.md`](ecosystem/status.md) — current migration and verification status.
- [`ecosystem/target-version.md`](ecosystem/target-version.md) — accepted architecture target and compatibility rules.
- [`ecosystem/specs/shared/decision-log.md`](ecosystem/specs/shared/decision-log.md) — cross-repository decisions.

## Naming compatibility

**Libre IA** is used on French public surfaces and **Libre AI** on GitHub and English surfaces. The historical `rumble-*` vocabulary remains only where it is a versioned crate, schema, fixture, path, or contract identifier. It is not a public brand and must not be introduced in new repository names or user-facing copy.

## Local verification

```sh
python3 ecosystem/governance/validate_repo_profiles.py
python3 -m unittest discover ecosystem/governance -v
python3 ecosystem/governance/ecosystem_policy.py check
```

Operational decisions are evaluated in this order: **Security > Quality > Performance > Completeness**. Sovereignty, privacy and license compatibility are release gates.
