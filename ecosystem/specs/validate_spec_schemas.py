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
    # Fixtures whose disagreement with their schema is REAL, DIAGNOSED, and not
    # ours to correct. Each entry is (filename, reason). A quarantined fixture is
    # still validated; the entry only changes what its failure means.
    #
    # This is not an allowlist. An allowlist mutes a case forever and reports the
    # suite as clean. A quarantine is a two-way join: the fixture is named, its
    # reason is in source, it is printed on every run, and the build FAILS the day
    # it starts conforming — because a quarantine that outlives the divergence it
    # describes is a permanent hole reporting itself as coverage.
    quarantine: tuple[tuple[str, str], ...] = ()


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
    # These 14 fixtures had never been validated by anything in this repository.
    # Their only consumer was `specs/harness/run_vertical_p0.py`, which shelled
    # out to the `cosmatic` and `wrench-inspect` Rust CLIs — both 404 — driven by
    # a workflow outside the root .github/workflows/ that GitHub therefore never
    # ran. That is why 7 of the 9 `.invalid` fixtures are structurally valid JSON
    # Schema: they encode BUSINESS-rule violations that only the Rust validator
    # detected. Those rules are mechanised below in has_handoff_semantic_violation
    # rather than by editing the fixtures, which control-plane ADR 0047 §3 freezes
    # as trace.
    #
    # `.gate.json` joins the pass suffixes for this suite only. The suffix is
    # documented nowhere, but the fixture carrying it declares `expected_gate`,
    # exactly as the refusal fixtures declare `expected_refusal`: a gated outcome
    # is structurally valid and blocked, not malformed. The classification is read
    # off the fixture, not guessed.
    Suite(
        name="implementation-handoff",
        schema=SPECS / "shared" / "contracts" / "implementation-handoff.v0.1.schema.json",
        fixtures=SPECS / "harness" / "fixtures" / "handoffs",
        pass_suffixes=(".valid.json", ".refusal.json", ".warning.json", ".gate.json"),
        quarantine=(
            (
                "feedmind-curated-export.valid.json",
                "artifact_refs[0] uses the retired vocabulary "
                "{artifact_id, artifact_type, hash, manifest_ref}; $defs/artifactRef now "
                "requires {kind, artifact_reference_id, artifact_kind, manifest_version, "
                "artifact_hash} — a rename with zero field overlap. The fixture is stale, "
                "NOT wrong: specs/harness/proofs/vertical-p0.proof.json, produced by the "
                "runtime of the same day, emits the same retired shape. The contract was "
                "revised and its fixture never migrated. Neither side is ours to correct: "
                "ADR 0047 §3 freezes the fixture as trace, and §1 routes contract "
                "amendments to the monorepo work-package regime. Editing either would "
                "destroy the only evidence of the divergence.",
            ),
        ),
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


def _parsed_timestamp(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def has_handoff_semantic_violation(obj: Any) -> bool:
    """Business rules for canvas.bolt_handoff.v0.1 that JSON Schema cannot express.

    Every rule below is READ OFF the frozen fixtures, never invented: each one is
    the single structural difference between an `.invalid` fixture and
    `canvas-minimal.valid.json`, and each fixture states its own intent in
    `planning_scope.goal` ("Invalid fixture: expired waiver.", ...). Two of the
    rules are self-declared by the fixture itself via `expected_refusal`.

    Scoped by `format`, like every other guard here, so it cannot perturb the
    nine pre-existing suites.
    """
    if not isinstance(obj, dict) or obj.get("format") != "canvas.bolt_handoff.v0.1":
        return False

    # Self-declared refusal: the fixture names the outcome it expects.
    # `expected_gate` is deliberately NOT included — a gated handoff is valid and
    # blocked, not malformed.
    if isinstance(obj.get("expected_refusal"), dict):
        return True

    # A planning request that traces to nothing cannot be planned against.
    if obj.get("kind") == "planning_request" and not obj.get("traceability_links"):
        return True

    waivers = [w for w in obj.get("active_waivers", []) if isinstance(w, dict)]

    # A waiver already expired when the handoff was created was never active.
    #
    # Compared against the handoff's own `source.created_at`, NEVER against the
    # wall clock. A `datetime.now()` comparison here would be a time bomb in a
    # required gate: feedmind-curated-export.valid.json carries a waiver expiring
    # 2026-09-30, so a wall-clock rule would turn this job red on 2026-10-01 with
    # no change to any file. Anchoring to created_at is both reproducible and the
    # stricter reading of the contract.
    created = _parsed_timestamp(obj.get("source", {}).get("created_at"))
    for waiver in waivers:
        expires = _parsed_timestamp(waiver.get("expires_at"))
        if expires is None or created is None:
            continue
        if expires <= created:
            return True

    # An unresolved blocker needs a waiver to carry it, or the handoff is asking
    # the planner to proceed past a known unknown.
    if not waivers:
        for risk in obj.get("risks", []):
            if (
                isinstance(risk, dict)
                and risk.get("status") == "open"
                and risk.get("severity") in {"high", "critical"}
            ):
                return True
        for question in obj.get("open_questions", []):
            if (
                isinstance(question, dict)
                and question.get("status") == "open"
                and question.get("impact") == "blocking"
            ):
                return True

    return False


def has_semantic_contract_violation(obj: Any) -> bool:
    return (
        has_invalid_hash(obj)
        or has_handoff_semantic_violation(obj)
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


def validate_suite(suite: Suite) -> tuple[int, int, int]:
    schema_obj = load_json(suite.schema)
    jsonschema.Draft202012Validator.check_schema(schema_obj)
    validator = jsonschema.Draft202012Validator(
        schema_obj, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )

    passed = 0
    negative = 0
    quarantined = 0
    fixtures = sorted(suite.fixtures.glob("*.json"))
    if not fixtures:
        raise AssertionError(f"{suite.name}: no fixtures found in {suite.fixtures}")

    quarantine = dict(suite.quarantine)
    present = {fixture.name for fixture in fixtures}
    for name in quarantine:
        if name not in present:
            raise AssertionError(
                f"{suite.name}: quarantine names a fixture that is not there: {name}. "
                "It was renamed or deleted - drop the entry."
            )

    for fixture in fixtures:
        obj = load_json(fixture)
        errors = sorted(validator.iter_errors(obj), key=lambda err: list(err.path))

        if fixture.name in quarantine:
            if suffix_matches(fixture, suite.pass_suffixes):
                conforms = not errors and not has_semantic_contract_violation(obj)
            else:
                conforms = bool(errors) or semantic_negative_guard(fixture, obj)
            if conforms:
                raise AssertionError(
                    f"{suite.name}: quarantine EXPIRED - {fixture.name} now conforms to "
                    f"{suite.schema.name}. The divergence it documented is gone; delete "
                    "the entry rather than carrying a hole that reports itself as coverage."
                )
            detail = "; ".join(error.message for error in errors[:2])
            print(f"QUARANTINED {suite.name}: {fixture.relative_to(ROOT)}: {detail}")
            quarantined += 1
            continue

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

    return passed, negative, quarantined


# Standalone documents validated against a schema without a fixtures directory
# (single canonical instances living outside ecosystem/specs/).
# target-version.v1.json retired with the pre-constellation strata
# (archive/pre-constellation-2026-07-19); its successor is the wave-0
# machine-readable inventory ecosystem/repositories.v1.yaml.
STANDALONE = []


# ---------------------------------------------------------------------------
# Tier 2 — schemas covered by META-validation only
# ---------------------------------------------------------------------------
# A schema with no instance data cannot be fixture-validated, but it must not
# therefore be ungoverned: it is compiled and meta-validated as Draft 2020-12 on
# every run, which catches a malformed schema, an unknown keyword, or a broken
# $ref. That is genuinely weaker than a Suite and is declared as such, so the
# tree gives a SIGNAL distinguishing these from the ten that validate instances.
#
# This is a classification, not an allowlist: membership is enforced, not
# asserted. `assert_no_instances` FAILS the build if instance data for one of
# these formats ever appears, forcing promotion to a real Suite. Coverage can
# only ratchet up.
#
# Authoring fixtures for these was rejected rather than done. Inventing instance
# data for a contract with no producer would fabricate coverage: the fixture
# would assert facts nobody verified, and a green suite would then vouch for it.
META_ONLY: dict[str, str] = {
    "ecosystem/specs/harness/stack-target-version.v0.1.schema.json": (
        "Lives in specs/harness, which control-plane ADR 0047 §3 freezes as trace "
        "(gelé en l'état, plus jamais amendé). Its only instance, "
        "ecosystem/target-version.v1.json, was retired by wave-0 option B in d9d1c43. "
        "Authoring a fixture would mean writing into a frozen tree."
    ),
    "ecosystem/specs/harness/stack-target-version.v0.2.schema.json": (
        "Same frozen tree as v0.1 (ADR 0047 §3). The retired ecosystem/target-version.v1.json "
        "did validate against this version cleanly, which is why the pair is kept as trace "
        "rather than deleted; restoring the document would resurrect a stratum option B retired."
    ),
    "ecosystem/specs/shared/contracts/app-store-release.v0.1.schema.json": (
        "No instance has ever existed in the repository's entire history, and the schema "
        "declares no `format` const, so an instance could not even be recognised. Authoring "
        "one is product work that ADR 0047 §1 routes to the monorepo work-package regime."
    ),
    "ecosystem/specs/shared/contracts/curated-item-export.v0.1.schema.json": (
        "Its three fixtures were deleted together with the specs/rumble-feed-mind tree in "
        "d9d1c43 (wave-0 option B). They still validate today, but restoring them would "
        "resurrect a retired stratum that a required job refuses on main."
    ),
    "ecosystem/specs/shared/contracts/spec-package.v0.1.schema.json": (
        "No instance has ever existed in the repository's entire history. Authoring one is "
        "product work that ADR 0047 §1 routes to the monorepo work-package regime."
    ),
}


def declared_format(schema_obj: Any) -> str | None:
    """The `format` const a conforming instance must carry, when the schema pins one."""
    if not isinstance(schema_obj, dict):
        return None
    fmt = schema_obj.get("properties", {}).get("format", {})
    const = fmt.get("const") if isinstance(fmt, dict) else None
    return const if isinstance(const, str) else None


def validate_meta_only() -> int:
    """Compile every Tier-2 schema, and refuse to let one keep that status silently."""
    for rel, reason in META_ONLY.items():
        schema_path = ROOT / rel
        if not schema_path.is_file():
            raise AssertionError(
                f"meta-only: declared schema is absent: {rel}. Drop the entry - a "
                "classification for a file that no longer exists is not coverage."
            )
        if not reason.strip():
            raise AssertionError(f"meta-only: {rel} carries no reason.")
        schema_obj = load_json(schema_path)
        jsonschema.Draft202012Validator.check_schema(schema_obj)

        fmt = declared_format(schema_obj)
        if fmt is not None:
            for candidate in sorted(SPECS.rglob("*.json")):
                if candidate.name.endswith(".schema.json"):
                    continue
                try:
                    obj = json.loads(candidate.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                if isinstance(obj, dict) and obj.get("format") == fmt:
                    raise AssertionError(
                        f"meta-only: {rel} is declared instance-less, but "
                        f"{candidate.relative_to(ROOT)} carries format '{fmt}'. "
                        "Promote it to a Suite - meta-validation is no longer the most "
                        "this schema can be held to."
                    )
        print(f"PASS meta-only schema: {rel}")
    return len(META_ONLY)


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
    total_quarantined = 0
    for suite in SUITES:
        passed, negative, quarantined = validate_suite(suite)
        total_passed += passed
        total_negative += negative
        total_quarantined += quarantined
    for schema_path, document in STANDALONE:
        total_negative += validate_standalone(schema_path, document)
        total_passed += 1
    meta_only = validate_meta_only()

    # Proof of execution: a run that validated nothing must never print OK.
    if total_passed == 0:
        print("FAIL: zero positive fixtures validated - the gate ran over nothing.", file=sys.stderr)
        return 1

    print(
        f"OK: {total_passed} positive fixtures and {total_negative} negative fixtures "
        f"validated across {len(SUITES)} suites; {meta_only} schemas meta-validated only; "
        f"{total_quarantined} fixture(s) quarantined."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
