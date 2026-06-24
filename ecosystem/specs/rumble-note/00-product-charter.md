# Product Charter — rumble-note

Status: Drafting.

## Mission

`rumble-note` is a local-first block-based personal knowledge product for turning human notes into explicit, traceable, reusable context for the agentic harness.

It is not primarily a generic note-taking app. Its core responsibility is the thinking surface between private capture and deliberate handoff: users capture fragments, structure them as blocks, link them, qualify them, and decide what should become a source, spec input, task candidate, learning-session context, or durable memory candidate.

## Target Users

- Solo builder or researcher preparing context for agentic work.
- Product/spec author turning scattered observations into structured inputs.
- Learner collecting source-grounded notes for later learning sessions.
- Operator who wants local control over sensitive working notes before sharing them with other ecosystem bricks.

## Jobs To Be Done

1. Capture a thought, quote, source reference, question, or decision quickly without deciding its final destination.
2. Break a document into stable addressable blocks.
3. Link blocks to sources, other notes, decisions, tasks, specs, or learning sessions.
4. Retrieve relevant blocks by text, type, labels, source, or relationship.
5. Prepare an explicit handoff package for the harness or another Rumble/Bolt/Wrench/Gear component.
6. Keep private notes local, exportable, auditable, and deletable.

## Product Promise

Users can keep personal notes locally, structure them at block level, and deliberately promote selected fragments into action-ready context without surrendering control to hidden ingestion, hidden memory, or automatic orchestration.

## Non-Goals

These are non-goals for `rumble-note` core, not forbidden ecosystem capabilities.

- Do not own massive file/web/PDF/repo ingestion; consume outputs from `wrench-loader` when needed.
- Do not own durable agentic memory or autonomous recall; hand off validated candidates to `gear-memory`.
- Do not own execution, planning, or agent task lifecycle; request/prepare handoffs for Bolt/`cos-matic`.
- Do not own the main visual graph/canvas experience; expose blocks and links for `rumble-canvas` or another visual surface.
- Do not require cloud sync for core truth; local-first operation is mandatory.
- Do not optimize for a full generic notes suite before validating block-level handoff.

## Product Boundaries

`rumble-note` owns:

- local workspace experience for personal notes;
- document/notebook organization;
- block creation, editing, ordering, nesting, and stable IDs;
- manual references, backlinks, labels, and block qualification;
- local search and retrieval over notes;
- explicit handoff packages from selected blocks.

`rumble-note` consumes or integrates with:

- `wrench-loader` for imported canonical source content;
- `gear-memory` for source/provenance primitives and durable memory candidates;
- Bolt/`cos-matic` for planning or task/session orchestration;
- `rumble-canvas` for visual exploration and spec/product-conception flows.

## Success Metrics

- A user can capture and retrieve a note block in under a few seconds while offline.
- A user can create a typed backlink between two blocks or a block and source.
- A user can select blocks and produce a deterministic handoff package.
- Handoff output is readable by humans and agents.
- Local export contains no hidden remote dependency.
- Product scope remains clear against Wrench, Gear, Bolt, and Canvas responsibilities.

## MVP Scope

1. Local workspace with notebooks and documents.
2. Block editor with stable block IDs and minimal block types.
3. Typed references/backlinks between blocks, documents, and sources.
4. Search by text, block type, labels, links, and handoff state.
5. Handoff builder for source/spec/task/learning-session/harness-context packages.
6. Privacy/export controls for local data.

## Post-MVP Scope

- Optional sync adapter with conflict handling.
- Import adapters consuming `wrench-loader` outputs.
- Visual exploration through `rumble-canvas` integration.
- Durable memory submission workflow to `gear-memory`.
- Collaborative workspace mode if the shared Rumble identity/membership model is accepted.

## Dependencies on Bolt/Wrench/Gear

- **Bolt / `cos-matic`:** receives planning-only handoff requests; owns execution and gates.
- **Wrench Loader:** extracts and normalizes external content; `rumble-note` references or receives extracted content but does not own parsing pipelines.
- **Gear Memory:** owns durable source, provenance, memory-entry, and possibly local search/index substrate.
- **Gear event/provenance primitives:** candidates for audit and traceability of handoffs.

## Risks

- Becoming a generic note app with no agentic differentiation.
- Absorbing ingestion and duplicating `wrench-loader`.
- Absorbing memory and duplicating `gear-memory`.
- Turning backlinks into decorative graph features rather than handoff context.
- Over-designing sync before local-first value is proven.
- Leaking private notes into harness context without explicit user action.
