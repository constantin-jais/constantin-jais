# ADR 0029 — rumble-ai-practices / rumble-lm boundary

Status: Proposed
Date: 2026-07-02
Decision owner: Constantin (product portfolio)
Related: D5 (rumble-ai-practices officialized); `rumble-ai-practices/docs/product-boundaries.md`

## Context

`rumble-ai-practices` was officialized as a Rumble product (D5). Its own `product-boundaries.md` admits a partial overlap with `rumble-lm`: both can run live, source-grounded learning sessions. The product self-documents that a separate repository is justified **only if** its content governance, media-bias audits, and pedagogical scoring genuinely differ from a generic live session — otherwise it should be "a content pack + specialized module for rumble-lm", not a full product.

That test was never resolved with product evidence. Officializing the product (D5) makes the ambiguity a governance liability: a fantom overlap between two Rumble products, both `Candidate`/early, competing for the same "live session" surface.

## Decision

1. **Draw the boundary by capability, not by repo convenience:**
   - `rumble-lm` **owns the live-session runtime**: session engine, presence, WebSocket participation, citation-gated grounding, aggregate signals, export. Any live session — generic or AI-practices — runs on lm's engine.
   - `rumble-ai-practices` **owns the domain content and its governance**: the sourced question corpus (NIST AI RMF, RGPD, EU AI Act, OWASP LLM Top 10, C2PA, ISO 42001, ANSSI), the media-bias audit rules, the pedagogical scoring model, and the review/approval workflow specific to this corpus. It does **not** re-implement a session runtime.

2. **Consumption model:** `rumble-ai-practices` is a **content pack + specialized scoring/audit module consumed by `rumble-lm`'s runtime**, not a parallel live-session product. It may keep a separate repo for its content governance and audit tooling, but the runtime dependency direction is one-way (ai-practices → lm), never a fork of lm's engine.

3. **Separate-repo justification is time-boxed to evidence:** the separate repo stands only while ai-practices produces domain value lm cannot (corpus governance, bias audit, scoring). If, at its next maturity review, ai-practices has not shipped approved corpus content or a distinct audit/scoring capability, it collapses into `rumble-lm/content/ai-practices` and the repo is archived.

## Consequences

- ai-practices does not build a session engine, presence, or WebSocket layer — those are lm's. This removes the largest overlap and the largest duplication risk.
- The corpus and audit rules become the product's real asset; the current blocker (0/30 questions approved) is the real maturity gate, not the runtime.
- The `docs/` language singularity (100% French) is acceptable for a French-audience training product, but the shared boundary and its contracts are documented in English here for ecosystem consistency.
- lm's contracts (session, activity, citation) must be consumable by an external content pack; if they are not yet, that gap is logged against lm, not ai-practices.

## Status note

Proposed: the "content pack consumed by lm" framing vs "autonomous product" is Constantin's call (D5 left it open). Merging as Accepted ratifies the content-pack boundary; amending before merge to keep ai-practices as a fully autonomous live-session product is the fork — but that path must then answer why it duplicates lm's runtime.
