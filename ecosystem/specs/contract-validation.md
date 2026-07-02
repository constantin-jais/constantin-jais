# Spec Contract Validation

Status: P0 CI recipe.

## Purpose

Validate JSON Schema Draft 2020-12 contracts and fixtures for ecosystem specs before implementation code consumes them.

Validated suites:

- Gear Memory: `gear/gear-memory.v0.1.schema.json` + `gear/fixtures/memory/`.
- Gear Loader: historical path `gear-loader/gear-loader.v0.1.schema.json` + `gear-loader/fixtures/` until schema migration.
- Bolt / cos-matic planning: `harness/cosmatic-planning.v0.1.schema.json` + `harness/fixtures/planning/`.

## Local / CI Command

From repository root:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

Equivalent expanded command:

```bash
python3 -m venv .venv-spec-contracts
.venv-spec-contracts/bin/python -m pip install -r ecosystem/specs/requirements-ci.txt
.venv-spec-contracts/bin/python ecosystem/specs/validate_spec_schemas.py
```

## Fixture Semantics

- `*.valid.json` must pass schema validation.
- `*.refusal.json` must pass schema validation because a structured refusal is a valid contract output.
- `*.warning.json` must pass schema validation.
- `*.invalid.json` must fail schema validation or one explicit semantic guard documented in `validate_spec_schemas.py`.

Semantic guards cover cross-object constraints JSON Schema cannot express cleanly in the current bundle shape, such as “OCR text emitted while OCR policy is disabled”.

## CI Binding

The repository uses GitHub Actions as the active CI target for these personal projects:

- root `.github/workflows/spec-contracts.yml`;
- job `json-schema-fixtures`;
- command: `sh ecosystem/specs/ci-validate-contracts.sh`;
- triggers: push, pull request, and manual `workflow_dispatch`.

Runner requirements:

- Python 3.12 from `actions/setup-python`;
- outbound package access for `jsonschema` and pinned transitive dependencies;
- no access to project secrets is required.

## GitLab / self-hosted compatibility

The validation remains CI-agnostic. A GitLab/self-hosted runner can still execute the same command:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

That compatibility is nice-to-have, not the active CI target for this repository.

## Sovereignty Note

GitHub Actions is accepted here because these are personal GitHub-hosted projects and this job validates only public-ish specs/fixtures with fake IDs, no secrets, no PII, and no runtime artifacts. Core ecosystem truth remains exportable and the validation command remains self-hostable.

If Forgejo/Woodpecker/GitLab bindings are added later, they must preserve:

- self-hostable runner path;
- no opaque storage of artifacts containing PII/secrets;
- no raw fixture body logging beyond safe validation output;
- dependency pinning/review for validator tools.
