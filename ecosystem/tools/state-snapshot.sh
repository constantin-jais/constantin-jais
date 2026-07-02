#!/bin/bash

# state-snapshot.sh — Archive ecosystem state for sovereignty backup and compliance.
#
# Usage:
#   state-snapshot.sh [DEST_DIR]
#
# Arguments:
#   DEST_DIR  Destination directory for the tarball (default: ../forge-snapshots relative to repo root).
#
# Description:
#   Creates a timestamped tar.gz archive containing:
#   - ecosystem/specs/shared/decision-log.md
#   - ecosystem/specs/shared/adrs/
#   - ecosystem/maturity/
#   - ecosystem/status.md, readiness-report.md, forge-health.md, overview.md
#
#   Archives are named: ecosystem-snapshot-YYYY-MM-DDTHH-MM-SSZ.tar.gz
#   Checksums (SHA256) are written to a companion .sha256 file.
#
#   All paths are relative to the repository root, ensuring portability.
#   No absolute machine-local paths are embedded.

set -euo pipefail

# Determine repository root.
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Set destination directory, default to ../forge-snapshots relative to repo root.
DEST_DIR="${1:-../forge-snapshots}"

# Create destination if it does not exist.
mkdir -p "$DEST_DIR"

# Generate timestamp for archive name (ISO 8601 UTC).
TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
ARCHIVE_NAME="ecosystem-snapshot-${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${DEST_DIR}/${ARCHIVE_NAME}"
CHECKSUM_PATH="${DEST_DIR}/${ARCHIVE_NAME}.sha256"

# Build list of files to archive.
# All paths are repo-relative; tar will preserve them.
CANDIDATES=(
  "ecosystem/specs/shared/decision-log.md"
  "ecosystem/specs/shared/adrs"
  "ecosystem/maturity"
  "ecosystem/status.md"
  "ecosystem/readiness-report.md"
  "ecosystem/forge-health.md"
  "ecosystem/overview.md"
)

FILES_TO_ARCHIVE=()
for f in "${CANDIDATES[@]}"; do
  if [ -e "$f" ]; then
    FILES_TO_ARCHIVE+=("$f")
  else
    echo "warning: skipping missing path: $f" >&2
  fi
done

# Create tarball with all files.
echo "Creating archive: $ARCHIVE_PATH"
tar -czf "$ARCHIVE_PATH" "${FILES_TO_ARCHIVE[@]}"

# Generate SHA256 checksum (sha256sum on Linux, shasum on macOS).
echo "Generating checksum..."
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$ARCHIVE_PATH" > "$CHECKSUM_PATH"
else
  shasum -a 256 "$ARCHIVE_PATH" > "$CHECKSUM_PATH"
fi

# Verify archive integrity by listing contents.
echo "Archive contents:"
tar -tzf "$ARCHIVE_PATH" | head -20

# Print summary.
echo ""
echo "Archive complete:"
echo "  Path: $ARCHIVE_PATH"
echo "  Size: $(du -h "$ARCHIVE_PATH" | cut -f1)"
echo "  Checksum: $(cat "$CHECKSUM_PATH")"
echo ""
echo "Checksum file: $CHECKSUM_PATH"
echo "To verify: sha256sum -c $CHECKSUM_PATH"
