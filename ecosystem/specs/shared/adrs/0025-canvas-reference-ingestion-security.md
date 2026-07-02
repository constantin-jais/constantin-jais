# ADR 0025 — Canvas Reference Ingestion: Blocking Scan Optional, Detection Mode Mandatory

Status: Proposed
Date: 2026-07-02
Decision owner: Rumble Canvas product
Related decision: D3 (decision-log), Canvas vision in overview.md

## Context

Canvas is a collaborative spec-production tool that ingests design references: other repos, design-system docs, screenshots, component examples. This ingestion must balance security and usability.

Two operational modes emerge:

1. **Advisory (detect mode)**: Security scans run, findings are annotated and travel with content, but do not block ingestion. User can review and decide. Annotations include confidence, remediation type, and provenance.

2. **Enforcement (blocking)**: Scans can refuse ingestion based on severity thresholds. Enforcement mode is only safe when the workspace holds write delegations to sensitive repos or is connected to protected data sources.

Users should control strictness, but they should not control whether scans exist. Scanning must always happen; visibility and enforcement are the user option.

## Decision

Adopt a two-tiered Canvas ingestion security model:

1. **Detection mode (always active)**: All ingestion goes through `gear-loader` hostile-content evidence generation (PII, prompt injection, active content, secrets scanning). Findings are:
   - Annotated with finding type, confidence, CWE/OWASP mapping, remediation suggestion, scanner version, and timestamp.
   - Travel with content throughout Canvas (not stripped on export).
   - Visible in Canvas UI by default (inline annotations or side panels).
   - Provide audit trail without blocking work.

2. **Enforcement mode (user-controlled)**: Can be activated per workspace when:
   - Workspace admin explicitly enables it in settings.
   - Integration with sensitive repos (requires Biscuit delegation with `sensitivity=high` or `sensitivity=internal`).
   - Previous security findings exist for the repo or source.

   When enforcement is active:
   - High/critical findings auto-escalate: prompt user to remediate or reject.
   - Medium findings are warnings with override capability (with audit reason).
   - Low findings are annotations only.

3. **Default posture**: New workspaces default to detection mode; enforcement is opt-in after intent review.

## Architecture objectives satisfied

| Objective                | ADR consequence                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Security by default      | Scans always run; users cannot disable visibility but can choose strictness.                                       |
| Bias toward productivity | Detection mode lets users iterate on content; enforcement is gated to sensitive contexts.                          |
| Audit trail              | Findings travel with content, making security decisions and rationale traceable.                                   |
| Gear integration         | `gear-loader` owns hostile-content evidence; Canvas consumes and presents results without reimplementing scanners. |

## Consequences

### Positive

- Canvas users see security signals without workflow disruption (detection mode).
- Sensitive workspaces (e.g., connected to internal repos) can enforce without blocking teams working on public references.
- Audit trail of findings and remediation decisions is permanent.
- Compliance teams can export Canvas artifacts with full evidence chain.

### Negative / Costs

- Two scanning modes require UI complexity: toggles, thresholds, escalation rules.
- Scanning adds ingestion latency; caching/async ingestion may be needed.
- False positives in detection mode can create annotation noise; tuning and classifier feedback loops are important.
- Gear integration requires `gear-loader` to be available and versioned consistently.

## Alternatives considered

### Blocking scan always; no override

Rejected. Would block legitimate ingestion of public references and slow iteration on speculative content.

### No scanning; rely on manual review

Rejected. Scalability and audit trail suffer; prompt injection and PII risks are unmanaged.

### Separate scanning service

Rejected. `gear-loader` already provides scanning; new service would duplicate.

## Required follow-up

- Implement `gear-loader` hostile-content evidence output format with finding structure (type, confidence, CWE, remediation).
- Add Canvas UI for detection-mode annotations and enforcement-mode toggles/thresholds.
- Define Biscuit caveats for workspace sensitivity flags that trigger enforcement eligibility.
- Write Canvas/Gear contract for ingestion request → evidence consumption flow.
- Implement async ingestion with progress UI if scan latency is >2s.
- Add Canvas export format to preserve findings metadata.

## Acceptance criteria

- An ingestion of a public GitHub README succeeds in detection mode with no blocking findings.
- An ingestion of the same README in a workspace connected to an internal repo prompts for enforcement-mode review.
- A PII-containing reference is ingested in detection mode with an annotation; enforcement mode blocks it with override option.
- Findings are visible in Canvas UI and included in artifact export.
- Workspace admin can toggle detection/enforcement in settings; toggle is audited.
