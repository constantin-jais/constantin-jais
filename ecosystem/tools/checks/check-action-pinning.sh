#!/usr/bin/env sh
# Frontier: SECURITY.md - "GitHub Actions must be pinned to commit SHAs."
#
# Declared as policy, enforced by nothing until this guard. Coverage is EVERY
# tracked workflow file, not only the ones GitHub happens to execute: an
# unpinned action sitting in the tree is a supply-chain instruction waiting for
# someone to move it into place.
#
# Proof of execution: the number of `uses:` references examined is printed, and
# a run that examined zero references FAILS (exit 2) instead of reporting
# success.
#
# Portability note: `grep -P` does not exist on BSD/macOS - it exits non-zero
# printing its usage, which reads exactly like "no match". Only POSIX ERE
# (`grep -E`) with explicit character classes is used below.
set -eu

cd "$(git rev-parse --show-toplevel)"

examined=0
offenders=""

for f in $(git ls-files '*.yml' '*.yaml'); do
  case "$f" in *workflows/*) ;; *) continue ;; esac
  while IFS= read -r line; do
    ref=$(printf '%s' "$line" | sed -n 's/.*uses:[[:space:]]*\([^[:space:]]*\).*/\1/p')
    [ -n "$ref" ] || continue
    # Local (./path) and docker:// references are not SHA-pinnable.
    case "$ref" in ./*|docker://*) continue ;; esac
    examined=$((examined + 1))
    sha=${ref##*@}
    if ! printf '%s' "$sha" | grep -qE '^[0-9a-f]{40}$'; then
      offenders="${offenders}${f}: ${ref}
"
    fi
  done <<EOF
$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:' "$f" || true)
EOF
done

echo "examined_action_refs=$examined"

if [ "$examined" -eq 0 ]; then
  echo "FAIL: zero action references examined - the guard is not looking at anything." >&2
  exit 2
fi

if [ -n "$offenders" ]; then
  printf 'FAIL: action not pinned to a 40-char commit SHA (see SECURITY.md):\n%s' "$offenders" >&2
  exit 1
fi

echo "OK: all $examined action references are SHA-pinned."
