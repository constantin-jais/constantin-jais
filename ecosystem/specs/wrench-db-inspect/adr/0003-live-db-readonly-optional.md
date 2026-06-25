# ADR-0003 — Live DB Inspection Is Read-Only And Optional

Status: Accepted.

## Context

Live database metadata can reveal production drift that migrations or schema dumps miss. It also introduces operational risk: credentials, environment coupling, accidental mutation, and report leakage.

## Decision

Live DB inspection is optional and must never be the only accepted source of truth for CI gates.

When enabled, it must:

- use a read-only database role;
- run in a read-only transaction where supported;
- query metadata only;
- avoid row reads from product tables;
- avoid function execution that can mutate or leak data;
- redact connection identifiers in reports;
- fail closed with `inspection_integrity` when metadata needed for P0 checks cannot be read.

Default CI mode should prefer migrations + sanitized schema dump + manifest. Live inspection is an additional drift signal.

## Consequences

- `wrench-db-inspect` remains non-mutating by default.
- No Rumble must grant production data access to run the baseline gate.
- Production drift can still be checked by deployments that explicitly opt in.
- Reports can be shared with agents/humans without exposing secrets or row data.

## Non-Goals

- No migration execution.
- No repair actions.
- No DB proxying.
- No credential storage or vault behavior.
