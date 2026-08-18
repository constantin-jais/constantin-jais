# Constantin Jais — Libre AI control plane

[![Spec contracts](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml)

Building resilient Rust and TypeScript systems for trustworthy AI, sovereign tooling, and auditable automation.

## Where the product truth lives

Since ADR-0020 (2026-07-28, hub archived 2026-07-30), Libre AI product truth is split across two separated authorities, both multi-repository by design: **[`libre-ai/governance`](https://github.com/libre-ai/governance)** — doctrine, invariants, ADRs, LEXICON, the ecosystem index, the `project.v1` card schema, and the cross-repo fleet gates — and **[`libre-ai/contracts`](https://github.com/libre-ai/contracts)** — the canonical contract authorities (schemas, vectors, catalog, compatibility policy) and the Specification Lock. Each repository's own state (maturity, exposure, evidence) lives in its `project.v1.yaml` card, aggregated by `governance`'s fleet gates. **[`libre-ai/libre-ai`](https://github.com/libre-ai/libre-ai)** is the archived hub the constellation was rebuilt from: read-only, kept for history plus [`ecosystem/migration-index.v1.yaml`](https://github.com/libre-ai/libre-ai/blob/main/ecosystem/migration-index.v1.yaml) (every migrated path to its destination) and [`ecosystem/FORGOTTEN.yaml`](https://github.com/libre-ai/libre-ai/blob/main/ecosystem/FORGOTTEN.yaml) (deliberately retired paths).

## What this repository is

This repository is the **control plane** of the Libre AI forge (control-plane ADR 0047). It governs how work is decided, not what products do:

- forge doctrine ADRs (`ecosystem/specs/shared/adrs/`)
- cross-project decision log and shared design studies
- decompositions of external systems used as inspiration inputs
- input manifests for future specification locks (e.g. orchestrator)

It is not a product runtime, and it contains no product specifications: those live in the `contracts` repository under its Specification Lock, with forge doctrine bounded by `governance`'s invariants register ([`docs/decisions/INVARIANTS.md`](https://github.com/libre-ai/governance/blob/main/docs/decisions/INVARIANTS.md)).

## Product portfolio (rebuild in progress)

Seven public products are being rebuilt from locked contracts: **Radar, Notebook, AI Practices, Sessions, Boussole Politique, Spec Studio, and Model Policy**. None is released yet — the transformation is gated (G0 freeze and G1 specification lock are complete; G2 canonical foundations is in progress). Status and evidence: [`STATUS.md`](https://github.com/libre-ai/libre-ai/blob/main/STATUS.md).

## Historical topology (frozen)

The pre-constellation strata (legacy product specifications, fleet cockpits, maturity ladders) are preserved in Git history under the archive tag [`archive/pre-constellation-2026-07-19`](https://github.com/constantin-jais/constantin-jais/tree/archive/pre-constellation-2026-07-19). `main` carries only the current truth (ADR-0009, wave 0).

## Operating principles

Security > Quality > Performance > Completeness, with sovereignty, privacy, and license compatibility as release gates. Licensing policy: differentiated EUPL / Apache-2.0 / CC BY with DCO and REUSE compliance ([monorepo ADR-0004](https://github.com/libre-ai/libre-ai/blob/main/docs/adr/0004-licensing-governance.md)).
