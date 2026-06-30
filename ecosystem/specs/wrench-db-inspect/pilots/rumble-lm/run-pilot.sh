#!/usr/bin/env bash
set -euo pipefail

PILOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_ROOT="$(cd "$PILOT_ROOT/../.." && pwd)"
REPO_ROOT="$(cd "$SPEC_ROOT/../../.." && pwd)"
PROTOTYPE="$REPO_ROOT/ecosystem/prototypes/wrench-db-inspect"
BIN="$PROTOTYPE/target/debug/wrench-db-inspect"

SCHEMA_DUMP="${SCHEMA_DUMP:-$PILOT_ROOT/inputs/schema.sql}"
MANIFEST="${MANIFEST:-$PILOT_ROOT/inputs/security-manifest.json}"
MIGRATIONS="${MIGRATIONS:-$PILOT_ROOT/inputs/migrations}"
PROFILE="${PROFILE:-release}"
GATE_PROFILES="${GATE_PROFILES:-$SPEC_ROOT/fixtures/gate-profiles/default.json}"
OUT_DIR="${OUT_DIR:-$PILOT_ROOT/reports}"
REPORT_BASE="$OUT_DIR/rumble-lm.$PROFILE"

if [[ ! -f "$SCHEMA_DUMP" ]]; then
  echo "Missing sanitized schema dump: $SCHEMA_DUMP" >&2
  echo "Provide SCHEMA_DUMP=/path/to/schema.sql or place inputs/schema.sql." >&2
  exit 2
fi

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing DB security manifest: $MANIFEST" >&2
  echo "Provide MANIFEST=/path/to/security-manifest.json or place inputs/security-manifest.json." >&2
  echo "Seed example: $SPEC_ROOT/examples/security-manifest.rumble-lm.example.json" >&2
  exit 2
fi

python3 "$SPEC_ROOT/scripts/validate-json-contracts.py" >/dev/null
cargo build --manifest-path "$PROTOTYPE/Cargo.toml" >/dev/null
mkdir -p "$OUT_DIR"

args=(
  run
  --manifest "$MANIFEST"
  --schema-dump "$SCHEMA_DUMP"
  --profile "$PROFILE"
  --gate-profile-config "$GATE_PROFILES"
  --report-json "$REPORT_BASE.json"
  --report-md "$REPORT_BASE.md"
)

if [[ -d "$MIGRATIONS" ]]; then
  args+=(--migrations "$MIGRATIONS")
fi

set +e
"$BIN" "${args[@]}"
code=$?
set -e

python3 -m json.tool "$REPORT_BASE.json" >/dev/null
python3 - <<PY
import json
from pathlib import Path
report = json.loads(Path('$REPORT_BASE.json').read_text())
summary = report['data']['summary']
redaction = report['meta'].get('redaction', {})
print('report:', '$REPORT_BASE.json')
print('status:', report['data']['status'])
print('gate_blocked:', summary.get('gate_blocked'))
print('findings:', len(report['data'].get('findings', [])))
print('redaction_applied:', redaction.get('applied'))
if redaction.get('secrets_or_pii_included') is not False:
    raise SystemExit('report redaction safety flag is not false')
PY

exit "$code"
