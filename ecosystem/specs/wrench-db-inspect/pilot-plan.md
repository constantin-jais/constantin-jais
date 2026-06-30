# Wrench DB Inspect — Rumble Pilot Plan

Status: Draft rollout plan.

## Purpose

This plan defines how to pilot `wrench-db-inspect` on a real Rumble without creating a migration big-bang or forcing product teams to adopt a premature platform.

The pilot validates the shared Wrench capability against one product, then converts useful findings into shared fixtures/rules rather than product-local DB security scripts.

## Recommended First Pilot

Recommended first pilot: `rumble-lm`.

Reason:

- It has high privacy impact: participant responses, sessions, sources, summaries, exports.
- Tenant isolation and RGPD requirements are explicit.
- Source-grounded learning may later use embeddings/vector search.
- A successful pilot strengthens the strictest data/privacy product first.

Fallback pilot: `rumble-crew`, if execution/evidence/log storage schemas are more concrete at implementation time.

## Pilot Objectives

1. Prove a Rumble DB manifest can describe real tenant/security intent.
2. Run the inspector in warning mode without blocking product work.
3. Identify false positives and missing rules as shared fixtures.
4. Promote only stable P0 rules to protected-branch blocking.
5. Avoid any product-local duplication of RLS/grant/migration checks.

## Entry Criteria

Before starting the pilot:

- The Rumble has a draft or actual Postgres schema/migrations.
- Non-system tables can be classified as:
  - `tenant_scoped`;
  - `global_reference`;
  - `audit_system`;
  - `ephemeral_local` if applicable.
- Expected DB roles are known at least conceptually:
  - app role;
  - read-only/reporting role;
  - migration role.
- The product can identify sensitive tables and embedding tables.
- No real production secrets or row data are needed for the pilot.

## Pilot Artifacts

The pilot must produce:

```text
rumble-*/
  db/security-manifest.json
  target/schema.sql
  target/wrench-db-inspect.json
  target/wrench-db-inspect.md
```

And in the ecosystem/spec repo:

```text
ecosystem/specs/wrench-db-inspect/pilots/<rumble-name>/
  pilot-report.md
  open-findings.md
  false-positive-notes.md
  fixture-candidates.md
```

## Pilot Manifest Example

Concrete examples aligned with the current `rumble-lm` data model are available at:

```text
ecosystem/specs/wrench-db-inspect/examples/security-manifest.rumble-lm.example.json
ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.pass.sql
ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.fail.sql
```

Important mapping: `rumble-lm` uses `workspace_id` as product-local tenant boundary. The manifest maps it to canonical `organization` tenancy.

Expected prototype behavior can be verified with:

```text
cd ecosystem/prototypes/wrench-db-inspect
./run-lm-examples.sh
```

Manual commands:

```text
# pass example: exit 0
wrench-db-inspect run \
  --manifest ecosystem/specs/wrench-db-inspect/examples/security-manifest.rumble-lm.example.json \
  --schema-dump ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.pass.sql \
  --profile protected_branch \
  --gate-profile-config ecosystem/specs/wrench-db-inspect/fixtures/gate-profiles/default.json

# fail example: exit 1, missing RLS + GRANT ALL on public.responses
wrench-db-inspect run \
  --manifest ecosystem/specs/wrench-db-inspect/examples/security-manifest.rumble-lm.example.json \
  --schema-dump ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.fail.sql \
  --profile protected_branch \
  --gate-profile-config ecosystem/specs/wrench-db-inspect/fixtures/gate-profiles/default.json
```

## Pilot Manifest Minimal Shape

```json
{
  "data": {
    "format": "wrench.db_inspect.manifest.v0.1",
    "product": "rumble-lm",
    "tenant": { "canonical_name": "organization", "column": "organization_id" },
    "roles": {
      "app": ["rumble_lm_app"],
      "readonly": ["rumble_lm_readonly"],
      "migration": ["rumble_lm_migrator"]
    },
    "tables": [
      {
        "name": "public.sessions",
        "classification": "tenant_scoped",
        "contains_personal_data": false,
        "contains_embeddings": false
      },
      {
        "name": "public.session_responses",
        "classification": "tenant_scoped",
        "contains_personal_data": true,
        "contains_embeddings": false
      },
      {
        "name": "public.source_embeddings",
        "classification": "tenant_scoped",
        "contains_personal_data": false,
        "contains_embeddings": true
      }
    ],
    "waivers": []
  },
  "meta": {
    "schema_version": "0.1"
  }
}
```

## Pilot Phases

### Phase 0 — Dry Contract Review

- Review product data/security spec.
- Draft manifest from spec, not from implementation guesswork.
- Identify ambiguous tables before writing enforcement logic.

Exit criteria:

- Every table has intended classification.
- Unknown tenancy decisions are documented as product questions.

### Phase 1 — Local Warning Run

Run with `local` profile:

```text
wrench-db-inspect run \
  --manifest db/security-manifest.json \
  --schema-dump target/schema.sql \
  --migrations db/migrations \
  --profile local \
  --gate-profile-config db/wrench-db-gate-profiles.json \
  --report-json target/wrench-db-inspect.json \
  --report-md target/wrench-db-inspect.md
```

Exit criteria:

- Report generates without secrets/PII.
- `meta.redaction.secrets_or_pii_included=false`.
- Any `meta.redaction.applied=true` is investigated.
- Findings are triaged into true positive / false positive / rule gap.

### Phase 2 — Pull Request Gate

Enable `pull_request` for P0 critical/high only.

Exit criteria:

- No critical false positives.
- Developers can remediate findings from report hints.
- Waivers are rare, bounded, reviewed, and expiring.

### Phase 3 — Protected Branch Gate

Enable `protected_branch`.

Exit criteria:

- Unknown table classification is zero.
- P0 parser/integrity uncertainty fails closed.
- No product-local duplicate DB security scripts remain except wrappers around `wrench-db-inspect`.

### Phase 4 — Release Gate

Enable `release`.

Exit criteria:

- No expired/incomplete waivers.
- No redaction applied in release reports.
- Coverage metrics are acceptable.
- Bolt records JSON report as gate evidence.

## Known Prototype Limitations For LM-Derived Tenant Schemas

The current prototype can use the LM manifest as a classification source, but it does not yet fully prove tenant isolation for tables whose tenant boundary is derived through foreign-key paths.

Examples:

- `source_sets` derives tenant from `session_id -> sessions.workspace_id`.
- `source_set_items` derives tenant from `source_set_id -> source_sets.session_id -> sessions.workspace_id`.
- `activity_options` derives tenant from `activity_id -> activities.session_id -> sessions.workspace_id`.
- `participants`, `responses`, `citations`, `summaries`, and `exports` derive tenant from `session_id -> sessions.workspace_id`.

Current limitation:

- `tenant_derivation` is parsed and conservatively validated for supported one-hop and multi-hop FK paths.
- Release profile blocks the current prototype rules `TENANT_DERIVATION_FK_REQUIRED` and `TENANT_DERIVATION_POLICY_REQUIRED`.
- Multi-hop LM derivations are not yet production-proven.
- The prototype now extracts FK and policy facts structurally from `sqlparser` where supported, including inline and table-level FKs.
- Policy proof now traverses the AST expression for `EXISTS` subqueries, parent-child join equality chains, and `current_setting('app.workspace_id', ...)` tenant equality.
- It remains conservative and pattern-based; broader SQL policy forms should be validated against a real LM schema before production release.
- Therefore, a minimal pass schema proves that the manifest and table-level P0 gates work, not that all LM derived-tenant policies are production-safe.

Required before production LM release gate:

- Parse and validate FK/relationship metadata for every `tenant_derivation` path.
- Require RLS policies on derived tables to constrain access through the declared path.
- Add fixtures for broken derivation paths and missing FK/policy joins.
- Promote derived-tenant policy proof to P0 for `release` once false positives are acceptable.

Until then, LM pilot findings for derived-tenant tables must be reviewed by a human security reviewer before release.

## Triage Rules

| Finding outcome | Action |
| --- | --- |
| True positive | Fix schema/migration/policy or add bounded waiver. |
| False positive | Add minimal fixture proving the false positive before changing rule. |
| Missing rule | Add fixture candidate and decide P0/P1/P2. |
| Ambiguous product intent | Update Rumble data/security spec before changing inspector. |
| Redaction applied | Treat as evidence design issue; do not ignore in release. |

## Success Metrics For Pilot

Pilot succeeds when:

- 100% non-system table classification.
- 100% tenant-scoped table RLS coverage or explicit accepted waiver.
- 0 secrets/PII in generated reports.
- 0 release waivers expired/incomplete.
- False positives are documented as fixtures.
- No Rumble-local RLS/grant/migration check duplicates the tool.
- Bolt/CI/harness consumes report contract instead of raw SQL.
- Forge scaffold expectations are validated against `forge-harness-integration.md`.

## Stop Conditions

Stop or pause the pilot if:

- reports include real secrets/PII;
- findings are too noisy to triage;
- product schema intent is not documented;
- a Rumble starts copying the prototype logic locally;
- live DB access is proposed as mandatory.

## Forge/Harness Feedback

The pilot must prove that DB inspection becomes part of the product build flow:

- Postgres-backed products produce `db/security-manifest.json`, sanitized `target/schema.sql`, and report artifacts.
- Non-Postgres products explicitly mark DB inspection as not applicable.
- Harness gates are derived from the JSON report fields, not raw SQL.
- Product findings become shared fixtures/rules or bounded waivers.
- No `rumble-*` product owns separate DB-security rule logic.

## Outputs Back To Shared Tool

Every pilot should feed back into shared assets:

- new fixtures;
- rule severity changes;
- remediation hints;
- manifest examples;
- gate-profile refinements;
- docs improvements.

The pilot is successful only if learning becomes shared Wrench capability, not product-local workaround.
