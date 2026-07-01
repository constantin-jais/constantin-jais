# Wrench DB Inspect — Bolt/CI/Harness Integration

Status: Draft integration contract.

## Purpose

This document defines how Bolt, CI pipelines, and the agentic harness should run `wrench-db-inspect`, consume its reports, and decide gates without re-parsing SQL or duplicating DB-security policy inside each Rumble.

`wrench-db-inspect` produces evidence. Bolt/CI/harness selects the gate profile and records the result. See `forge-harness-integration.md` for the scaffold-level contract across `rumble-*` builds.

## Required Inputs

For a Postgres-backed Rumble, protected-branch and release gates should provide:

- `--manifest db/security-manifest.json`
- `--schema-dump target/schema.sql`
- `--migrations db/migrations` when available
- `--profile protected_branch | release`
- `--gate-profile-config <profiles.json>` or accepted built-in profiles
- `--report-json target/wrench-db-inspect.json`
- `--report-md target/wrench-db-inspect.md`

No secrets, DSNs, row data, raw embeddings, prompts, or PII may be passed as report metadata. A non-Postgres Rumble must explicitly declare DB inspection as not applicable so the harness can distinguish "not applicable" from "missing gate".

## Reference Command

```text
wrench-db-inspect run \
  --manifest db/security-manifest.json \
  --schema-dump target/schema.sql \
  --migrations db/migrations \
  --profile protected_branch \
  --gate-profile-config db/wrench-db-gate-profiles.json \
  --report-json target/wrench-db-inspect.json \
  --report-md target/wrench-db-inspect.md
```

## Exit Codes

| Code | Meaning | CI behavior |
| --- | --- | --- |
| `0` | No blocking condition for selected profile. | Pass; upload reports. |
| `1` | Blocking findings or report-level gate. | Fail gate; upload reports. |
| `2` | Invalid invocation/configuration/input read failure. | Fail as infrastructure/config error. |
| `3` | Reserved for future inspection-integrity failure. | Fail closed. |

## Report Consumption Rules

Bolt/CI/harness must read only the report contract, not raw SQL:

- `data.summary.gate_blocked` is the authoritative gate boolean.
- `data.findings[*].gate` explains per-finding decisions.
- `data.report_gate` explains report-level decisions such as redaction applied in release.
- `meta.redaction.secrets_or_pii_included` must be `false`.
- `meta.redaction.applied=true` requires review; in `release`, it blocks.
- `data.metrics` should be stored for trends but not used to invent hidden gates unless the selected profile says so.

## Required CI/Harness Artifacts

On every run, CI/harness should retain:

- JSON report: machine-readable evidence.
- Markdown report: human/agent-readable summary.
- Tool version and command invocation.
- Input references/hashes when available.

CI/harness must not upload raw DB dumps containing row data or credentials.

## Bolt/Harness Gate Record Shape

Bolt/harness should record a gate result similar to:

```json
{
  "data": {
    "gate": "wrench-db-inspect",
    "profile": "protected_branch",
    "status": "failed",
    "gate_blocked": true,
    "report_artifact": "artifact://wrench-db-inspect.json",
    "blocking_findings": ["RLS_REQUIRED_TENANT_TABLE"],
    "report_gate_blocked": false
  },
  "meta": {
    "schema_version": "0.1"
  }
}
```

## Suggested GitHub Actions Shape

```yaml
name: db-security

on:
  pull_request:
  push:
    branches: [main]

jobs:
  wrench-db-inspect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build schema dump
        run: ./scripts/db/schema-dump.sh > target/schema.sql
      - name: Run wrench-db-inspect
        run: |
          wrench-db-inspect run \
            --manifest db/security-manifest.json \
            --schema-dump target/schema.sql \
            --migrations db/migrations \
            --profile protected_branch \
            --gate-profile-config db/wrench-db-gate-profiles.json \
            --report-json target/wrench-db-inspect.json \
            --report-md target/wrench-db-inspect.md
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: wrench-db-inspect
          path: |
            target/wrench-db-inspect.json
            target/wrench-db-inspect.md
```

Note: GitHub Actions is shown only as a portable CI contract example. Sovereign/self-hosted runners should use the same command and artifact semantics.

## Rollout Plan

1. Add forge scaffold support for Postgres applicability, `db/security-manifest.json`, sanitized `target/schema.sql`, and report artifacts.
2. Run in `local`/warning mode on each Rumble to collect false positives.
3. Require manifests for all Postgres-backed Rumbles.
4. Enable `pull_request` for P0 critical/high.
5. Enable `protected_branch` once unknown states are low.
6. Enable `release` with strict waiver and redaction behavior.
7. Promote recurring product cases to shared fixtures/rules instead of product-local scripts.

## Anti-Duplication Rule

Rumbles may wrap this command for convenience, but must not implement independent local logic for:

- RLS coverage;
- grants;
- dangerous migrations;
- `pgvector` tenant filtering;
- waiver validity;
- redaction gate behavior.

New recurring issues should become shared fixtures in `wrench-db-inspect`, not product-local scripts.

## Harness Observable Gates

The harness should expose the report as typed gates/metrics rather than free-form logs. Minimum gates are defined in `forge-harness-integration.md` and include:

- manifest/schema presence for Postgres products;
- `data.summary.gate_blocked == false`;
- `meta.redaction.secrets_or_pii_included == false`;
- `meta.redaction.applied == false` for release;
- zero unclassified tables, missing RLS, dangerous grants/migrations, pgvector leakage, invalid waivers, and failed tenant derivations in strict profiles.

These gates are derived from the JSON report; the harness must not re-parse SQL or maintain a parallel DB-security rule set.
