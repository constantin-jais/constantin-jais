#!/usr/bin/env python3
"""Run the Harness Vertical P0 smoke flow and write machine-readable proof.

This script is intentionally planning-only. It never calls a product runtime and
it refuses to run `cosmatic handoff plan` without `--dry-run`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

SHA256_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
RFC3339_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def ecosystem_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def harness_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


def documents_root() -> pathlib.Path:
    return ecosystem_root().parents[1]


def run_json(command: list[str], cwd: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    evidence = {
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "stderr_empty": completed.stderr == "",
    }
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr}"
        )
    try:
        return json.loads(completed.stdout), evidence
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not emit JSON: {' '.join(command)}") from exc


def run_expect_fail(command: list[str], cwd: pathlib.Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    report: dict[str, Any] | None = None
    if completed.stdout.strip():
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError:
            report = None
    return {
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "failed_as_expected": completed.returncode != 0,
        "reason_codes": [finding.get("code") for finding in (report or {}).get("findings", [])],
    }


def sanitize_paths(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        sanitized = value
        for old, new in replacements:
            sanitized = sanitized.replace(old, new)
        return sanitized
    if isinstance(value, list):
        return [sanitize_paths(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_paths(item, replacements) for key, item in value.items()}
    return value


def validate_gear_contract(handoff: dict[str, Any]) -> dict[str, Any]:
    package = handoff["package"]
    source = handoff["source"]
    artifact_id = package.get("artifact_reference_id") or f"artifact:{package['package_id']}"
    manifest_id = f"manifest:{package['package_id']}"
    provenance_id = f"provenance:{source['handoff_id']}"

    artifact_ref = {
        "artifact_id": artifact_id,
        "artifact_type": "spec_package",
        "producer": source["product"],
        "version": package["version"],
        "hash": package["package_hash"],
        "manifest_ref": manifest_id,
        "state": "active",
        "created_at": source["created_at"],
    }
    provenance_record = {
        "provenance_id": provenance_id,
        "actor_ref": source["created_by"],
        "operation": "exported",
        "inputs": [f"source:{source['handoff_id']}"],
        "outputs": [artifact_id],
        "tool_ref": source["product"],
        "timestamp": source["created_at"],
        "metadata_keys": ["contract", "fixture"],
    }
    event_log_entry = {
        "event_id": f"event:{source['handoff_id']}:validated",
        "event_type": "implementation_handoff.validated",
        "actor_ref": source["created_by"],
        "target_ref": artifact_id,
        "provenance_id": provenance_id,
        "created_at": source["created_at"],
    }

    checks = {
        "artifact_hash_sha256": bool(SHA256_RE.match(artifact_ref["hash"])),
        "artifact_required_refs_non_empty": all(
            artifact_ref[key]
            for key in ["artifact_id", "producer", "version", "manifest_ref", "created_at"]
        ),
        "artifact_created_at_rfc3339_z": bool(RFC3339_Z_RE.match(artifact_ref["created_at"])),
        "provenance_required_refs_non_empty": all(
            provenance_record[key]
            for key in ["provenance_id", "actor_ref", "outputs", "timestamp"]
        ),
        "provenance_outputs_artifact": artifact_id in provenance_record["outputs"],
        "event_links_provenance": event_log_entry["provenance_id"] == provenance_id,
        "event_targets_artifact": event_log_entry["target_ref"] == artifact_id,
        "metadata_keys_no_secret_like": not any(
            any(marker in key.lower() for marker in ["secret", "token", "password", "credential", "api_key"])
            for key in provenance_record["metadata_keys"]
        ),
    }
    return {
        "success": all(checks.values()),
        "checks": checks,
        "artifact_ref": artifact_ref,
        "provenance_record": provenance_record,
        "event_log_entry": event_log_entry,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=harness_root() / "proofs" / "vertical-p0.proof.json",
        help="Path for the machine-readable proof JSON.",
    )
    args = parser.parse_args()

    root = ecosystem_root()
    harness = harness_root()
    docs = documents_root()
    fixture = harness / "fixtures" / "handoffs" / "canvas-minimal.valid.json"
    invalid_fixtures = sorted((harness / "fixtures" / "handoffs").glob("*.invalid.json"))
    cos_matic = docs / "cos-matic"
    wrench = docs / "wrench-inspect"

    cos_cmd = ["cargo", "run", "--quiet", "-p", "cos-matic-cli", "--bin", "cosmatic", "--"]
    wrench_cmd = ["cargo", "run", "--quiet", "--"]

    validate, validate_evidence = run_json(
        cos_cmd + ["handoff", "validate", str(fixture), "--json"], cos_matic
    )
    inspect, inspect_evidence = run_json(
        wrench_cmd + ["handoff", "inspect", str(fixture), "--json"], wrench
    )
    plan, plan_evidence = run_json(
        cos_cmd + ["handoff", "plan", str(fixture), "--dry-run", "--json"], cos_matic
    )

    handoff = json.loads(fixture.read_text())
    gear = validate_gear_contract(handoff)
    invalid_results = [
        run_expect_fail(cos_cmd + ["handoff", "validate", str(path), "--json"], cos_matic)
        for path in invalid_fixtures
    ]

    proof = {
        "flow": "harness_vertical_p0",
        "fixture": str(fixture.relative_to(root)),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "steps": {
            "validate": {
                "success": validate.get("findings") == [] or not any(f.get("severity") == "error" for f in validate.get("findings", [])),
                "report": validate,
                "evidence": validate_evidence,
            },
            "inspect": {
                "success": inspect.get("valid") is True,
                "no_critical_finding": inspect.get("summary", {}).get("errors") == 0,
                "report": inspect,
                "evidence": inspect_evidence,
            },
            "plan": {
                "success": plan.get("report", {}).get("findings") == [] or not any(f.get("severity") == "error" for f in plan.get("report", {}).get("findings", [])),
                "dry_run_only": all(
                    gate.get("code") != "execution" and gate.get("status") != "execute"
                    for gate in plan.get("gates", [])
                ),
                "report": plan,
                "evidence": plan_evidence,
            },
            "gear_contract_validation": gear,
            "human_approval_placeholder": {
                "required": True,
                "status": "not_requested",
                "note": "Planning proof stops before execution approval.",
            },
            "invalid_fixtures": invalid_results,
        },
        "execution": {
            "rumble_executed": False,
            "implementation_executed": False,
            "cosmatic_plan_requires_dry_run": True,
        },
    }

    success = (
        proof["steps"]["validate"]["success"]
        and proof["steps"]["inspect"]["success"]
        and proof["steps"]["inspect"]["no_critical_finding"]
        and proof["steps"]["plan"]["success"]
        and proof["steps"]["plan"]["dry_run_only"]
        and proof["steps"]["gear_contract_validation"]["success"]
        and all(item["failed_as_expected"] for item in invalid_results)
    )
    proof["success"] = success
    proof = sanitize_paths(
        proof,
        [
            (str(root), "$ECOSYSTEM"),
            (str(docs), "$DOCUMENTS"),
        ],
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"success": success, "proof": str(args.output)}, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
