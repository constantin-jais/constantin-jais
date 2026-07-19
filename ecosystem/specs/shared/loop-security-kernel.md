# Loop-security kernel — input for the orchestrator Specification Lock

- Status: Proposed (control-plane input, 2026-07-19). Not doctrine until the monorepo consumes it under its Specification Lock and the owner ratifies.
- Chapter of the lock: authorization + control protocol + harness
- Consumes: `agent-conversational-memory-design.md` (memory S1–S4), `odysseus-decomposition.md` E22/E23/E10
- Answers: monorepo invariant I-18 (ADR-0009 §6) — the loop-security kernel that gates wave 3

## Why this exists

The 2026-07-19 constellation vision ratified self-feeding agent loops as the project's product zero. A loop that feeds on its own operational output is also a loop that can poison itself: operational data is untrusted content, and the agents that improve the tools are the agents those tools govern. ADR-0009 §6 names the kernel; the loop-security adversarial review sized the threats (agent identity absent from every lock; ops data never classified; layer-3 mutations unprotected). This document specifies the kernel so the orchestrator lock can enforce it, not merely state it.

## K1 — Agent identity (the absent lock)

The G1 identity lock (`IDENTITY-AUTHORIZATION.md`) covers humans and sessions, never agent fleets. The kernel adds an agent identity taxonomy, to be expressed as locked Biscuit facts:

- `agent_fleet(agent_id, fleet)` — every agent belongs to exactly one fleet (e.g. forge, product-ops).
- `mission_agent(agent_id, mission_id)` — an agent operates within one mission; cross-mission operation is denied by an authorizer `check if`.
- `capability_scope(agent_id, capability_set)` — explicit permission vector (which tools, which write paths, never CI/gates by default).
- Revocation is **per `agent_id`**, not per token: a revoked agent issues no new tokens; the revocation store fails closed (unavailable ⇒ deny), consistent with the G1 Biscuit doctrine.

## K2 — Data reliability classification

Every payload carries `reliability ∈ {authoritative, derived, operational}` at capture:

- `authoritative` — source-controlled (signed Git commits, Biscuit-verified decisions, the invariants register).
- `derived` — computed from authoritative (extracted facts, plan decisions), tracing to its authoritative spans.
- `operational` — tool outputs, API and web responses, git logs. **Never authoritative.**

Invariant: no write to a source of truth (doctrine, gates, revocation list, permission vocabulary, contracts) may be justified by `operational` data alone. Operational data enters plans as evidence, never as directive (facts are never commands).

## K3 — Envelope integrity

E22 gives the untrusted-context envelope (escape + tag + label). The kernel adds integrity: every recalled memory payload carries an envelope signature (Ed25519 or HMAC) verifiable offline, so a stripped or altered envelope is detectable. A surface that re-serializes recalled data re-applies the envelope; it is never left to caller discipline.

## K4 — Layer-3 and guardrail mutations

Writes to layer-3 bricks (envelope patterns, memory schema, provenance contracts, proof format) and to guardrails (CI workflows, the invariants register, the revocation list) require, in order: human review, a signature attesting the decision-log entry that approved them, and a bounded rollback point. **No auto-merge on these paths** — enforced by CODEOWNERS on the sensitive lane plus the monorepo's existing doctrine-governance gate. Tool-state retrieval that feeds such a mutation uses DNS-pinned transport (E10) and a timestamped signature; a DNS/data mismatch aborts.

## K5 — Immutable register in production

The invariants register is mutable only by reviewed pull request; no loop mutates it in production. This is the structural guarantee behind "no loop modifies its own guardrails" — the closing invariant of the self-feeding loop.

## Enforcement boundary

K1–K5 are the **entry gate of wave 3** (EXECUTION-SEQUENCING.md): the orchestrator lock cannot open real agent execution until they are specified in the monorepo and locked. Dogfooding-first applies: the forge itself is the first system these controls govern, and its evidence of doing so is published (I-20).
