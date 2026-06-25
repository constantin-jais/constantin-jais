#!/usr/bin/env python3
"""Prove FeedMind planning-only handoff readiness.

Runs cos-matic validate, wrench-inspect inspect, and cos-matic plan --dry-run
against the FeedMind curated export handoff fixture. No implementation work is
executed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


def ecosystem_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def documents_root() -> pathlib.Path:
    return ecosystem_root().parents[1]


def run_json(command: list[str], cwd: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    completed = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    evidence = {"command": command, "cwd": str(cwd), "exit_code": completed.returncode, "stderr_empty": completed.stderr == ""}
    if completed.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(command)}\n{completed.stderr}")
    return json.loads(completed.stdout), evidence


def sanitize_paths(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        result = value
        for old, new in replacements:
            result = result.replace(old, new)
        return result
    if isinstance(value, list):
        return [sanitize_paths(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_paths(item, replacements) for key, item in value.items()}
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=ecosystem_root() / "specs" / "rumble-feed-mind" / "proofs" / "handoff-planning.proof.json")
    args = parser.parse_args()

    root = ecosystem_root()
    docs = documents_root()
    fixture = root / "specs" / "harness" / "fixtures" / "handoffs" / "feedmind-curated-export.valid.json"
    cos_matic = docs / "cos-matic"
    wrench = docs / "wrench-inspect"

    cos_cmd = ["cargo", "run", "--quiet", "-p", "cos-matic-cli", "--bin", "cosmatic", "--"]
    wrench_cmd = ["cargo", "run", "--quiet", "--"]

    validate, validate_evidence = run_json(cos_cmd + ["handoff", "validate", str(fixture), "--json"], cos_matic)
    inspect, inspect_evidence = run_json(wrench_cmd + ["handoff", "inspect", str(fixture), "--json"], wrench)
    plan, plan_evidence = run_json(cos_cmd + ["handoff", "plan", str(fixture), "--dry-run", "--json"], cos_matic)

    proof = {
        "flow": "feedmind_handoff_planning",
        "fixture": str(fixture.relative_to(root)),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "steps": {
            "validate": {"success": not any(f.get("severity") == "error" for f in validate.get("findings", [])), "report": validate, "evidence": validate_evidence},
            "inspect": {"success": inspect.get("valid") is True, "no_critical_finding": inspect.get("summary", {}).get("errors") == 0, "report": inspect, "evidence": inspect_evidence},
            "plan": {"success": not any(f.get("severity") == "error" for f in plan.get("report", {}).get("findings", [])), "dry_run_only": True, "report": plan, "evidence": plan_evidence},
            "human_approval_placeholder": {"required": True, "status": "not_requested", "note": "Planning proof stops before execution approval."},
        },
        "execution": {"implementation_executed": False, "rumble_executed": False},
    }
    proof["success"] = proof["steps"]["validate"]["success"] and proof["steps"]["inspect"]["no_critical_finding"] and proof["steps"]["plan"]["dry_run_only"]
    proof = sanitize_paths(proof, [(str(root), "$ECOSYSTEM"), (str(docs), "$DOCUMENTS")])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"success": proof["success"], "proof": str(args.output)}, indent=2))
    return 0 if proof["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
