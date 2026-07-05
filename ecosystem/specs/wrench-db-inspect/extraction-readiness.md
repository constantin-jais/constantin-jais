# Wrench DB Inspect — Extraction Readiness Checklist

Status: Draft checklist for creating the dedicated `wrench-db-inspect` repository.

## Purpose

This checklist defines when the prototype under `ecosystem/prototypes/wrench-db-inspect` is ready to be extracted into a standalone repository without losing safety, contracts, or ecosystem boundaries.

Extraction must preserve the contract-first posture: specs, fixtures, reports, ecosystem/harness integration, and gates remain authoritative; code follows them.

## Must-Have Before Extraction

### Contracts

- [ ] `README.md` in the new repo states mission, hard boundaries, non-goals, and sovereignty constraints.
- [ ] JSON report remains `{ data, meta }`.
- [ ] Manifest contract remains `{ data, meta }`.
- [ ] Gate profile contract remains `{ data, meta }`.
- [ ] Exit codes remain documented and tested.
- [ ] Report redaction metadata remains present:
  - `meta.redaction.secrets_or_pii_included`
  - `meta.redaction.applied`
  - `data.metrics.redactions_applied_count`

### Fixtures and Tests

- [ ] All current fixtures are copied into the repo or imported as test fixtures.
- [ ] `run-fixtures.sh` equivalent exists.
- [ ] Unit tests cover P0 rules, P1 warnings, waivers, gate profiles, and redaction.
- [ ] Golden/report-shape tests are added before public release.
- [ ] Redaction regression tests include fake DSN/token/password/comment strings.
- [ ] Invalid profile config exits `2` and does not emit a misleading pass report.

### Security Behavior

- [ ] Default mode is non-mutating.
- [ ] No live DB connection exists unless explicitly read-only and optional.
- [ ] No row data, raw embeddings, prompts, DSNs, tokens, credentials, or PII appear in reports.
- [ ] Release profile blocks invalid waivers.
- [ ] Release profile blocks report-level redaction applied.
- [ ] Unknown P0 analysis state fails closed in strict profiles.

### Scope Boundaries

- [ ] The repo does not become an ORM.
- [ ] The repo does not execute migrations.
- [ ] The repo does not proxy DB traffic.
- [ ] The repo does not store credentials.
- [ ] The repo does not replace app authorization.
- [ ] The repo does not absorb generic `wrench-inspect` responsibilities.

### Sovereignty and Dependencies

- [ ] Direct dependencies use compatible licenses.
- [ ] No mandatory SaaS or hosted service is required.
- [ ] Core operation works offline with SQL/schema/manifest fixtures.
- [ ] Dependency license audit is documented.

### CI/Bolt/Harness Integration

- [ ] CLI supports:
  - `--manifest`
  - `--schema-dump`
  - `--migrations`
  - `--profile`
  - `--gate-profile-config`
  - `--report-json`
  - `--report-md`
- [ ] JSON report is the machine-readable source of truth.
- [ ] Markdown report is human/agent-readable only.
- [ ] Bolt/CI/harness consumes `data.summary.gate_blocked`, `data.findings[*].gate`, `data.report_gate`, and `meta.redaction`.
- [ ] Bolt/CI/harness does not re-parse raw SQL.
- [ ] Ecosystem scaffold for Postgres-backed `rumble-*` products creates/validates `db/security-manifest.json`, sanitized `target/schema.sql`, and report artifacts.
- [ ] Non-Postgres `rumble-*` products can explicitly mark DB inspection as not applicable.
- [ ] Harness gates from `harness-integration.md` are mapped to typed gate results/metrics.

## Should-Have Before Public Release

- [ ] Replace remaining text heuristics with structured SQL/AST parsing where feasible.
- [ ] Add line/span evidence without leaking sensitive content.
- [ ] Add SARIF only after core JSON is stable.
- [ ] Add changelog and rule versioning.
- [ ] Add performance benchmarks on representative migration sets.
- [ ] Add example manifests for `rumble-lm`, `rumble-note`, `rumble-crew`, and `rumble-canvas`.

## Extraction Steps

1. Create repository `wrench-db-inspect`.
2. Copy prototype code into the repo as initial crate.
3. Copy fixtures and docs from `ecosystem/specs/wrench-db-inspect` or keep them vendored/subtree until contracts stabilize.
4. Add CI running unit tests and fixture suite.
5. Add ecosystem/harness integration examples and typed gate mapping.
6. Add license file and dependency license audit.
7. Tag initial version `v0.1.0-prototype` or equivalent.
8. Update ecosystem docs to point to the standalone repo.
9. Keep specs in ecosystem as control-plane contracts until the repo owns its own mirrored docs.

## Definition of Ready

The standalone repo is ready for first Rumble pilot when:

- all P0 fixtures pass;
- reports are deterministic;
- no redaction regression exists;
- gate profiles work for `local`, `protected_branch`, and `release`;
- one real Rumble manifest can be validated without product-local DB security scripts;
- ecosystem/harness can consume the report as typed gate evidence;
- false positives from the pilot are documented as shared fixtures or rule refinements.
