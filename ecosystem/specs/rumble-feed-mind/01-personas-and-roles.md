# Personas and Roles — rumble-feed-mind

Status: Draft.

## Personas

### Solo Watcher

Needs to follow many sources, reduce noise, and keep useful items for later reuse.

### Technical Curator

Needs explainable filtering rules, exports, and source provenance for agents or knowledge bases.

### Analyst / Educator

Needs curated source collections that can feed learning sessions, articles, reports, or notes.

## Roles

| Role | Goal | Main permissions |
| --- | --- | --- |
| Owner | Own feed workspace, provider policy, exports, billing/self-host settings. | Manage feeds/rules/keys/exports. |
| Curator | Triage feeds and tune rules. | Add/edit feeds, create rules, tag/save items. |
| Reviewer | Validate rule behavior and curated exports. | Review explanations, approve exports. |
| Viewer | Read curated items and exported collections. | Read-only. |
| Agent | Suggest rules, tags, summaries, and export candidates. | Suggest only; no direct truth mutation. |
| System | Poll feeds, evaluate rules, record events. | Deterministic background actions. |

## Permission Challenges

- BYOK secrets are Owner-only and must never be visible after creation.
- Agent suggestions require human acceptance.
- Rule changes should be auditable because they affect future triage.
- Exports to other Rumbles require explicit target and data class selection.

## Shared Candidates

- ActorReference / Membership / RoleAssignment.
- Provider/BYOK policy.
- ExportPackage.
- SourceReference.
