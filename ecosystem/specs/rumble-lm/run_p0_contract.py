#!/usr/bin/env python3
"""Run the Rumble LM P0 contract proof.

The proof is fixture-only: it validates the contract boundary without calling UI,
LLM providers, Wrench, Gear, Bolt, or Biscuit runtimes.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


def lm_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


def run_validator(fixture: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    command = [sys.executable, str(lm_root() / "validate_p0_contract.py"), str(fixture), "--json"]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        report = {
            "valid": False,
            "findings": [
                {
                    "severity": "error",
                    "code": "validator_output_invalid",
                    "message": "Validator did not emit JSON.",
                    "target": str(fixture),
                }
            ],
        }
    evidence = {
        "command": command,
        "exitCode": completed.returncode,
        "stderrEmpty": completed.stderr == "",
    }
    return report, evidence


def sanitize_paths(value: Any, root: pathlib.Path) -> Any:
    if isinstance(value, str):
        return value.replace(str(root), "$RUMBLE_LM_SPEC")
    if isinstance(value, list):
        return [sanitize_paths(item, root) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_paths(item, root) for key, item in value.items()}
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=lm_root() / "proofs" / "p0-contract.proof.json",
    )
    args = parser.parse_args()

    root = lm_root()
    valid_fixture = root / "fixtures" / "p0-source-grounded-session.valid.json"
    invalid_fixture = root / "fixtures" / "p0-source-grounded-session.invalid.json"

    valid_report, valid_evidence = run_validator(valid_fixture)
    invalid_report, invalid_evidence = run_validator(invalid_fixture)

    invalid_codes = {item.get("code") for item in invalid_report.get("findings", [])}
    expected_invalid_codes = {
        "source_set_required",
        "generation_source_not_required",
        "citation_support_weak",
        "hidden_profiling_forbidden",
        "participant_export_private_data",
        "export_checksum_required",
        "delegation_workspace_mismatch",
        "secret_or_pii_in_logs",
        "sovereignty_filter_failed",
    }

    proof = {
        "schema": "rumble_lm.p0_contract_proof.v0.1",
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "scope": "fixture-only contract proof; no product runtime or external provider called",
        "validFixture": {
            "path": str(valid_fixture),
            "passed": valid_report.get("valid") is True and valid_evidence["exitCode"] == 0,
            "report": valid_report,
            "evidence": valid_evidence,
        },
        "invalidFixture": {
            "path": str(invalid_fixture),
            "failedAsExpected": invalid_report.get("valid") is False and invalid_evidence["exitCode"] != 0,
            "expectedCodesPresent": sorted(expected_invalid_codes & invalid_codes),
            "missingExpectedCodes": sorted(expected_invalid_codes - invalid_codes),
            "report": invalid_report,
            "evidence": invalid_evidence,
        },
        "boundariesProved": [
            "Rumble LM stores source-set refs/snapshots, not source truth.",
            "Wrench/Gear source provenance is required before grounding.",
            "Bolt generation remains draft-only and cannot publish.",
            "Validated citations are required for source-derived generated claims.",
            "Participant-facing exports exclude private responses by default.",
            "Biscuit-style delegations are scoped, expiring, revocable, and least-privilege.",
            "Default analytics are aggregate-only with no hidden learner profile.",
            "Sovereignty filters block mandatory US SaaS, opaque storage, blocking licenses, silent provider fallback, and PII logs."
        ],
        "execution": {
            "uiExecuted": False,
            "wrenchCalled": False,
            "gearCalled": False,
            "boltCalled": False,
            "biscuitRuntimeCalled": False,
            "llmProviderCalled": False,
        },
    }
    proof["success"] = (
        proof["validFixture"]["passed"]
        and proof["invalidFixture"]["failedAsExpected"]
        and not proof["invalidFixture"]["missingExpectedCodes"]
    )
    proof = sanitize_paths(proof, root)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"success": proof["success"], "proof": str(args.output)}, indent=2))
    return 0 if proof["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
