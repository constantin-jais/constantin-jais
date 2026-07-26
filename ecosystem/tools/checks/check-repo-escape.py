#!/usr/bin/env python3
"""Frontier: "tracked tooling never resolves a path above the repository root."

A script in this repository that reaches for a sibling directory assumes a
checkout layout the repository cannot guarantee, and silently couples this
bounded context to another one. The failure mode is not a crash: it is a script
that appears to work on one machine and quietly does nothing everywhere else.

Proof of execution: the number of scripts examined is printed, and a run that
examined zero scripts FAILS (exit 2) rather than reporting success.

Frozen-trace exemption -- control-plane ADR 0047 section 3
----------------------------------------------------------
ADR 0047 section 3 freezes the Harness Vertical P0 stratum "en l'etat comme
trace, plus jamais amende". Its script half cannot be repaired (the sibling
checkouts it resolves are 404) and cannot be deleted, so its single offending
line is named below by fingerprint.

The exemption is a JOIN, not a mute. Offending findings and exemptions are
matched in BOTH directions, and either mismatch fails the build:

    finding with no exemption -> FAIL: a second, real defect. It must be fixed,
                                 not exempted; widening is how a guard dies.
    exemption with no finding -> FAIL: the exemption expired, because the file
                                 was deleted or the line was edited.

The second direction is the point. An exemption that outlives the defect it
describes is a permanent hole that reports itself as coverage. Fingerprinting
the exact line -- not the file -- keeps it nominative: a *second* escape added
to the very same frozen file is still reported.

Stdlib-only on purpose: this runs in CI with no package installation step.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


def repo_root() -> Path:
    """Resolve the repository root from git, never from __file__ or a hardcoded path."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip()).resolve()


ROOT = repo_root()

PATTERNS = [
    (re.compile(r"\.\./\.\."), "relative path climbing two or more levels"),
    (re.compile(r"parents\[\s*\d+\s*\]\s*\.\s*parents\[\s*\d+\s*\]"), "chained .parents[] climb"),
    (re.compile(r"ecosystem_root\(\)\.parents\["), "climb above the repository root"),
    (re.compile(r"\bgit\s+-C\s+\.\./"), "git -C into a sibling checkout"),
]


class Exemption(NamedTuple):
    """One frozen-trace finding that is known, arbitrated, and unfixable."""

    path: str
    why: str
    line_sha256: str


def fingerprint(line: str) -> str:
    """Whitespace-normalised SHA-256 of an offending source line.

    Normalising collapses reindentation noise; hashing keeps the offending text
    out of THIS file. Quoting `run_vertical_p0.py`'s escaping line verbatim here
    would make this control its own offender -- a guard that has to exempt
    itself has already lost the argument.
    """
    return hashlib.sha256(" ".join(line.split()).encode("utf-8")).hexdigest()


# Nominative exemptions: one exact (file, defect, line) triple each, never a
# directory and never a pattern. Adding an entry is an owner decision recorded
# against an ADR, not a way to make a red control green.
#
# ecosystem/specs/harness/run_vertical_p0.py -- the Harness Vertical P0 script
# resolves the sibling checkouts of `cos-matic` and `wrench-inspect` by climbing
# out of the repository. Both targets are 404 and the workflow that called it is
# invisible to GitHub, so the escape is inert; ADR 0047 section 3 forbids both
# amending and deleting the stratum, which is why it is exempted rather than
# fixed.
FROZEN_TRACE_EXEMPTIONS: tuple[Exemption, ...] = (
    Exemption(
        path="ecosystem/specs/harness/run_vertical_p0.py",
        why="climb above the repository root",
        line_sha256="7d7102f8810a20b1f44119d44749af13e04f7caf54b384c4021b72da06a0d7a5",
    ),
)


def main() -> int:
    files = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.py", "*.sh", "*.bash"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    examined = len(files)
    print(f"examined_scripts={examined}")
    print(f"frozen_trace_exemptions={len(FROZEN_TRACE_EXEMPTIONS)}")

    if examined == 0:
        print(
            "FAIL: zero scripts examined - the guard is not looking at anything.",
            file=sys.stderr,
        )
        return 2

    # key -> human-readable evidence, for every escape currently in the tree.
    findings: dict[Exemption, str] = {}
    for rel in files:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, why in PATTERNS:
                if pattern.search(line):
                    key = Exemption(rel, why, fingerprint(line))
                    findings.setdefault(key, f"  {rel}:{lineno}\t{why}\n    {line.strip()}")

    known = set(FROZEN_TRACE_EXEMPTIONS)
    new_cases = [evidence for key, evidence in findings.items() if key not in known]
    stale = [exemption for exemption in FROZEN_TRACE_EXEMPTIONS if exemption not in findings]

    failed = False

    if new_cases:
        print("FAIL: tracked tooling resolves a path outside this repository:", file=sys.stderr)
        for evidence in new_cases:
            print(evidence, file=sys.stderr)
        print(
            "  Fix it. Do not widen the frozen-trace exemption to cover it.",
            file=sys.stderr,
        )
        failed = True

    if stale:
        print(
            "FAIL: frozen-trace exemption expired - no such finding in the tree:",
            file=sys.stderr,
        )
        for exemption in stale:
            print(f"  {exemption.path}\t{exemption.why}", file=sys.stderr)
            print(f"    line sha256 {exemption.line_sha256} matches nothing", file=sys.stderr)
        print(
            "  The file was deleted or the line was edited. Drop the entry from"
            " FROZEN_TRACE_EXEMPTIONS.",
            file=sys.stderr,
        )
        failed = True

    if failed:
        return 1

    print(
        f"OK: none of the {examined} tracked scripts escape the repository root,"
        f" beyond the {len(FROZEN_TRACE_EXEMPTIONS)} frozen-trace line(s) exempted"
        " by control-plane ADR 0047 section 3."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
