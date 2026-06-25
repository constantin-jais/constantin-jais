# Gear Boundaries

Status: Draft / P0 substrate contract.

## Doctrine

Gear owns infrastructure physics: storage, indexing, integrity, provenance,
packaging, distribution wiring, offline/local-first substrate, and sync
primitives.

Gear does not own product UX, product workflows, agent decisions, ingestion
rules, learning/session/note/canvas semantics, or business meaning.

## Boundary Tests

| Question | Owner |
| --- | --- |
| Does it store, index, verify, package, sync, or distribute? | Gear |
| Does it decide what should happen next? | Bolt |
| Does it parse, transform, inspect, or validate content? | Wrench |
| Does it define what a user sees or means by the data? | Rumble |

## P0 Contract Placement

| Contract | Primary owner | Consumers | Notes |
| --- | --- | --- | --- |
| `SourceRef` | `gear-memory` | Rumble, Wrench, Bolt, Gear Depot | Stable reference to raw or canonical input. Wrench may produce it, but Gear stores and indexes it. |
| `ArtifactRef` | `gear-depot` | Rumble, Bolt, Wrench, Gear Cable | Stable reference to produced, versioned, packageable, or distributable output. |
| `ProvenanceRecord` | Gear shared shape, stored by `gear-memory` and `gear-depot` | All layers | Records actor, operation, inputs, outputs, and tool/build references without secrets. |
| `MemoryEntry` | `gear-memory` | Rumble Note, Rumble LM, Rumble Canvas, Bolt | Indexable context record with deletion and stale propagation. |
| `CodeMap` | `gear-memory` stores/indexes; Wrench parses | Bolt, Rumble Crew, Rumble Canvas, Wrench Inspect | Reproducible code/source graph over `SourceRef`, symbols, and typed edges. Not code truth and not an explainer brain. |
| `EventLogEntry` | Gear shared shape, first modeled in `gear-memory` | All layers | Append-only audit substrate. Product event names remain product-owned. |
| `PackageManifest` / `ArtifactManifest` | `gear-depot` | Rumble exports, Bolt handoffs, Gear Cable releases | Integrity, retention, revocation, distribution metadata. |

## Source vs Artifact Decision

`Source` is referenced input or material that another layer can cite, index, or
ground against. It may be a file, URL, feed item, note block, transcript,
document, dataset, or Wrench canonical extraction.

`Artifact` is produced output that is packageable, versioned, immutable once
published, distributed, retained, revoked, or verified. It may be a spec
package, implementation handoff payload, curated export, learning export,
inspection report, release asset, or build output.

The same real-world object can move across lifecycles:

```text
feed item as observed input -> SourceRef
curated feed bundle exported to LM -> ArtifactRef
artifact later used to ground a new session -> SourceRef pointing at ArtifactRef
```

This duality is explicit. Gear must not infer product meaning from it.

## RGPD and Security Requirements

- References must support `deleted`, `anonymized`, `revoked`, and `stale` states
  without deleting audit metadata that is legally retained.
- Debug output and event metadata must exclude secrets, API keys, tokens, raw
  credentials, and full sensitive content.
- Metadata writers must reject secret-like keys such as `secret`, `token`,
  `password`, `credential`, and `api_key`; redaction is a fallback for debug
  display, not the primary control.
- Content hashes must be stable over canonical bytes, not display projections,
  and must use lowercase or uppercase hexadecimal SHA-256 formatted as
  `sha256:<64 hex chars>`.
- Timestamps must be RFC3339 / ISO 8601 strings with an explicit offset, for
  example `2026-06-30T00:00:00Z`.
- Actor references are attribution snapshots, not identity ownership.
- Product layers decide retention policy; Gear enforces and records the
  resulting state transitions.
