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
| `ecosystem/tools/checks/check-workflow-location.sh` | `Stack workflow conventions` (required) | Workflow files live only under the root `.github/workflows/`. |
| `ecosystem/tools/checks/check-repo-escape.py`       | `Stack workflow conventions` (required) | No tracked script resolves a path above the repo root.        |
| `ecosystem/tools/checks/check-schema-coverage.py`   | not wired — see below                   | Every versioned JSON Schema is covered by a validation suite. |

### The frozen-trace exemption, and why it expires

`check-workflow-location.sh` and `check-repo-escape.py` both reported exactly one
finding, and the same one: the **Harness Vertical P0** stratum
(`ecosystem/.github/workflows/harness-vertical-p0.yml` and
`ecosystem/specs/harness/run_vertical_p0.py`). That stratum is inert — the
workflow does not appear in `gh api .../actions/workflows`, its `paths:` filters
name a layout that no longer exists, and its `cos-matic` / `wrench-inspect`
checkouts are 404 — but control-plane ADR 0047 §3 freezes it _en l'état comme
trace, plus jamais amendé_: it may be neither repaired nor deleted.

Both controls are therefore wired with a **nominative exemption**: the exact
paths, never a directory and never a pattern, each carrying its ADR reference in
the source. The exemption is a two-way join against the findings, and both
directions fail the build:

- an offender that is **not** named — a second workflow outside the root, a
  second escaping script, or even a second escaping line inside the exempted
  file — fails. The exemption is line-scoped for `check-repo-escape.py`, so
  exempting one line of a file does not shelter the rest of it.
- a named path that is **no longer** an offender — deleted, renamed, moved to
  the root, or whose fingerprinted line was edited — fails as an **expired**
  exemption.

The second direction is the reason the exemption is acceptable at all. An
exemption that outlives the defect it describes is a permanent hole that reports
itself as coverage: the control would keep printing `OK` while carrying an
exception for something that no longer exists. Breaking the build the day it
stops being true sends it back for arbitration instead of letting it rot. If the
P0 stratum is ever unfrozen, these two controls are what will say so.

One control remains deliberately **placed but not wired**:

```bash
python3 ecosystem/tools/checks/check-schema-coverage.py
```

It reports six schemas that no validation suite references. Covering them means
authoring contract fixtures — product work that the same ADR routes to the
monorepo work-package regime — so wiring it is an owner decision, not a
mechanical edit.

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
