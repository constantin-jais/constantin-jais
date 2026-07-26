#!/usr/bin/env python3
"""Frontier: "every versioned JSON Schema contract is covered by the validation gate."

A `*.schema.json` in the tree that no Suite in `ecosystem/specs/validate_spec_schemas.py`
references is a contract nobody checks: it reads as governed and is not. The
danger is not the uncovered schema itself, it is that the tree gives no signal
distinguishing it from the nine that are genuinely validated on every pull
request.

Proof of execution: the number of schemas examined and the number referenced by
the validator are printed. A run that examined zero schemas, or that cannot find
the validator, FAILS (exit 2) rather than reporting success.

Stdlib-only on purpose: this runs in CI with no package installation step.

NOT WIRED into a required job yet. Wiring it today would make `main` red: six
schemas are uncovered and covering them means authoring contract fixtures, which
control-plane ADR 0047 routes to the monorepo work-package regime (and two of
the six sit in the `specs/harness` tree that the same ADR freezes as trace).
Weakening the check with an allowlist to make it green would defeat its purpose.
See the pull request that introduced this file for the full disposition.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    """Resolve the repository root from git, never from __file__ or a hardcoded path.

    Resolving from __file__ is what made an earlier draft of this check report
    `FAIL: validator not found` whenever it ran from any directory other than the
    one it happened to live in.
    """
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip()).resolve()


ROOT = repo_root()
VALIDATOR = ROOT / "ecosystem" / "specs" / "validate_spec_schemas.py"

# Schemas the owner has explicitly decided to leave outside the gate.
# Every entry needs a reason; an empty allowlist is the target state, and
# growing this dict to make the check pass is the failure mode it exists to
# prevent.
ALLOWLIST: dict[str, str] = {}


def main() -> int:
    if not VALIDATOR.is_file():
        print(f"FAIL: validator not found at {VALIDATOR}", file=sys.stderr)
        return 2

    source = VALIDATOR.read_text(encoding="utf-8")
    referenced = set(re.findall(r'"([A-Za-z0-9._-]+\.schema\.json)"', source))

    schemas = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.schema.json"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    examined = len(schemas)
    print(f"examined_schemas={examined}")
    print(f"referenced_by_validator={len(referenced)}")

    if examined == 0:
        print(
            "FAIL: zero schemas examined - the guard is not looking at anything.",
            file=sys.stderr,
        )
        return 2

    uncovered = [
        s
        for s in schemas
        if Path(s).name not in referenced and Path(s).name not in ALLOWLIST
    ]
    if uncovered:
        print(
            "FAIL: schema present in the tree but referenced by no validation suite:",
            file=sys.stderr,
        )
        for schema in uncovered:
            print(f"  {schema}", file=sys.stderr)
        return 1

    print(f"OK: all {examined} schemas are referenced by the validation gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
