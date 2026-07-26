#!/usr/bin/env sh
# Frontier: "GitHub Actions workflows live only at the repository root."
#
# GitHub reads ONLY <root>/.github/workflows/. A workflow file anywhere else is
# inert: it cannot be distinguished from a live gate by reading the tree, and
# `gh api .../actions/workflows` will not list it. That gap is how a repository
# comes to believe it is guarded by a job that has never run once.
#
# Proof of execution: the number of workflow files examined is printed, and a
# run that examined zero files FAILS (exit 2) instead of reporting success.
# "Found nothing" and "could not look" must never render identically.
#
# ---------------------------------------------------------------------------
# Frozen-trace exemption — control-plane ADR 0047 §3
# ---------------------------------------------------------------------------
# ADR 0047 §3 freezes the Harness Vertical P0 stratum "en l'état comme trace,
# plus jamais amendé". That stratum can be neither repaired (its `paths:` filters
# target a directory layout that no longer exists, and its cos-matic /
# wrench-inspect checkouts are 404) nor deleted. Its workflow half is therefore
# named below: one exact path, never a directory and never a pattern.
#
# The exemption is a JOIN, not a mute. Offenders and exempted paths are compared
# in BOTH directions, and either mismatch fails the build:
#
#   offender not named below  -> FAIL: a second, real defect. Exempting it would
#                                be widening the hole; it must be fixed instead.
#   named path not an offender -> FAIL: the exemption has expired, because the
#                                path was deleted, moved to the root, or renamed.
#
# The second direction is the point. An exemption that outlives the defect it
# describes is a permanent hole that reports itself as coverage: the control
# would keep printing OK while silently carrying an exception for a file that no
# longer exists. Failing the day it stops being true forces it back to
# arbitration instead of letting it rot.
set -eu

cd "$(git rev-parse --show-toplevel)"

# One line per exempted path. Adding a line is an owner decision, not a fix.
EXEMPT='ecosystem/.github/workflows/harness-vertical-p0.yml'

# POSIX list membership: newline sentinels on both sides, no external command.
# Deliberately not `grep`: `grep -P` does not exist on BSD/macOS and fails by
# printing its usage, which reads exactly like "no match" to a caller that does
# not check the status. This control runs on macOS and on ubuntu-latest.
contains() { # $1 = needle, $2 = newline-separated haystack
  case "
$2
" in
  *"
$1
"*) return 0 ;;
  esac
  return 1
}

examined=0
offenders=""

for f in $(git ls-files '*.yml' '*.yaml'); do
  case "$f" in
    *workflows/*) ;;
    *) continue ;;
  esac
  examined=$((examined + 1))
  case "$f" in
    .github/workflows/*) continue ;;
  esac
  offenders="${offenders}${f}
"
done

exempt_count=0
for e in $EXEMPT; do
  exempt_count=$((exempt_count + 1))
done

echo "examined_workflow_files=$examined"
echo "frozen_trace_exemptions=$exempt_count"

if [ "$examined" -eq 0 ]; then
  echo "FAIL: zero workflow files examined - the guard is not looking at anything." >&2
  exit 2
fi

failed=0

new_cases=""
for f in $offenders; do
  contains "$f" "$EXEMPT" || new_cases="${new_cases}  ${f}
"
done

stale=""
for e in $EXEMPT; do
  contains "$e" "$offenders" || stale="${stale}  ${e}
"
done

if [ -n "$new_cases" ]; then
  printf 'FAIL: workflow file outside the root .github/workflows/ (never runs):\n%s' "$new_cases" >&2
  echo "  Move it to .github/workflows/. Do not widen the frozen-trace exemption." >&2
  failed=1
fi

if [ -n "$stale" ]; then
  printf 'FAIL: frozen-trace exemption expired - the named path is no longer an offender:\n%s' "$stale" >&2
  echo "  It was deleted, renamed, or moved to the root. Drop the line from EXEMPT." >&2
  failed=1
fi

[ "$failed" -eq 0 ] || exit 1

echo "OK: $examined workflow files examined; all live under .github/workflows/ except the $exempt_count frozen-trace path(s) exempted by control-plane ADR 0047 §3."
