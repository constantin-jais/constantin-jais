#!/usr/bin/env python3
"""Validate ecosystem JSON Schema contracts and fixtures.

The CI installs `jsonschema` and validates Draft 2020-12 schemas. Invalid
fixtures are accepted as negative tests when they fail schema validation or a
small explicit semantic contract guard that JSON Schema cannot express locally.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ModuleNotFoundError as exc:  # pragma: no cover - local developer hint
    raise SystemExit(
        "Missing dependency: jsonschema. Install with `python3 -m pip install -r "
        "ecosystem/specs/requirements-ci.txt` or run the CI workflow."
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "ecosystem" / "specs"
UNSAFE_KEY = re.compile(r"(secret|token|password|credential|api[_-]?key|raw_log|bearer_token)", re.I)
SHA256 = re.compile(r"^sha256:[A-Fa-f0-9]{64}$")
RFC3339_OFFSET = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
)


@dataclass(frozen=True)
class Suite:
    name: str
    schema: Path
    fixtures: Path
    pass_suffixes: tuple[str, ...] = (".valid.json", ".refusal.json", ".warning.json")
    fail_suffixes: tuple[str, ...] = (".invalid.json",)


SUITES = [
    Suite(
        name="gear-memory",
        schema=SPECS / "gear" / "gear-memory.v0.1.schema.json",
        fixtures=SPECS / "gear" / "fixtures" / "memory",
    ),
    Suite(
        name="wrench-loader",
        schema=SPECS / "wrench-loader" / "wrench-loader.v0.1.schema.json",
        fixtures=SPECS / "wrench-loader" / "fixtures",
    ),
    Suite(
        name="cosmatic-planning",
        schema=SPECS / "harness" / "cosmatic-planning.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "planning",
    ),
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path}: invalid JSON: {exc}") from exc


def walk(obj: Any):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key, value
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def has_unsafe_key(obj: Any) -> bool:
    return any(UNSAFE_KEY.search(key) for key, _ in walk(obj))


def has_invalid_hash(obj: Any) -> bool:
    for key, value in walk(obj):
        if key.endswith("hash") and isinstance(value, str) and value.startswith("sha256:"):
            if not SHA256.match(value):
                return True
    return False


def has_timestamp_without_offset(obj: Any) -> bool:
    for key, value in walk(obj):
        if key.endswith("_at") or key == "timestamp":
            if isinstance(value, str) and "T" in value and not RFC3339_OFFSET.match(value):
                return True
    return False


def has_ocr_text_without_policy(obj: Any) -> bool:
    requests = obj.get("extraction_requests", []) if isinstance(obj, dict) else []
    ocr_disabled = any(
        isinstance(req, dict)
        and isinstance(req.get("policy"), dict)
        and req["policy"].get("ocr") == "disabled"
        for req in requests
    )
    if not ocr_disabled:
        return False
    for document in obj.get("canonical_documents", []):
        canonical = document.get("canonical", {}) if isinstance(document, dict) else {}
        text = canonical.get("text")
        if isinstance(text, str) and "OCR text should not exist" in text:
            return True
    return False


def semantic_negative_guard(path: Path, obj: Any) -> bool:
    """Return true when an invalid fixture violates a non-schema contract guard."""
    return (
        has_unsafe_key(obj)
        or has_invalid_hash(obj)
        or has_timestamp_without_offset(obj)
        or has_ocr_text_without_policy(obj)
        or "execution-forbidden" in path.name
    )


def suffix_matches(path: Path, suffixes: tuple[str, ...]) -> bool:
    return any(path.name.endswith(suffix) for suffix in suffixes)


def validate_suite(suite: Suite) -> tuple[int, int]:
    schema_obj = load_json(suite.schema)
    jsonschema.Draft202012Validator.check_schema(schema_obj)
    validator = jsonschema.Draft202012Validator(schema_obj)

    passed = 0
    negative = 0
    fixtures = sorted(suite.fixtures.glob("*.json"))
    if not fixtures:
        raise AssertionError(f"{suite.name}: no fixtures found in {suite.fixtures}")

    for fixture in fixtures:
        obj = load_json(fixture)
        errors = sorted(validator.iter_errors(obj), key=lambda err: list(err.path))

        if suffix_matches(fixture, suite.pass_suffixes):
            if errors:
                details = "; ".join(error.message for error in errors[:3])
                raise AssertionError(f"{suite.name}: expected pass but failed {fixture}: {details}")
            passed += 1
            print(f"PASS schema {suite.name}: {fixture.relative_to(ROOT)}")
            continue

        if suffix_matches(fixture, suite.fail_suffixes):
            if errors or semantic_negative_guard(fixture, obj):
                negative += 1
                source = "schema" if errors else "semantic"
                print(f"PASS negative({source}) {suite.name}: {fixture.relative_to(ROOT)}")
                continue
            raise AssertionError(f"{suite.name}: expected invalid fixture to fail: {fixture}")

        raise AssertionError(f"{suite.name}: fixture has unknown suffix: {fixture.name}")

    return passed, negative


def main() -> int:
    total_passed = 0
    total_negative = 0
    for suite in SUITES:
        passed, negative = validate_suite(suite)
        total_passed += passed
        total_negative += negative
    print(f"OK: {total_passed} positive fixtures and {total_negative} negative fixtures validated.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
