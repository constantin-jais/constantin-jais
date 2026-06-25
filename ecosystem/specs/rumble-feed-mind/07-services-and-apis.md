# Services and APIs — rumble-feed-mind

Status: Draft / contract-first; endpoint names are illustrative.

## Service boundaries

| Service | Owns | Must not own |
| --- | --- | --- |
| Feed API | Product CRUD for feeds, items, rules, curated items, exports. | Generic ingestion for other products. |
| Worker | Polling, normalization, deterministic rule evaluation. | Bolt orchestration or durable memory truth. |
| Provider adapter | Provider-backed explanation behind policy. | Raw key lifecycle beyond secret adapter. |
| Export service | Builds `CuratedItemExport`, validates privacy constraints. | Gear artifact storage semantics. |
| Audit service | Safe event/report refs. | Raw logs or long-term source truth. |

## API envelope

All JSON APIs SHOULD use:

```json
{
  "data": {},
  "meta": {
    "request_id": "safe-request-id",
    "policy_ref": "optional-policy-ref"
  }
}
```

Errors SHOULD include safe codes, not raw provider secrets or private content.

## Feed APIs

### `POST /feeds`

Input:

- feed URL;
- optional folder/tag;
- polling policy.

Output:

- `feed_source_id`;
- validation status;
- safe source hash.

Gates:

- URL validation;
- no credentialed/private URL export by default.

### `GET /feeds/{id}`

Returns feed metadata, status, last poll state, safe provenance refs.

## Item APIs

### `GET /items`

Filters:

- feed;
- state;
- tag;
- privacy classification;
- rule decision.

### `PATCH /items/{id}/triage`

Actions:

- save;
- reject;
- needs_review;
- override decision;
- set privacy classification.

Creates event `feed_item_triaged` or `feed_item_overridden`.

## Rule APIs

### `POST /rules`

Creates deterministic or provider-assisted rule draft.

Provider-assisted rules require:

- accepted Provider/BYOK policy;
- provider class not blocked;
- minimized sample context.

### `POST /rules/{id}/evaluate-sample`

Returns safe explanation and evidence hashes.

Must not return raw provider prompt or key material.

### `POST /rules/{id}/accept`

Requires human action and creates `rule_accepted` event.

## Provider/BYOK APIs

### `GET /provider-policy`

Returns current policy refs and provider classes, not keys.

### `POST /provider-policy/byok-keys`

Stores a key write-only.

Rules:

- plaintext accepted only in request body over TLS;
- encrypt immediately;
- never return plaintext;
- log only key ref/provider class.

### `POST /provider-policy/byok-keys/{key_ref}/rotate`

Creates new key version and retires previous version.

### `DELETE /provider-policy/byok-keys/{key_ref}`

Deletes/deactivates key and creates audit event.

## Export APIs

### `POST /curated-items/{id}/export-preview`

Builds a non-persistent preview of `CuratedItemExport`.

Validation:

- `no_handoff` blocks export;
- `sensitive` requires inclusion reason and approval;
- no BYOK material;
- no downstream execution;
- artifact/provenance refs ready or pending.

### `POST /exports`

Creates a validated export artifact.

Output:

- export id;
- export hash;
- artifact/provenance refs;
- Wrench finding summary.

### `POST /exports/{id}/submit-handoff`

Future only. Submits context to planning-only harness path. Must never execute implementation.

## Billing / Stripe adapter

Stripe APIs, if enabled, are an optional adapter:

- must not be required for local/self-hosted core use;
- must be feature/config gated;
- must not appear in curated exports;
- must have sovereignty risk documentation and DPA/payment policy.

## Auth / delegation

- Product session auth may remain JWT temporarily if documented as local/session-only.
- Inter-service or harness delegation must use shared delegated authorization direction (Biscuit) or accepted waiver.
- Exports and handoffs require actor refs and approval refs.

## Wrench/Gear APIs

FeedMind should call or produce refs for:

- Wrench inspection report for PII/secrets/export validity;
- Gear Memory `SourceRef`/`ProvenanceRecord`;
- Gear Depot `ArtifactRef`/manifest.

These are references/projections, not product workflow ownership.
