# Ecosystem Tools

This directory contains operational and governance scripts for the Rumble/Bolt/Wrench/Gear ecosystem.

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

- `DEST_DIR` (optional): Destination directory for archives. Defaults to `../forge-snapshots` relative to the repository root.

**Output:**

Creates a timestamped tarball (`ecosystem-snapshot-YYYY-MM-DDTHH-MM-SSZ.tar.gz`) containing:

- `ecosystem/specs/shared/decision-log.md` — All governance decisions.
- `ecosystem/specs/shared/adrs/` — Architecture Decision Records.
- `ecosystem/specs/shared/maturity/` — Product maturity matrices and readiness data.
- `readiness-report.md` — Readiness and compliance status.
- `forge-health.md` — Ecosystem health metrics.
- `status.md` — Current operational status (if present).

Checksums (`SHA256`) are written to a companion `.sha256` file for integrity verification.

**Automation:**

Schedule this script weekly or monthly via `cron`:

```bash
0 2 * * 0 cd /path/to/repo && ./ecosystem/tools/state-snapshot.sh
```

**Portability:**

The script uses `git rev-parse --show-toplevel` to find the repository root and preserves relative paths in the tarball. No absolute machine-local paths are embedded.
