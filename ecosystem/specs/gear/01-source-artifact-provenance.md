# Source, Artifact, and Provenance Contracts

Status: Draft / P0 substrate contract.

## SourceRef

Owner: `gear-memory`.

Purpose: identify source material without importing product semantics.

```json
{
  "source_id": "src_01",
  "source_type": "file | url | feed_item | note_block | transcript | document | dataset | artifact",
  "origin_product": "rumble-feed-mind | rumble-note | rumble-lm | rumble-canvas | rumble-cos | gear-loader | gear-depot",
  "uri": "optional",
  "content_hash": "sha256:...",
  "provenance_id": "prov_01",
  "state": "active | stale | deleted | anonymized",
  "created_at": "2026-06-30T00:00:00Z"
}
```

Rules:

- `source_id`, `origin_product`, and `provenance_id` must be non-empty.
- `content_hash` is required for materialized content and must be formatted as
  `sha256:<64 hex chars>`.
- `created_at` must be RFC3339 / ISO 8601 with an explicit offset.
- `uri` is optional because local/private sources may only expose opaque IDs.
- `artifact` source type is allowed only when a prior artifact is reused as
  grounding input.
- `state=deleted` or `state=anonymized` must propagate to related memory index
  entries.

## ArtifactRef

Owner: `gear-depot`.

Purpose: identify produced output that can be packaged, verified, retained,
revoked, or distributed.

```json
{
  "artifact_id": "art_01",
  "artifact_type": "spec_package | handoff_payload | curated_export | learning_export | release_asset | inspection_report",
  "producer": "rumble-canvas | rumble-lm | rumble-feed-mind | rumble-cos | wrench-inspect | gear-cable",
  "version": "1.0.0",
  "hash": "sha256:...",
  "manifest_ref": "manifest_01",
  "state": "active | revoked | superseded | deleted",
  "created_at": "2026-06-30T00:00:00Z"
}
```

Rules:

- `artifact_id`, `producer`, `version`, and `manifest_ref` must be non-empty.
- `hash` is over canonical artifact bytes or the canonical package manifest when
  bytes are split across files, and must be formatted as
  `sha256:<64 hex chars>`.
- `created_at` must be RFC3339 / ISO 8601 with an explicit offset.
- `manifest_ref` points to an `ArtifactManifest`.
- Revocation changes availability and trust state; it must not mutate the
  original artifact hash.

## ProvenanceRecord

Owner: Gear shared shape; stored by `gear-memory` for sources/memory and
`gear-depot` for artifacts/distribution.

```json
{
  "provenance_id": "prov_01",
  "actor_ref": "actor_01",
  "operation": "created | imported | transformed | indexed | exported | signed | distributed | revoked | deleted | anonymized",
  "inputs": ["src_01"],
  "outputs": ["art_01"],
  "tool_ref": "optional",
  "timestamp": "2026-06-30T00:00:00Z",
  "metadata": {}
}
```

Rules:

- `provenance_id`, `actor_ref`, and `outputs` must be non-empty.
- `timestamp` must be RFC3339 / ISO 8601 with an explicit offset.
- `metadata` must not contain secrets or raw sensitive content.
- `metadata` validation must reject secret-like keys before persistence.
- `inputs` and `outputs` are references, not embedded payloads.
- Wrench tools may be referenced in `tool_ref`; Gear records the operation but
  does not own transformation logic.
- Bolt decisions may be referenced as inputs, but Gear does not decide.

## Product Impact

| Product | Impact |
| --- | --- |
| Canvas | `SpecPackage` and `ImplementationHandoff` become artifacts with provenance and stable hashes. Canvas still owns spec semantics. |
| Note | note blocks and exports become sources or artifacts by lifecycle; Note still owns block UX and graph. |
| LM | session source sets reference `SourceRef`; session exports reference `ArtifactRef`. |
| FeedMind | feed items are sources; curated exports are artifacts. Rule decisions remain product-owned. |
| Crew | evidence and runtime logs should reference artifacts without storing sensitive log content in product tables. |
