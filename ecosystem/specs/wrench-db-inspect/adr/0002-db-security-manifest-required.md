# ADR-0002 — DB Security Manifest Required For Postgres Rumbles

Status: Accepted.

## Context

`wrench-db-inspect` cannot safely infer every table's tenant semantics from SQL names alone. Rumble products may contain tenant-scoped data, global reference data, audit/system tables, embeddings, local-first projections, and integration metadata.

Failing open on unknown classification would create a silent tenant-isolation bypass risk.

## Decision

Every Rumble using PostgreSQL for product data must provide a `wrench.db_inspect.manifest.v0.1` manifest before `wrench-db-inspect` can be used as a protected-branch, release, or harness gate. The forge scaffold should require this manifest for Postgres-backed `rumble-*` products and should mark DB inspection as not applicable for products without Postgres.

The manifest must declare at minimum:

- product name;
- tenant canonical name (`organization`);
- tenant column or approved tenant mapping;
- app, read-only, and migration roles;
- table classification for every non-system table;
- whether a table contains personal data;
- whether a table contains embeddings/vector-search material;
- explicit waivers, if any.

## Consequences

- Unknown table classification is a blocking P0 condition for strict gate profiles.
- Product teams must state DB security intent before relying on automated proof.
- The inspector remains evidence-producing, not policy-authoring.
- Rumbles avoid local, divergent table-classification conventions.
- The harness can distinguish missing DB evidence from explicit non-Postgres/non-applicable products.

## Non-Goals

- The manifest is not an ORM schema.
- The manifest is not a migration source of truth.
- The manifest does not store credentials, DSNs, row samples, prompts, source text, embeddings, or PII.
