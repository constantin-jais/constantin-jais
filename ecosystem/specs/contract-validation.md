# Spec Contract Validation

Status: P0 CI recipe.

## Purpose

Validate JSON Schema Draft 2020-12 contracts and fixtures for ecosystem specs before implementation code consumes them.

Validated suites — this list is the declared mirror of the `SUITES` table in
`validate_spec_schemas.py`; the two must not drift:

- Bolt / cos-matic planning: `harness/cosmatic-planning.v0.1.schema.json` + `harness/fixtures/planning/`.
- Human approval: `harness/human-approval.v0.1.schema.json` + `harness/fixtures/human-approval/`.
- Approval key registry: `harness/approval-key-registry.v0.1.schema.json` + `harness/fixtures/approval-key-registry/`.
- Rumble delivery maturity: `harness/rumble-delivery-maturity.v0.1.schema.json` + `harness/fixtures/maturity/`.
- Workspace identity: `shared/contracts/workspace-identity.v0.1.schema.json` + `shared/contracts/fixtures/workspace-identity/`.
- Authorization registries: `shared/contracts/authorization-registries.v0.1.schema.json` + `shared/contracts/fixtures/authorization-registries/`.
- Parser runtime attestation: `shared/contracts/parser-runtime-attestation.v0.1.schema.json` + `shared/contracts/fixtures/parser-runtime-attestation/`.
- Progress snapshot: `shared/contracts/progress-snapshot.v0.1.schema.json` + `shared/contracts/fixtures/progress-snapshot/`.
- Job runtime: `shared/contracts/job-runtime.v0.1.schema.json` + `shared/contracts/fixtures/job-runtime/`.
- Implementation handoff: `shared/contracts/implementation-handoff.v0.1.schema.json` + `harness/fixtures/handoffs/`.

The Gear Memory and Gear Loader suites were retired with their spec trees
(`archive/pre-constellation-2026-07-19`, wave 0 option B) and are no longer
validated here.

## Coverage tiers

Every versioned schema in the tree is covered, and the tier says how strongly:

- **Tier 1 — fixture-validated.** A suite above validates real instance data.
- **Tier 2 — meta-validated only.** The schema has no instance data anywhere, so
  it is compiled and checked as Draft 2020-12 on every run and declared in the
  `META_ONLY` map of `validate_spec_schemas.py` **with the reason it has none**.

Tier 2 is deliberately weaker. Naming it is the point: an uncovered schema must
not read like a covered one. Fixtures were **not** invented to lift these into
Tier 1 — instance data asserting facts no producer ever emitted would fabricate
coverage, and a green suite would then vouch for it.

Membership is enforced in both directions by
`ecosystem/tools/checks/check-schema-coverage.py` (required job
`Stack workflow conventions`) and by the validator itself: a schema in neither
tier fails, a schema in both fails, a `META_ONLY` entry naming an absent schema
fails, and a Tier-2 schema fails **the day instance data for its format appears**,
forcing promotion to Tier 1. Coverage can only ratchet up.

## Local / CI Command

From repository root:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

Equivalent expanded command:

```bash
uv run --script ecosystem/specs/validate_spec_schemas.py
```

Dependencies are declared in the script's PEP 723 header and pinned in
`ecosystem/specs/validate_spec_schemas.py.lock`. Refresh the lock after
changing the header with `uv lock --script ecosystem/specs/validate_spec_schemas.py`.

## Fixture Semantics

- `*.valid.json` must pass schema validation.
- `*.refusal.json` must pass schema validation because a structured refusal is a valid contract output.
- `*.warning.json` must pass schema validation.
- `*.invalid.json` must fail schema validation or one explicit semantic guard documented in `validate_spec_schemas.py`.
- `*.gate.json` must pass schema validation: a gated handoff is structurally valid and blocked, not malformed. Used by the implementation-handoff suite only, where the fixture carrying it declares `expected_gate` exactly as refusal fixtures declare `expected_refusal`.

Semantic guards cover cross-object constraints JSON Schema cannot express cleanly in the current bundle shape, such as “OCR text emitted while OCR policy is disabled”.

Guards must be scoped by the instance `format` so a rule written for one contract
cannot perturb another, and must never compare against the wall clock: a
time-dependent guard turns a required job red on a date with no change to any
file. The handoff waiver rule therefore measures expiry against the handoff's own
`source.created_at`, not against `now`.

## Quarantined fixtures

A `quarantine` entry on a suite names a fixture whose disagreement with its schema
is real, diagnosed, and **not ours to correct** — typically because control-plane
ADR 0047 §3 freezes the fixture as trace while §1 routes the contract amendment to
the monorepo work-package regime.

This is not an allowlist. An allowlist mutes a case and reports the suite clean; a
quarantine names the fixture, carries its diagnosis in source, prints
`QUARANTINED` on every run, and **fails the build the day the fixture starts
conforming** — because a quarantine outliving the divergence it describes is a
permanent hole reporting itself as coverage. Editing a frozen fixture to green a
gate is forbidden: it would destroy the only evidence of the disagreement.

Currently quarantined: `harness/fixtures/handoffs/feedmind-curated-export.valid.json`.

## CI Binding

The repository uses GitHub Actions as the active CI target for these personal projects:

- root `.github/workflows/spec-contracts.yml`;
- job `json-schema-fixtures`;
- command: `sh ecosystem/specs/ci-validate-contracts.sh`;
- triggers: push, pull request, and manual `workflow_dispatch`.

Runner requirements:

- `uv` from `astral-sh/setup-uv` (provisions Python per the script's `requires-python`);
- outbound package access for `jsonschema` and the transitive dependencies pinned in `validate_spec_schemas.py.lock`;
- no access to project secrets is required.

## GitLab / self-hosted compatibility

The validation remains CI-agnostic. A GitLab/self-hosted runner can still execute the same command:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

That compatibility is nice-to-have, not the active CI target for this repository.

## Sovereignty Note

GitHub Actions is accepted here because these are personal GitHub-hosted projects and this job validates only public-ish specs/fixtures with fake IDs, no secrets, no PII, and no runtime artifacts. Core ecosystem truth remains exportable and the validation command remains self-hostable.

If alternate forge or CI bindings are added later, they must preserve:

- self-hostable runner path;
- no opaque storage of artifacts containing PII/secrets;
- no raw fixture body logging beyond safe validation output;
- dependency pinning/review for validator tools.
