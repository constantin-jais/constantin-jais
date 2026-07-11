# ADR 0038 — Rust core and specialized adapter boundary

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Related: ADR 0029, ADR 0033, ADR 0034

## Context

Some document, browser and provider integrations cannot be implemented with the portable Rust core alone. Treating every exception as either forbidden or part of the core would respectively block required interoperability or expand the trusted computing base without control.

## Decision

Rust owns durable decisions, validation, authorization, orchestration, persistence contracts and evidence. A specialized adapter may use another runtime only when no reasonable Rust path meets the required fidelity.

A specialized adapter must:

1. implement a Rust-owned, versioned input/output contract;
2. run out of process when parsing hostile input or loading a large native runtime;
3. have no network unless the contract explicitly requires an allowlisted destination;
4. enforce CPU, RSS, disk, file-count and wall-time budgets outside the guest process;
5. return typed warnings and fail closed when fidelity or safety is inconclusive;
6. use synthetic fixtures and carry license, SBOM, provenance and compromise references;
7. remain replaceable without changing product domain contracts.

`specialized-adapter` is distinct from a native FFI escape hatch. FFI linked into a product shares its blast radius and requires a separate portability decision.

## Consequences

- Products never import parser- or provider-specific DTOs.
- Gear may host document workers behind Gear contracts.
- TypeScript remains permissible only at explicitly ratified browser/Office boundaries.
- Every exception has an owner, expiry/review condition and kill switch.

## Acceptance criteria

- contract tests pass with the adapter enabled and disabled;
- a killed/timed-out adapter cannot corrupt canonical state;
- network-denial and resource-limit tests are executable;
- no secret, raw token or document content appears in evidence logs.
