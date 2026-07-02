# Contract — CuratedItemExport v0.1

Status: Draft / FeedMind blocker.  
Schema: `curated-item-export.v0.1.schema.json`.

## Purpose

`CuratedItemExport` is the minimal portable export from `rumble-feed-mind` to other Rumbles, Gear, Wrench, or Bolt planning flows.

It represents a human-curated feed item with safe metadata, source references, rule-decision evidence, privacy classification, and artifact/provenance refs. It is not a raw feed dump and must not contain BYOK keys, tokens, passwords, payment details, or unreviewed private content.

## Boundary

| Concern | Owner |
| --- | --- |
| Feed triage UX, curation reason, product labels | Rumble FeedMind |
| Feed parsing/extraction if reused | Gear Loader |
| Source identity and provenance | Gear Memory |
| Export artifact integrity | Gear Depot |
| Downstream planning | Bolt / `cos-matic` only through planning-only handoff |

## Required Shape

```json
{
  "format": "feedmind.curated_item_export.v0.1",
  "export_id": "export-demo",
  "origin_product": "rumble-feed-mind",
  "created_by": "actor-ref",
  "created_at": "2026-06-30T00:00:00Z",
  "purpose": "note_context",
  "privacy_classification": "normal",
  "item": {},
  "source_ref": {},
  "curation": {},
  "rule_evidence": [],
  "constraints": {},
  "artifact_ref": {},
  "provenance_ref": {}
}
```

## Privacy / Safety Rules

1. `privacy_classification = no_handoff` must block export.
2. `sensitive` exports require explicit human inclusion reason and approval ref.
3. `content_excerpt` is optional and must be minimized; `content_hash` is required.
4. BYOK/API keys, provider raw credentials, auth tokens, payment details, emails, and raw private annotations are forbidden.
5. Logs and reports may include IDs, hashes, and safe labels only.
6. Rule evidence must explain why an item was curated without exposing private prompts or provider secrets.

## Lifecycle Mapping

A curated item can be:

- a Gear Memory `SourceRef` when used as grounding input;
- a Gear Depot `ArtifactRef` when exported as a packaged deliverable;
- both over time, because source/artifact are lifecycle roles.

## Minimal Downstream Uses

| Destination | Use |
| --- | --- |
| `rumble-note` | Add source-grounded note context. |
| `rumble-lm` | Build source set for session preparation. |
| `rumble-cos` | Prepare public content source candidate. |
| Bolt | Planning-only request after package/handoff validation. |
| Gear Memory | Index source ref and provenance, not product workflow. |

## Gates Before Harness Handoff

A FeedMind handoff is blocked until:

1. `CuratedItemExport` validates;
2. Provider/BYOK policy validates;
3. no critical Wrench PII/secrets finding exists;
4. artifact/provenance refs validate;
5. human approval placeholder exists for any downstream execution.
