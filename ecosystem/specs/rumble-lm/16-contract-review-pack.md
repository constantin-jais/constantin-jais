# Contract Review Pack — rumble-lm P0

Status: Ready for owner review.  
Related contracts: [`15-contracts-v0.1.md`](./15-contracts-v0.1.md).  
Fixture proof: [`proofs/p0-contract.proof.json`](./proofs/p0-contract.proof.json).

## Purpose

This pack is the handoff for reviewing the Rumble LM P0 contracts before implementation.

Review outcome must be one of:

- `accepted` — contract can be implemented as-is for P0;
- `accepted_with_changes` — implementation may start after listed edits;
- `blocked` — implementation must not start for this boundary;
- `deferred_with_stub` — P0 may use a local stub that preserves the contract and migration path.

No reviewer should approve a contract by accepting product-local duplication of their layer's responsibility.

---

## Review Gates

### Gate 1 — Anti-duplication

Reviewer confirms that Rumble LM consumes the lower-layer capability and does not reimplement its durable responsibility.

### Gate 2 — Contract sufficiency

Reviewer confirms that required fields, invariants, refusal modes, and audit evidence are enough for P0.

### Gate 3 — Sovereignty/security

Reviewer confirms:

- no mandatory US SaaS;
- no opaque storage;
- no blocking-license dependency implied;
- no raw PII/secrets/tokens in logs;
- deployment policy controls any model/provider routing.

### Gate 4 — Stub safety

If the real capability is not ready, reviewer confirms whether a stub is acceptable and what it must not hide.

---

## Bolt Review — SourceGroundedGenerationRequest

### Scope to review

- `SourceGroundedGenerationRequest v0.1`
- `SourceGroundedGenerationResponse v0.1`
- Bolt-related delegation facts/caveats

### Rumble LM expectation

Rumble sends bounded product intent:

- session objective;
- audience;
- source set revision;
- output schema;
- activity/summary constraints;
- citation-required flag;
- privacy/provider policy refs.

Bolt returns:

- draft activity/summary refs;
- citation candidate refs;
- warnings/refusals;
- generation metadata.

Bolt must not publish, validate facilitator decisions, store source truth, or own Rumble session state.

### Questions for Bolt owner

1. Is `run:request` acceptable for P0 generation, or is a narrower `generation:request` action needed?
2. Are `purpose`, `outputSchema`, `citationRequired`, and `providerPolicyRef` sufficient gates?
3. Should Bolt return draft payloads directly or only refs created by Rumble after schema validation?
4. What refusal codes are mandatory for P0 beyond `source_set_required`?
5. What metadata is safe to expose without leaking provider secrets or prompts containing PII?

### Acceptance criteria

- Bolt can refuse without side effects.
- Bolt output cannot publish participant-visible content.
- Bolt can prove provider policy was enforced or refuse when unknown.
- Bolt metadata is audit-safe.

---

## Wrench Review — CitationSupportValidationResult

### Scope to review

- source import/provenance assumptions from Gear Loader;
- `CitationSupportValidationRequest v0.1`;
- `CitationSupportValidationResult v0.1`.

### Rumble LM expectation

Wrench provides extraction and advisory support evidence. Facilitator validation remains required for publication/export.

### Questions for Wrench owner

1. Is `supportLevel = Strong | Partial | Weak | Contradicted | NotReviewed` sufficient for P0?
2. Should `Partial` satisfy mandatory grounding or require facilitator waiver/explicit review?
3. What source context is needed: quote only, surrounding context ref, full chunk, or retrieval handle?
4. Which extraction warnings should block source-grounded generation?
5. Should citation support validation live in Gear Loader, Wrench Inspect, or a dedicated Wrench validator?

### Acceptance criteria

- Wrench result is advisory, not publication authority.
- Weak/contradicted/stale citations cannot satisfy grounding gates.
- Result shape provides enough explanation for facilitator review.
- No raw source body is emitted into logs/audit metadata.

---

## Gear Review — Source/Export Contracts

### Scope to review

- Gear Memory source refs/chunks/provenance assumptions;
- `SessionExportArtifactManifest v0.1`;
- artifact refs, checksum, retention/revocation fields.

### Rumble LM expectation

Gear owns durable references and verifiability. Rumble owns session/export semantics and audience filtering.

### Questions for Gear owner

1. Are `SourceRef`, `SourceChunkRef`, `sourceRevision`, and provenance snapshots sufficient for citation review/export?
2. Is the export manifest compatible with Gear Depot `ArtifactRef`/`ArtifactManifest` direction?
3. Should checksum be over final artifact bytes, manifest, or both?
4. How should revocation refs represent managed links vs downloaded files?
5. Is `source_provenance` safe for participant-facing exports by default?

### Acceptance criteria

- Rumble does not store source truth as durable memory.
- Export manifest has artifact ref, checksum, audience, included/excluded data classes, policy snapshot, and revocation ref.
- Artifact metadata contains no raw private responses or secrets.
- Deletion/anonymization and retention can be represented by refs/policies.

---

## Biscuit/Auth Review — LM Delegation Profile

### Scope to review

- LM Biscuit delegation profile in `15-contracts-v0.1.md`;
- delegated actions for source import, generation, validation, export, participant submission.

### Rumble LM expectation

All service-to-service delegated rights use the shared Biscuit contract. Participant guest join tokens may remain session-scoped until a future explicit decision.

### Questions for Biscuit/Auth owner

1. Are LM operations mapped to existing shared actions correctly?
2. Is `run:request` too broad for generation?
3. Should participant response submission use Biscuit in P0 or remain product-scoped session token?
4. What caveats are mandatory for audience and data classes in export tokens?
5. What revocation lookup behavior is required for sensitive export/generation operations?

### Acceptance criteria

- No product-specific internal delegation token format.
- Tokens are scoped by organization/workspace/session/action/purpose.
- Export tokens are constrained by audience and data classes.
- Generation tokens cannot publish or validate.
- Raw tokens/bearer headers are never logged.

---

## Review Record Template

```yaml
review:
  reviewer: ""
  layer: "bolt | wrench | gear | biscuit-auth"
  outcome: "accepted | accepted_with_changes | blocked | deferred_with_stub"
  date: "YYYY-MM-DD"
  contract_refs:
    - "15-contracts-v0.1.md#..."
  required_changes: []
  accepted_stub_limits: []
  security_notes: []
  sovereignty_notes: []
  follow_up_adrs: []
```

---

## Current Review Status

| Layer | Status | Blocker to implementation? | Notes |
| --- | --- | --- | --- |
| Bolt | Not reviewed | Yes for real integration; no for contract-preserving stub | Need generation request/refusal review. |
| Wrench | Not reviewed | Yes for real integration; no for contract-preserving stub | Need citation support semantics review. |
| Gear | Not reviewed | Yes for real integration; no for contract-preserving stub | Need export/source ref manifest review. |
| Biscuit/Auth | Not reviewed | Yes for real internal delegation; no for non-security fixture proof | Need caveat/action mapping review. |

## Recommendation

Implementation may start only as a **stubbed P0 vertical** if each stub:

- emits the contract shapes in `15-contracts-v0.1.md`;
- is visibly marked as stub output;
- is covered by fixture tests;
- cannot silently become durable ingestion, memory, orchestration, artifact storage, or auth logic.
