# Wrench DB Inspect — SQL/Database Security Inspector

Status: Draft accepted for P0/P1 prototype scoping.

## Quick Summary

`wrench-db-inspect` is the shared Wrench inspector for PostgreSQL database security evidence across Rumble products. It centralizes checks that would be dangerous to duplicate locally: tenant isolation, RLS, grants, unsafe migrations, `pgvector` leakage, and DB-adapter safety signals.

It produces safe CI/Bolt evidence for humans and agents. It does not execute migrations, proxy database traffic, store credentials, replace application authorization, or become an ORM.

## How To Read This Spec

- Start with **Mission** and **Hard Boundaries** to understand what the tool owns and refuses.
- Use **P0/P1/P2 Scope** to decide which rules block, warn, or remain advisory.
- Use **Inputs** and **JSON Report Contract** to implement integrations.
- Use **Avoiding False Positives and Silent Bypass** before changing rule severity.
- Use **Bolt/CI Gate Integration** for pipeline behavior.
- Use `ci-integration.md` for concrete Bolt/CI commands, artifacts, and rollout.
- Use `gate-profiles.md` to understand configurable blocking policy.
- Use `acceptance-tests.md`, `fixtures/`, `success-metrics.md`, and `completeness-plan.md` to verify implementation quality and remaining work.

Companion contracts:

- `acceptance-tests.md` defines fixture-driven acceptance criteria before implementation.
- `success-metrics.md` defines how to measure implementation success and adoption quality.
- `completeness-plan.md` maps each rule to required fixtures, gates, and pre-production gaps.
- `gate-profiles.md` defines the configurable CI/Bolt blocking policy.
- `ci-integration.md` defines command-line integration, report artifacts, exit codes, and rollout.
- `fixtures/` contains sanitized SQL/manifest/report contract cases.
- `contracts/manifest.v0.1.schema.json` and `contracts/report.v0.1.schema.json` define the JSON contracts.
- `scripts/validate-json-contracts.py` validates fixture/example manifests and expected reports offline.
- `adr/0002-db-security-manifest-required.md` requires DB security manifests for Postgres Rumbles.
- `adr/0003-live-db-readonly-optional.md` keeps live DB inspection optional and read-only.
- `adr/0004-prototype-to-dedicated-repo.md` proposes extracting the prototype into a dedicated repo.
- `extraction-readiness.md` defines the checklist before extraction.
- `pilot-plan.md` defines how to pilot the inspector on the first real Rumble.
- `examples/security-manifest.rumble-lm.example.json` seeds the first LM manifest.
- `pilots/rumble-lm/` contains the initial pilot workspace.
- `../../prototypes/wrench-db-inspect/` contains a Rust prototype for the first fixture gates.

## Mission

`wrench-db-inspect` is a Wrench-layer inspector for database security evidence. It validates PostgreSQL-oriented SQL, migrations, schema dumps, read-only live database metadata, `pgvector` usage, grants, row-level security, and tenant-isolation conventions for Rumble products.

It exists to produce deterministic CI gates and readable reports for humans and agents. It strengthens every Rumble without owning runtime access, migrations, application authorization, credentials, or product policy.

Success is measured by reduced duplicated DB-security logic in Rumbles, high tenant/RLS/grant coverage, low false positives, zero report leakage, and reliable Bolt/CI gate evidence. See `success-metrics.md`.

Tenant means `organization` unless a product spec explicitly maps a stronger local name to the same boundary.

## Hard Boundaries

`wrench-db-inspect` is not:

- an ORM;
- a migration runner or migration planner;
- a database proxy;
- a vault, secrets manager, or credential broker;
- a runtime authorization engine;
- a replacement for application-level permission checks;
- a generic structural/design inspector; that remains `wrench-inspect`.

Default mode is non-mutating. Any future live database support must use read-only transactions/roles and must never execute DDL/DML.

## Design Inputs From Prior Art

The stack audit identifies useful patterns without importing product scope:

- SQL linting and validation patterns: parse first, normalize AST, attach evidence to concrete SQL spans.
- Embedded/local SQL storage references: keep DB inspection portable and self-hostable; do not require hosted services.
- Distributed SQL/sync references: treat replication and local-first modes as extra threat surfaces, not as reasons to own storage.
- API contract testing references: apply contract/golden-fixture discipline to reports and gates, but do not turn API testing into DB runtime behavior.

## P0 Scope — Blocking Security Checks

P0 findings are CI gate candidates. A P0 check must be deterministic enough to fail a build when confidence is `high`, or require explicit waiver when confidence is lower but risk is critical.

### RLS and Tenant Isolation

- Every tenant-scoped table has RLS enabled.
- RLS is forced where table ownership or privileged app roles could bypass ordinary policies (`FORCE ROW LEVEL SECURITY` when applicable).
- Tenant-scoped tables contain an `organization_id` column or an explicit manifest mapping to organization tenancy.
- Policies constrain access by `organization_id` using approved session context or token-derived claims.
- No tenant policy relies only on application-side comments, naming, or informal conventions.
- Cross-tenant administrative policies are explicit, named, and limited to audited admin/service roles.
- Tables containing sensitive product data are classified as tenant-scoped, global-reference, or audit/system in the manifest; unclassified tables fail P0 when used by Rumbles.

### Grants and Privileges

- Application roles do not own schema objects in production migrations.
- Application roles do not have broad `SUPERUSER`, `BYPASSRLS`, `CREATEDB`, `CREATEROLE`, or unbounded schema privileges.
- Public schema/default privileges are not open to untrusted roles.
- `GRANT ALL` on tenant/sensitive tables is blocked unless explicitly justified and waived.
- Read-only/reporting roles cannot read tenant-scoped tables without RLS-compatible policies.

### Dangerous Migrations

- Destructive DDL is flagged: `DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, unqualified `DELETE`, unqualified `UPDATE`, unsafe type rewrites, disabling constraints/triggers/RLS.
- `ALTER TABLE ... DISABLE ROW LEVEL SECURITY` and `ALTER TABLE ... NO FORCE ROW LEVEL SECURITY` are critical unless in an isolated test fixture.
- Migrations introducing tenant-scoped tables must introduce classification, RLS enablement, policies, and grants in the same migration batch or linked manifest.
- Raw SQL execution from adapters must reject multi-statement surprise where the adapter contract claims single-statement execution.

### `pgvector` Leakage

- Vector embedding tables are classified as tenant-scoped unless manifest marks them global-public with justification.
- Embedding rows include `organization_id` or join to a tenant-scoped owner with enforceable RLS.
- Similarity-search helper functions/views preserve tenant filters before ranking/limit.
- Vector indexes are checked for table ownership/classification; indexes alone are not treated as isolation.
- Reports must never include raw embeddings, source text, prompts, or reconstructed semantic content.

### Adapter Safety Signals

- DB adapters in supported code paths do not use unchecked `unwrap`, `expect`, or `panic!` for connection, query, row decoding, tenant context, migration, or auth-related failures.
- P0 targets Rust first; other languages can be added as parser support matures.
- Findings point to source locations and error-handling remediation, not to runtime secrets or query parameter values.

## P1 Scope — Strong Recommendations

- Detect missing foreign-key/index support for `organization_id` where it affects safe joins or policy performance.
- Detect SECURITY DEFINER functions without fixed `search_path`, owner review, and tenant checks.
- Detect views/functions that may bypass RLS expectations.
- Detect nullable `organization_id` on tenant-scoped tables unless documented for global rows with explicit policies.
- Validate audit/event tables: append-only intent, tenant attribution, no raw secrets/log bodies in metadata.
- Check migration ordering and rollback notes for high-risk DDL.
- Compare schema dump against migrations to detect drift.
- Check local/dev fixtures do not normalize unsafe production grants.
- Verify manifests are versioned and bound to a product/workspace context.

## P2 Scope — Advisory and Ecosystem Hygiene

- Suggest policy naming conventions and common remediation snippets.
- Produce trend metrics over time: finding counts, waived risk age, table coverage.
- Emit SARIF or other external report formats after the core `{ data, meta }` JSON is stable.
- Support additional dialects only as advisory parsing; PostgreSQL remains normative for security gates.
- Add richer code-adapter checks for TypeScript/Hono or other stacks once parser support is reliable.

## Inputs

Inputs are explicit and source-ranked. Reports must record input provenance without secrets.

| Input | P0 use | Notes |
| --- | --- | --- |
| Raw SQL files | Yes | Parse DDL/DCL/DML snippets and policy definitions. |
| Migration directory | Yes | Ordered analysis, migration-batch checks, destructive-change detection. |
| Schema dump | Yes | Baseline truth for tables, RLS, grants, policies, extensions, functions. Must be sanitized. |
| Live DB read-only inspection | Optional P0 | Only with read-only role/transaction; metadata queries only; no secrets in report. |
| Manifest | Yes for classification | Declares tenant model, table classification, expected app roles, allowed waivers, product context. |
| Source adapter paths | Yes for Rust P0 | Static scan for panic/unwrap around DB/security code. |

### Minimal Manifest Shape

```json
{
  "data": {
    "format": "wrench.db_inspect.manifest.v0.1",
    "product": "rumble-lm",
    "tenant": { "canonical_name": "organization", "column": "organization_id" },
    "roles": {
      "app": ["rumble_app"],
      "readonly": ["rumble_readonly"],
      "migration": ["rumble_migrator"]
    },
    "tables": [
      {
        "name": "session_responses",
        "classification": "tenant_scoped",
        "contains_personal_data": true,
        "contains_embeddings": false
      }
    ],
    "waivers": []
  },
  "meta": {
    "schema_version": "0.1",
    "generated_at": "2026-06-30T00:00:00Z"
  }
}
```

## Finding Taxonomy

### Severity

| Severity | Meaning | Default gate |
| --- | --- | --- |
| `critical` | Likely cross-tenant leak, RLS bypass, privileged role exposure, or destructive migration risk. | Block CI unless approved waiver. |
| `high` | Strong security defect with plausible exploit path or data-loss risk. | Block CI for protected branches. |
| `medium` | Risky pattern, incomplete evidence, or context-dependent bypass. | Warn or require review depending gate profile. |
| `low` | Hygiene issue with limited direct risk. | Warn. |
| `info` | Coverage/status evidence. | Never blocks. |

### Categories

- `tenant_isolation`
- `rls_policy`
- `grant_privilege`
- `migration_safety`
- `pgvector_leakage`
- `adapter_safety`
- `manifest_coverage`
- `schema_drift`
- `audit_privacy`
- `inspection_integrity`

### Confidence

- `high`: direct evidence from parsed SQL/schema/live metadata.
- `medium`: strong signal but manifest/source context incomplete.
- `low`: heuristic signal; cannot block without configured strict mode.

### Evidence Requirements

Each finding includes:

- stable `id` and `rule_id`;
- `severity`, `category`, and `confidence`;
- sanitized `subject` such as table, role, policy, migration file, function, or source file;
- evidence snippets limited to SQL structure, line ranges, object names, and hashes;
- no row data, query parameters, raw embeddings, prompts, source text, tokens, DSNs, cookies, or private keys;
- remediation hints;
- gate impact and waiver eligibility.

## JSON Report Contract

All JSON reports use the envelope `{ data, meta }`.

```json
{
  "data": {
    "format": "wrench.db_inspect.report.v0.1",
    "status": "failed",
    "summary": {
      "critical": 1,
      "high": 2,
      "medium": 1,
      "low": 0,
      "info": 3,
      "gate_blocked": true
    },
    "scope": {
      "product": "rumble-lm",
      "tenant": "organization",
      "inputs": [
        {
          "kind": "migration_dir",
          "path": "db/migrations",
          "content_hash": "sha256:..."
        },
        {
          "kind": "manifest",
          "path": "db/security-manifest.json",
          "content_hash": "sha256:..."
        }
      ]
    },
    "findings": [
      {
        "id": "fnd_0001",
        "rule_id": "RLS_REQUIRED_TENANT_TABLE",
        "category": "rls_policy",
        "severity": "critical",
        "confidence": "high",
        "title": "Tenant-scoped table has RLS disabled",
        "subject": {
          "type": "table",
          "name": "session_responses",
          "classification": "tenant_scoped"
        },
        "evidence": [
          {
            "kind": "schema_fact",
            "object": "public.session_responses",
            "fact": "relrowsecurity=false",
            "source": "schema_dump",
            "location": { "file": "schema.sql", "line": 42 }
          }
        ],
        "remediation": {
          "hint": "Enable and force RLS, then add policies constrained by organization_id.",
          "example": "ALTER TABLE public.session_responses ENABLE ROW LEVEL SECURITY;"
        },
        "gate": {
          "blocks": true,
          "profile": "protected_branch",
          "waiver_allowed": true,
          "waiver_requires": ["human_owner", "security_reviewer", "expiry"]
        }
      }
    ],
    "coverage": {
      "tables_total": 12,
      "tenant_scoped_tables": 8,
      "tenant_scoped_with_rls": 7,
      "policies_checked": 15,
      "grants_checked": 9,
      "migrations_checked": 23,
      "adapter_files_checked": 4
    }
  },
  "meta": {
    "schema_version": "0.1",
    "tool": "wrench-db-inspect",
    "tool_version": "0.1.0",
    "generated_at": "2026-06-30T00:00:00Z",
    "run_id": "uuid",
    "redaction": {
      "mode": "strict",
      "secrets_or_pii_included": false
    }
  }
}
```

## Avoiding False Positives and Silent Bypass

- Parse SQL into structured statements; do not rely on regex for P0 findings.
- Separate `not_applicable`, `passed`, `failed`, and `unknown` rule states.
- Treat unknown classification as a finding, not as pass.
- Require manifests for ambiguity: table classification, tenant column mapping, approved app roles, and waiver policy.
- Attach every P0 failure to concrete evidence. If evidence cannot be shown safely, show object/line/hash instead.
- Record skipped files, parse errors, unsupported dialect features, and live-inspection failures as `inspection_integrity` findings.
- Fail closed for P0 gate profiles when parser errors affect tenant/RLS/grant analysis.
- Make waivers explicit, expiring, human-approved, and bound to rule + subject + input hash.
- Never infer safety from naming alone. Names can increase suspicion but cannot prove isolation.
- Support allowlists only through manifest entries with justification, owner, reviewer, and expiry.
- Run differential checks between migrations and schema dumps to detect drift or missing migration coverage.

## Bolt/CI Gate Integration

`wrench-db-inspect` produces evidence; Bolt decides sequencing and gate policy.

Recommended command shape:

```text
wrench-db-inspect run \
  --manifest db/security-manifest.json \
  --migrations db/migrations \
  --schema-dump target/schema.sql \
  --adapter-src crates/app/src/db \
  --profile protected_branch \
  --report-json target/wrench-db-inspect.json \
  --report-md target/wrench-db-inspect.md
```

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | No blocking findings for selected profile. |
| `1` | Blocking findings. |
| `2` | Invalid invocation/configuration. |
| `3` | Inspection integrity failure that makes P0 result unreliable. |

Gate profiles:

- `local`: warn on medium/high, block critical high-confidence only.
- `pull_request`: block critical/high high-confidence; surface medium.
- `protected_branch`: block critical/high and parser/integrity uncertainty over P0 areas.
- `release`: protected-branch rules plus no expired waiver and no unknown tenant classification.

Bolt consumes the JSON report as an artifact reference, reads `summary.gate_blocked`, verifies `meta.redaction.secrets_or_pii_included=false`, and records finding IDs as gate evidence. Bolt must not re-interpret raw SQL; it can require rerun, waiver, or human approval.

## Test Strategy With SQL Fixtures

Fixture layout:

```text
fixtures/
  pass/
    rls_tenant_policy_ok/
    pgvector_tenant_search_ok/
    grants_minimal_ok/
  fail/
    rls_missing_on_tenant_table/
    policy_without_organization_filter/
    grant_all_to_app_role/
    app_role_bypassrls/
    dangerous_drop_table/
    disable_rls_migration/
    pgvector_global_embedding_leak/
    rust_adapter_unwrap_db_error/
  unknown/
    unclassified_table/
    unsupported_sql_construct/
    live_metadata_unavailable/
  waiver/
    critical_with_valid_expiring_waiver/
    expired_waiver_blocks/
```

Test layers:

- Parser unit tests: statement classification, policy extraction, grant extraction, destructive DDL detection.
- Rule tests: one fixture per rule with expected finding IDs and severities.
- Golden report tests: JSON `{ data, meta }` stable shape, sorted findings, deterministic IDs, no secrets/PII fields.
- Redaction tests: DSN/token/embedding/source-text samples never appear in output.
- Gate tests: profile-to-exit-code matrix.
- Drift tests: migrations vs schema dump disagreement produces `schema_drift` or `inspection_integrity` findings.
- Adapter tests: Rust DB adapter snippets with/without `unwrap`, `expect`, `panic!` around security-sensitive paths.

## ADR-0001 — Boundary With `wrench-inspect`

See also:

- `adr/0002-db-security-manifest-required.md`
- `adr/0003-live-db-readonly-optional.md`

Status: Accepted.

### Decision

`wrench-db-inspect` owns database-security inspection for SQL/Postgres/RLS/grants/migrations/pgvector/tenant-isolation evidence. `wrench-inspect` remains the general structural, design, policy, content, readiness, and cross-artifact inspector.

### Rationale

Database isolation failures are high-impact and require specialized parsing, schema semantics, role/grant reasoning, and CI gate profiles. Folding this into a generic inspector would either weaken P0 safety or make `wrench-inspect` a database-security owner by accident.

### Consequences

- Rumble specs can call both inspectors: `wrench-inspect` for product/spec readiness and `wrench-db-inspect` for database security.
- `wrench-db-inspect` may emit findings that `wrench-inspect` references, but it does not judge product UX, journeys, screens, or business completeness.
- `wrench-inspect` may verify that a product declares DB security requirements, but it does not parse SQL/RLS/grants as the source of truth.
- Bolt gates should keep separate evidence artifacts so DB security waivers cannot silently waive unrelated product readiness failures.
