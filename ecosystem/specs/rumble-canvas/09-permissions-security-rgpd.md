# Permissions, Security, RGPD — rumble-canvas

Status: Draft.

## Security Principles

- Rumble Canvas never executes implementation work.
- Handoff is planning-only until Bolt gates and human approval allow otherwise.
- Agent output is suggestion, not accepted truth.
- Every approval, waiver, package, and handoff is attributable.
- Secrets and unnecessary PII must not enter logs, exports, or handoff payloads.

## Role Matrix

| Action | Owner | Editor | Reviewer | Viewer | Agent | System |
| --- | --- | --- | --- | --- | --- | --- |
| Manage workspace | Yes | No | No | No | No | No |
| Edit draft section | Yes | Yes | No | No | Suggest | No |
| Review section | Yes | No | Yes | No | Suggest | No |
| Approve package | Yes | No | No | No | No | No |
| Approve high/critical waiver | Owner approval required | No | Reviewer approval required | No | No | No |
| Prepare handoff | Yes | Delegated | No | No | No | No |
| Submit handoff | Yes | Delegated | No | No | No | No |
| Execute implementation | No | No | No | No | No | No |

## Waiver Policy

- Low/medium waiver: Owner approval required.
- High/critical waiver: distinct human Owner + Reviewer approval required.
- Agents and runtime services cannot approve waivers.
- Expired waivers are invalid.
- Waivers require rationale and target.

## PII Classification

| Data | Classification | Notes |
| --- | --- | --- |
| Workspace metadata | Low/medium | Names may contain personal/client data. |
| Spec content | Medium/high | User-authored; may include sensitive business/PII. |
| Comments | Medium/high | May include personal data. |
| Actor display names | PII | Minimize in exports. |
| Handoff payload | Medium/high | Must be reviewed before external transmission. |
| Logs | No PII target | Store IDs/hashes, not full content. |

## RGPD Rights

MVP must support:

- export workspace/package data;
- archive workspace;
- delete draft content when no approved package depends on it;
- anonymize actor display names where legally required;
- retain audit records where legitimate interest/security requires it.

## Handoff Data Minimization

Handoff payload should include:

- package identifiers;
- structured summaries required for planning;
- traceability links;
- risks/waivers/open questions;
- capability candidates;
- constraints.

Handoff payload should not include:

- secrets;
- provider API keys;
- full private comments unless required;
- unrelated workspace data;
- raw source documents unless explicitly scoped.

## Threat Notes

| Threat | Mitigation |
| --- | --- |
| Rumble triggers execution directly | Execution policy forbidden; Bolt must reject execution-enabled handoffs. |
| Agent writes accepted truth | Agent suggestions require human acceptance. |
| Waiver abuse | High/critical waivers require separation of duties. |
| PII leakage in logs | Log IDs/hashes/findings, not full content. |
| Stale package mutation | Approved package references immutable revisions and package hash. |
