# rumble-lm — Wrench DB Inspect Pilot Report

Status: Not started.

## Pilot Goal

Validate `wrench-db-inspect` against `rumble-lm` database security needs: sessions, participant responses, sources, summaries, exports, and possible embeddings.

## Current Phase

Phase 0 — Dry Contract Review.

## Required Inputs

- `db/security-manifest.json`
- sanitized `target/schema.sql`
- `db/migrations` if available
- gate profile config

## Initial Risk Focus

- Tenant isolation by `organization_id`.
- Participant response privacy.
- Source/export retention and RGPD constraints.
- Future `pgvector` source/embedding leakage.
- Admin/facilitator access policies not bypassing tenant rules.

## Pilot Findings Summary

To be filled after first run.

| Severity | Count | Notes |
| --- | ---: | --- |
| critical | 0 | Not run yet. |
| high | 0 | Not run yet. |
| medium | 0 | Not run yet. |
| low | 0 | Not run yet. |

## Decisions Needed

- Confirm actual table list and classifications.
- Confirm DB roles naming.
- Confirm whether embeddings are in MVP or post-MVP.
- Confirm whether audit tables are tenant-scoped or audit/system with tenant attribution.

## Exit Criteria

- All non-system tables classified.
- No report redaction in release mode.
- No critical/high false positives before protected-branch gate.
- Any new recurring issue becomes shared fixture.
