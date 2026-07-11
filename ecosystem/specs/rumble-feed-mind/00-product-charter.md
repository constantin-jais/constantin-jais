# Product Charter — rumble-feed-mind

Status: Imported / needs ecosystem alignment.

## Mission

`rumble-feed-mind` is an intelligent feed and watch pipeline that turns high-volume feeds into structured, explainable, reusable knowledge for humans and the agentic harness.

It helps users collect, filter, explain, tag, summarize, and export information from feeds without trapping knowledge in a silo.

## Product Promise

Users can define understandable rules, process large volumes of incoming content, and produce curated knowledge artifacts that can feed notes, learning sessions, specs, blog posts, or agent context.

## Target Users

- Technical power users doing daily watch/veille.
- Builders who want curated sources for personal knowledge and agentic workflows.
- Analysts or educators preparing source-grounded content.
- Future teams sharing feed collections and insights.

## Jobs To Be Done

1. When I follow many feeds, I want irrelevant items filtered so that I spend time only on meaningful content.
2. When an item is selected or rejected, I want to understand why so that the system remains trustworthy.
3. When a useful item appears, I want to save it as structured context so that it can feed notes, learning sessions, specs, or blog content.
4. When I define a rule, I want to express intent in natural language and see how it behaves.
5. When I export my data, I want feeds, rules, decisions, tags, and curated items to remain portable.

## Product Boundaries

### Owns

- Feed subscription UX.
- Feed polling configuration from a user/product perspective.
- Rule authoring and explainability UX.
- Item triage, tagging, saved items, and curated collections.
- Export/handoff of curated knowledge artifacts.

### Does Not Own

- Generic ingestion/extraction engine: belongs to Wrench when reused beyond feeds.
- Long-term semantic memory/index: belongs to Gear Memory.
- Artifact integrity/provenance: belongs to Gear Depot when exported/shared.
- Agent orchestration: belongs to Bolt / `cos-matic`.
- Learning session UX: belongs to `rumble-lm`.
- Personal block notes UX: belongs to `rumble-note`.

## MVP Scope

- Feed subscriptions.
- Feed polling worker.
- Item list and reading/triage workflow.
- Natural-language rule definition.
- Rule evaluation explanation.
- Save/export curated item.
- BYOK or sovereign model configuration with strict secret handling.
- Basic source/export handoff to the ecosystem.

## Post-MVP Scope

- Team/shared feed spaces.
- Advanced scoring and semantic clustering.
- Multi-source channels beyond RSS.
- Deeper integration with `rumble-note`, `rumble-lm`, and `rumble-libre-ia`.
- Offline/mobile client if stack decision remains valid.

## Dependencies on Bolt/Wrench/Gear

### Bolt

- Optional planning for rule refinement or recurring watch workflows.
- Future task creation for review/report generation.

### Wrench

- Feed parsing and content extraction may become `wrench-feed-loader` or part of `wrench-loader` if reused.
- Rule/result inspection may become a Wrench validation capability.

### Gear

- Curated items become `Source` or `Artifact` references.
- Exports need provenance, hashes, and retention metadata.
- Saved knowledge may be indexed by Gear Memory.

## Stack / Compliance Challenge

Current local repository metadata indicates:

- Rust backend workspace;
- Axum, SQLx, PostgreSQL, Redis;
- planned mobile/web client from the existing PRD;
- license aligned to `MIT` at workspace level.

The product now follows the ecosystem preference for permissive sovereign OSS licensing. Any future license exception must be documented by ADR/waiver.

## Main Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Becomes a generic feed reader | High | Keep focus on explainable curation and harness-ready exports. |
| Duplicates Wrench ingestion | High | Extract feed parsing/extraction if reused by other products. |
| Duplicates Gear Memory | High | FeedMind owns UX/triage; Gear owns memory/index substrate. |
| BYOK secrets mishandled | Critical | Secrets must never appear in logs/exports/handoffs. |
| License drift conflicts with ecosystem policy | Medium | Keep MIT workspace license; document any future exception by ADR/waiver. |
| US model/provider dependency | High | BYOK plus provider policy; sovereign/local options needed for core truth. |

## Shared Capability Candidates

| Candidate | Proposed owner | Reason |
| --- | --- | --- |
| Feed source | Wrench Loader / Gear Source | Feed URLs and fetched items are reusable sources. |
| Rule explanation | Rumble FeedMind first; Wrench Inspect later | Rule decisions need explainability and validation. |
| Curated item export | Gear artifact + Gear memory | Saved items feed notes, LM, COS, agents. |
| Watch workflow | Bolt | Recurring watch/report tasks need orchestration. |
| Provider/BYOK policy | Shared security/Gear/Bolt policy | Secrets and model routing affect multiple products. |

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Is `rumble-feed-mind` an active Rumble product or a source pipeline feeding other Rumbles? | High | Open |
| Should feed parsing live in this product or be extracted to Wrench? | High | Open |
| Should saved items become Gear `Source` first or Rumble `Artifact` first? | High | Open |
| Is AGPL acceptable, or must the project relicense/receive a waiver? | High | Accepted: workspace license is MIT. |
| Is Expo/mobile still the target client stack, or should Rumble interactive stack converge on Rust/Dioxus? | High | Accepted: interactive Rumble target is Rust/Dioxus; legacy TS/mobile surfaces are migration references only. |
