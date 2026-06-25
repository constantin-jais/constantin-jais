# Contract — Bolt Refusal Codes v0.1

Status: Draft / P0 harness contract.  
Owner: Bolt / `cos-matic`.  
Scope: validation, planning-only gates, idempotency, evidence references, and sovereignty checks.

## Purpose

Bolt refusals must be deterministic, machine-readable, and stable enough for Rumble UX, Wrench reports, Gear provenance, and audit exports to consume without inventing local error vocabularies.

A refusal is not an exception fallback. It is a first-class orchestration outcome.

## Response Shape

Minimum JSON shape:

```json
{
  "status": "refused",
  "reason_code": "execution_policy_forbidden",
  "severity": "critical",
  "findings": [
    {
      "code": "allow_execution_true",
      "severity": "critical",
      "message": "P0 handoffs must be planning-only and may not authorize execution.",
      "path": "$.execution_policy.allow_execution"
    }
  ],
  "remediation": [
    "Set execution_policy.allow_execution=false.",
    "Request a separate human-approved execution gate after planning."
  ]
}
```

Rules:

- `reason_code` is one of the canonical codes below.
- `findings[].message` must be safe to display; no raw secrets, tokens, credentials, raw logs, or PII bodies.
- `path` uses JSONPath-like notation when the finding maps to a payload field.
- Refusals must be auditable with actor, timestamp, handoff id, payload hash, and package hash when available.
- Bolt must not silently rewrite unsafe input into safe input.

## Canonical Codes

| Code | Severity | Trigger | Expected owner to remediate |
| --- | --- | --- | --- |
| `unknown_format` | error | `format` is not supported | Rumble producer |
| `invalid_kind` | error | `kind` is not `planning_request` | Rumble producer |
| `invalid_schema` | error | payload fails JSON Schema | Rumble producer |
| `missing_package_hash` | error | `package.package_hash` is missing or malformed | Rumble producer / Gear package export |
| `empty_package_items` | error | `package.items` is empty | Rumble producer |
| `execution_policy_forbidden` | critical | execution is allowed or human approval is not required in P0 | Rumble producer / requester |
| `blocking_question_without_waiver` | error | blocking open question lacks accepted waiver | Rumble owner/reviewer |
| `high_risk_without_waiver` | critical | high/critical risk lacks accepted waiver | Rumble owner/reviewer |
| `expired_waiver` | error | waiver is expired at validation time | Rumble reviewer |
| `invalid_waiver_separation` | critical | high/critical waiver is self-approved or lacks reviewer separation | Rumble owner/reviewer |
| `missing_waiver_rationale` | error | waiver lacks rationale | Rumble reviewer |
| `traceability_below_threshold` | error | traceability coverage is below policy threshold | Rumble producer / Wrench inspector |
| `capability_owner_missing` | warning | capability candidate affecting scope has no proposed owner layer | Rumble producer / architecture reviewer |
| `handoff_hash_conflict` | error | same `handoff_id` submitted with different payload hash | Bolt/Rumble integration |
| `missing_required_wrench_report` | error | policy requires a Wrench report ref that is absent | Rumble producer / Wrench pipeline |
| `wrench_report_failed` | error | required Wrench report has failed/high/critical findings | Rumble producer / Wrench remediation |
| `artifact_integrity_failed` | error | artifact ref/hash/manifest is missing, malformed, or mismatched | Gear producer / Rumble export |
| `sovereignty_policy_violation` | critical | handoff/plan requires forbidden SaaS, opaque storage, blocking license, PII logs, or unauthorized provider transmission | Architecture/security reviewer |
| `prompt_injection_risk` | error | payload attempts to treat artifact/evidence/spec text as instructions | Rumble producer / Bolt policy |
| `pii_or_secret_leak_risk` | critical | payload/report/audit output would expose PII, secrets, tokens, credentials, or raw logs | Producer/security reviewer |
| `planning_failed` | error | dry-run planning failed after validation | Bolt implementation |
| `internal_error` | error | unexpected Bolt failure; must fail closed | Bolt implementation |

## Warning vs Refusal

Warnings do not block planning by default, but must be visible in the plan and audit trail.

Current warning-class canonical code:

- `capability_owner_missing`.

A deployment policy may upgrade any warning to a blocking refusal.

## Gate-Required Codes

Some findings may produce `gate_required` instead of immediate `refused` during dry-run planning:

| Code | Gate type |
| --- | --- |
| `missing_required_wrench_report` | `wrench_report_passed` |
| `artifact_integrity_failed` | `artifact_integrity` |
| `sovereignty_policy_violation` | `sovereignty_policy` |
| `high_risk_without_waiver` | `risk_waiver` |
| `blocking_question_without_waiver` | `risk_waiver` |
| `execution_policy_forbidden` | never gate-required in P0; always refused |

## Compatibility

- Codes are append-only within `v0.1` unless a code is proven unsafe.
- Renaming a code requires a new contract version.
- Rumble UIs should display unknown codes safely as generic refusal with raw code visible.

## Acceptance Tests

- An execution-capable handoff returns `execution_policy_forbidden`.
- A missing/malformed package hash returns `missing_package_hash`.
- An empty package returns `empty_package_items`.
- A blocking open question without waiver returns `blocking_question_without_waiver`.
- A high/critical risk without waiver returns `high_risk_without_waiver`.
- An expired waiver returns `expired_waiver`.
- A same `handoff_id` with different hash returns `handoff_hash_conflict`.
- A missing required Wrench report blocks planning with `missing_required_wrench_report`.
- A sovereignty violation returns or gates on `sovereignty_policy_violation`.
- No refusal output contains raw PII, secrets, tokens, credentials, or raw logs.
