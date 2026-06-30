# Wrench DB Inspect Completeness Plan

This document defines how `wrench-db-inspect` moves from prototype to pre-production candidate without relying on informal confidence. Completeness includes both rule correctness and integration into forge/harness evidence for `rumble-*` builds.

## Completion rule

A rule is considered complete only when it has all four proofs:

1. a sanitized pass or non-triggering fixture when applicable;
2. a sanitized fail fixture;
3. an expected gate outcome for `local`, `protected_branch`, or `release`;
4. documentation of known false-positive / false-negative limits.

No P0/P1 rule should be promoted without an executable fixture.

## Coverage matrix

| Area | Rule / control | Fixture coverage | Gate coverage | Status |
| --- | --- | --- | --- | --- |
| RLS | `RLS_REQUIRED_TENANT_TABLE` | pass + fail | protected branch blocks | covered |
| RLS | `FORCE_RLS_REQUIRED_TENANT_TABLE` | pass + fail | protected branch blocks | covered |
| RLS | `DISABLE_RLS_FORBIDDEN` | fail | protected branch blocks | covered |
| RLS | `SET_ROW_SECURITY_OFF_FORBIDDEN` | fail | protected branch blocks | covered |
| RLS | `NO_FORCE_RLS_FORBIDDEN` | fail | protected branch blocks | covered |
| RLS policy | `DROP_POLICY_DANGEROUS` | fail | protected branch blocks | covered |
| Grants | `GRANT_ALL_ON_TENANT_TABLE` | pass + fail | protected branch blocks, local warns | covered |
| Grants | `GRANT_TO_UNKNOWN_ROLE` | fail | protected branch blocks | covered |
| Grants | `GRANT_ALL_TO_PUBLIC_DANGEROUS` | fail | protected branch blocks | covered |
| Grants | `GRANT_ALL_ON_SCHEMA_DANGEROUS` | fail | protected branch blocks | covered |
| Grants | `GRANT_ALL_TABLES_IN_SCHEMA_DANGEROUS` | fail | protected branch blocks | covered |
| Grants | `DEFAULT_PRIVILEGES_GRANT_ALL_DANGEROUS` | fail | protected branch blocks | covered |
| Manifest | `TABLE_CLASSIFICATION_REQUIRED` | fail | protected branch blocks | covered |
| Tenant derivation | `TENANT_DERIVATION_FK_REQUIRED` | fail | release blocks | covered, one-hop and multi-hop FK chain |
| Tenant derivation | `TENANT_DERIVATION_POLICY_REQUIRED` | pass + fail, reversed equality, wrong setting, multi-hop | release blocks | covered, pattern-based AST |
| Tenant derivation | `TENANT_DERIVATION_PATH_UNSUPPORTED` | malformed path only | release blocks | covered by fail-closed parser path |
| Migrations | `DROP_TABLE_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `DROP_COLUMN_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `DROP_CONSTRAINT_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `DROP_FOREIGN_KEY_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `ALTER_COLUMN_DROP_NOT_NULL_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `TRUNCATE_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `UNQUALIFIED_DELETE_DANGEROUS` | fail | protected branch blocks | covered |
| Migrations | `UNQUALIFIED_UPDATE_DANGEROUS` | fail | protected branch blocks | covered |
| Pgvector | `PGVECTOR_TENANT_FILTER_REQUIRED` | fail + LM examples | protected branch blocks | partial heuristic |
| Views/functions | `VIEW_TENANT_FILTER_REQUIRED` | warn | protected branch warns | covered as P1 |
| Views/functions | `FUNCTION_TENANT_FILTER_REQUIRED` | warn | protected branch warns | covered as P1 |
| Functions | `SECURITY_DEFINER_SEARCH_PATH_REQUIRED` | warn | protected branch warns | covered as P1 |
| Manifest | `WAIVER_INVALID` | fail | release blocks | covered |
| Reports | final redaction + release review block | redaction fixture | release blocks if applied | covered |

## Remaining work before pre-production candidate

### P0 blockers

- Validate against a real sanitized `rumble-lm` schema dump and manifest.
- Add the forge/harness scaffold hook so every Postgres-backed `rumble-*` produces manifest, sanitized schema dump, and `wrench-db-inspect` report artifacts.
- Ensure non-Postgres `rumble-*` products explicitly mark DB inspection as not applicable.

### P1 robustness

- Add tenant-derivation fixtures for non-qualified tables and explicit `JOIN` variants if the real LM schema uses them.
- Improve pgvector analysis from heuristic text detection to AST/function-body aware checks where parser support allows it.
- Add fixtures for non-ALL `ALTER DEFAULT PRIVILEGES` cases if product schemas use them.

### P2 extraction readiness

- Add `cargo clippy -- -D warnings` to CI.
- Add snapshot tests for canonical reports.
- Move prototype to dedicated repository once `rumble-lm` pilot and forge/harness integration are clean.

## Completeness gates

Before declaring complete for extraction:

```bash
cargo fmt --check
cargo clippy -- -D warnings
cargo test
python3 ../../specs/wrench-db-inspect/scripts/validate-json-contracts.py
./run-fixtures.sh
./run-lm-examples.sh
```

Additionally:

- no report may contain secrets, DSNs, row data, prompt/source text, raw embeddings, or PII;
- all P0/P1 rules must appear in this matrix;
- all known parser limitations must be documented with either a fixture or an explicit non-goal;
- release profile must block critical/high findings, invalid waivers, active report redaction, and tenant derivation failures;
- `forge-harness-integration.md` gates must be mapped to harness observability for Postgres-backed `rumble-*` products;
- recurring product findings must become shared fixtures/rules or bounded waivers, never product-local DB-security check duplication.
