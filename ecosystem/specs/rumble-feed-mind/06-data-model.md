# Data Model — rumble-feed-mind

Status: Draft / aligned with active Rust/PostgreSQL repo but not a DB truth dump.

## Principles

- Store product state in FeedMind; store durable shared refs/artifacts in Gear when exported.
- Store hashes and references in exports, not raw secrets/private content.
- Treat source/artifact as lifecycle roles: a feed item can be a source, an export can be an artifact, and an artifact can later be reused as source.

## Tables / collections

### `feed_workspaces`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Workspace boundary. |
| `owner_actor_ref` | string | ActorReference, not full identity truth. |
| `name` | string | User-facing. |
| `provider_policy_id` | nullable string | Active policy ref. |
| `created_at` | timestamp | RFC3339 projection. |

### `feed_sources`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Local product id. |
| `workspace_id` | ref | Tenant/workspace isolation. |
| `url_hash` | sha256 | Avoid leaking URL in exported evidence by default. |
| `url_encrypted_or_local` | string | Product store only, not export default. |
| `title_snapshot` | string | Safe display. |
| `polling_policy` | json | Interval/status. |
| `last_polled_at` | timestamp | Optional. |
| `source_ref_id` | nullable string | Gear Memory after export/index. |

### `feed_items`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Local item id. |
| `feed_source_id` | ref | Parent source. |
| `title` | string | Export max 300 chars. |
| `content_snapshot` | text/json | Product store; minimized in exports. |
| `content_hash` | sha256 | Required for export. |
| `source_url_hash` | sha256 | Required for export. |
| `published_at` | timestamp | Optional. |
| `fetched_at` | timestamp | Required. |
| `privacy_classification` | enum | `public`, `normal`, `private`, `sensitive`, `no_handoff`. |
| `state` | enum | `new`, `saved`, `rejected`, `needs_review`, `exported`, `deleted`. |

### `rules`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Rule id. |
| `workspace_id` | ref | Isolation. |
| `intent_text` | text | User-authored; may be private. |
| `rule_kind` | enum | deterministic/provider_assisted. |
| `provider_policy_ref` | nullable string | Required for provider-assisted. |
| `status` | enum | draft/accepted/disabled. |
| `created_by` | actor ref | Safe attribution. |
| `created_at` | timestamp | Audit. |

### `rule_evaluations`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Evaluation id. |
| `rule_id` | ref | Parent rule. |
| `feed_item_id` | ref | Item. |
| `decision` | enum | match/no_match/manual_override/not_evaluated. |
| `confidence` | number | 0..1. |
| `explanation` | string | Safe explanation; no secret/prompt raw dump. |
| `evidence_hash` | sha256 | Hash of evidence snapshot. |
| `evaluator_kind` | enum | deterministic/local/provider. |
| `created_at` | timestamp | Audit. |

### `curated_items`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | uuid/string | Curated id. |
| `feed_item_id` | ref | Source item. |
| `tags` | string[] | Safe labels. |
| `curation_reason` | string | Exported if safe. |
| `curated_by` | actor ref | Attribution. |
| `curated_at` | timestamp | Audit. |

### `curated_item_exports`

| Field | Type | Notes |
| --- | --- | --- |
| `export_id` | string | Maps to `CuratedItemExport.export_id`. |
| `workspace_id` | ref | Isolation. |
| `purpose` | enum | note_context/learning_source/cos_source/spec_context/agent_context/local_export. |
| `privacy_classification` | enum | Must not be `no_handoff`. |
| `export_hash` | sha256 | Stable canonical JSON hash. |
| `artifact_reference_id` | nullable string | Gear Depot id. |
| `provenance_id` | string | Gear Memory provenance. |
| `approval_ref` | nullable string | Required for sensitive exports. |
| `created_by` | actor ref | Safe attribution. |
| `created_at` | timestamp | Audit. |

### `provider_policies`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Policy ref. |
| `workspace_id` | ref | Isolation. |
| `provider_class` | enum | local/eu_open_or_sovereign/eu_commercial/us_proprietary. |
| `allowed_provider_refs` | string[] | No raw keys. |
| `blocked_provider_refs` | string[] | Explicit blocks. |
| `retention_policy_ref` | string | Required. |
| `log_redaction_policy_ref` | string | Required. |
| `created_at` | timestamp | Audit. |

### `byok_key_refs`

| Field | Type | Notes |
| --- | --- | --- |
| `key_ref` | string | Opaque ref. |
| `workspace_id` | ref | Isolation. |
| `provider_ref` | string | Provider id/class. |
| `ciphertext` | bytes/string | Product secret store only. |
| `key_version` | integer | Rotation. |
| `created_at` | timestamp | Audit. |
| `deleted_at` | nullable timestamp | Deletion. |

## Export projection

`CuratedItemExport` includes only:

- item id/title/excerpt/hash/source URL hash;
- source ref;
- curation reason;
- rule evidence summary/hash;
- constraints proving no secrets/BYOK/downstream execution;
- artifact/provenance refs.

It excludes:

- BYOK ciphertext/plaintext;
- JWT/session tokens;
- Stripe/payment IDs;
- private raw content unless explicit sensitive inclusion is approved;
- provider prompts/responses unless separately classified and minimized.
