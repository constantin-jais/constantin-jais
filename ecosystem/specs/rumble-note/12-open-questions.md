# Open Questions — rumble-note

Status: Drafting.

| Question | Impact | Owner | Status | Recommendation |
| --- | --- | --- | --- | --- |
| What exact local database/storage engine should MVP use? | High | Architecture | Open | Prefer open-source local structured store with FTS support; decide in ADR before implementation. |
| Are Markdown files source of truth or export projection? | High | Product/Architecture | Open | Treat structured local store as source of truth for MVP; Markdown as deterministic export. |
| What is the canonical block ID format? | High | Architecture | Open | Use stable opaque IDs; avoid path-derived IDs so moves preserve identity. |
| Should block revisions snapshot full content or content hashes only? | High | Security/Product | Open | Store hashes in package manifest; include content in handoff items only when user confirms. |
| Is local encryption at rest required for MVP? | Medium | Security | Open | Not required for first spec, but evaluate before implementation if notes may contain sensitive data. |
| What is the minimum secure credential storage for downstream targets? | High | Security | Open | Use OS/local secure storage where possible; never store credentials in note DB/plain exports. |
| Should local event log be mandatory or configurable? | Medium | Product/Security | Open | Mandatory for handoff lifecycle; configurable/minimal for ordinary editing/search. |
| What exact handoff JSON schema version should be first? | High | Architecture | Open | Define `note.handoff.v0.1` before implementing export/submission. |
| Should `Workspace` be shared Rumble or Gear-level? | High | Ecosystem Architecture | Open | Keep product-local now, map fields to shared primitive later. |
| Should `SourceReference` wrap Gear source IDs from day one? | High | Gear/Wrench/Rumble | Open | Support optional canonical IDs but do not require Gear availability for MVP. |
| What source metadata is required for `verified` state? | Medium | Wrench/Gear | Open | Require locator + provenance + checksum/evidence where available. |
| How strict should source requirements be for learning-session handoff? | Medium | Product | Open | Blocking for source-grounded claims; warning for personal reflections. |
| Does MVP need saved searches or collections? | Low | Product | Deferred | Defer unless handoff package assembly becomes painful. |
| Does MVP need nested notebooks? | Low | Product | Rejected for MVP | One notebook level; use nested blocks inside documents. |
| Should semantic/embedding search be supported? | Medium | Product/Gear | Deferred | Not MVP; deterministic local search first. |
| How should future sync resolve conflicts? | High | Architecture | Deferred | No silent merges; explicit conflict objects and UI required. |
| Is future sync Gear-owned or app-owned? | High | Ecosystem Architecture | Open | Likely Gear substrate with Rumble UX adapter. |
| What is the relation between `rumble-note` handoff and `rumble-canvas` spec package? | High | Rumble Architecture | Open | Note exports context; Canvas owns spec package/review lifecycle. |
| Should task candidates create Bolt tasks directly? | High | Bolt/Rumble | Answered for MVP | No direct task lifecycle ownership; planning/context handoff only. |
| When can blocks become Gear Memory entries? | Medium | Gear/Rumble | Deferred | Post-MVP explicit promotion workflow with user confirmation and provenance. |
| Should visual graph exploration be in note? | Medium | Product | Rejected for MVP | Expose references/backlinks; visual exploration belongs to canvas surface. |
| What collaboration model is needed? | Medium | Product/Security | Deferred | Solo local MVP first; collaborative mode requires shared identity/membership model. |
| What accessibility baseline is required before implementation starts? | Medium | Product/Quality | Open | Keyboard navigation + screen-reader labels for MVP core flows. |
| Should specs be maintained in English or French? | Low | Product | Open | Current specs in English; product UI can be bilingual later. |
| Which acceptance tests are mandatory for first implementation slice? | High | Quality | Open | Start with capture, stable IDs, references, search, handoff privacy, export. |

## Decisions Needed Before Implementation

1. Local storage engine and migration strategy.
2. First handoff schema: `note.handoff.v0.1`.
3. Block ID and revision/hash strategy.
4. Whether encryption at rest is required in MVP.
5. Exact MVP cut for source verification.

## Deferred Explicitly

- Mandatory sync.
- Collaboration.
- Semantic search.
- Durable Gear Memory promotion.
- Visual graph editor.
- Plugin system.
- Broad ingestion UI.

## Risks to Revisit

- Product may still drift toward generic notes if handoff builder is weak.
- Product may duplicate Gear Memory if memory candidates become too central too early.
- Product may duplicate Wrench Loader if source import UX expands beyond references and selected outputs.
- Product may become too schema-heavy if block editing feels slow.
