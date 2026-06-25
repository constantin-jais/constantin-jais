#!/usr/bin/env python3
"""Validate Rumble LM P0 source-grounded contract fixtures.

This validator is intentionally dependency-free and runtime-free. It validates
agent-readable fixture contracts before any product UI or integration code exists.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from typing import Any

RFC3339_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA256_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SECRET_KEYS = ("secret", "token", "bearer", "password", "credential", "api_key", "rawresponse")
PRIVATE_EXPORT_CLASSES = {"private_responses", "facilitator_only_notes"}
UNSUPPORTED_SUPPORT_LEVELS = {"Weak", "Contradicted", "NotReviewed"}
UNSATISFYING_CITATION_STATUSES = {"Rejected", "Stale", "Candidate"}


def finding(code: str, message: str, target: str, severity: str = "error") -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message, "target": target}


def get_path(value: dict[str, Any], dotted: str, default: Any = None) -> Any:
    current: Any = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def has_secret_like_metadata(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).replace("_", "").lower()
            if any(marker in normalized for marker in SECRET_KEYS):
                return True
            if has_secret_like_metadata(item):
                return True
    elif isinstance(value, list):
        return any(has_secret_like_metadata(item) for item in value)
    return False


def validate_fixture(doc: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    if doc.get("schema") != "rumble_lm.p0_source_grounded_session_fixture.v0.1":
        findings.append(finding("schema_invalid", "Fixture schema is missing or unsupported.", "schema"))

    workspace_id = doc.get("workspaceId")
    session_id = get_path(doc, "session.sessionId")
    source_set = doc.get("sourceSet", {})
    source_refs = source_set.get("sourceRefs") or []
    source_ref_ids = {item.get("sourceRef") for item in source_refs if isinstance(item, dict)}
    chunk_ref_ids = {
        chunk
        for item in source_refs
        if isinstance(item, dict)
        for chunk in item.get("sourceChunkRefs", [])
    }

    if not workspace_id:
        findings.append(finding("workspace_required", "Workspace is required.", "workspaceId"))
    if not session_id:
        findings.append(finding("session_required", "Session is required.", "session.sessionId"))

    if get_path(doc, "sourceSet.owner") != "rumble-lm-selection-only":
        findings.append(
            finding(
                "source_truth_owned_by_rumble",
                "Rumble LM must store source-set selection only, not durable source truth or memory.",
                "sourceSet.owner",
            )
        )
    if source_set.get("status") not in {"Ready", "Locked"}:
        findings.append(finding("source_set_not_ready", "Source-grounded P0 requires a ready or locked source set.", "sourceSet.status"))
    if not source_refs:
        findings.append(finding("source_set_required", "Source-grounded generation requires at least one source ref.", "sourceSet.sourceRefs"))

    for index, source in enumerate(source_refs):
        provenance = source.get("provenance", {}) if isinstance(source, dict) else {}
        if provenance.get("owner") != "gear-memory":
            findings.append(finding("source_provenance_not_gear", "Source provenance must be Gear-owned.", f"sourceSet.sourceRefs[{index}].provenance.owner"))
        if provenance.get("producedBy") != "wrench-loader":
            findings.append(finding("source_not_extracted_by_wrench", "Canonical extraction must come from Wrench Loader.", f"sourceSet.sourceRefs[{index}].provenance.producedBy"))
        source_hash = provenance.get("hash", "")
        if not (isinstance(source_hash, str) and source_hash.startswith("sha256:") and SHA256_HEX_RE.match(source_hash.removeprefix("sha256:"))):
            findings.append(finding("source_hash_invalid", "Source provenance requires sha256 hash.", f"sourceSet.sourceRefs[{index}].provenance.hash"))
        extracted_at = provenance.get("extractedAt")
        if not (isinstance(extracted_at, str) and RFC3339_Z_RE.match(extracted_at)):
            findings.append(finding("source_extracted_at_invalid", "Source extraction timestamp must be RFC3339 Z.", f"sourceSet.sourceRefs[{index}].provenance.extractedAt"))

    generation = doc.get("generationRequest", {})
    if get_path(generation, "sourceSet.required") is not True:
        findings.append(finding("generation_source_not_required", "Source-grounded generation must require a source set.", "generationRequest.sourceSet.required"))
    if get_path(generation, "constraints.citationRequired") is not True:
        findings.append(finding("generation_citation_not_required", "Source-grounded generation must require citations.", "generationRequest.constraints.citationRequired"))
    if not get_path(generation, "constraints.providerPolicyRef"):
        findings.append(finding("provider_policy_required", "Generation requires an explicit provider policy ref.", "generationRequest.constraints.providerPolicyRef"))

    citations_by_id = {citation.get("citationId"): citation for citation in doc.get("citations", []) if isinstance(citation, dict)}

    for activity in doc.get("activities", []):
        activity_id = activity.get("activityId")
        if activity.get("generated") and activity.get("status") not in {"Draft", "Validated", "Published", "Closed"}:
            findings.append(finding("activity_status_invalid", "Generated activity has unsupported lifecycle status.", f"activities.{activity_id}.status"))
        for claim in activity.get("claims", []):
            if activity.get("groundingMode") == "SourceGrounded" and claim.get("claimClass") == "SourceDerived":
                refs = claim.get("citationRefs") or []
                if not refs:
                    findings.append(finding("citation_required", "Source-derived generated claim requires citation refs.", f"claims.{claim.get('claimId')}"))
                for ref in refs:
                    citation = citations_by_id.get(ref)
                    if not citation:
                        findings.append(finding("citation_missing", "Claim references missing citation.", f"claims.{claim.get('claimId')}.citationRefs"))
                        continue
                    if citation.get("status") in UNSATISFYING_CITATION_STATUSES:
                        findings.append(finding("citation_status_unsatisfied", "Rejected/stale/candidate citation cannot satisfy grounding.", f"citations.{ref}.status"))
                    if citation.get("supportLevel") in UNSUPPORTED_SUPPORT_LEVELS:
                        findings.append(finding("citation_support_weak", "Weak/contradicted/not-reviewed citation cannot satisfy grounding.", f"citations.{ref}.supportLevel"))
                    if citation.get("sourceRef") not in source_ref_ids:
                        findings.append(finding("citation_source_missing", "Citation source ref is not in the session source set.", f"citations.{ref}.sourceRef"))
                    if citation.get("sourceChunkRef") not in chunk_ref_ids:
                        findings.append(finding("citation_chunk_missing", "Citation chunk ref is not in the session source set.", f"citations.{ref}.sourceChunkRef"))

    responses = doc.get("responses", {})
    if responses.get("crossSessionLearnerProfileCreated") is True:
        findings.append(finding("hidden_profiling_forbidden", "P0 forbids hidden cross-session learner profiles.", "responses.crossSessionLearnerProfileCreated"))
    if responses.get("rawResponsesIncludedInFixture") is True:
        findings.append(finding("raw_responses_forbidden", "Contract fixture/proofs must not include raw participant responses.", "responses.rawResponsesIncludedInFixture"))
    if get_path(doc, "session.analyticsMode") != "aggregate_only":
        findings.append(finding("analytics_must_be_aggregate", "Default P0 analytics must be aggregate-only.", "session.analyticsMode"))

    summary = doc.get("summary", {})
    if summary.get("audience") == "Participants" and summary.get("privacyGate") != "passed":
        findings.append(finding("summary_privacy_gate_required", "Participant-facing summary must pass privacy gate.", "summary.privacyGate"))
    for claim in summary.get("claims", []):
        if claim.get("claimClass") == "SourceDerived":
            for ref in claim.get("citationRefs", []):
                citation = citations_by_id.get(ref)
                if not citation or citation.get("status") != "Validated" or citation.get("supportLevel") in UNSUPPORTED_SUPPORT_LEVELS:
                    findings.append(finding("summary_citation_unsatisfied", "Summary source-derived claim requires validated supporting citation.", f"summary.claims.{claim.get('claimId')}"))

    export = doc.get("exportManifest", {})
    included = set(export.get("includedDataClasses") or [])
    if export.get("audience") == "Participants" and included & PRIVATE_EXPORT_CLASSES:
        findings.append(finding("participant_export_private_data", "Participant export must not include private/facilitator-only data by default.", "exportManifest.includedDataClasses"))
    checksum = export.get("checksum") or {}
    if not (isinstance(checksum, dict) and checksum.get("algorithm") == "sha256" and SHA256_HEX_RE.match(str(checksum.get("value", "")))):
        findings.append(finding("export_checksum_required", "Export manifest requires sha256 checksum.", "exportManifest.checksum"))
    if not export.get("artifactRef"):
        findings.append(finding("export_artifact_ref_required", "Export manifest requires Gear artifact ref.", "exportManifest.artifactRef"))
    if get_path(export, "validation.privacyGate") != "passed" or get_path(export, "validation.citationGate") != "passed":
        findings.append(finding("export_gates_required", "Export requires passed privacy and citation gates.", "exportManifest.validation"))
    if not get_path(export, "revocation.revocationRef"):
        findings.append(finding("export_revocation_ref_required", "Managed export requires revocation ref.", "exportManifest.revocation.revocationRef"))

    delegations = doc.get("delegations", [])
    if not delegations:
        findings.append(finding("delegation_required", "P0 fixture requires delegated rights evidence.", "delegations"))
    required_delegation_actions = {"source:attach", "run:request", "export:create"}
    observed_actions = {item.get("action") for item in delegations if isinstance(item, dict)}
    missing_actions = required_delegation_actions - observed_actions
    for action in sorted(missing_actions):
        findings.append(finding("delegation_action_missing", f"Missing delegated action {action}.", "delegations"))
    for index, delegation in enumerate(delegations):
        facts = delegation.get("facts", {}) if isinstance(delegation, dict) else {}
        if facts.get("workspace") != workspace_id:
            findings.append(finding("delegation_workspace_mismatch", "Delegation workspace must match fixture workspace.", f"delegations[{index}].facts.workspace"))
        if facts.get("session") and facts.get("session") != session_id:
            findings.append(finding("delegation_session_mismatch", "Delegation session must match fixture session.", f"delegations[{index}].facts.session"))
        if not delegation.get("expiresAt"):
            findings.append(finding("delegation_expiry_required", "Delegated rights must be time-bounded.", f"delegations[{index}].expiresAt"))
        if not delegation.get("revocationRef"):
            findings.append(finding("delegation_revocation_required", "Delegated rights must have revocation ref.", f"delegations[{index}].revocationRef"))
        if delegation.get("action") == "run:request" and "activity:publish" not in set(delegation.get("forbiddenCapabilities", [])):
            findings.append(finding("bolt_publish_forbidden_missing", "Bolt generation delegation must explicitly forbid publishing.", f"delegations[{index}].forbiddenCapabilities"))
        if delegation.get("action") == "export:create" and "private_response:read" not in set(delegation.get("forbiddenCapabilities", [])):
            findings.append(finding("export_private_read_forbidden_missing", "Export delegation must forbid private response reads by default.", f"delegations[{index}].forbiddenCapabilities"))

    if has_secret_like_metadata(doc.get("auditLogSample", [])):
        findings.append(finding("secret_or_pii_in_logs", "Audit/log samples must not contain raw responses, tokens, bearer headers, or secrets.", "auditLogSample"))

    sovereignty = doc.get("sovereignty", {})
    for key in ["mandatoryUsSaas", "opaqueStorage", "blockingLicenseDependency", "silentThirdPartyModelFallback", "piiInLogs"]:
        if sovereignty.get(key) is not False:
            findings.append(finding("sovereignty_filter_failed", f"Sovereignty filter must be false: {key}.", f"sovereignty.{key}"))

    return findings


def validate_path(path: pathlib.Path) -> dict[str, Any]:
    doc = json.loads(path.read_text())
    findings = validate_fixture(doc)
    return {
        "schema": "rumble_lm.p0_contract_validation_report.v0.1",
        "fixture": str(path),
        "valid": not any(item["severity"] == "error" for item in findings),
        "findings": findings,
        "summary": {
            "errors": sum(1 for item in findings if item["severity"] == "error"),
            "warnings": sum(1 for item in findings if item["severity"] == "warning"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=pathlib.Path)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args()

    report = validate_path(args.fixture)
    report["validatedAt"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "valid" if report["valid"] else "invalid"
        print(f"{args.fixture}: {status} ({report['summary']['errors']} errors)")
        for item in report["findings"]:
            print(f"- {item['severity']} {item['code']} {item['target']}: {item['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
