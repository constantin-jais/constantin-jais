# Product Charter — rumble-lm

Status: Drafting.

## Mission

`rumble-lm` is a sovereign learning and facilitation platform for source-grounded sessions, live activities, group engagement, and collective understanding.

The P0 product slice is defined in [`14-source-grounded-product-slice.md`](./14-source-grounded-product-slice.md): a synchronous collective session flow with source import, facilitator-approved activities, citation-gated generation, participant responses, aggregate synthesis, and audience-scoped export.

Initial implementation-facing contracts are defined in [`15-contracts-v0.1.md`](./15-contracts-v0.1.md). Owner review is prepared in [`16-contract-review-pack.md`](./16-contract-review-pack.md), and the allowed stub-first implementation path is defined in [`17-p0-stub-implementation-plan.md`](./17-p0-stub-implementation-plan.md).

## Initial Scope To Specify

- Facilitator, participant, learner, and admin roles.
- Source ingestion and grounding flow.
- Session lifecycle.
- Activity types: quiz, prompt, summary, discussion, vote, reflection.
- Live participation model.
- Citation and grounding verification.
- Learning outcomes and analytics.
- Export and follow-up artifacts.

## Main Boundary

`rumble-lm` must not become a generic chatbot. It is judged by learning outcomes, grounding, engagement, and facilitation reliability.

It also must not become a full LMS, durable ingestion engine, durable memory system, generation orchestrator, artifact store, or product-specific authorization-token subsystem. It consumes Wrench Loader, Gear Memory/Gear artifact capabilities, Bolt, and Biscuit for those responsibilities.

## P0 Contract Summary

| Product responsibility | Consumed shared capability |
| --- | --- |
| Session UX, live activities, citation review, participant workflow, synthesis validation | Rumble LM |
| Canonical source extraction | Wrench Loader |
| Source refs, chunks, provenance, retrieval handles | Gear Memory |
| Draft generation orchestration and gates | Bolt |
| Delegated operation rights | Biscuit shared authorization contract |
| Export artifact refs, manifests, checksums | Gear artifact/depot capability |

## Sovereignty Filters

- No mandatory US SaaS dependency.
- No blocking-license dependency in the production stack.
- No opaque storage for source truth, responses, summaries, exports, or audit evidence.
- No raw participant responses, source excerpts, bearer tokens, or secrets in logs.
- Starred repositories are design benchmarks and risk comparators, not a backlog of dependencies.
