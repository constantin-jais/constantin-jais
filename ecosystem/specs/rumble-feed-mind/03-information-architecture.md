# Information Architecture — rumble-feed-mind

Status: Draft / harness alignment.

## Top-level spaces

| Space | Purpose | Notes |
| --- | --- | --- |
| Dashboard | Show feed health, review queue, rule impact, export readiness. | No secrets or raw provider diagnostics. |
| Feeds | Manage feed subscriptions, folders, polling status, source provenance. | Feed parsing may later move to Wrench Loader. |
| Inbox | Read and triage fetched feed items. | Product owns triage state; Gear owns source/provenance refs when exported. |
| Rules | Author deterministic and provider-assisted rules, evaluate samples, inspect explanations. | Provider/BYOK policy required before AI-backed rules. |
| Curated Items | Review saved items, tags, reasons, and export candidates. | Main source for `CuratedItemExport`. |
| Exports | Build, inspect, approve, and download/submit exports. | Exports are planning/context artifacts, never execution triggers. |
| Provider Policy | Configure allowed providers, BYOK refs, sovereign defaults, retention. | Owner-only; keys are never displayed after creation. |
| Audit | Review safe event log and Wrench findings. | Safe refs/hashes only; no raw secrets/PII. |

## Navigation model

```text
Dashboard
├── Feeds
│   ├── Feed detail
│   └── Poll history
├── Inbox
│   └── Item detail
├── Rules
│   ├── Rule editor
│   └── Rule evaluation report
├── Curated Items
│   └── Curated item detail
├── Exports
│   ├── Export builder
│   └── Export review
├── Provider Policy
└── Audit
```

## Object relationships

```text
FeedWorkspace
  ├─ FeedSource
  │   └─ FeedItem
  │       ├─ RuleEvaluation
  │       └─ CuratedItem
  │           └─ CuratedItemExport
  ├─ Rule
  ├─ ProviderPolicy
  └─ AuditEvent
```

## Cross-layer references

| FeedMind object | Shared/Gear/Wrench relationship |
| --- | --- |
| `FeedSource` | Candidate Wrench Loader input; may produce Gear `SourceRef`. |
| `FeedItem` | Product triage object; can become Gear `SourceRef` when exported. |
| `RuleEvaluation` | Product explanation now; Wrench validation candidate later. |
| `CuratedItemExport` | Draft contract `shared/contracts/curated-item-export.v0.1.md`; Gear artifact/source refs. |
| `ProviderPolicy` | Instantiates `shared/contracts/provider-byok-policy.v0.1.md`. |

## Information hiding rules

- BYOK keys are never part of navigation payloads after creation.
- Payment/Stripe identifiers stay in billing/admin internals, not curation/export surfaces.
- Raw feed private content is not shown in exports unless explicitly included and classified.
- Audit views show safe IDs, hashes, statuses, and actor refs.
