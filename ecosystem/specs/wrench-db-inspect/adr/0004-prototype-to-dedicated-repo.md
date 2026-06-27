# ADR-0004 — Extract Prototype To Dedicated Repository

Status: Proposed.

## Context

`wrench-db-inspect` now has a working prototype, fixtures, gate profiles, redaction behavior, and CI/Bolt integration contracts inside the ecosystem control-plane repository.

Keeping implementation code indefinitely inside `ecosystem/prototypes` would blur responsibilities. The ecosystem repository should remain the strategic/spec control plane, while `wrench-db-inspect` should become a Wrench tool repository that can version, test, release, and integrate independently.

## Decision

Extract the prototype into a dedicated `wrench-db-inspect` repository once the extraction readiness checklist is satisfied.

The ecosystem repository remains the upstream contract/control plane until the dedicated repo mirrors or owns stable docs.

## Rationale

- Keeps Wrench tooling implementation separate from ecosystem strategy docs.
- Allows independent CI, releases, dependency audit, and issue tracking.
- Prevents Rumbles from copying prototype code locally.
- Preserves contract-first development through fixtures and report schemas.

## Consequences

- The prototype directory becomes temporary and should eventually be removed or replaced by a link/reference.
- Specs, fixtures, and ADRs must be kept in sync during transition.
- The dedicated repo must preserve all hard boundaries: no ORM, no migration runner, no DB proxy, no vault, no runtime authorization engine.

## Non-Goals

- No production live DB inspection as part of extraction.
- No widening to non-Postgres dialects before P0 Postgres quality is stable.
- No integration with hosted SaaS as a requirement.
