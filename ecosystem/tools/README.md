# Ecosystem Tools

This directory contains operational and governance scripts for the Rumble/Bolt/Wrench/Gear ecosystem.

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
