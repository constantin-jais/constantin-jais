# Wrench DB Inspect Fixtures

These fixtures are executable contracts for `wrench-db-inspect`.

Each case should contain:

- `schema.sql` — sanitized PostgreSQL schema or SQL excerpt;
- `manifest.json` — `{ data, meta }` DB security manifest;
- optional `migrations/` — ordered SQL migrations;
- optional `expected-report.json` — minimal expected report shape.

Fixtures must not contain real secrets, DSNs, row data, raw embeddings, prompts, source text, or personal data.

## Cases

| Case | Purpose |
| --- | --- |
| `pass/rls_tenant_policy_ok` | Positive tenant table with RLS, forced RLS, tenant policy, least-privilege grant. |
| `pass/tenant_derivation_table_level_fk_ok` | Positive one-hop derived tenant path with table-level FK and policy join; passes in `release`. |
| `pass/tenant_derivation_reversed_equality_ok` | Positive one-hop derived tenant path with reversed equality operands; passes in `release`. |
| `pass/tenant_derivation_multihop_ok` | Positive multi-hop derived tenant path with FK chain and policy proof; passes in `release`. |
| `fail/rls_missing_on_tenant_table` | Tenant table classified in manifest but RLS not enabled. |
| `fail/grant_all_to_app_role` | Over-broad app grant on tenant-scoped table. |
| `fail/grant_to_unknown_role` | Grant to role absent from manifest. |
| `fail/pgvector_global_embedding_leak` | Embedding search without enforceable tenant filter. |
| `unknown/unclassified_table` | Schema table missing manifest classification. |
| `waiver/critical_with_valid_expiring_waiver` | Critical finding remains visible but gate passes due to bounded waiver. |
| `waiver/critical_with_expired_waiver` | Release profile blocks an expired waiver. |
| `waiver/critical_with_incomplete_waiver` | Release profile blocks a waiver missing required reviewer metadata. |
| `fail/rls_not_forced_on_tenant_table` | Tenant table has RLS enabled but not forced. |
| `fail/disable_rls_migration` | Migration disables RLS. |
| `fail/set_row_security_off` | Migration/session SQL disables PostgreSQL `row_security`. |
| `fail/dangerous_drop_table` | Migration drops a table. |
| `fail/dangerous_drop_column` | Migration drops a column. |
| `fail/drop_policy_dangerous` | Migration drops an RLS policy. |
| `fail/drop_constraint_dangerous` | Migration drops a constraint. |
| `fail/drop_foreign_key_dangerous` | Migration drops a foreign key. |
| `fail/no_force_rls_forbidden` | Migration disables forced RLS. |
| `fail/drop_not_null_dangerous` | Migration drops a `NOT NULL` constraint from a column. |
| `fail/truncate_dangerous` | Migration truncates a table. |
| `fail/unqualified_delete` | Migration deletes without `WHERE`. |
| `fail/unqualified_update` | Migration updates without `WHERE`. |
| `warn/security_definer_missing_search_path` | P1 warning for `SECURITY DEFINER` function without fixed `search_path`. |
| `warn/tenant_column_nullable` | P1 warning for nullable tenant column on tenant-scoped table. |
| `warn/view_without_tenant_filter` | P1 warning for view reading tenant table without explicit tenant filter. |
| `warn/function_without_tenant_filter` | P1 warning for function reading tenant table without explicit tenant filter. |
| `fail/grant_all_schema_dangerous` | Over-broad `GRANT ALL ON SCHEMA`. |
| `fail/grant_all_tables_in_schema_dangerous` | Over-broad `GRANT ALL ON ALL TABLES IN SCHEMA`. |
| `fail/grant_all_public_dangerous` | Over-broad grant to `PUBLIC`. |
| `fail/default_privileges_grant_all_dangerous` | Over-broad `ALTER DEFAULT PRIVILEGES ... GRANT ALL` for future objects. |
| `fail/tenant_derivation_wrong_setting` | Derived tenant policy uses the wrong session setting; blocks in `release`. |
| `fail/tenant_derivation_path_invalid` | Derived tenant path syntax is malformed/unsupported; blocks in `release`. |
| `fail/tenant_derivation_multihop_policy_missing` | Multi-hop derived tenant path with FK chain but missing policy proof; blocks in `release`. |
| `redaction/secret_like_sql_comments` | Regression fixture ensuring fake DSN/token/comment content does not leak into JSON/Markdown reports. |
| `fail/tenant_derivation_missing_fk` | Derived tenant path declared in manifest but not backed by FK evidence; blocks in `release`. |
| `fail/tenant_derivation_policy_without_join` | FK exists but RLS policy does not enforce declared tenant derivation; blocks in `release`. |
