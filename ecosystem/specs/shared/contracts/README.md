# Shared Contracts Index

Status: Draft.

This directory contains cross-product contracts that Rumble/Bolt/Wrench/Gear consumers must treat as versioned boundaries, not implementation notes.

## Contracts

| Contract                                            | Status     | Purpose                                                                                                                                             |
| --------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implementation-handoff.v0.1.md`                    | Draft / P0 | Planning-only Rumble-to-Bolt handoff contract.                                                                                                      |
| `implementation-handoff.v0.1.schema.json`           | Draft / P0 | JSON Schema for `ImplementationHandoff v0.1`.                                                                                                       |
| `bolt-refusal-codes.v0.1.md`                        | Draft / P0 | Canonical Bolt refusal/gate reason codes for handoff validation, planning, evidence, idempotency, and sovereignty.                                  |
| `app-store-release.v0.1.md`                         | Accepted   | Stable Rumble-to-Gear Cable boundary for TestFlight/App Store publication through pinned `asc`.                                                     |
| `app-store-release.v0.1.schema.json`                | Accepted   | JSON Schema for `App Store Release Contract v0.1`.                                                                                                  |
| `delegated-authorization-biscuit.v0.1.md`           | Draft / P0 | Shared Biscuit delegated-authorization facts, rights, lifecycle, audit, and product matrix.                                                         |
| `delegated-authorization-biscuit.v0.1.tests.md`     | Draft / P0 | Product-neutral conformance tests for Biscuit delegation.                                                                                           |
| `delegated-authorization-biscuit.v0.1.prototype.md` | Draft      | Pre-implementation spike plan for verifier/authorizer behavior.                                                                                     |
| `workspace-identity.v0.1.md`                        | Draft      | Shared actor/workspace/membership/role model; decision material for ADR 0028 (ownership).                                                           |
| `../gear-loader/gear-loader.v0.1.schema.json`       | Draft / P0 | JSON Schema bundle for Gear Loader (formerly wrench-loader) extraction requests, canonical documents, Gear source candidates, and evidence reports. |
| `../../harness/cosmatic-planning.v0.1.schema.json`  | Draft / P0 | JSON Schema bundle for Bolt/cos-matic planning requests, evidence refs, gates, plan reports, run intents, refusals, and audit events.               |

## Quality Rules

- A product must not create a new delegation token format without first checking `delegated-authorization-biscuit.v0.1.md`.
- Canonical JSON/Schema contracts remain the source of truth where available; Markdown explains boundaries and acceptance criteria.
- Contracts must define owners, non-goals, safe audit fields, and acceptance tests before implementation.
- Contract examples must use fake opaque IDs only; no personal data, source excerpts, credentials, bearer tokens, or live secrets.

## Related ADRs

| ADR                                                      | Status   | Scope                                                   |
| -------------------------------------------------------- | -------- | ------------------------------------------------------- |
| `../adrs/0001-biscuit-shared-delegated-authorization.md` | Accepted | Biscuit as the shared delegated-authorization contract. |
| `../adrs/0009-biscuit-public-key-distribution.md`        | Proposed | Versioned self-hostable Biscuit public keyset.          |
| `../adrs/0010-biscuit-revocation-storage.md`             | Proposed | Hybrid revocation storage with safe refs only.          |
