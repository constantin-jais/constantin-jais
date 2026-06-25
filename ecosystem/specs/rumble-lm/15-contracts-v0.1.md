# Contracts v0.1 — rumble-lm

Status: Draft contracts before code.  
Related slice: [`14-source-grounded-product-slice.md`](./14-source-grounded-product-slice.md).  
Related ADR: [`../shared/adrs/0002-rumble-lm-source-grounded-session-p0.md`](../shared/adrs/0002-rumble-lm-source-grounded-session-p0.md).

## Purpose

This file defines the first contract shapes that must exist before implementing `rumble-lm` P0.

They are product-facing contracts, not final shared platform APIs. Once stabilized and reused by other products, they may move to `specs/shared/contracts/` or lower-layer repositories.

Fixture proof:

```bash
python3 ecosystem/specs/rumble-lm/run_p0_contract.py
```

Fixtures:

- `fixtures/p0-source-grounded-session.valid.json`
- `fixtures/p0-source-grounded-session.invalid.json`

---

## Contract: SourceGroundedGenerationRequest v0.1

### Owner boundary

- Rumble LM owns request intent, session context, activity/summary semantics, and publication gate.
- Bolt owns orchestration, model/tool routing under deployment policy, and refusal/gate evidence.
- Wrench/Gear provide source refs, chunks, provenance, and citation validation evidence.

### Request shape

```json
{
  "schema": "rumble_lm.source_grounded_generation_request.v0.1",
  "requestId": "uuid-or-client-id",
  "workspaceId": "workspace-id",
  "sessionId": "session-id",
  "actor": {
    "actorId": "actor-id",
    "role": "Facilitator"
  },
  "purpose": "activity_generation | summary_generation",
  "objective": "session objective",
  "audience": "facilitator | participants | admin_audit | machine_readable",
  "sourceSet": {
    "sourceSetId": "source-set-id",
    "revision": 1,
    "sourceRefs": ["gear-source-ref"],
    "required": true
  },
  "constraints": {
    "activityTypes": ["Quiz", "Reflection"],
    "maxDrafts": 5,
    "language": "fr",
    "citationRequired": true,
    "unsupportedClaimsAllowed": true,
    "privacyPolicyRef": "policy-ref",
    "providerPolicyRef": "provider-policy-ref"
  },
  "outputSchema": {
    "kind": "activity_drafts | summary_draft",
    "version": "v0.1"
  },
  "delegationRef": "biscuit-delegation-id",
  "idempotencyKey": "client-key"
}
```

### Response shape

```json
{
  "schema": "rumble_lm.source_grounded_generation_response.v0.1",
  "requestId": "uuid-or-client-id",
  "status": "drafts_created | refused | partial",
  "draftRefs": ["activity-id-or-summary-id"],
  "citationCandidateRefs": ["citation-id"],
  "warnings": [
    {
      "code": "weak_grounding",
      "target": { "type": "activity", "id": "..." },
      "message": "Citation support needs facilitator review."
    }
  ],
  "refusal": {
    "code": "source_set_required",
    "message": "A ready source set is required for source-grounded generation.",
    "recovery": "Import or select sources, then retry."
  },
  "generationMetadata": {
    "orchestrator": "bolt",
    "runRef": "bolt-run-or-plan-ref",
    "modelPolicyRef": "provider-policy-ref",
    "createdAt": "2026-06-30T00:00:00Z"
  }
}
```

### Invariants

- A source-grounded request with no ready source set is refused.
- `citationRequired=true` means generated source-derived claims must produce citation candidates or unsupported markers.
- Response metadata must not include secrets, raw provider keys, raw Biscuit tokens, or raw participant responses.
- Generated outputs are drafts only; no publication right is implied.

---

## Contract: CitationSupportValidationResult v0.1

### Owner boundary

- Rumble owns citation candidate lifecycle and facilitator validation.
- Wrench owns advisory support evidence.

### Request fields

```json
{
  "schema": "rumble_lm.citation_support_validation_request.v0.1",
  "workspaceId": "workspace-id",
  "sessionId": "session-id",
  "citationId": "citation-id",
  "claim": "generated or facilitator-visible claim",
  "quote": "quoted source excerpt",
  "sourceRef": "gear-source-ref",
  "sourceChunkRef": "gear-source-chunk-ref",
  "sourceRevision": "revision-or-hash",
  "surroundingContextRef": "optional-context-ref",
  "delegationRef": "biscuit-delegation-id"
}
```

### Result fields

```json
{
  "schema": "rumble_lm.citation_support_validation_result.v0.1",
  "citationId": "citation-id",
  "supportLevel": "Strong | Partial | Weak | Contradicted | NotReviewed",
  "explanation": "Short human-readable rationale.",
  "warnings": [
    {
      "code": "quote_too_narrow",
      "message": "The quoted excerpt omits relevant surrounding context."
    }
  ],
  "validatorMetadata": {
    "validator": "wrench-citation-support-validator",
    "version": "v0.1",
    "createdAt": "2026-06-30T00:00:00Z"
  }
}
```

### Invariants

- `Weak`, `Contradicted`, `Rejected`, `Stale`, and `NotReviewed` cannot satisfy mandatory grounding gates.
- Wrench results are advisory evidence; only facilitator validation changes citation status to `Validated`.
- Results must not log or emit raw source text beyond the specific quote already approved for citation review.

---

## Contract: SessionExportArtifactManifest v0.1

### Owner boundary

- Rumble owns export audience, included data classes, filtering, and product semantics.
- Gear artifact/depot capability owns artifact ref, checksum, integrity/provenance metadata, and revocation/retention references.

### Manifest shape

```json
{
  "schema": "rumble_lm.session_export_artifact_manifest.v0.1",
  "exportId": "export-id",
  "workspaceId": "workspace-id",
  "sessionId": "session-id",
  "format": "Markdown | HTML | PDF | JSON | Bundle",
  "audience": "FacilitatorOnly | Participants | AdminAudit | MachineReadable",
  "includedDataClasses": [
    "session_metadata",
    "activities",
    "aggregate_results",
    "validated_summary",
    "citations",
    "source_provenance"
  ],
  "excludedDataClasses": [
    "private_responses",
    "facilitator_only_notes"
  ],
  "sourceRefs": ["gear-source-ref"],
  "citationRefs": ["citation-id"],
  "summaryRefs": ["summary-id"],
  "artifactRef": "gear-artifact-ref",
  "checksum": {
    "algorithm": "sha256",
    "value": "hex"
  },
  "policySnapshot": {
    "exportPolicyRef": "policy-ref",
    "retentionPolicyRef": "retention-ref",
    "visibilityModesApplied": ["AnonymousToParticipants", "AggregateOnly"]
  },
  "validation": {
    "validatedBy": "actor-id",
    "validatedAt": "2026-06-30T00:00:00Z",
    "privacyGate": "passed",
    "citationGate": "passed"
  },
  "revocation": {
    "revocationRef": "revocation-ref",
    "revokedAt": null
  }
}
```

### Invariants

- Manifest audience and included data classes are mandatory.
- Participant-facing exports exclude facilitator-only notes and private responses unless policy explicitly allows and the audience supports it.
- Artifact checksum is mandatory for durable exports.
- Downloaded files cannot be recalled; revocation applies to managed references/access metadata.

---

## Contract: LM Biscuit Delegation Profile v0.1

### Shared base

LM uses the shared contract [`../shared/contracts/delegated-authorization-biscuit.v0.1.md`](../shared/contracts/delegated-authorization-biscuit.v0.1.md).

### Required facts/caveats for LM operations

| Operation | Required action | Required caveats/facts |
| --- | --- | --- |
| Import source | `source:attach` | `organization`, `workspace`, `resource("session", session_id)`, `purpose("source_import")`, expiry, revocation ref |
| Read source chunks for generation | `source:read` | `organization`, `workspace`, `source_set_revision`, `purpose("source_grounded_generation")`, provider policy ref |
| Request generation | `run:request` | `organization`, `workspace`, `resource("session", session_id)`, output schema, citation-required flag |
| Validate citation advisory | `source:read` or future `citation:validate` | `organization`, `workspace`, `citation_id`, source/chunk refs, advisory-only caveat |
| Create export | `export:create` | `organization`, `workspace`, `resource("session", session_id)`, audience, allowed data classes, checksum-required caveat |
| Read export | `export:read` | `organization`, `workspace`, `artifact_ref`, audience, retention/revocation refs |
| Submit participant response | product-scoped participant token or future delegated action | session, activity run, participant scope, expiry, visibility snapshot |

### Invariants

- Admin metadata access does not imply content access.
- Tokens with mismatched workspace/session/source/artifact facts are rejected before product policy evaluation.
- Tokens cannot grant publication, facilitator validation, or visibility override unless a future explicit action and ADR define it.
- Raw Biscuit tokens and bearer headers are never logged.

---

## Contract Acceptance Tests

- A generation request without `sourceSet.required=true` and ready source refs is refused for source-grounded mode.
- A Bolt response with drafts does not change activity status beyond `Draft`.
- A citation validation result marked `Weak` cannot be converted to `Validated` without replacement, edit, or unsupported marker.
- A participant export manifest containing `private_responses` fails privacy gate by default.
- An export manifest without checksum fails artifact readiness.
- A generation delegation token cannot create exports.
- An export delegation token cannot read source chunks beyond included citation/source refs.
- Logs for all contract calls include refs/status/reason codes only, not raw response content, secrets, bearer headers, or raw tokens.
