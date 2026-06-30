# Wrench DB Inspect — Forge & Harness Integration

Status: Integration positioning for `rumble-*` builds.

## Positioning

`wrench-db-inspect` is the shared Wrench database-security gate for Postgres-backed `rumble-*` products. It must be integrated as forge/harness evidence, not as a product-local checklist.

The intended loop is:

1. a `rumble-*` product declares whether it uses Postgres;
2. if yes, the forge scaffold requires a DB security manifest and sanitized schema dump step;
3. CI/harness runs `wrench-db-inspect` with the selected profile;
4. Bolt/harness stores the JSON/Markdown reports as evidence artifacts;
5. recurring findings become shared fixtures/rules in `wrench-db-inspect`, not duplicated product scripts.

## Product contract

Every Postgres-backed `rumble-*` should provide:

```text
rumble-*/
  db/
    security-manifest.json
    migrations/
  target/
    schema.sql
    wrench-db-inspect.report.json
    wrench-db-inspect.report.md
```

A product that does not use Postgres should declare that explicitly in its build metadata/spec so the harness can mark DB inspection as not applicable rather than missing.

## Forge scaffold requirements

When the forge creates or upgrades a Postgres-backed `rumble-*`, it should add:

- `db/security-manifest.json` seeded from the appropriate shared example;
- a schema dump command that emits sanitized DDL only to `target/schema.sql`;
- a `wrench-db-inspect` job for `pull_request`, `protected_branch`, and `release` contexts;
- artifact upload for JSON and Markdown reports;
- a note forbidding product-local RLS/grant/migration checker duplication.

Reference command:

```bash
wrench-db-inspect run \
  --manifest db/security-manifest.json \
  --schema-dump target/schema.sql \
  --migrations db/migrations \
  --profile protected_branch \
  --gate-profile-config db/wrench-db-gate-profiles.json \
  --report-json target/wrench-db-inspect.report.json \
  --report-md target/wrench-db-inspect.report.md
```

## Harness gates

The harness should expose these observable gates from the report contract:

| Gate | Source | Expected |
| --- | --- | --- |
| `db_manifest_present` | build inputs | true for Postgres products |
| `db_schema_dump_present` | build inputs | true for Postgres products |
| `db_inspect_gate_blocked` | `data.summary.gate_blocked` | false |
| `db_inspect_report_redaction_applied` | `meta.redaction.applied` | false in release |
| `db_inspect_secrets_or_pii_included` | `meta.redaction.secrets_or_pii_included` | false |
| `db_unclassified_tables_count` | findings with `TABLE_CLASSIFICATION_REQUIRED` | 0 |
| `db_rls_missing_count` | findings with `RLS_REQUIRED_TENANT_TABLE` | 0 |
| `db_force_rls_missing_count` | findings with `FORCE_RLS_REQUIRED_TENANT_TABLE` | 0 in protected/release |
| `db_dangerous_grants_count` | `grant_privilege` blocking findings | 0 |
| `db_dangerous_migrations_count` | `migration_safety` blocking findings | 0 |
| `db_tenant_derivation_failed_count` | `TENANT_DERIVATION_*` blocking findings | 0 in release |
| `db_pgvector_leakage_count` | `PGVECTOR_TENANT_FILTER_REQUIRED` | 0 |
| `db_invalid_waiver_count` | `WAIVER_INVALID` | 0 in release |

The harness must consume the JSON report contract. It must not re-parse raw SQL or create hidden policy logic.

## Build lifecycle

For every product build involving DB changes:

1. generate sanitized schema dump;
2. validate manifest/report contracts;
3. run `wrench-db-inspect`;
4. attach reports as artifacts;
5. fail or pass based on the selected profile;
6. triage findings into product fixes, bounded waivers, or shared fixture/rule improvements.

## Finding feedback loop

When a product exposes a new recurring DB-security case:

- if true positive: fix product schema/migration/policy;
- if false positive: add a minimal sanitized fixture before changing the rule;
- if unsupported but safe SQL form: add fixture + parser/rule enhancement;
- if product exception: add bounded waiver with owner, reviewer, expiry, rule, and exact subject;
- never copy inspector logic into the `rumble-*` repo.

## Completeness signal

A `rumble-*` product is considered DB-gate integrated when:

- its Postgres applicability is explicit;
- manifest and sanitized schema dump are produced by the build;
- `wrench-db-inspect` runs in PR/protected/release contexts;
- JSON/Markdown reports are stored as harness artifacts;
- release blocks on report redaction, invalid waivers, high/critical findings, and tenant derivation failures;
- all recurring product-specific cases have been promoted to shared fixtures or documented as bounded waivers.
