# Gear Specifications

Gear is the infrastructure layer for verifiable local-first truth.

It owns storage, indexing, provenance, artifacts, distribution wiring, offline-first primitives, lifecycle state, and verification. It turns sources, artifacts, memory snapshots, code maps, and events into stable references that can be audited, replayed, deleted, anonymized, revoked, and consumed safely by Rumble products, Wrench tools, and Bolt.

Short rule:

> Gear makes references trustworthy. Gear does not decide what to do with them.

## Start Here

Read in this order:

1. `ONBOARDING.md` — Gear in 5–10 minutes, scope, examples, checklist.
2. `00-gear-boundaries.md` — responsibility boundaries and P0 ownership.
3. `04-gear-memory-substrate.md` — Gear Memory charter and object model.
4. `05-gear-memory-consumer-alignment.md` — how Rumbles/Bolt/Wrench consume Gear.
5. `06-p0-implementation-roadmap.md` — first Rust-first implementation path.
6. `gear-memory.v0.1.schema.json` + `fixtures/memory/` — contract validation examples.

## What Gear Centralizes

| Need | Gear answer |
| --- | --- |
| source identity and citation | `SourceRef` |
| produced output/package identity | `ArtifactRef` / `ArtifactManifest` |
| indexed context | `MemoryEntry` |
| code/source graph | `CodeMap` + typed edges |
| provenance | `ProvenanceRecord` |
| audit substrate | `EventLogEntry` |
| deletion/anonymization/revocation | lifecycle states + tombstones |

## What Gear Prevents

Gear prevents each Rumble from creating incompatible local versions of:

- source stores;
- evidence stores;
- memory/search indexes;
- code graph maps;
- artifact manifests;
- provenance logs;
- deletion/anonymization propagation;
- stale/revoked reference handling.

## Files

| File | Purpose |
| --- | --- |
| `ONBOARDING.md` | Fast explanation of Gear scope, solved problems, flows, and checklist. |
| `00-gear-boundaries.md` | Gear layer boundaries and P0 contract ownership. |
| `01-source-artifact-provenance.md` | `SourceRef`, `ArtifactRef`, and `ProvenanceRecord` contracts. |
| `02-memory-entry-contract.md` | `MemoryEntry` and `EventLogEntry` contracts. |
| `03-depot-artifact-manifest.md` | Gear Depot artifact manifest contract. |
| `04-gear-memory-substrate.md` | Gear Memory responsibility charter, object model, indexing strategy, security/RGPD risks, tests, ADR list. |
| `05-gear-memory-consumer-alignment.md` | Rumble/Bolt/Wrench adoption seams and anti-duplication matrix. |
| `06-p0-implementation-roadmap.md` | Rust-first P0 implementation plan, storage/API/tests, and non-goals. |
| `gear-memory.v0.1.schema.json` | JSON Schema for Gear Memory P0 contracts. |
| `fixtures/memory/` | Valid and invalid Gear Memory contract fixtures. |

## Boundary Reminder

Gear stores, indexes, verifies, packages, syncs, and connects.

Gear does not decide, orchestrate, parse, validate, rank product importance, execute workflows, or define product UX.

## Validation

From repository root:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

This validates Gear Memory, Gear Loader, and Bolt/cos-matic planning schemas and fixtures.
