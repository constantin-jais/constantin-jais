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
set -eu

cd "$(git rev-parse --show-toplevel)"

examined=0
offenders=""

for f in $(git ls-files '*.yml' '*.yaml'); do
  case "$f" in
    *workflows/*) ;;
    *) continue ;;
  esac
  examined=$((examined + 1))
  case "$f" in
    .github/workflows/*) ;;
    *) offenders="${offenders}${f}
" ;;
  esac
done

echo "examined_workflow_files=$examined"

if [ "$examined" -eq 0 ]; then
  echo "FAIL: zero workflow files examined - the guard is not looking at anything." >&2
  exit 2
fi

if [ -n "$offenders" ]; then
  printf 'FAIL: workflow file outside the root .github/workflows/ (never runs):\n%s' "$offenders" >&2
  exit 1
fi

echo "OK: all $examined workflow files live under .github/workflows/."
