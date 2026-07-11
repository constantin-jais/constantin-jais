# Libre AI ecosystem control plane

[![Spec contracts](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml)

This repository governs the public Libre AI portfolio: product boundaries, shared contracts, maturity evidence, repository profiles, and branch policy. It is not a product runtime and does not make a design or implementation repository public.

## Public portfolio

Maturity is evidence-based, not aspirational. `contract-first` and `specification` do not mean that a product is available to end users.

| Surface | Responsibility | Maturity |
| --- | --- | --- |
| [Libre AI Website](https://github.com/libre-ai/website) | Institutional and educational publication | `usable` |
| [Sessions](https://github.com/libre-ai/sessions) | Source-grounded learning and facilitation | `contract-first` |
| [Feed Radar](https://github.com/libre-ai/feed-radar) | Explainable feed-to-knowledge curation | `dojo` |
| [Spec Studio](https://github.com/libre-ai/spec-studio) | Product conception and specification handoffs | `contract-first` |
| [Agent Board](https://github.com/libre-ai/agent-board) | Human/agent teamwork and approvals | `specification` |
| [Notebook](https://github.com/libre-ai/notebook) | Local-first personal knowledge | `specification` |
| [AI Practices](https://github.com/libre-ai/ai-practices) | Professional AI-practice training | `dojo` |
| [Benchmarks](https://github.com/libre-ai/benchmarks) | Versioned comparison evidence | `recurring` |
| [Dioxus App Template](https://github.com/libre-ai/dioxus-app-template) | Generated Portal template distribution | `usable` |

## Infrastructure

The infrastructure repositories are independently testable and communicate through explicit handoffs. They are not public product brands.

| Repository | Owns | Does not own |
| --- | --- | --- |
| [Portal](https://github.com/libre-ai/portal) | Client primitives, adapters, token compilation and templates | Product workflows or artifact distribution |
| [Bolt](https://github.com/libre-ai/bolt) | Bounded planning, orchestration and execution gates | Product UX, storage or inspection truth |
| [Wrench](https://github.com/libre-ai/wrench) | Independent inspection and evidence | Runtime ownership or product decisions |
| [Gear](https://github.com/libre-ai/gear) | Context, ingestion, artifacts and supply/distribution | Product semantics or orchestration |

## Governance entry points

- [`ecosystem/governance/repo-profiles.json`](ecosystem/governance/repo-profiles.json) — public names, canonical URLs, maturity and required checks for all 13 public repositories.
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
