# ADR 0020 — Bolt Sovereignty Gate Is Blocking

Status: Accepted
Date: 2026-06-30

## Context

The ecosystem treats sovereignty as a hard filter: no mandatory US SaaS for core truth, no opaque storage, no blocking licenses, no PII in logs, and no unapproved provider transmission. Bolt is the layer that can stop unsafe plans before implementation.

## Decision

Bolt P0 includes a blocking `sovereignty_policy` gate. Planning is refused or blocked when a handoff, evidence ref, capability candidate, dependency, or requested output requires incompatible SaaS, license, opaque storage, external model transmission, or PII/logging behavior.

Waivers are allowed only when explicit, scoped, expiring, and reviewable; high/critical risks require reviewer separation.

## Consequences

- Sovereignty violations are visible before execution.
- Rumbles cannot bypass policy through local planning logic.
- Exceptions remain auditable.

## Acceptance Tests

- A mandatory US SaaS dependency for core truth blocks planning.
- AGPL/SSPL or unverified-license direct dependency blocks unless waived by policy.
- PII-in-logs proposal blocks with safe refusal.
