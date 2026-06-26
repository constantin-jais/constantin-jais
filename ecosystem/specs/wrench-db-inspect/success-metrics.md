# Wrench DB Inspect — Success Metrics

Status: Draft measurement contract.

## Purpose

These metrics define how to know whether `wrench-db-inspect` succeeds after implementation. The goal is not to maximize rule count. The goal is to reduce dangerous DB/security duplication across Rumbles while producing trustworthy CI evidence without leaking secrets or PII.

Metrics are aggregate and report-level only. They must not include row data, raw embeddings, prompts, credentials, DSNs, query parameter values, user names, emails, or free-text product content.

## North-Star Outcomes

`wrench-db-inspect` is successful when:

1. Rumbles stop implementing local DB-security checks for RLS, grants, migrations, `pgvector`, and tenant isolation.
2. CI/Bolt can block high-risk DB changes with deterministic, explainable evidence.
3. Product teams get useful remediation without excessive false positives.
4. Reports remain safe to share with humans and agents.
5. The tool stays an inspector, not an ORM, migration runner, proxy, vault, or runtime policy engine.

## Metric Groups

### 1. Coverage Metrics

These measure whether the inspector sees enough of the DB security surface.

| Metric | Meaning | Initial target |
| --- | --- | --- |
| `tenant_table_classification_coverage` | Tenant/global/audit classification for non-system tables. | 100% for protected branch/release. |
| `tenant_rls_coverage` | Tenant-scoped tables with RLS enabled. | 100% for protected branch/release. |
| `tenant_force_rls_coverage` | Tenant-scoped tables with forced RLS where applicable. | 100% or explicit waiver. |
| `policy_tenant_filter_coverage` | Tenant policies/functions/views with explicit `organization_id` constraint. | Trending toward 100%; P0/P1 split by confidence. |
| `grant_coverage` | App/read-only/migration roles inspected against table grants. | 100% of manifest roles. |
| `migration_coverage` | Ordered migrations parsed or explicitly reported as unsupported. | 100% parsed or fail-closed for P0. |
| `pgvector_tenant_coverage` | Embedding tables/search helpers classified and tenant-filtered. | 100% for tables marked `contains_embeddings=true`. |
| `adapter_scan_coverage` | DB adapter files scanned for panic/unwrap safety. | 100% of configured adapter paths when enabled. |

### 2. Gate Effectiveness Metrics

These measure whether CI/Bolt gates catch important problems at the right moment.

| Metric | Meaning | Initial target |
| --- | --- | --- |
| `blocking_findings_by_profile` | Count of findings that block per `local`, `pull_request`, `protected_branch`, `release`. | Stable and explainable. |
| `critical_escape_rate` | Critical DB issues found after merge/release that should have been caught earlier. | 0. |
| `waiver_rate_by_rule` | Share of findings waived per rule. | Low; rising trend triggers rule/product review. |
| `expired_waiver_count` | Waivers past expiry still present in CI inputs. | 0 in release. |
| `waiver_invalid_count` | Separate `WAIVER_INVALID` findings for expired/incomplete waiver metadata. | 0 in release. |
| `unknown_state_count` | Unsupported SQL, missing manifest classification, unreadable input, parser uncertainty. | 0 in release; visible elsewhere. |
| `time_to_remediate_high_critical` | Time between first finding and fix/valid waiver. | Decreasing trend. |

### 3. Signal Quality Metrics

These measure whether developers trust the tool.

| Metric | Meaning | Initial target |
| --- | --- | --- |
| `false_positive_rate_reviewed` | Reviewed findings marked incorrect or too noisy. | < 10% for P0 before enforcing broadly. |
| `false_negative_incidents` | Incidents/manual discoveries missed by existing rules. | 0 critical; trend down for high/medium. |
| `finding_actionability_score` | Human review score: evidence + remediation enough to act. | ≥ 4/5 for P0. |
| `duplicate_finding_rate` | Same root issue reported multiple times confusingly. | Low; exact target after first runs. |
| `determinism_rate` | Same inputs produce same finding IDs/order/status. | 100%. |

### 4. Safety and Privacy Metrics

These ensure the inspector remains safe to run and share.

| Metric | Meaning | Target |
| --- | --- | --- |
| `report_secret_leak_count` | Secrets/DSNs/tokens detected in generated reports. | 0. |
| `report_pii_leak_count` | PII or row/free-text content detected in reports. | 0. |
| `raw_embedding_leak_count` | Raw vectors or source text emitted in reports. | 0. |
| `mutating_operation_count` | Live inspection attempts DDL/DML or row reads. | 0. |
| `redaction_status` | `meta.redaction.secrets_or_pii_included` remains false and `meta.redaction.applied` indicates whether final-pass redaction changed the report. | Always no secrets/PII; `applied=true` blocks/requires review in release. |
| `redaction_regression_pass` | Fake DSN/token/password fixtures and synthetic future evidence snippets are absent from JSON/Markdown reports. | 100%. |
| `redactions_applied_count` | Number of final report string redactions applied. Useful for detecting accidental evidence leakage before publish. | Tracked; unexpected non-zero requires review. |

### 5. Adoption and Anti-Duplication Metrics

These measure whether the shared tool prevents risky local reinvention.

| Metric | Meaning | Initial target |
| --- | --- | --- |
| `rumble_db_manifest_adoption` | Rumbles with Postgres that provide DB security manifest. | 100% before release gates. |
| `local_db_security_check_count` | Product-local scripts duplicating RLS/grant/migration checks. | Trend toward 0 or wrappers only. |
| `shared_fixture_reuse_count` | Rumbles adding issues as shared fixtures instead of local-only tests. | Increasing. |
| `bolt_gate_integration_count` | Bolt/CI pipelines consuming JSON report as evidence. | All Postgres-backed Rumbles. |
| `manual_security_review_reduction` | Repeated manual DB review items automated by the inspector. | Increasing without losing quality. |

### 6. Performance and Operability Metrics

These keep the tool usable in CI.

| Metric | Meaning | Initial target |
| --- | --- | --- |
| `ci_runtime_seconds` | Wall time for typical migration/schema inspection. | < 30s for MVP projects. |
| `report_size_bytes` | JSON report size. | Small enough for CI artifacts; no raw content. |
| `parser_error_rate` | Parse errors per run/input. | Decreasing; P0-affecting errors fail closed. |
| `fixture_pass_rate` | Contract fixture suite pass rate. | 100%. |
| `profile_config_validation_failures` | Invalid gate config detected before run. | 0 in committed CI configs. |

## Suggested Report Additions

Future reports should include safe aggregate metrics under `data.metrics`:

```json
{
  "data": {
    "metrics": {
      "tenant_table_classification_coverage": 1.0,
      "tenant_rls_coverage": 1.0,
      "tenant_force_rls_coverage": 0.875,
      "unknown_state_count": 0,
      "waiver_count": 1,
      "waiver_invalid_count": 0,
      "blocking_finding_count": 0,
      "parser_error_count": 0,
      "redactions_applied_count": 0
    }
  },
  "meta": {
    "redaction": {
      "secrets_or_pii_included": false
    }
  }
}
```

## Success Thresholds By Maturity

### Prototype

- Fixture suite green.
- Deterministic JSON shape.
- No secrets/PII in fixtures or reports.
- P0 rules represented by at least one pass and one fail fixture.

### MVP CI Gate

- Protected branch blocks P0 critical/high with high confidence.
- Manifest coverage required for every non-system table.
- Unknown P0 analysis state fails closed.
- Reports include coverage metrics and safe redaction metadata.
- Bolt consumes report artifacts without re-parsing SQL.

### Production-Ready

- False positive rate reviewed and acceptable.
- Critical escape rate remains 0 over multiple release cycles.
- Rumbles no longer maintain divergent DB-security scripts.
- Gate profiles are explicit, versioned, reviewed, and auditable.
- Live DB inspection, if enabled, is read-only and optional.

## Review Cadence

- Per PR: gate status, blocking findings, report redaction.
- Weekly during adoption: false positives, unknown states, waiver trends.
- Per release: coverage, expired waivers, critical escape rate, duplicate local checks.
- Per incident/security review: missed rule candidates become shared fixtures before code changes.
