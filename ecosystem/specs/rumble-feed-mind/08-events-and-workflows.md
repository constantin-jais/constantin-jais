# Events and Workflows — rumble-feed-mind

Status: Draft / event-minded alignment.

## Event principles

- Events are product audit facts, not Gear workflow ownership.
- Events contain safe actor refs, target refs, hashes, and policy refs.
- Events never contain BYOK keys, JWTs, Stripe secrets, raw provider prompts, or unminimized private feed content.
- Gear `EventLogEntry` may store safe projections when events become shared audit substrate.

## Core events

| Event | Trigger | Safe payload |
| --- | --- | --- |
| `feed_source.created` | Feed URL accepted. | feed_source_id, workspace_id, actor_ref, url_hash. |
| `feed_source.polled` | Worker poll completed. | feed_source_id, item_count, status, timestamp. |
| `feed_item.discovered` | New item normalized. | feed_item_id, feed_source_id, content_hash, source_url_hash. |
| `rule.created` | Rule draft saved. | rule_id, rule_kind, actor_ref. |
| `rule.sample_evaluated` | Sample evaluation run. | rule_id, item_ids/hashes, evidence_hash, provider_policy_ref. |
| `rule.accepted` | Human accepts rule. | rule_id, actor_ref, policy_ref. |
| `feed_item.classified` | Rule/system classifies item. | feed_item_id, rule_id, decision, evidence_hash. |
| `feed_item.overridden` | User overrides classification. | feed_item_id, previous_decision, new_decision, actor_ref. |
| `curated_item.saved` | Item saved as useful. | curated_item_id, feed_item_id, tags, actor_ref. |
| `curated_item_export.previewed` | Export preview generated. | export_preview_id, curated_item_ids, target, findings_summary. |
| `curated_item_export.created` | Validated export created. | export_id, export_hash, artifact_ref, provenance_ref. |
| `provider_policy.updated` | Provider policy changed. | policy_ref, provider_classes, actor_ref. |
| `byok_key.created` | Key stored. | key_ref, provider_ref, key_version; no key value. |
| `byok_key.rotated` | Key rotated. | old_key_ref, new_key_ref, actor_ref. |
| `byok_key.deleted` | Key deleted/deactivated. | key_ref, actor_ref, timestamp. |

## Workflow: feed polling

```text
feed_source.created
→ feed_source.polled
→ feed_item.discovered*
→ rule_evaluated/classified*
```

Failure behavior:

- network/provider failures produce safe status events;
- no credentials in error details;
- repeated failures can disable polling after policy threshold.

## Workflow: provider-assisted rule acceptance

```text
rule.created(draft)
→ provider_policy_checked
→ rule.sample_evaluated
→ human reviews explanation/evidence
→ rule.accepted OR rule.rejected
```

Gates:

- Provider/BYOK policy accepted;
- no blocked provider;
- context minimized;
- explanation/evidence stored safely.

## Workflow: curated item export

```text
curated_item.saved
→ curated_item_export.previewed
→ Wrench PII/secrets/export inspection
→ human approval
→ curated_item_export.created
→ optional Gear source/artifact/provenance refs
```

Stop conditions:

- item is `no_handoff`;
- sensitive item lacks explicit inclusion reason/approval;
- export contains BYOK material/secrets;
- Wrench critical finding;
- artifact/provenance refs malformed.

## Workflow: harness submission

FeedMind does not submit directly to execution. If a future export feeds Bolt:

```text
CuratedItemExport
→ SpecPackage/context package
→ ImplementationHandoff planning_request
→ cosmatic validate
→ Wrench inspect
→ cosmatic plan --dry-run
→ human approval placeholder
→ no execution
```

## Retention defaults

| Data | Default |
| --- | --- |
| Feed URL | Product store only; exports use hash/ref unless user includes URL. |
| Feed item snapshot | Retain per workspace policy; deleted/anonymized on request. |
| Rule evaluation evidence | Retain safe explanation/hash; raw provider prompt not retained by default. |
| BYOK key ciphertext | Retain until deletion/rotation; never exported. |
| Curated exports | Retain artifact/provenance refs; purge content per policy. |
| Audit events | Retain safe refs/hashes; no raw secrets. |

## Wrench/Gear projections

- Wrench reports: PII/secrets, export validity, provider policy conformance.
- Gear Memory: `SourceRef`, `ProvenanceRecord`, `EventLogEntry` safe projection.
- Gear Depot: `ArtifactRef` / manifest for export artifacts.
