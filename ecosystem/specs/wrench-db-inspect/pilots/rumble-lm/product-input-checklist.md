# rumble-lm Product-Dependent Pilot Checklist

This checklist is the bridge between the product data model and a real `wrench-db-inspect` run.

## Required sanitized inputs

- [ ] `inputs/schema.sql` exists and contains DDL/RLS/grants only.
- [ ] No row data, prompts, source excerpts, response content, raw embeddings, DSNs, tokens, cookies, or personal data.
- [ ] `inputs/security-manifest.json` validates against `contracts/manifest.v0.1.schema.json` via `scripts/validate-json-contracts.py`.
- [ ] Optional `inputs/migrations/` contains sanitized migration excerpts only.

## Expected tenant mapping

- Canonical tenant: `organization`.
- Product alias: `workspace`.
- Tenant column: `workspace_id`.
- Approved session setting for RLS policies: `current_setting('app.workspace_id', true)`.

## Table classification draft

| Table | Classification | Tenant evidence expected | Personal data | Embeddings | Pilot check |
| --- | --- | --- | --- | --- | --- |
| `public.sessions` | `tenant_scoped` | direct `workspace_id NOT NULL` | yes | no | [ ] |
| `public.source_sets` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | maybe | no | [ ] |
| `public.source_set_items` | `tenant_scoped` | `source_set_id -> public.source_sets -> sessions.workspace_id` | maybe/source metadata | no | [ ] |
| `public.activities` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | yes | no | [ ] |
| `public.activity_options` | `tenant_scoped` | `activity_id -> public.activities -> sessions.workspace_id` | maybe | no | [ ] |
| `public.activity_runs` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | low | no | [ ] |
| `public.participants` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | yes | no | [ ] |
| `public.responses` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | high | no | [ ] |
| `public.citations` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | maybe/source excerpts | no | [ ] |
| `public.summaries` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | high | no | [ ] |
| `public.exports` | `tenant_scoped` | `session_id -> public.sessions.workspace_id` | high | no | [ ] |
| `public.audit_events` | `audit_system` | direct `workspace_id NOT NULL`, no response/source content in metadata | limited actor refs | no | [ ] |
| future `public.source_embeddings` | `tenant_scoped` unless justified public | direct or derived tenant path | source-derived | yes | [ ] |

## Pilot commands

From the repository root:

```bash
cd ecosystem/specs/wrench-db-inspect/pilots/rumble-lm
./run-pilot.sh
```

Override paths if inputs live elsewhere:

```bash
SCHEMA_DUMP=/tmp/rumble-lm.schema.sql \
MANIFEST=/tmp/rumble-lm.security-manifest.json \
MIGRATIONS=/tmp/rumble-lm-migrations \
PROFILE=release \
./run-pilot.sh
```

## Triage requirements

For every finding:

- [ ] classify as true positive, false positive, product decision, or parser/tool limitation;
- [ ] record in `open-findings.md` or `false-positive-notes.md`;
- [ ] convert any recurring true positive into a fixture candidate;
- [ ] do not accept waiver without owner, reviewer, expiry, rule, and subject binding.

## Completion criteria

The product-dependent pilot is complete when:

- [ ] `PROFILE=release ./run-pilot.sh` exits `0`, or all blocking findings have accepted bounded waivers;
- [ ] no report redaction is applied in release evidence;
- [ ] all non-system tables are classified;
- [ ] all tenant-scoped tables have RLS enabled and forced;
- [ ] all derived tenant paths are proven by FK-chain and policy-chain evidence, or triaged as unsupported safe SQL forms requiring a fixture/rule update;
- [ ] pgvector/embedding tables are either absent or tenant-filtered before vector ranking;
- [ ] reports are reviewed and safe to attach as CI/Bolt evidence.
