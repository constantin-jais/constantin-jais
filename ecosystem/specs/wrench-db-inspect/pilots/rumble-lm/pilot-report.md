# rumble-lm — Wrench DB Inspect Pilot Report

Status: Ready for product inputs.

## Pilot Goal

Validate `wrench-db-inspect` against `rumble-lm` database security needs: sessions, participant responses, sources, summaries, exports, and possible embeddings.

## Current Phase

Phase 1 — Product input intake prepared; waiting for sanitized schema dump and product manifest.

## Required Inputs

- Example manifest seed: `ecosystem/specs/wrench-db-inspect/examples/security-manifest.rumble-lm.example.json`
- Pass schema example: `ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.pass.sql`
- Fail schema example: `ecosystem/specs/wrench-db-inspect/examples/schema.rumble-lm.fail.sql`
- Product manifest: `inputs/security-manifest.json` or external `MANIFEST=...`
- sanitized schema dump: `inputs/schema.sql` or external `SCHEMA_DUMP=...`
- optional sanitized migrations: `inputs/migrations` or external `MIGRATIONS=...`
- gate profile config: `fixtures/gate-profiles/default.json`
- Pilot runbook: `product-input-checklist.md`
- Sanitized schema export guide: `sanitized-schema-export.md`
- Executable script: `run-pilot.sh`

## Initial Risk Focus

- Tenant isolation by `organization_id`.
- Participant response privacy.
- Source/export retention and RGPD constraints.
- Future `pgvector` source/embedding leakage.
- Admin/facilitator access policies not bypassing tenant rules.

## Pilot Findings Summary

No real product schema dump is present in this repository. Findings remain pending until `run-pilot.sh` is executed with sanitized product inputs.

| Severity | Count | Notes |
| --- | ---: | --- |
| critical | 0 | Not run yet. |
| high | 0 | Not run yet. |
| medium | 0 | Not run yet. |
| low | 0 | Not run yet. |

## Decisions Needed

- Confirm actual table list and classifications against `product-input-checklist.md`.
- Confirm DB roles naming for app, readonly, and migration roles.
- Confirm whether embeddings are in MVP or post-MVP.
- Confirm whether audit tables are tenant-scoped or `audit_system` with tenant attribution.
- Confirm whether real multi-hop tenant derivation policies match the supported AST proof pattern; broaden fixtures if the schema uses different safe SQL forms.

## Exit Criteria

- All non-system tables classified.
- No report redaction in release mode.
- No critical/high false positives before protected-branch gate.
- Any new recurring issue becomes shared fixture.
