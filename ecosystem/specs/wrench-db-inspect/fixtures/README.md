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
| `fail/rls_missing_on_tenant_table` | Tenant table classified in manifest but RLS not enabled. |
| `fail/grant_all_to_app_role` | Over-broad app grant on tenant-scoped table. |
| `fail/pgvector_global_embedding_leak` | Embedding search without enforceable tenant filter. |
| `unknown/unclassified_table` | Schema table missing manifest classification. |
| `waiver/critical_with_valid_expiring_waiver` | Critical finding remains visible but gate passes due to bounded waiver. |
| `waiver/critical_with_expired_waiver` | Release profile blocks an expired waiver. |
| `waiver/critical_with_incomplete_waiver` | Release profile blocks a waiver missing required reviewer metadata. |
| `fail/rls_not_forced_on_tenant_table` | Tenant table has RLS enabled but not forced. |
| `fail/disable_rls_migration` | Migration disables RLS. |
| `fail/dangerous_drop_table` | Migration drops a table. |
| `fail/dangerous_drop_column` | Migration drops a column. |
| `fail/truncate_dangerous` | Migration truncates a table. |
| `fail/unqualified_delete` | Migration deletes without `WHERE`. |
| `fail/unqualified_update` | Migration updates without `WHERE`. |
| `warn/security_definer_missing_search_path` | P1 warning for `SECURITY DEFINER` function without fixed `search_path`. |
| `warn/tenant_column_nullable` | P1 warning for nullable tenant column on tenant-scoped table. |
| `warn/view_without_tenant_filter` | P1 warning for view reading tenant table without explicit tenant filter. |
| `warn/function_without_tenant_filter` | P1 warning for function reading tenant table without explicit tenant filter. |
| `redaction/secret_like_sql_comments` | Regression fixture ensuring fake DSN/token/comment content does not leak into JSON/Markdown reports. |
| `pending/tenant_derivation_missing_fk` | Pending/xfail fixture: derived tenant path declared in manifest but not backed by FK evidence. Not run until derivation validation exists. |
| `pending/tenant_derivation_policy_without_join` | Pending/xfail fixture: FK exists but RLS policy does not enforce declared tenant derivation. Not run until derivation validation exists. |
