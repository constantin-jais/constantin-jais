# User Journeys — rumble-feed-mind

Status: Draft.

## Journey: Add Feed Source

Trigger: user wants to track a new source.  
Actor: Owner or Curator.

Happy path:

1. User submits feed URL.
2. System validates URL and feed format.
3. System creates `FeedSource`.
4. Worker fetches first batch.
5. Items become `FeedItem` records with provenance.

Events:

- `feed_source_created`
- `feed_source_polled`
- `feed_item_discovered`

Shared extraction:

- feed parsing may move to Wrench.
- item provenance may become Gear Source metadata.

## Journey: Create Natural-Language Rule

Actor: Owner or Curator.

Happy path:

1. User writes rule intent.
2. System stores rule draft.
3. System evaluates sample items.
4. System displays explanation and examples.
5. User accepts rule.

Events:

- `rule_created`
- `rule_sample_evaluated`
- `rule_accepted`

Risks:

- provider transmission of feed content;
- hidden rule behavior;
- key leakage.

## Journey: Triage Feed Items

Actor: Curator or System.

Happy path:

1. New item arrives.
2. Rules evaluate item.
3. System assigns decision: keep, reject, needs_review.
4. Explanation is stored.
5. User can override.

Events:

- `rule_evaluated`
- `feed_item_classified`
- `feed_item_overridden`

## Journey: Export Curated Item

Actor: Owner or Curator.

Targets:

- `rumble-note` as note/context fragment;
- `rumble-lm` as session source;
- `rumble-cos` as article/resource seed;
- Gear Memory as source/context;
- Gear Depot as export artifact.

Happy path:

1. User selects curated item(s).
2. User selects target and data classes.
3. System builds `CuratedItemExport`.
4. Export includes provenance, rule explanation, source URL, content snapshot/hash.
5. Target receives source/artifact reference.

Events:

- `curated_item_export_created`
- `curated_item_export_submitted`

## Journey: Provider/BYOK Setup

Actor: Owner.

Happy path:

1. Owner selects provider policy.
2. Owner stores key in encrypted secret storage.
3. System validates provider without logging key.
4. Rule evaluation uses policy.

Acceptance:

- key never appears in logs;
- export never includes key;
- provider policy is visible in audit metadata.
