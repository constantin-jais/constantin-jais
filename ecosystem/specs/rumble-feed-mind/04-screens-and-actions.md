# Screens and Actions — rumble-feed-mind

Status: Draft / no new UI authorized before security/dependency blockers clear.

## Screen: Dashboard

Actions:

- View feed health summary.
- View review queue count.
- View rule impact summary.
- View export warnings.

Acceptance notes:

- Shows aggregate counts only.
- No raw secrets, provider keys, or payment data.

## Screen: Feeds

Actions:

- Add feed URL.
- Validate feed URL.
- Edit polling policy.
- Disable feed.
- View last poll status.

Boundary:

- FeedMind owns subscription UX.
- Reusable parsing/extraction becomes Gear Loader candidate.

## Screen: Inbox / Item detail

Actions:

- Read item summary/snapshot.
- Mark item saved/rejected/needs-review.
- Add tags.
- Override rule decision.
- Open source URL externally.

Safety:

- Private item content is not exported by default.
- User override creates audit event.

## Screen: Rules

Actions:

- Create deterministic rule.
- Draft natural-language rule intent.
- Evaluate rule on sample items.
- Accept/reject rule.
- View explanation and evidence.

Provider/BYOK constraints:

- Natural-language provider-backed evaluation is disabled unless Provider/BYOK policy is accepted.
- Provider calls must use minimized context.
- Keys are referenced by key id/version only.

## Screen: Curated Items

Actions:

- Review saved item.
- Edit curation reason.
- Select export purpose.
- Preview `CuratedItemExport`.
- Flag item as no-handoff.

Contract mapping:

- Preview must show `privacy_classification`, `content_hash`, `source_ref`, `rule_evidence`, `artifact_ref`, and `provenance_ref` readiness.

## Screen: Export Builder

Actions:

- Select curated items.
- Select target: `rumble-note`, `rumble-lm`, `rumble-cos`, Gear, local export.
- Select data classes.
- Run export validation.
- Request human approval.
- Generate export artifact.

Non-actions:

- Cannot trigger Bolt execution.
- Cannot include BYOK material.
- Cannot export `no_handoff` items.

## Screen: Provider Policy

Actions:

- Select provider class: local, EU/sovereign, EU commercial, US proprietary waiver.
- Add BYOK key.
- Rotate key.
- Delete key.
- View provider policy audit refs.

Safety:

- Keys are write-only.
- US proprietary providers are blocked by default and require explicit waiver.

## Screen: Audit

Actions:

- View event log entries.
- View Wrench findings.
- View export/provenance refs.
- Export audit evidence without secrets.

## Action authorization summary

| Action | Owner | Requires human approval | Notes |
| --- | --- | --- | --- |
| Add feed | Owner/Curator | No | URL validation required. |
| Accept provider-backed rule | Owner/Curator | Yes | Requires Provider/BYOK policy. |
| Save curated item | Curator | No | Creates event. |
| Export curated item | Owner/Curator | Yes | Requires `CuratedItemExport` validation. |
| Submit to harness | Owner | Yes | Planning-only; no execution. |
| Manage BYOK key | Owner | Yes | Key never displayed after creation. |
