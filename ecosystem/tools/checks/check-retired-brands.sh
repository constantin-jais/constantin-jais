#!/usr/bin/env sh
# Frontier: "a retired brand never appears outside a dated record."
#
# A retired brand surviving in a living document is not a cosmetic blemish: it is
# a document asserting, in the present tense, a name the owner has withdrawn. A
# reader cannot tell it from current truth, because nothing on the line says it
# is dead.
#
# This control replaces an inline step in stack-conventions.yml that greps a
# hardcoded list of eight paths. THREE of those paths — ecosystem/target-version.md,
# ecosystem/product-portfolio.md, ecosystem/product-readiness.md — are paths the
# step immediately above it FAILS the build for having ("retired strata stay
# retired"). They can never exist. grep reports "No such file or directory" and
# exits 2; `2>/dev/null || true` discards both the message and the status. The
# step still works over its five real paths — it is degraded, not blind — but it
# reports a corpus of eight while examining five, and nothing says so. Declared
# coverage and real coverage drifted apart silently, which is the exact failure
# mode a control exists to prevent.
#
# It also looked at neither ecosystem/specs/, nor docs/, nor ecosystem/reviews/ —
# so the whole ADR series, the whole contract series and the decision log were
# outside the corpus. This version enumerates from `git grep` over every tracked
# text file instead of from a hand-maintained list, so a new document joins the
# corpus by existing.
#
# Proof of execution: the number of tracked text files examined is printed, and a
# run that examined zero FAILS (exit 2) rather than reporting success. "Found
# nothing" and "could not look" must never render identically.
#
# Exit codes: 0 conform · 1 real gap · 2 unable to search.
#
# ---------------------------------------------------------------------------
# What is guarded, and what is deliberately NOT
# ---------------------------------------------------------------------------
# Guarded: the brands whose retirement is SETTLED in the decision log —
# "Daidalos" (and daidalos.dev, never purchased) and "Free AI" (and free-ai.fr),
# both flipped to Superseded on 2026-07-19 by monorepo ADR-0008.
#
# NOT guarded: « Libre IA ». The arbitration §6.1 reserved to the owner is now
# SETTLED — the decision-log row of 2026-07-19 prevails by posteriority over
# control-plane ADR 0046 (2026-07-12), which carries a historical note saying so.
# The spelling question is closed; encoding it here is still refused, and the
# reason changed from "the owner has not decided" to "this token cannot be
# expressed without failing on live truth". Measured, not assumed:
#
#   token `libre ia` alone      -> 14 hits / 5 files, ALL legitimate
#   tokens `libre ia`+`libre-ia`-> 23 hits / 8 files, ALL legitimate
#
# (Reproduce by adding the tokens to brand_files/brand_hits below and running.
# The counts include the ADR 0046 historical note itself: the token would fail on
# the very document that records the decision it claims to enforce.)
#
# Three reasons it stays out, each fatal on its own:
#
#   1. `libre-ia.fr` is NOT retired. ADR 0046 keeps it defensive and 301-redirected
#      and no later decision withdrew it; the 2026-07-24 row corrected the org blog
#      FIELD to libre-ai.fr, it did not retire the domain. `free-ai` subsumes
#      free-ai.fr because that domain IS dead. The analogy breaks here.
#   2. `rumble-libre-ia` is a live legacy product slug (ecosystem/specs/README.md,
#      curated-item-export.v0.1.md, and a maturity fixture frozen as trace by
#      ADR 0047 §3). The guard's own remedy line — "Rename it to the current
#      brand" — would be actively wrong advice on all three.
#   3. It would fail on its own documentation. ecosystem/tools/README.md names
#      « Libre IA » precisely to say it is NOT guarded, and that file is a LIVING
#      document — it cannot be exempted as a "dated record" without making the
#      exemption list lie about what it contains. (This script escapes only
#      because it is already exempt for naming Daidalos and Free AI.)
#
# And the EXEMPT list is brand-agnostic: exempting ADR 0037/0042/0046 for
# « Libre IA » would also exempt them for Daidalos and Free AI — silently widening
# the holes this control exists to keep narrow.
#
# What DOES enforce the spelling: « Libre IA » in a living document is caught by
# review, and the monorepo runs its own doctrine guard for its own corpus
# (2026-07-24 row, monorepo PR #239). Per-context replication, not a shared table.
# Today no living document in THIS repo asserts « Libre IA » as the current brand:
# every occurrence is a dated record or a negative citation like this one.
#
# ---------------------------------------------------------------------------
# Dated-record exemptions
# ---------------------------------------------------------------------------
# Three tracked files legitimately name a retired brand. Each is a DATED record:
# every assertion in it is anchored to a date and reads as "what was true then",
# never as current truth. That is the whole reason the decision log is a living
# registry rather than a purge target — see its header. Naming a dead brand is
# what those files are FOR.
#
# The exemption is a JOIN, not a mute. Named paths and offenders are compared in
# BOTH directions, and either mismatch fails the build:
#
#   offender not named below   -> FAIL: a retired brand reached a living document.
#   named path with no hit     -> FAIL: the exemption expired — the file was
#                                 renamed, deleted, or scrubbed. A silent
#                                 exemption for a file that no longer needs one
#                                 is a permanent hole reporting itself as
#                                 coverage.
set -eu

cd "$(git rev-parse --show-toplevel)"

# One line per exempted path, exact paths only — never a directory, never a
# pattern. A directory exemption would silently cover files added to it later.
EXEMPT='ecosystem/specs/shared/decision-log.md
ecosystem/reviews/hygiene-audit-2026-07-09.md
ecosystem/tools/checks/check-retired-brands.sh'

# Tokens are short and unescaped on purpose. A previous incident in this repo:
# `git grep -P 'foo\.bar@'` returned zero on a file that contained the token,
# because the escaping interacted with the stored text. Short literal tokens
# matched case-insensitively cannot fail that way. `free-ai` subsumes
# `free-ai.fr`; `daidalos` subsumes `daidalos.dev`.
#
# Deliberately NOT plain `grep`: `grep -P` does not exist on BSD/macOS and fails
# by printing its usage, which reads exactly like "no match" to a caller that
# does not check the status. `git grep` behaves identically on macOS and on
# ubuntu-latest, and -I skips binaries.
brand_files() {
  git grep -I -l -i -e 'daidalos' -e 'free-ai' -e 'free ai' || true
}

brand_hits() { # $1 = path
  git grep -I -n -i -e 'daidalos' -e 'free-ai' -e 'free ai' -- "$1" || true
}

# POSIX list membership: newline sentinels on both sides, no external command.
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

# Every tracked text file. `-e ''` matches every line, so -l yields the corpus
# git grep is actually able to search — not a hand-kept list that can drift.
text_files=$(git grep -I -l -e '' || true)

examined=0
for f in $text_files; do
  examined=$((examined + 1))
done

exempt_count=0
for e in $EXEMPT; do
  exempt_count=$((exempt_count + 1))
done

echo "examined_text_files=$examined"
echo "dated_record_exemptions=$exempt_count"

if [ "$examined" -eq 0 ]; then
  echo "FAIL: zero text files examined - the guard is not looking at anything." >&2
  exit 2
fi

matches=$(brand_files)

failed=0

offenders=""
for f in $matches; do
  contains "$f" "$EXEMPT" || offenders="${offenders}${f}
"
done

stale=""
for e in $EXEMPT; do
  contains "$e" "$matches" || stale="${stale}  ${e}
"
done

if [ -n "$offenders" ]; then
  echo "FAIL: retired brand in a living document (not a dated record):" >&2
  for f in $offenders; do
    brand_hits "$f" | while IFS= read -r line; do
      printf '  %s\n' "$line" >&2
    done
  done
  echo "  Rename it to the current brand. Do not add the file to EXEMPT." >&2
  failed=1
fi

if [ -n "$stale" ]; then
  printf 'FAIL: dated-record exemption expired - the named path no longer names a retired brand:\n%s' "$stale" >&2
  echo "  It was deleted, renamed, or scrubbed. Drop the line from EXEMPT." >&2
  failed=1
fi

[ "$failed" -eq 0 ] || exit 1

echo "OK: $examined text files examined; retired brands appear only in the $exempt_count dated record(s) that exist to name them."
