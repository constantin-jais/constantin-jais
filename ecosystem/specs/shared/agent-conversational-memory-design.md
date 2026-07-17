# Agent Conversational Memory — Design Spec (Bolt policy / Gear storage)

- Status: Proposed (review of this spec gates any code increment)
- Date: 2026-07-17
- Provenance: increment N4 of `tencentdb-agent-memory-decomposition.md`; Q1–Q4 arbitrated 2026-07-17 (decision-log).

## 1. Purpose and scope

Give agent-factory agents durable, provenance-complete memory of their own work sessions: what was decided, what evidence was produced, what facts were established — recallable across sessions without replaying transcripts.

In scope: session-scoped capture (L0), fact extraction (L1), recall, compaction of live context, erasure. Out of scope (explicitly): user profiling and any L3-class persona consolidation (Q4 standing constraint), L2 scene blocks (rumble-note territory, need-captured in its ROADMAP), product-facing memory for rumble-note/feed-mind (they are later consumers per Q1, priority is agent-factory), cross-context memory of any kind (bounded-context rule; mirrors the E14/T-cross quarantines), networked memory services (no gateway; local process boundaries only).

## 2. Layer split (normative)

This is the structural decision of the 2026-07-17 arbitration; violating it reproduces the reference plugin's monolith.

| Concern                                        | Owner                          | Never owned by |
| ---------------------------------------------- | ------------------------------ | -------------- |
| What to capture, when to recall, budgets       | agent-factory (engine/harness) | gear           |
| Compaction thresholds and canvas semantics     | agent-factory                  | gear           |
| Memory tool surface exposed to agents          | agent-factory                  | gear           |
| Schema, storage, indexing, retrieval mechanics | `context-kit/memory`           | agent-factory  |
| Provenance chain, hashes, timestamps           | `context-kit/memory`           | agent-factory  |
| Erasure and tombstone propagation              | `context-kit/memory`           | agent-factory  |

Bolt never stores; Gear never decides. The interface between the two is `gear.memory` contract shapes plus the existing gear-memory CLI/store surface — no private side-channel.

## 3. Storage design (gear side)

### 3.1 Layers

- **L0 — session entries**: append-only records of agent-session events worth remembering (decisions, evidence references, tool-result digests). Not a full transcript mirror: capture policy (bolt) selects entries; storage (gear) never filters.
- **L1 — extracted facts**: atomic, typed statements derived from one or more L0 entries, each carrying source-span references to the L0 rows that ground it, plus dedup lineage (which prior fact a new one supersedes or duplicates).

No L2/L3 in this design. The reference project's L2 (scenes) and L3 (personas) are respectively a rumble-note concern and a Q4-quarantined concern.

### 3.2 Engine and locality

Same posture as the existing `SqliteStore`: one SQLite file, WAL, per-workspace, git-ignored (`./.gear-memory/db.sqlite3` — same file as the code-map store; conversational tables are additional tables in the same single inspectable engine, per the rung-commutativity decision of 2026-07-02). No hidden global cache, explicit `--db` override, bundle export/import inherits the planned P2 mechanics.

Retrieval starts at the rungs that exist: catalog queries now, FTS5 when rung 2 lands. Vector is untouched by this spec (ladder rung 5, `04-gear-memory-substrate.md` Stage 4 requirements apply if it ever becomes relevant).

### 3.3 Candidate `gear.memory` v0.2 shapes

Per the 2026-07-02 rule, these open contracts v0.2 only when agent-factory actually emits them; listed here as the producer's declared intent, not a frozen schema:

- `ConversationEntry` (new): session id, sequence, timestamp, entry kind (decision | evidence-ref | tool-digest | note), content, content hash.
- `MemoryEntry` (extended): fact type, source-span refs into `ConversationEntry` rows, dedup lineage (supersedes / duplicates).
- `ProvenanceRecord`, `EventLogEntry` (reused as-is).

Downward-traceability invariant: every L1 fact resolves to its L0 evidence in one join; every recall result returns references and hashes, never floating prose. This is the T1 pattern and it is non-negotiable — it is what makes erasure provable.

### 3.4 Erasure

ADR 0006 tombstone doctrine applied to conversations: deleting an L0 entry (or a whole session) tombstones it and invalidates every L1 fact whose source spans reference it; invalidated facts leave auditable tombstones and disappear from all retrieval surfaces. Acceptance: after erasure, no query surface (catalog, FTS when present) returns searchable payload from the erased chain.

## 4. Policy design (bolt side)

### 4.1 Capture

Explicit, evidence-oriented, selective: decisions taken, refusals and their reasons, evidence artifacts produced, tool-result digests above a size threshold. Cadence and thresholds are configuration with recorded defaults, not constants. No ambient full-transcript recording — capture is a deliberate act of the harness, inspectable in the session log.

### 4.2 Recall

Recall is budgeted (max entries, max tokens) and always returns references + excerpts, letting the agent decide what to drill into — the two-tool restraint of the reference project (memory search + conversation search, T12) is the right surface size.

### 4.3 Compaction invariants (T2/T10/T11)

Whatever the concrete mechanism (Mermaid canvas or otherwise), these four invariants are the requirement:

1. **Externalize before summarizing** — full content is written to an addressable location before any summary replaces it in context.
2. **Summaries carry addresses** — every summarized item keeps a resolvable identifier back to the externalized content.
3. **One live summary slot** — exactly one summary artifact in the live context, replaced in place, never accumulated.
4. **Deletion leaves a pointer** — aggressively removed context is replaced by its summary artifact, so nothing becomes unreachable.

Two-tier thresholds (mild replace / aggressive delete) as in T11, both configurable.

## 5. Evaluation (dogfooding)

Two-conditions protocol (E21 skeleton) with the T17 conversational dimensions: same task set run with and without memory; measured on fact-recall correctness across sessions, wide-context retrieval, and dual accounting (task quality **and** tokens consumed — memory value is quality at bounded cost). One-shot benchmark per the 2026-07-02 decision; wrench-inspect Eval Lab remains demand-gated. Zeros are findings.

## 6. Increment ladder (each gated, in order)

1. **C1 — gear storage**: conversational tables behind the existing `Store` trait, contract fixtures, erasure acceptance tests. Opens `gear.memory` v0.2 with the §3.3 shapes as actually emitted.
2. **C2 — bolt capture/recall**: harness hooks producing C1 entries and consuming recall, with capture policy recorded as evidence.
3. **C3 — compaction**: the §4.3 invariants implemented over live context, with the E21+T17 benchmark as its acceptance.

C1 has no dependency on C2/C3 semantics beyond §3.3; C2/C3 must not start before C1's contract shapes are real (no abstraction without a producer).

## 7. Alignment

- **Layer model (ADR 0033)** and Q1/Q3 arbitration: policy in bolt, storage in gear, enrichment of existing repos, extraction only via the ADR 0022 five-condition rule.
- **ADR 0006**: ladder order untouched; single-engine posture extended, not forked; tombstones extended to conversational chains.
- **Q4 standing constraint**: no persona consolidation anywhere in this design; agent session memory is the developer's own local data, which is precisely why it can proceed while persona-adjacent product work stays constrained.
- **Bounded-context rule**: one store per workspace; no cross-workspace or cross-context recall surface.

## 8. Sources

- `tencentdb-agent-memory-decomposition.md` — T1/T2/T10/T11/T12/T17 rows and deep dives; sovereignty audit.
- Decision-log 2026-07-17 rows (arbitration Q1–Q3; Q4 confirmation + increments), 2026-07-02 rows (contracts v0.2 producer rule, rung commutativity, one-shot evaluation), 2026-06-30 (progressive indexing ladder).
- `specs/gear/04-gear-memory-substrate.md` — substrate constraints this design inherits.
