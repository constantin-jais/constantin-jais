#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/../../.." && pwd)"
BIN="$ROOT/target/debug/wrench-db-inspect"
FIXTURES="$REPO_ROOT/ecosystem/specs/wrench-db-inspect/fixtures"
OUT="${TMPDIR:-/tmp}/wrench-db-inspect-fixtures"
GATE_PROFILES="$FIXTURES/gate-profiles/default.json"

python3 "$REPO_ROOT/ecosystem/specs/wrench-db-inspect/scripts/validate-json-contracts.py" >/dev/null
cargo build --manifest-path "$ROOT/Cargo.toml" >/dev/null
rm -rf "$OUT"
mkdir -p "$OUT"

run_case() {
  local case="$1"
  local expected="$2"
  local profile="${3:-protected_branch}"
  local report_base="${case//\//__}__$profile"
  set +e
  "$BIN" run \
    --manifest "$FIXTURES/$case/manifest.json" \
    --schema-dump "$FIXTURES/$case/schema.sql" \
    --migrations "$FIXTURES/$case/migrations" \
    --profile "$profile" \
    --gate-profile-config "$GATE_PROFILES" \
    --report-json "$OUT/$report_base.json" \
    --report-md "$OUT/$report_base.md"
  local code=$?
  set -e
  if [[ "$code" != "$expected" ]]; then
    echo "FAIL $case: expected exit $expected, got $code" >&2
    exit 1
  fi
  python3 -m json.tool "$OUT/$report_base.json" >/dev/null
  echo "OK $case profile=$profile exit=$code"
}

run_case pass/rls_tenant_policy_ok 0
run_case pass/tenant_derivation_table_level_fk_ok 0 release
run_case pass/tenant_derivation_reversed_equality_ok 0 release
run_case pass/tenant_derivation_multihop_ok 0 release
run_case fail/rls_missing_on_tenant_table 1
run_case fail/grant_all_to_app_role 1
run_case fail/grant_to_unknown_role 1
run_case fail/pgvector_global_embedding_leak 1
run_case unknown/unclassified_table 1
run_case waiver/critical_with_valid_expiring_waiver 0
run_case waiver/critical_with_expired_waiver 1 release
run_case waiver/critical_with_incomplete_waiver 1 release
run_case fail/rls_not_forced_on_tenant_table 1
run_case fail/disable_rls_migration 1
run_case fail/set_row_security_off 1
run_case fail/dangerous_drop_table 1
run_case fail/dangerous_drop_column 1
run_case fail/drop_policy_dangerous 1
run_case fail/drop_constraint_dangerous 1
run_case fail/drop_foreign_key_dangerous 1
run_case fail/no_force_rls_forbidden 1
run_case fail/drop_not_null_dangerous 1
run_case fail/truncate_dangerous 1
run_case fail/unqualified_delete 1
run_case fail/unqualified_update 1
run_case warn/security_definer_missing_search_path 0
run_case warn/tenant_column_nullable 0
run_case warn/view_without_tenant_filter 0
run_case warn/function_without_tenant_filter 0
run_case fail/grant_all_to_app_role 0 local
run_case fail/grant_all_schema_dangerous 1
run_case fail/grant_all_tables_in_schema_dangerous 1
run_case fail/grant_all_public_dangerous 1
run_case fail/default_privileges_grant_all_dangerous 1
run_case redaction/secret_like_sql_comments 0
run_case fail/tenant_derivation_wrong_setting 1 release
run_case fail/tenant_derivation_path_invalid 1 release
run_case fail/tenant_derivation_multihop_policy_missing 1 release
run_case fail/tenant_derivation_missing_fk 1 release
run_case fail/tenant_derivation_policy_without_join 1 release

if grep -R -E 'sk_test_fixture_redaction_123456|fixture_password|postgres://fixture_user' "$OUT"; then
  echo "FAIL redaction: secret-like fixture content leaked into reports" >&2
  exit 1
fi

"$ROOT/run-lm-examples.sh"

echo "Reports: $OUT"
