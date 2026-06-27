#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/../../.." && pwd)"
BIN="$ROOT/target/debug/wrench-db-inspect"
EXAMPLES="$REPO_ROOT/ecosystem/specs/wrench-db-inspect/examples"
GATE_PROFILES="$REPO_ROOT/ecosystem/specs/wrench-db-inspect/fixtures/gate-profiles/default.json"
OUT="${TMPDIR:-/tmp}/wrench-db-inspect-lm-examples"

cargo build --manifest-path "$ROOT/Cargo.toml" >/dev/null
rm -rf "$OUT"
mkdir -p "$OUT"

run_example() {
  local name="$1"
  local expected="$2"
  set +e
  "$BIN" run \
    --manifest "$EXAMPLES/security-manifest.rumble-lm.example.json" \
    --schema-dump "$EXAMPLES/schema.rumble-lm.$name.sql" \
    --profile protected_branch \
    --gate-profile-config "$GATE_PROFILES" \
    --report-json "$OUT/rumble-lm-$name.json" \
    --report-md "$OUT/rumble-lm-$name.md"
  local code=$?
  set -e
  if [[ "$code" != "$expected" ]]; then
    echo "FAIL rumble-lm $name: expected exit $expected, got $code" >&2
    exit 1
  fi
  python3 -m json.tool "$OUT/rumble-lm-$name.json" >/dev/null
  echo "OK rumble-lm $name exit=$code"
}

run_example pass 0
run_example fail 1

if grep -R -E 'postgres://|sk_test_|fixture_password' "$OUT"; then
  echo "FAIL rumble-lm examples: secret-like content leaked into reports" >&2
  exit 1
fi

echo "LM example reports: $OUT"
