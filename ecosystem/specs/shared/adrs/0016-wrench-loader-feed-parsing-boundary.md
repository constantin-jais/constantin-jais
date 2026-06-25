# ADR 0016 — Feed Parsing in Wrench Loader, Feed Product Logic Outside

Status: Accepted
Date: 2026-06-30

## Context

`rumble-feed-mind`, `rumble-note`, `rumble-lm`, and `rumble-cos` need feed item normalization. But subscription management, triage rules, ranking, curation, and polling workflows are product/orchestration concerns.

Creating a separate feed loader before the product slice stabilizes risks premature fragmentation.

## Decision

RSS, Atom, and JSON Feed parsing belong in `wrench-loader` P0 as deterministic input normalization. Feed polling, subscription UX, rule evaluation, ranking, explanations, and curated export remain `rumble-feed-mind`/Rumble product logic. Scheduling recurring fetches belongs to Bolt when orchestration is needed.

A future split to `wrench-feed-loader` requires an ADR showing independent complexity and avoiding product logic leakage.

## Consequences

- Feed parsing is not duplicated across Rumbles.
- FeedMind remains a curation product, not a parser implementation detail.
- Loader remains bounded extraction, not a crawler/feed brain.

## Acceptance Tests

- Given RSS/Atom/JSON Feed fixtures, Loader normalizes item metadata and content deterministically.
- Given polling interval or ranking rules, Loader rejects ownership and returns a boundary error.
- Given a curated feed bundle, Gear Depot owns artifact packaging while Gear Memory can later index it as artifact-as-source.
