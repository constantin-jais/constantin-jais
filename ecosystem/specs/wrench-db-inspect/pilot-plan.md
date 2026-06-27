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
- Bolt/CI consumes report contract instead of raw SQL.

## Stop Conditions

Stop or pause the pilot if:

- reports include real secrets/PII;
- findings are too noisy to triage;
- product schema intent is not documented;
- a Rumble starts copying the prototype logic locally;
- live DB access is proposed as mandatory.

## Outputs Back To Shared Tool

Every pilot should feed back into shared assets:

- new fixtures;
- rule severity changes;
- remediation hints;
- manifest examples;
- gate-profile refinements;
- docs improvements.

The pilot is successful only if learning becomes shared Wrench capability, not product-local workaround.
