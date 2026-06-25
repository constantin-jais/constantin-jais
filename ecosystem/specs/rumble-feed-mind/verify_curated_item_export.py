#!/usr/bin/env python3
"""Validate FeedMind CuratedItemExport fixtures and emit proof.

No product runtime is called. This is a deterministic contract/safety smoke:
- structural contract checks;
- Wrench-like PII/secrets/export-policy checks;
- Gear-like artifact/source/provenance reference checks.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from typing import Any

SHA256_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
RFC3339_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SECRET_KEYS = ("secret", "token", "password", "credential", "api_key", "apikey")
PII_KEYS = ("email", "phone", "address", "payment", "stripe", "card")


def root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


def validate_export(payload: dict[str, Any]) -> tuple[bool, list[dict[str, str]]]:
    findings: list[dict[str, str]] = []

    def error(code: str, path: str, message: str) -> None:
        findings.append({"severity": "error", "code": code, "path": path, "message": message})

    if payload.get("format") != "feedmind.curated_item_export.v0.1":
        error("unsupported_format", "format", "expected feedmind.curated_item_export.v0.1")
    for key in ["export_id", "origin_product", "created_by", "created_at", "purpose", "privacy_classification"]:
        if not str(payload.get(key, "")).strip():
            error("missing_required_field", key, f"{key} is required")
    if not RFC3339_Z_RE.match(str(payload.get("created_at", ""))):
        error("invalid_timestamp", "created_at", "created_at must be RFC3339 UTC")

    item = payload.get("item", {})
    for key in ["item_id", "title", "content_hash", "source_url_hash"]:
        if not str(item.get(key, "")).strip():
            error("missing_item_field", f"item.{key}", f"item.{key} is required")
    for key in ["content_hash", "source_url_hash"]:
        if not SHA256_RE.match(str(item.get(key, ""))):
            error("invalid_hash", f"item.{key}", f"item.{key} must be sha256:<64 hex>")

    if payload.get("privacy_classification") == "no_handoff":
        error("no_handoff_export_forbidden", "privacy_classification", "no_handoff items cannot be exported")
    if payload.get("privacy_classification") == "sensitive" and not payload.get("approval_ref"):
        error("sensitive_export_requires_approval", "approval_ref", "sensitive export needs approval_ref")

    constraints = payload.get("constraints", {})
    if constraints.get("contains_secrets") is not False or constraints.get("contains_byok_material") is not False:
        error("secret_or_byok_material_forbidden", "constraints", "exports must not contain secrets or BYOK material")
    if constraints.get("allow_downstream_execution") is not False:
        error("downstream_execution_forbidden", "constraints.allow_downstream_execution", "export cannot allow execution")
    if constraints.get("contains_raw_private_content") is not False:
        error("raw_private_content_forbidden", "constraints.contains_raw_private_content", "raw private content is not allowed")

    artifact = payload.get("artifact_ref", {})
    if not all(str(artifact.get(key, "")).strip() for key in ["artifact_id", "artifact_type", "hash", "manifest_ref"]):
        error("artifact_ref_invalid", "artifact_ref", "artifact ref requires id/type/hash/manifest_ref")
    if not SHA256_RE.match(str(artifact.get("hash", ""))):
        error("artifact_hash_invalid", "artifact_ref.hash", "artifact hash must be sha256:<64 hex>")

    source = payload.get("source_ref", {})
    if source.get("content_hash") != item.get("content_hash"):
        error("source_hash_mismatch", "source_ref.content_hash", "source hash must match item content_hash")
    if not str(source.get("provenance_id", "")).strip():
        error("source_provenance_missing", "source_ref.provenance_id", "source provenance is required")

    provenance = payload.get("provenance_ref", {})
    if provenance.get("provenance_id") != source.get("provenance_id"):
        error("provenance_ref_mismatch", "provenance_ref.provenance_id", "provenance must link source_ref")
    if not RFC3339_Z_RE.match(str(provenance.get("timestamp", ""))):
        error("provenance_timestamp_invalid", "provenance_ref.timestamp", "provenance timestamp must be RFC3339 UTC")

    unsafe_paths = unsafe_key_paths(payload)
    if unsafe_paths:
        error("unsafe_metadata_keys", "payload", ", ".join(unsafe_paths))

    return not any(f["severity"] == "error" for f in findings), findings


def unsafe_key_paths(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if any(marker in lowered for marker in SECRET_KEYS + PII_KEYS):
                # Allow hashed/minimized source URL and explicit boolean safety flags.
                if key not in {"source_url_hash", "contains_secrets", "contains_byok_material"}:
                    found.append(f"{path}.{key}")
            found.extend(unsafe_key_paths(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found.extend(unsafe_key_paths(child, f"{path}[{idx}]"))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=root() / "proofs" / "curated-item-export.proof.json")
    args = parser.parse_args()

    fixtures = root() / "fixtures" / "curated-item-exports"
    valid_path = fixtures / "minimal.valid.json"
    invalid_paths = sorted(fixtures.glob("*.invalid.json"))

    valid_payload = json.loads(valid_path.read_text())
    valid_ok, valid_findings = validate_export(valid_payload)

    invalid_results = []
    for path in invalid_paths:
        payload = json.loads(path.read_text())
        ok, findings = validate_export(payload)
        invalid_results.append({
            "fixture": str(path.relative_to(root())),
            "failed_as_expected": not ok,
            "reason_codes": [finding["code"] for finding in findings if finding["severity"] == "error"],
        })

    proof = {
        "flow": "feedmind_curated_item_export_smoke",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "valid_fixture": {
            "fixture": str(valid_path.relative_to(root())),
            "success": valid_ok,
            "findings": valid_findings,
        },
        "invalid_fixtures": invalid_results,
        "wrench_like_checks": {
            "no_secret_or_byok_material": valid_payload["constraints"]["contains_secrets"] is False and valid_payload["constraints"]["contains_byok_material"] is False,
            "no_downstream_execution": valid_payload["constraints"]["allow_downstream_execution"] is False,
            "no_unsafe_metadata_keys": not unsafe_key_paths(valid_payload),
        },
        "gear_like_checks": {
            "artifact_ref_valid": bool(SHA256_RE.match(valid_payload["artifact_ref"]["hash"])),
            "source_ref_hash_matches_item": valid_payload["source_ref"]["content_hash"] == valid_payload["item"]["content_hash"],
            "provenance_links_source": valid_payload["provenance_ref"]["provenance_id"] == valid_payload["source_ref"]["provenance_id"],
        },
    }
    proof["success"] = (
        proof["valid_fixture"]["success"]
        and all(item["failed_as_expected"] for item in invalid_results)
        and all(proof["wrench_like_checks"].values())
        and all(proof["gear_like_checks"].values())
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"success": proof["success"], "proof": str(args.output)}, indent=2))
    return 0 if proof["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
