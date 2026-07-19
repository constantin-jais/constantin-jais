#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema==4.23.0"]
# ///
"""Validate ecosystem JSON Schema contracts and fixtures.

The CI installs `jsonschema` and validates Draft 2020-12 schemas. Invalid
fixtures are accepted as negative tests when they fail schema validation or a
small explicit semantic contract guard that JSON Schema cannot express locally.
"""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ModuleNotFoundError as exc:  # pragma: no cover - local developer hint
    raise SystemExit(
        "Missing dependency: jsonschema. Run via `uv run --script "
        "ecosystem/specs/validate_spec_schemas.py` (or `sh "
        "ecosystem/specs/ci-validate-contracts.sh`)."
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
    # gear-memory and gear-loader suites retired with their spec trees
    # (archive/pre-constellation-2026-07-19, wave 0 option B).
    Suite(
        name="cosmatic-planning",
        schema=SPECS / "harness" / "cosmatic-planning.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "planning",
    ),
    Suite(
        name="human-approval",
        schema=SPECS / "harness" / "human-approval.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "human-approval",
    ),
    Suite(
        name="approval-key-registry",
        schema=SPECS / "harness" / "approval-key-registry.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "approval-key-registry",
    ),
    Suite(
        name="rumble-delivery-maturity",
        schema=SPECS / "harness" / "rumble-delivery-maturity.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "maturity",
    ),
    Suite(
        name="workspace-identity",
        schema=SPECS / "shared" / "contracts" / "workspace-identity.v0.1.schema.json",
        fixtures=SPECS / "shared" / "contracts" / "fixtures" / "workspace-identity",
    ),
    Suite(
        name="authorization-registries",
        schema=SPECS / "shared" / "contracts" / "authorization-registries.v0.1.schema.json",
        fixtures=SPECS / "shared" / "contracts" / "fixtures" / "authorization-registries",
    ),
    Suite(
        name="parser-runtime-attestation",
        schema=SPECS / "shared" / "contracts" / "parser-runtime-attestation.v0.1.schema.json",
        fixtures=SPECS / "shared" / "contracts" / "fixtures" / "parser-runtime-attestation",
    ),
    Suite(
        name="progress-snapshot",
        schema=SPECS / "shared" / "contracts" / "progress-snapshot.v0.1.schema.json",
        fixtures=SPECS / "shared" / "contracts" / "fixtures" / "progress-snapshot",
    ),
    Suite(
        name="job-runtime",
        schema=SPECS / "shared" / "contracts" / "job-runtime.v0.1.schema.json",
        fixtures=SPECS / "shared" / "contracts" / "fixtures" / "job-runtime",
    ),
]

LEVEL_ORDER = {f"R{i}": i for i in range(11)}


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


def has_duplicate_approval_key_ref(obj: Any) -> bool:
    if not isinstance(obj, dict) or obj.get("format") != "bolt.approval_key_registry.v0.1":
        return False
    seen: set[str] = set()
    for key in obj.get("keys", []):
        if not isinstance(key, dict):
            continue
        key_ref = key.get("public_key_ref")
        if not isinstance(key_ref, str):
            continue
        if key_ref in seen:
            return True
        seen.add(key_ref)
    return False


def has_maturity_semantic_violation(obj: Any) -> bool:
    if not isinstance(obj, dict) or obj.get("format") != "rumble.delivery_maturity.v0.1":
        return False

    current = LEVEL_ORDER.get(obj.get("current_level", ""), -1)
    target = LEVEL_ORDER.get(obj.get("target_level", ""), -1)
    next_level = LEVEL_ORDER.get(obj.get("next_level", obj.get("current_level", "")), current)
    if current < 0 or target < 0 or target < current or next_level < current:
        return True

    axes = obj.get("axes", {})
    core = axes.get("core", {}) if isinstance(axes, dict) else {}
    security = axes.get("security", {}) if isinstance(axes, dict) else {}
    release = axes.get("release", {}) if isinstance(axes, dict) else {}

    core_level = LEVEL_ORDER.get(core.get("level", ""), -1) if isinstance(core, dict) else -1
    core_status = core.get("status") if isinstance(core, dict) else None
    security_status = security.get("status") if isinstance(security, dict) else None
    release_status = release.get("status") if isinstance(release, dict) else None

    # R7 mobile must not be claimed without a non-duplicated portable core,
    # except for projects explicitly marked as non-applicable static content sites
    # below R7.
    if current >= 7 and (core_level < 2 or core_status in {"blocked", "not_applicable"}):
        return True

    # Commercializable maturity cannot hide security/release/open-question gaps.
    if current >= 10:
        if security_status != "pass" or release_status != "pass":
            return True
        if obj.get("open_questions"):
            return True

    promotion = obj.get("promotion_candidate")
    if isinstance(promotion, dict):
        if promotion.get("status") == "blocked" and not promotion.get("blocked_by"):
            return True
        if promotion.get("status") == "pass" and promotion.get("blocked_by"):
            return True

    return False


def has_authorization_registry_semantic_violation(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if obj.get("format") == "bolt.biscuit_keyset.v0.1":
        key_ids: set[str] = set()
        public_keys: set[str] = set()
        for key in obj.get("keys", []):
            if not isinstance(key, dict):
                continue
            key_id = key.get("key_id")
            public_key = key.get("public_key_hex")
            if isinstance(key_id, str):
                if key_id in key_ids:
                    return True
                key_ids.add(key_id)
            if isinstance(public_key, str):
                normalized = public_key.lower()
                if normalized in public_keys:
                    return True
                public_keys.add(normalized)
            try:
                not_before = datetime.fromisoformat(
                    key.get("not_before", "").replace("Z", "+00:00")
                )
                not_after = datetime.fromisoformat(
                    key.get("not_after", "").replace("Z", "+00:00")
                )
            except (AttributeError, TypeError, ValueError):
                return True
            if not_before >= not_after:
                return True
        return False
    if obj.get("format") == "bolt.biscuit_revocations.v0.1":
        revocation_refs: set[str] = set()
        root_block_ids: set[str] = set()
        for entry in obj.get("entries", []):
            if not isinstance(entry, dict):
                continue
            revocation_ref = entry.get("revocation_ref")
            root_block_id = entry.get("root_block_id")
            if isinstance(revocation_ref, str):
                if revocation_ref in revocation_refs:
                    return True
                revocation_refs.add(revocation_ref)
            if isinstance(root_block_id, str):
                normalized = root_block_id.lower()
                if normalized in root_block_ids:
                    return True
                root_block_ids.add(normalized)
    return False


def has_progress_semantic_violation(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    completed = obj.get("completed_units")
    total = obj.get("total_units")
    return isinstance(completed, int) and isinstance(total, int) and completed > total


def has_job_runtime_semantic_violation(obj: Any) -> bool:
    if not isinstance(obj, dict) or obj.get("format") != "sessions.job_runtime.v0.1":
        return False
    jobs = obj.get("jobs", [])
    if any(
        isinstance(job, dict)
        and isinstance(job.get("attempts"), int)
        and isinstance(job.get("max_attempts"), int)
        and job["attempts"] > job["max_attempts"]
        for job in jobs
    ):
        return True
    event_ids = {
        event.get("event_id")
        for event in obj.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("event_id"), str)
    }
    return any(
        isinstance(claim, dict)
        and isinstance(claim.get("event"), dict)
        and claim["event"].get("event_id") not in event_ids
        for claim in obj.get("claims", [])
    )


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


def has_semantic_contract_violation(obj: Any) -> bool:
    return (
        has_invalid_hash(obj)
        or has_timestamp_without_offset(obj)
        or has_ocr_text_without_policy(obj)
        or has_duplicate_approval_key_ref(obj)
        or has_maturity_semantic_violation(obj)
        or has_authorization_registry_semantic_violation(obj)
        or has_progress_semantic_violation(obj)
        or has_job_runtime_semantic_violation(obj)
    )


def semantic_negative_guard(path: Path, obj: Any) -> bool:
    """Return true when an invalid fixture violates a non-schema contract guard."""
    return (
        has_unsafe_key(obj)
        or has_semantic_contract_violation(obj)
        or "execution-forbidden" in path.name
    )


def suffix_matches(path: Path, suffixes: tuple[str, ...]) -> bool:
    return any(path.name.endswith(suffix) for suffix in suffixes)


def validate_suite(suite: Suite) -> tuple[int, int]:
    schema_obj = load_json(suite.schema)
    jsonschema.Draft202012Validator.check_schema(schema_obj)
    validator = jsonschema.Draft202012Validator(
        schema_obj, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )

    passed = 0
    negative = 0
    fixtures = sorted(suite.fixtures.glob("*.json"))
    if not fixtures:
        raise AssertionError(f"{suite.name}: no fixtures found in {suite.fixtures}")

    for fixture in fixtures:
        obj = load_json(fixture)
        errors = sorted(validator.iter_errors(obj), key=lambda err: list(err.path))

        if suffix_matches(fixture, suite.pass_suffixes):
            semantic_violation = has_semantic_contract_violation(obj)
            if errors or semantic_violation:
                details = "; ".join(error.message for error in errors[:3])
                if semantic_violation:
                    details = f"{details}; semantic contract violation".lstrip("; ")
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


# Standalone documents validated against a schema without a fixtures directory
# (single canonical instances living outside ecosystem/specs/).
STANDALONE = [
    (
        SPECS / "harness" / "stack-target-version.v0.2.schema.json",
        ROOT / "ecosystem" / "target-version.v1.json",
    ),
]


def validate_standalone(schema_path: Path, document: Path) -> int:
    schema_obj = load_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema_obj)
    validator = jsonschema.Draft202012Validator(
        schema_obj, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )
    obj = load_json(document)
    errors = sorted(validator.iter_errors(obj), key=lambda err: list(err.path))
    if errors:
        details = "; ".join(error.message for error in errors[:3])
        raise AssertionError(
            f"standalone: {document.relative_to(ROOT)} failed {schema_path.name}: {details}"
        )
    if has_unsafe_key(obj):
        raise AssertionError(f"standalone: {document.relative_to(ROOT)} contains an unsafe key")
    print(f"PASS schema standalone: {document.relative_to(ROOT)}")

    negative = 0
    required_cases = [([], field) for field in schema_obj.get("required", [])]
    authorization_schema = schema_obj.get("properties", {}).get("authorization", {})
    required_cases.extend(
        (["authorization"], field) for field in authorization_schema.get("required", [])
    )
    for parent_path, field in required_cases:
        mutated = deepcopy(obj)
        parent = mutated
        for segment in parent_path:
            parent = parent[segment]
        parent.pop(field)
        if not any(validator.iter_errors(mutated)):
            location = ".".join([*parent_path, field])
            raise AssertionError(
                f"standalone: deleting required field {location} unexpectedly passed"
            )
        negative += 1
    print(f"PASS negative(required fields) standalone: {negative} removals refused")
    return negative


def main() -> int:
    total_passed = 0
    total_negative = 0
    for suite in SUITES:
        passed, negative = validate_suite(suite)
        total_passed += passed
        total_negative += negative
    for schema_path, document in STANDALONE:
        total_negative += validate_standalone(schema_path, document)
        total_passed += 1
    print(f"OK: {total_passed} positive fixtures and {total_negative} negative fixtures validated.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
