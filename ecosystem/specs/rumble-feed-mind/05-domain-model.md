# Domain Model — rumble-feed-mind

Status: Draft / alignment model.

## Boundary Rule

`rumble-feed-mind` owns feed/watch product semantics and UX. It may start with local parsing/evaluation, but reusable ingestion, provenance, memory, artifacts, and orchestration should move down to Wrench/Gear/Bolt.

## Entities

### FeedWorkspace

User/product boundary for feeds, rules, provider policy, and exports.

Shared candidate: Workspace / project space.

### FeedSource

A subscribed feed URL and polling configuration.

Fields:

- id;
- workspace_id;
- url;
- title_snapshot;
- status;
- polling_policy;
- last_polled_at;
- provenance_json.

Candidate owner if extracted: Wrench Loader for parsing/polling rules; Gear for Source reference.

### FeedItem

A fetched item from a feed.

Fields:

- id;
- feed_source_id;
- source_url;
- title;
- summary/content snapshot;
- published_at;
- fetched_at;
- content_hash;
- provenance_json;
- status.

Candidate owner: product owns triage state; Gear owns source/provenance reference.

### Rule

A user-authored filtering/triage rule.

Fields:

- id;
- workspace_id;
- intent_text;
- rule_type;
- status;
- provider_policy_ref;
- created_by;
- created_at.

### RuleEvaluation

An evaluation of a rule against a feed item.

Fields:

- id;
- rule_id;
- feed_item_id;
- decision;
- confidence;
- explanation;
- evaluator_kind;
- provider_metadata_without_secrets;
- created_at.

Candidate owner: product first; Wrench Inspect later for validation/explainability checks.

### CuratedItem

A feed item selected as useful knowledge.

Fields:

- id;
- feed_item_id;
- tags;
- note;
- curation_reason;
- curated_by;
- curated_at.

### CuratedItemExport

A package/handoff from curated content to another Rumble or Gear.

Fields:

- id;
- workspace_id;
- target;
- item_ids;
- data_classes;
- export_hash;
- artifact_reference_id;
- created_by;
- created_at.

Candidate owner: Gear artifact once export/provenance becomes shared.

### ProviderPolicy

Allowed provider/model routing and BYOK settings.

Fields:

- id;
- workspace_id;
- allowed_providers;
- transmission_policy;
- pii_policy;
- key_reference;

Candidate owner: shared security policy / Gear secret adapter / Bolt policy.

## Shared Extraction Decisions To Make

| Concept | Keep in FeedMind first | Extract when |
| --- | --- | --- |
| FeedSource parsing | Yes | another Rumble needs feed ingestion. |
| RuleEvaluation | Yes | validation/explanation becomes reusable. |
| CuratedItemExport | No, align with Gear early | exports feed multiple products. |
| ProviderPolicy | No, define shared policy early | BYOK used by LM/Canvas/FeedMind. |
| WatchWorkflow | No, Bolt candidate | recurring reports/tasks appear. |

## Stack Challenge

Current repository includes Rust backend and web/mobile client history. Ecosystem direction is Rust core + Dioxus for interactive Rumbles. Therefore:

- Rust core/backend aligns.
- Existing web/mobile client must either migrate toward Dioxus or receive an ADR exception.
- Workspace license is MIT; future license exceptions require ADR/waiver before core integration.
