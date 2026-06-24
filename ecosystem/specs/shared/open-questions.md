# Open Questions

## Ecosystem-Level

| Question | Impact | Owner | Status |
| --- | --- | --- | --- |
| Should `workspace` be a shared Rumble primitive or a Gear-level tenant/context primitive? | High | Architecture | Open |
| Should `source` and `artifact` be separate concepts everywhere? | High | Architecture | Open |
| What is the minimum shared identity/auth model across all Rumbles? | High | Security/Product | Open |
| What shared policy decides who can approve high/critical waivers across products? | High | Security/Product | Partially accepted for Canvas MVP: distinct human Owner + Reviewer; cross-product policy remains open. |
| Which products require local-first behavior from day one? | High | Product | Open |
| Should specs live in root `specs/` or inside each product repository? | Medium | Architecture | Open |
| Should specs be written in English, French, or mixed by audience? | Medium | Product | Open |

## Product-Level

### rumble-canvas

| Question | Impact | Status |
| --- | --- | --- |
| Is it primarily a team product, a solo product, or both? | High | Partially answered: MVP supports solo plus small team via minimal membership/role assignments. |
| What is the first canonical deliverable: PRD, screen map, user story map, data model, or implementation plan? | High | Open |
| How strict are validation gates before Bolt execution? | High | Partially answered: Canvas handoff is planning-only and cannot authorize execution; execution remains behind Bolt/`cos-matic` gates. |
| Should `TraceabilityLink` be first-class in MVP? | High | Accepted. |
| Should `Waiver` be a first-class entity? | Medium | Accepted: first-class minimal/extensible MVP. |
| Should spec content be Markdown, structured JSON, or dual-format? | High | Accepted: dual-format. |
| What is the first Bolt handoff format? | High | Accepted: planning-only `ImplementationHandoff` using `canvas.bolt_handoff.v0.1`, targeting `cos-matic` for MVP. |
| Which spec completeness checks belong in Wrench? | Medium | Open |

### rumble-cos

| Question | Impact | Status |
| --- | --- | --- |
| Is the primary unit an article, course, resource, project page, or learning path? | High | Open |
| Does it need a private editorial workflow or static publishing only? | Medium | Open |

### rumble-crew

| Question | Impact | Status |
| --- | --- | --- |
| What is the canonical lifecycle of an agent task? | High | Open |
| Are agents users, service accounts, or runtime identities? | High | Open |
| Which actions require explicit human approval? | High | Open |

### rumble-feed-mind

| Question | Impact | Status |
| --- | --- | --- |
| Is it an active Rumble product or primarily a source pipeline feeding other Rumbles? | High | Open |
| Should feed parsing/extraction stay product-local or become Wrench capability? | High | Open |
| Is AGPL acceptable, or must the project relicense / receive a documented waiver? | High | Open |
| Should current Rust backend + Expo client remain, or should interactive Rumble stack converge? | High | Open |
| What is the minimum curated-item export/handoff format? | High | Open |

### rumble-lm

| Question | Impact | Status |
| --- | --- | --- |
| What is the canonical session lifecycle? | High | Accepted for MVP: Draft → Prepared → Live → Closed → Synthesized → Exported → Archived. |
| Are quizzes/activities first-class objects or generated session blocks? | High | Accepted for MVP: first-class `Activity` objects with lifecycle, citations, responses, and analytics. |
| How are citations and grounding verified? | High | Accepted for MVP: generated source-grounded claims require citation resolution; facilitator final validation, Wrench validator advisory. |
| What retention defaults apply to raw responses, summaries, exports, and audit events? | High | Open |
| Should live participation/presence become shared Rumble/Gear infrastructure after MVP? | Medium | Open |
| Which generation backend policy is allowed per deployment? | High | Open |

### rumble-note

| Question | Impact | Status |
| --- | --- | --- |
| What is the minimal block model? | High | Open |
| How does local-first sync work? | High | Open |
| What is the handoff from personal note to spec/task/session/source? | High | Open |
