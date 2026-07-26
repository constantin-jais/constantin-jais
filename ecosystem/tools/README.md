# Ecosystem Tools

This directory contains operational and governance scripts for the Rumble/Bolt/Wrench/Gear ecosystem.

## checks/ — frontier controls

Mechanised boundary checks. Each one prints how many items it examined and exits
non-zero when that number is zero: a control that scans nothing must fail, never
pass, so that "found nothing" and "could not look" are distinguishable in the log.
All are stdlib-only or POSIX shell and resolve the repository root through
`git rev-parse --show-toplevel`, so they run identically from any directory and
carry no machine-local path.

Wired controls run inside an existing **required** job. A control living in its
own workflow would produce a non-required check — mergeable while red.

| Control                                             | Wired into                              | Asserts                                                       |
| --------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------- |
| `ecosystem/tools/checks/check-action-pinning.sh`    | `Stack workflow conventions` (required) | Every `uses:` in every tracked workflow is SHA-pinned.        |
| `ecosystem/tools/checks/check-doc-paths.py`         | `Stack workflow conventions` (required) | Operational documents cite only paths that exist.             |
| `ecosystem/tools/checks/check-workflow-location.sh` | not wired — see below                   | Workflow files live only under the root `.github/workflows/`. |
| `ecosystem/tools/checks/check-repo-escape.py`       | not wired — see below                   | No tracked script resolves a path above the repo root.        |
| `ecosystem/tools/checks/check-schema-coverage.py`   | not wired — see below                   | Every versioned JSON Schema is covered by a validation suite. |

Three controls are deliberately **placed but not wired**: each currently reports a
real finding whose correction requires an owner decision, not a mechanical edit.
Wiring them today would turn `main` red; weakening them with an allowlist to make
them green would destroy the reason they exist. Run them by hand:

```bash
sh ecosystem/tools/checks/check-workflow-location.sh
python3 ecosystem/tools/checks/check-repo-escape.py
python3 ecosystem/tools/checks/check-schema-coverage.py
```

The first two both report the dormant Harness Vertical P0 stratum, whose disposition
is frozen as trace by control-plane ADR 0047. The third reports six schemas that no
validation suite references; covering them means authoring contract fixtures, which
the same ADR routes to the monorepo work-package regime.

## readme_guardrail.py

Validates the canonical README header introduced by the 2026-07-04 rollout. The contract is documented in [`../specs/shared/readme-standard.md`](../specs/shared/readme-standard.md).

**Usage:**

```bash
python3 ecosystem/tools/readme_guardrail.py ../repo-a ../repo-b/README.md
python3 ecosystem/tools/readme_guardrail.py --from-list readme-paths.txt
python3 ecosystem/tools/readme_guardrail.py --self-test
```

The guardrail is dependency-free and checks only mechanical drift: required fields, layer and `deployment_class` vocabulary, maturity qualifier, sovereign licensing wording, required sections, and machine-local paths. It does not rewrite README files and does not replace human review of maturity evidence.

## state-snapshot.sh

Archives ecosystem state for sovereignty backup, compliance audits, and disaster recovery.

**Usage:**

```bash
./state-snapshot.sh [DEST_DIR]
```

**Arguments:**

- `DEST_DIR` (optional): Destination directory for archives. Defaults to `../ecosystem-snapshots` relative to the repository root.

**Output:**

Creates a timestamped tarball (`ecosystem-snapshot-YYYY-MM-DDTHH-MM-SSZ.tar.gz`) containing:

The living control-plane documents — exactly those the required `Stack workflow conventions` job asserts must exist, plus the ADR directory:

- `ecosystem/specs/shared/decision-log.md` — All governance decisions.
- `ecosystem/specs/shared/adrs/` — Architecture Decision Records.
- `ecosystem/governance/upstream-contributions.md` — Upstream contribution gates.
- `ecosystem/plans/cold-backlog.md` — Meta backlog surviving the monorepo boundary.
- `ecosystem/plans/orchestrator-lock-inputs.md` — Input manifests for the monorepo locks.

The pre-constellation candidates (maturity matrices, readiness report, health and status pages) were retired by wave 0 option B; two of them are actively refused on `main` by the same required job, so they can never be archived.

Checksums (`SHA256`) are written to a companion `.sha256` file for integrity verification.

**Automation:**

Schedule this script weekly or monthly via `cron`:

```bash
0 2 * * 0 cd /path/to/repo && ./ecosystem/tools/state-snapshot.sh
```

**Portability:**

The script uses `git rev-parse --show-toplevel` to find the repository root and preserves relative paths in the tarball. No absolute machine-local paths are embedded.
