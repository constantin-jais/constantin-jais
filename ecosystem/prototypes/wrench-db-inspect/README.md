# wrench-db-inspect prototype

This is the local Rust prototype for the `wrench-db-inspect` contracts in `ecosystem/specs/wrench-db-inspect`.

It demonstrates the intended CLI, report envelope, fixture-driven rules, gate behavior, and safe output constraints before a production repository exists. It is intentionally not a final production implementation.

## What This Prototype Proves

- SQL/schema + manifest inputs can produce deterministic findings.
- P0 findings can block CI through exit code `1`.
- P1 findings can remain visible without blocking adoption.
- JSON reports use `{ data, meta }`, include safe `data.metrics`, and Markdown reports are human/agent-readable.
- Fixtures can encode security regressions before production code exists.

## What It Does Not Prove Yet

- Full PostgreSQL grammar coverage.
- Low false-positive rate on real Rumble schemas.
- Live DB inspection.
- Production-grade waiver lifecycle.
- Final Bolt integration around gate profile selection. Prototype profile configuration is implemented with `--gate-profile-config <path>`; the contract is in `../../specs/wrench-db-inspect/gate-profiles.md`.

## Dependencies

Dependencies are permissive and sovereignty-compatible for this prototype:

- `serde` / `serde_json`: MIT OR Apache-2.0;
- `sqlparser`: Apache-2.0;
- `regex`: MIT OR Apache-2.0 (transitive `aho-corasick`: Unlicense OR MIT).

## Structure

```text
src/
  main.rs       CLI wiring and file IO
  manifest.rs   manifest contract parsing
  sql_facts.rs  SQL/DDL/DCL fact extraction via sqlparser + fallback strategy
  rules.rs      security rule evaluation and waiver matching
  report.rs       JSON/Markdown report rendering
  redaction.rs    final-pass redaction scanner for report strings
  gate_profile.rs gate profile config, action resolution, gate decisions
  finding.rs      finding model and severity ordering
```

## Current rules

The prototype uses `serde_json` for manifests/reports and `sqlparser` for supported PostgreSQL DDL/DCL facts. PostgreSQL functions and extension-specific constructs still use conservative text fallback where parser support is incomplete.

- `RLS_REQUIRED_TENANT_TABLE`
- `GRANT_ALL_ON_TENANT_TABLE`
- `PGVECTOR_TENANT_FILTER_REQUIRED`
- `TABLE_CLASSIFICATION_REQUIRED`
- `FORCE_RLS_REQUIRED_TENANT_TABLE`
- `DISABLE_RLS_FORBIDDEN`
- `DROP_TABLE_DANGEROUS`
- `DROP_COLUMN_DANGEROUS`
- `TRUNCATE_DANGEROUS`
- `UNQUALIFIED_DELETE_DANGEROUS`
- `UNQUALIFIED_UPDATE_DANGEROUS`

Current P1 warning rules:

- `SECURITY_DEFINER_SEARCH_PATH_REQUIRED`
- `TENANT_COLUMN_NOT_NULL_REQUIRED`
- `VIEW_TENANT_FILTER_REQUIRED`
- `FUNCTION_TENANT_FILTER_REQUIRED`

## Success Criteria For The Prototype

The prototype is healthy when:

- `cargo test` passes;
- `./run-fixtures.sh` passes all fixtures, including release-profile expired/incomplete waiver cases and separate `WAIVER_INVALID` accounting;
- generated JSON reports parse successfully;
- P0 fail fixtures exit `1`;
- pass/waiver/warn fixtures exit `0`;
- reports do not include row data, raw embeddings, prompts, credentials, DSNs, or PII;
- redaction fixtures with fake DSNs/tokens/comments do not leak those strings into JSON or Markdown reports;
- final report rendering redacts DSN/token/password-like patterns even if future evidence snippets accidentally contain them;
- JSON reports expose `data.metrics.redactions_applied_count` for review.

Broader success metrics for the project are defined in `../../specs/wrench-db-inspect/success-metrics.md`.

## Run tests

```text
cargo test
./run-fixtures.sh
```

## Run a fixture

```text
cargo run -- run \
  --manifest ../../specs/wrench-db-inspect/fixtures/fail/rls_missing_on_tenant_table/manifest.json \
  --schema-dump ../../specs/wrench-db-inspect/fixtures/fail/rls_missing_on_tenant_table/schema.sql \
  --profile protected_branch \
  --gate-profile-config ../../specs/wrench-db-inspect/fixtures/gate-profiles/default.json \
  --report-json /tmp/wrench-db-inspect.report.json \
  --report-md /tmp/wrench-db-inspect.report.md
```

Expected exit codes match the spec:

- `0` when no unwaived blocking finding exists;
- `1` when protected-branch blocking findings exist;
- `2` for invalid invocation/configuration.

## Boundaries

- No DB connection.
- No mutation.
- No row data.
- No secrets/PII in reports.
- No ORM or migration behavior.
