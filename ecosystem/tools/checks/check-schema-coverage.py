#!/usr/bin/env python3
"""Frontier: "every versioned JSON Schema contract is covered, and says how."

A `*.schema.json` that no validation suite references is a contract nobody
checks: it reads as governed and is not. The danger is not the uncovered schema
itself, it is that the tree gives no signal distinguishing it from the ones that
are genuinely validated on every pull request.

Coverage has two tiers, and this control asserts every schema is in exactly one:

  Tier 1 - fixture-validated. A `Suite` in ecosystem/specs/validate_spec_schemas.py
           validates real instance data against the schema.
  Tier 2 - meta-validated only. The schema has no instance data anywhere, so it is
           compiled and checked as Draft 2020-12 on every run and declared in that
           validator's META_ONLY map WITH THE REASON it has no fixtures.

Tier 2 is deliberately weaker, which is the point: naming it makes the weakness
readable instead of letting an uncovered schema pass for a covered one. It is not
an allowlist, because membership is enforced on the other side too — the validator
FAILS if instance data for a Tier-2 format ever appears, forcing promotion to
Tier 1. Coverage can only ratchet up.

The validator is read with `ast`, not with a regex over its source. A regex
matching quoted filenames counts a schema named in a COMMENT as covered, which is
the exact failure this control exists to prevent: coverage claimed by prose.
Parsing the syntax tree only ever sees real string constants.

Proof of execution: the number of schemas examined and the size of each tier are
printed. A run that examined zero schemas, or that cannot find or parse the
validator, FAILS (exit 2) rather than reporting success.

Exit codes: 0 conform · 1 real gap · 2 unable to search.

Stdlib-only on purpose: this runs in CI with no package installation step.
"""

from __future__ import annotations

import ast
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
SCHEMA_SUFFIX = ".schema.json"


def meta_only_node(tree: ast.Module) -> ast.Dict | None:
    """The module-level `META_ONLY: dict[str, str] = {...}` value, if present."""
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.Assign):
            targets = list(node.targets)
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "META_ONLY":
                return node.value if isinstance(node.value, ast.Dict) else None
    return None


def main() -> int:
    if not VALIDATOR.is_file():
        print(f"FAIL: validator not found at {VALIDATOR}", file=sys.stderr)
        return 2

    try:
        tree = ast.parse(VALIDATOR.read_text(encoding="utf-8"), filename=str(VALIDATOR))
    except SyntaxError as exc:
        print(f"FAIL: validator does not parse: {exc}", file=sys.stderr)
        return 2

    meta_node = meta_only_node(tree)
    if meta_node is None:
        print(
            "FAIL: no module-level META_ONLY dict in the validator - the tier-2 "
            "declaration is gone, so no schema can be shown to be covered by it.",
            file=sys.stderr,
        )
        return 2

    # Tier 2: exact repo-relative paths, read straight from the dict keys.
    tier2: dict[str, str] = {}
    for key, value in zip(meta_node.keys, meta_node.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            print("FAIL: META_ONLY has a non-literal key; it must stay auditable.", file=sys.stderr)
            return 2
        reason = ""
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            reason = value.value
        elif isinstance(value, ast.JoinedStr):
            reason = "<f-string>"
        else:
            # Implicit concatenation of string literals parses to a single Constant,
            # so anything else here is a computed reason - not auditable in source.
            print(
                f"FAIL: META_ONLY entry {key.value} has a non-literal reason.",
                file=sys.stderr,
            )
            return 2
        tier2[key.value] = reason

    # Tier 1: every other *.schema.json string constant in the syntax tree.
    meta_keys = {k.value for k in meta_node.keys if isinstance(k, ast.Constant)}
    tier1_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
            # `len(text) > len(SCHEMA_SUFFIX)` rejects the bare ".schema.json"
            # literal the validator uses to filter filenames. Counting it added a
            # phantom entry to this tier that named no schema.
            if (
                text.endswith(SCHEMA_SUFFIX)
                and len(text) > len(SCHEMA_SUFFIX)
                and text not in meta_keys
            ):
                tier1_names.add(Path(text).name)

    schemas = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", f"*{SCHEMA_SUFFIX}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    examined = len(schemas)
    print(f"examined_schemas={examined}")
    print(f"tier1_fixture_validated={len(tier1_names)}")
    print(f"tier2_meta_validated={len(tier2)}")

    if examined == 0:
        print(
            "FAIL: zero schemas examined - the guard is not looking at anything.",
            file=sys.stderr,
        )
        return 2

    failed = False

    # A tier-2 entry naming a schema that is not tracked is a stale declaration.
    tracked = set(schemas)
    stale = sorted(set(tier2) - tracked)
    if stale:
        print("FAIL: META_ONLY declares a schema that is not tracked:", file=sys.stderr)
        for rel in stale:
            print(f"  {rel}", file=sys.stderr)
        print("  It was renamed or deleted. Drop the entry.", file=sys.stderr)
        failed = True

    uncovered: list[str] = []
    both: list[str] = []
    for rel in schemas:
        in_tier1 = Path(rel).name in tier1_names
        in_tier2 = rel in tier2
        if in_tier1 and in_tier2:
            both.append(rel)
        elif not in_tier1 and not in_tier2:
            uncovered.append(rel)

    if uncovered:
        print("FAIL: schema covered by no validation tier:", file=sys.stderr)
        for rel in uncovered:
            print(f"  {rel}", file=sys.stderr)
        print(
            "  Add a Suite with real fixtures, or declare it in META_ONLY with the "
            "reason it has none. Do not invent fixtures to make this pass.",
            file=sys.stderr,
        )
        failed = True

    if both:
        print("FAIL: schema claimed by BOTH tiers - the signal is ambiguous:", file=sys.stderr)
        for rel in both:
            print(f"  {rel}", file=sys.stderr)
        print("  A fixture-validated schema must not also be declared meta-only.", file=sys.stderr)
        failed = True

    if failed:
        return 1

    print(
        f"OK: all {examined} schemas are covered - "
        f"{examined - len(tier2)} by fixture suites, {len(tier2)} meta-validated only."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
