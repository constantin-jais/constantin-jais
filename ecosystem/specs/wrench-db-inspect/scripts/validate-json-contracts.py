#!/usr/bin/env python3
"""Offline contract validator for wrench-db-inspect fixtures.

This intentionally avoids external JSON Schema dependencies. The canonical schemas live in
../contracts/*.schema.json; this script enforces the same required envelope/format/safety fields
for fixture CI and local pre-flight checks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
EXAMPLES = ROOT / "examples"
CONTRACTS = ROOT / "contracts"

SEVERITIES = {"critical", "high", "medium", "low", "info"}
CONFIDENCES = {"high", "medium", "low"}
STATUSES = {"passed", "failed", "passed_with_waiver"}


def fail(path: Path, message: str) -> None:
    raise AssertionError(f"{path}: {message}")


def require(condition: bool, path: Path, message: str) -> None:
    if not condition:
        fail(path, message)


def load(path: Path) -> Any:
    with path.open() as fh:
        return json.load(fh)


def validate_envelope(obj: Any, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    require(isinstance(obj, dict), path, "top-level must be object")
    require(set(obj.keys()) == {"data", "meta"}, path, "top-level keys must be exactly data/meta")
    require(isinstance(obj["data"], dict), path, "data must be object")
    require(isinstance(obj["meta"], dict), path, "meta must be object")
    require(obj["meta"].get("schema_version") == "0.1", path, "meta.schema_version must be 0.1")
    return obj["data"], obj["meta"]


def validate_manifest(path: Path) -> None:
    data, _meta = validate_envelope(load(path), path)
    require(data.get("format") == "wrench.db_inspect.manifest.v0.1", path, "invalid manifest format")
    for key in ["product", "tenant", "roles", "tables", "waivers"]:
        require(key in data, path, f"missing data.{key}")
    tenant = data["tenant"]
    require(isinstance(tenant, dict), path, "tenant must be object")
    for key in ["canonical_name", "column"]:
        require(isinstance(tenant.get(key), str) and tenant[key], path, f"tenant.{key} must be non-empty string")
    if "product_alias" in tenant:
        require(isinstance(tenant.get("product_alias"), str), path, "tenant.product_alias must be string")
    roles = data["roles"]
    require(isinstance(roles, dict), path, "roles must be object")
    for key in ["app", "readonly", "migration"]:
        require(isinstance(roles.get(key), list), path, f"roles.{key} must be array")
        require(all(isinstance(v, str) and v for v in roles[key]), path, f"roles.{key} values must be strings")
    tables = data["tables"]
    require(isinstance(tables, list), path, "tables must be array")
    for idx, table in enumerate(tables):
        require(isinstance(table, dict), path, f"tables[{idx}] must be object")
        for key in ["name", "classification", "contains_personal_data", "contains_embeddings"]:
            require(key in table, path, f"tables[{idx}] missing {key}")
        require(isinstance(table["name"], str) and table["name"], path, f"tables[{idx}].name invalid")
        require(table["classification"] in {"tenant_scoped", "public_reference", "internal", "audit", "audit_system", "unknown"}, path, f"tables[{idx}].classification invalid")
        require(isinstance(table["contains_personal_data"], bool), path, f"tables[{idx}].contains_personal_data must be bool")
        require(isinstance(table["contains_embeddings"], bool), path, f"tables[{idx}].contains_embeddings must be bool")
    require(isinstance(data["waivers"], list), path, "waivers must be array")


def validate_report(path: Path) -> None:
    data, meta = validate_envelope(load(path), path)
    require(data.get("format") == "wrench.db_inspect.report.v0.1", path, "invalid report format")
    require(data.get("status") in STATUSES, path, "invalid data.status")
    summary = data.get("summary")
    require(isinstance(summary, dict), path, "summary must be object")
    require(isinstance(summary.get("gate_blocked"), bool), path, "summary.gate_blocked must be bool")
    findings = data.get("findings")
    require(isinstance(findings, list), path, "findings must be array")
    for idx, finding in enumerate(findings):
        require(isinstance(finding, dict), path, f"findings[{idx}] must be object")
        for key in ["rule_id", "category", "severity", "confidence", "subject"]:
            require(key in finding, path, f"findings[{idx}] missing {key}")
        require(isinstance(finding["rule_id"], str) and finding["rule_id"], path, f"findings[{idx}].rule_id invalid")
        require(finding["severity"] in SEVERITIES, path, f"findings[{idx}].severity invalid")
        require(finding["confidence"] in CONFIDENCES, path, f"findings[{idx}].confidence invalid")
        subject = finding["subject"]
        require(isinstance(subject, dict), path, f"findings[{idx}].subject must be object")
        require(isinstance(subject.get("type"), str) and subject["type"], path, f"findings[{idx}].subject.type invalid")
        require(isinstance(subject.get("name"), str) and subject["name"], path, f"findings[{idx}].subject.name invalid")
    redaction = meta.get("redaction")
    require(isinstance(redaction, dict), path, "meta.redaction must be object")
    require(redaction.get("secrets_or_pii_included") is False, path, "reports must declare no secrets/PII included")


def main() -> int:
    for schema in [CONTRACTS / "manifest.v0.1.schema.json", CONTRACTS / "report.v0.1.schema.json"]:
        load(schema)
    manifest_paths = list(FIXTURES.rglob("manifest.json")) + list(EXAMPLES.glob("security-manifest*.json"))
    report_paths = list(FIXTURES.rglob("expected-report.json"))
    for path in sorted(manifest_paths):
        validate_manifest(path)
    for path in sorted(report_paths):
        validate_report(path)
    print(f"validated {len(manifest_paths)} manifests and {len(report_paths)} expected reports")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
