#!/usr/bin/env python3
"""Frontier: "tracked tooling never resolves a path above the repository root."

A script in this repository that reaches for a sibling directory assumes a
checkout layout the repository cannot guarantee, and silently couples this
bounded context to another one. The failure mode is not a crash: it is a script
that appears to work on one machine and quietly does nothing everywhere else.

Proof of execution: the number of scripts examined is printed, and a run that
examined zero scripts FAILS (exit 2) rather than reporting success.

Stdlib-only on purpose: this runs in CI with no package installation step.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


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

# Line-scoped escape hatch, mirroring the tree's existing `allow-local-path`
# convention. It must stay line-scoped and explicit: a directory-wide or
# pattern-wide allowlist would turn this guard into decoration.
EXEMPT = re.compile(r"allow-repo-escape")


def main() -> int:
    files = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.py", "*.sh", "*.bash"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    examined = len(files)
    print(f"examined_scripts={examined}")

    if examined == 0:
        print(
            "FAIL: zero scripts examined - the guard is not looking at anything.",
            file=sys.stderr,
        )
        return 2

    offenders: list[str] = []
    for rel in files:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if EXEMPT.search(line):
                continue
            for pattern, why in PATTERNS:
                if pattern.search(line):
                    offenders.append(f"  {rel}:{lineno}\t{why}\n    {line.strip()}")

    if offenders:
        print("FAIL: tracked tooling resolves a path outside this repository:", file=sys.stderr)
        for offender in offenders:
            print(offender, file=sys.stderr)
        return 1

    print(f"OK: none of the {examined} tracked scripts escape the repository root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
