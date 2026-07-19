# Constantin Jais — Libre AI control plane

[![Spec contracts](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml)

Building resilient Rust and TypeScript systems for trustworthy AI, sovereign tooling, and auditable automation.

## Where the product truth lives

Since 2026-07-16, all Libre AI product work happens in the canonical base repository: **[`libre-ai/libre-ai`](https://github.com/libre-ai/libre-ai)** — specifications, contracts, architecture, work packages, and shared foundations. The target topology is multi-repository (monorepo ADR-0008): real product repositories will reopen on the preserved historical product URLs, consuming the base as a versioned dependency, while legacy tooling repositories are retired after verified capture. The authoritative freeze record is [`ecosystem/LEGACY-MANIFEST.yaml`](https://github.com/libre-ai/libre-ai/blob/main/ecosystem/LEGACY-MANIFEST.yaml).

## What this repository is

This repository is the **control plane** of the Libre AI forge (control-plane ADR 0047). It governs how work is decided, not what products do:

- forge doctrine ADRs (`ecosystem/specs/shared/adrs/`)
- cross-project decision log and shared design studies
- decompositions of external systems used as inspiration inputs
- input manifests for future specification locks (e.g. orchestrator)

It is not a product runtime, and it contains no product specifications: those live in the base repository under its G1 specification standard, with doctrine bounded by its invariants register ([`docs/decisions/INVARIANTS.md`](https://github.com/libre-ai/libre-ai/blob/main/docs/decisions/INVARIANTS.md)).

## Product portfolio (rebuild in progress)

Seven public products are being rebuilt from locked contracts: **Radar, Notebook, AI Practices, Sessions, Boussole Politique, Spec Studio, and Model Policy**. None is released yet — the transformation is gated (G0 freeze and G1 specification lock are complete; G2 canonical foundations is in progress). Status and evidence: [`STATUS.md`](https://github.com/libre-ai/libre-ai/blob/main/STATUS.md).

## Historical topology (frozen)

The pre-monorepo multi-repository portfolio and its maturity ladder are preserved as a frozen snapshot for provenance in [`ecosystem/status.md`](ecosystem/status.md) (final: 2026-07-14). They are no longer individually governed.

## Operating principles

Security > Quality > Performance > Completeness, with sovereignty, privacy, and license compatibility as release gates. Licensing policy: differentiated EUPL / Apache-2.0 / CC BY with DCO and REUSE compliance ([monorepo ADR-0004](https://github.com/libre-ai/libre-ai/blob/main/docs/adr/0004-licensing-governance.md)).
