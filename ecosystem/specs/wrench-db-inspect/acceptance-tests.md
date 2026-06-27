# Wrench DB Inspect — Acceptance Tests

Status: Draft contract before implementation.

## Scope

These acceptance tests define the minimum behavior expected from `wrench-db-inspect` before any production use as a Bolt/CI gate.

The tests are fixture-driven and must be runnable offline. They must not require a live database, network service, SaaS, secrets, or personal data.

## Test Command Contract

Reference command for fixture tests:

```text
wrench-db-inspect run \
  --manifest fixtures/<case>/manifest.json \
  --schema-dump fixtures/<case>/schema.sql \
  --migrations fixtures/<case>/migrations \
  --profile protected_branch \
  --report-json target/<case>.report.json
```

If a fixture has no migration directory, the implementation may pass only `--schema-dump` and `--manifest`, but the expected outcome must stay identical.

## Global Acceptance Criteria

For every fixture run:

- output JSON uses the `{ data, meta }` envelope;
- `data.format = "wrench.db_inspect.report.v0.1"`;
- findings are deterministic and sorted by severity then `rule_id` then subject;
- no finding evidence contains row data, query parameter values, DSNs, tokens, raw credentials, raw embeddings, prompts, or source text;
- parser/inspection uncertainty is represented as `inspection_integrity` or `manifest_coverage`, never silently ignored;
- exit code follows the selected gate profile;
- report includes input content hashes or stable fixture-relative references.

## P0 Fixture Matrix

| Fixture | Expected status | Expected blocking | Required finding rules |
| --- | --- | --- | --- |
| `pass/rls_tenant_policy_ok` | `passed` | false | none blocking |
| `fail/rls_missing_on_tenant_table` | `failed` | true | `RLS_REQUIRED_TENANT_TABLE` |
| `fail/grant_all_to_app_role` | `failed` | true | `GRANT_ALL_ON_TENANT_TABLE` |
| `fail/pgvector_global_embedding_leak` | `failed` | true | `PGVECTOR_TENANT_FILTER_REQUIRED` |
| `unknown/unclassified_table` | `failed` for `protected_branch` | true | `TABLE_CLASSIFICATION_REQUIRED` |
| `waiver/critical_with_valid_expiring_waiver` | `passed_with_waiver` | false | `RLS_REQUIRED_TENANT_TABLE` marked waived |
| `waiver/critical_with_expired_waiver` with `release` | `failed` | true | waiver reason `expired` |
| `waiver/critical_with_incomplete_waiver` with `release` | `failed` | true | waiver reason `missing reviewer` |
| `fail/rls_not_forced_on_tenant_table` | `failed` | true | `FORCE_RLS_REQUIRED_TENANT_TABLE` |
| `fail/disable_rls_migration` | `failed` | true | `DISABLE_RLS_FORBIDDEN` |
| `fail/dangerous_drop_table` | `failed` | true | `DROP_TABLE_DANGEROUS` |
| `fail/dangerous_drop_column` | `failed` | true | `DROP_COLUMN_DANGEROUS` |
| `fail/truncate_dangerous` | `failed` | true | `TRUNCATE_DANGEROUS` |
| `fail/unqualified_delete` | `failed` | true | `UNQUALIFIED_DELETE_DANGEROUS` |
| `fail/unqualified_update` | `failed` | true | `UNQUALIFIED_UPDATE_DANGEROUS` |
| `warn/security_definer_missing_search_path` | `passed` | false | `SECURITY_DEFINER_SEARCH_PATH_REQUIRED` medium |
| `warn/tenant_column_nullable` | `passed` | false | `TENANT_COLUMN_NOT_NULL_REQUIRED` medium |
| `warn/view_without_tenant_filter` | `passed` | false | `VIEW_TENANT_FILTER_REQUIRED` medium |
| `warn/function_without_tenant_filter` | `passed` | false | `FUNCTION_TENANT_FILTER_REQUIRED` medium |

## Scenario Tests

### AT-001 — Tenant table with RLS and tenant policy passes

Given a tenant-scoped table classified in the manifest,
And the table has `organization_id`, RLS enabled, forced RLS, and policies constrained by `current_setting('app.organization_id', true)`,
When the inspector runs with `protected_branch`,
Then no blocking findings are emitted,
And exit code is `0`.

### AT-002 — Missing RLS blocks CI

Given a tenant-scoped table classified in the manifest,
And the table does not enable RLS,
When the inspector runs with `protected_branch`,
Then it emits `RLS_REQUIRED_TENANT_TABLE` with `critical` severity and `high` confidence,
And exit code is `1`.

### AT-003 — Over-broad app grant blocks CI

Given an app role declared in the manifest,
And a tenant-scoped table grants `ALL` to that role,
When the inspector runs,
Then it emits `GRANT_ALL_ON_TENANT_TABLE`,
And remediation suggests least-privilege grants.

### AT-004 — pgvector search without tenant filter blocks CI

Given a table containing embeddings,
And a similarity search function or view ranks/limits before enforcing organization isolation,
When the inspector runs,
Then it emits `PGVECTOR_TENANT_FILTER_REQUIRED`,
And the report does not include raw vectors or source text.

### AT-005 — Unknown table classification fails closed

Given a schema contains a non-system table not classified by the manifest,
When the inspector runs with `protected_branch` or `release`,
Then it emits `TABLE_CLASSIFICATION_REQUIRED`,
And the gate blocks because tenant isolation cannot be proven.

### AT-006 — Valid waiver is explicit and bounded

Given a critical finding exists,
And the manifest includes a waiver bound to the exact rule, subject, owner, reviewer, expiry, and input hash or fixture reference,
When the inspector runs before expiry,
Then the finding remains present but marked `waived`,
And `data.summary.gate_blocked = false`,
And `data.status = "passed_with_waiver"`.

### AT-007 — Expired or incomplete waiver does not pass release

Given a waiver is expired, missing expiry, missing owner, missing reviewer, or not bound to rule + subject,
When the inspector runs with `release`,
Then the original DB finding remains visible,
And a separate `WAIVER_INVALID` finding is emitted for waiver accounting,
And `gate.blocks=true`,
And `gate.reason` explains the waiver defect without exposing sensitive content.

### AT-008 — Dangerous migrations block CI

Given a migration disables RLS, drops a table/column, truncates data, or runs `DELETE`/`UPDATE` without a `WHERE` clause,
When the inspector runs with `protected_branch`,
Then it emits the matching `migration_safety` finding,
And exit code is `1`.

### AT-009 — P1 warnings do not block protected branch

Given a `SECURITY DEFINER` function lacks fixed `search_path`, a tenant-scoped table has nullable `organization_id`, or a view/function reads a tenant table without an explicit tenant filter,
When the inspector runs with `protected_branch`,
Then it emits a `medium` finding,
And exit code is `0`,
And `data.summary.gate_blocked = false`.

### AT-010 — Report redaction is mandatory

Given fixture SQL contains fake secret-like comments, fake tokens, or placeholder DSNs,
When JSON and Markdown reports are generated,
Then secret-like values are omitted from both reports,
And source SQL comments are not copied as evidence,
And final report rendering redacts DSN/token/password-like patterns if future evidence snippets contain them,
And `meta.redaction.secrets_or_pii_included = false`.

Forbidden regression strings include fixture-only values such as `sk_test_fixture_redaction_123456`, `fixture_password`, and `postgres://fixture_user`.

When profile is `release` and final report rendering applies redaction, the report-level gate must block with reason `redaction applied in release requires review`.

## Pending Tenant-Derivation Acceptance Tests

These fixtures are intentionally not part of `run-fixtures.sh` until derived-tenant validation is implemented.

| Fixture | Future expected status | Required future rule |
| --- | --- | --- |
| `pending/tenant_derivation_missing_fk` | `failed` in `release` | `TENANT_DERIVATION_FK_REQUIRED` |
| `pending/tenant_derivation_policy_without_join` | `failed` in `release` | `TENANT_DERIVATION_POLICY_REQUIRED` |

Future acceptance:

- Given a table declares `tenant_derivation`, the inspector validates the relationship path is backed by FK/relationship evidence.
- Given a derived table has RLS, the inspector validates the policy constrains access through the declared tenant path.
- Given derived-tenant validation is unsupported in `release`, the gate must fail closed or require explicit waiver.

## Bolt/CI Acceptance

A Bolt gate consuming the report must:

- trust `summary.gate_blocked` and exit code, not reinterpret raw SQL;
- attach the JSON report as evidence artifact;
- require human security review for critical/high waivers;
- fail if `meta.redaction.secrets_or_pii_included != false`;
- fail if the report format version is unsupported.
