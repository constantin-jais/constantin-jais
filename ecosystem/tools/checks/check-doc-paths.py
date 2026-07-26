#!/usr/bin/env python3
"""Frontier: "an operational document only cites paths that exist in this repository."

Scope is deliberately narrow: the documents a contributor follows in order to DO
something. Narrative documents (decompositions, frozen reviews, plans citing the
monorepo) legitimately cite paths outside this tree and are out of scope by
construction -- widening the scope to them would force an allowlist, and an
allowlist is how a guard stops guarding.

Backtick-quoted repo-relative paths are resolved against three bases: the
document's own directory, the repository root, and `ecosystem/` (the historical
root many in-tree documents were written against, back when that directory was
its own repository). A cited path that resolves against none of them is a broken
instruction.

Those three bases are a RESOLUTION rule, not an exemption: every cited path must
still name a file that exists. Widening resolution never lets a missing file
pass, which is why this check carries no allowlist -- an allowlist would.

Proof of execution: the number of documents and of cited paths examined is
printed. A run that examined zero cited paths, or that finds a governed document
missing from the tree, FAILS (exit 2) rather than reporting success -- "found
nothing" and "could not look" must never render identically.

Stdlib-only on purpose: this runs in CI with no package installation step.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    """Resolve the repository root from git, never from __file__ or a hardcoded path.

    Resolving from __file__ silently breaks the moment the script is invoked
    from another working directory; a machine-local absolute path breaks for
    every other checkout and leaks the author's home layout.
    """
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip()).resolve()


ROOT = repo_root()

# Documents that orient a contributor toward an action.
GOVERNED = [
    "docs/ecosystem.md",
    "docs/branch-protection.md",
    "docs/agent-merge-policy.md",
    "docs/release-verification.md",
    "docs/secret-scanning.md",
    "ecosystem/specs/contract-validation.md",
    "ecosystem/specs/README.md",
    "ecosystem/specs/harness/README.md",
    "ecosystem/specs/shared/contracts/README.md",
    "ecosystem/tools/README.md",
    "CONTRIBUTING.md",
]

BACKTICK = re.compile(r"`([^`\s]+)`")
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")
EXT = re.compile(r"\.(md|json|py|sh|yml|yaml|toml|lock|txt)$")


def main() -> int:
    examined = 0
    missing: list[tuple[str, int, str]] = []

    for rel in GOVERNED:
        doc = ROOT / rel
        if not doc.is_file():
            print(f"FAIL: governed document listed but absent: {rel}", file=sys.stderr)
            return 2
        for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            for match in BACKTICK.finditer(line):
                cited = match.group(1)
                if not PATHLIKE.match(cited) or "/" not in cited:
                    continue
                if not (EXT.search(cited) or cited.endswith("/")):
                    continue
                # URLs, home-relative and absolute paths are not repo citations.
                if cited.startswith(("http", "~", "/")):
                    continue
                examined += 1
                candidate = cited.rstrip("/")
                bases = (doc.parent, ROOT, ROOT / "ecosystem")
                if any((base / candidate).exists() for base in bases):
                    continue
                missing.append((rel, lineno, cited))

    print(f"examined_documents={len(GOVERNED)}")
    print(f"examined_cited_paths={examined}")

    if examined == 0:
        print(
            "FAIL: zero cited paths examined - the guard is not looking at anything.",
            file=sys.stderr,
        )
        return 2

    if missing:
        print("FAIL: operational document cites a path that does not exist:", file=sys.stderr)
        for rel, lineno, cited in missing:
            print(f"  {rel}:{lineno}\t{cited}", file=sys.stderr)
        return 1

    print(f"OK: all {examined} cited paths resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
