# Agent Conversational Memory — Design Spec (Bolt policy / Gear storage)

- Status: **Accepted 2026-07-17 (R2)** — R1 applied the three-lens adversarial review; R2 applied the delegated challenge pass on R1's new material and was ratified under Constantin's challenge-then-continue instruction (decision-log). Code stays gated on the monorepo package locks (§8).
- Date: 2026-07-17 (initial); R1 same day
- Provenance: increment N4 of `tencentdb-agent-memory-decomposition.md`; Q1–Q4 arbitrated 2026-07-17; contract posture (option A, reference-only) arbitrated 2026-07-17 (decision-log).
- ADR citations in this document are **control-plane ADRs** (`specs/shared/adrs/`, series 0001–0046) unless explicitly marked as monorepo ADRs (`libre-ai/libre-ai/docs/adr/`, a distinct series that also starts at 0001).

## 1. Purpose and scope

Give agent-factory agents durable, provenance-complete memory of their own work sessions: what was decided, what evidence was produced, what facts were established — recallable across sessions without replaying transcripts.

**Scope: the local, single-user forge.** This design covers agent memory on the developer's machine — one human, local processes, no tenants. Hosted agent execution (a future Missions-style runtime executing agents server-side) is **explicitly out of scope**: the moment agent memory lives server-side it becomes platform data — mandatory opaque tenant, normative retention, 35-day backup expiry — governed by the monorepo's `DATA-LIFECYCLE.md` and monorepo ADR-0002, and it requires its own design pass.

Justification boundary (stated precisely, because the loose version does not hold): this work proceeds not because session data "belongs to the developer" — captured tool output routinely contains third-party content (web pages, licensed code, data read by tools) — but because it is **local, single-user, and never consolidated into person-profiles**. The Q4 standing constraint is untouched.

In scope: session-scoped capture (L0), fact extraction (L1), recall, compaction of live context, erasure, retention. Out of scope (explicitly): user profiling and any L3-class persona consolidation (Q4), L2 scene blocks (rumble-note territory, need-captured in the decomposition), product-facing memory (rumble-note/feed-mind are later consumers per Q1), cross-context memory of any kind (bounded-context rule; mirrors the E14/T-cross quarantines), networked memory services (no gateway; local process boundaries only).

## 2. Layer split (normative)

This is the structural decision of the 2026-07-17 arbitration; violating it reproduces the reference plugin's monolith.

| Concern                                                                                        | Owner                          | Never owned by |
| ---------------------------------------------------------------------------------------------- | ------------------------------ | -------------- |
| What to capture, when to recall, budgets                                                       | agent-factory (engine/harness) | gear           |
| Extraction policy: when L1 runs, prompts/model choice, quality gate thresholds                 | agent-factory                  | gear           |
| Extraction result storage: fact records, dedup lineage                                         | `context-kit/memory`           | agent-factory  |
| Compaction thresholds and canvas semantics                                                     | agent-factory                  | gear           |
| Definition and exposure of the memory tool surface (which tools agents get, with what budgets) | agent-factory                  | gear           |
| Query/retrieval mechanics behind those tools                                                   | `context-kit/memory`           | agent-factory  |
| Schema, storage, indexing                                                                      | `context-kit/memory`           | agent-factory  |
| Provenance chain, hashes, timestamps                                                           | `context-kit/memory`           | agent-factory  |
| Erasure, retention, and tombstone propagation                                                  | `context-kit/memory`           | agent-factory  |

Bolt never stores; Gear never decides. The interface between the two is `gear.memory` contract shapes plus the existing gear-memory CLI/store surface — no private side-channel.

## 3. Threat model and security requirements

Absent from R0; binding from R1 on. Trust boundaries:

- **Trusted**: the harness process, the local store files, the capture/recall policy code.
- **Untrusted: everything captured.** Tool outputs, web content, file contents read in session can contain secrets or adversarial instructions — untrusted at capture time, and **still untrusted when recalled later**. Durable storage does not launder trust.

Requirements, binding on C1/C2:

- **S1 — Secret scanning at the capture boundary.** Every candidate L0 entry passes the same class of scanning gear-loader already runs at its ingestion boundary (pattern regexes for keys/tokens/credentials + Shannon-entropy escalation to Critical). Critical findings block the capture or redact the span; the scan outcome is recorded in the entry's provenance. A secret must never become a durable memory.
- **S2 — Recall returns untrusted context.** Recalled content is delivered inside an explicit untrusted-context envelope (guard markers, escaped content, `trusted: false` tagging — the odysseus E22 doctrine, which already names memories among the surfaces to wrap). Memory is evidence to consult, never instructions to follow. The envelope is applied by the recall surface itself, not left to caller discipline — this is the defense against persisted prompt injection (hostile content captured once, replayed into every future session). The envelope covers **every payload egress**: recall excerpts and drill-down reads of full content alike.
- **S3 — No cross-context recall.** One store per workspace; no query surface reaches across workspaces or contexts.
- **S4 — Local process boundaries only.** No network listener, no gateway; the OS user boundary is the auth boundary.

## 4. Storage design (gear side)

### 4.1 Layers

- **L0 — session entries**: append-only records of agent-session events worth remembering (decisions, evidence references, tool-result digests). Not a full transcript mirror: capture policy (bolt) selects entries; storage (gear) never filters. Traceability is therefore complete **over what was captured** — selectivity bounds the evidence, and the capture policy in force is itself recorded (§5.1) so that boundary stays auditable.
- **L1 — extracted facts**: atomic, typed statements derived from one or more L0 entries, each carrying source-span references to the L0 rows that ground it, plus dedup lineage (which prior fact a new one supersedes or duplicates).

No L2/L3 in this design: the reference project's L2 (scenes) is a rumble-note concern; its L3 (personas) is Q4-quarantined.

### 4.2 Engine, locality, and data classes

- **Own file: `./.gear-memory/sessions.sqlite3`** — deliberately **separate** from the code-map store (`db.sqlite3`). Code maps are _derived and regenerable_ (losing them costs a re-index); conversational memory is _primary and non-regenerable_ (losing it is final). The two classes must not share a lifecycle, a backup posture, or a deletion regime. Note: the 2026-07-02 rung-commutativity decision concerns index rungs over one corpus within one engine; it is not a license to mix data families in one file — R0 over-read it, R1 corrects that.
- WAL, per-workspace, git-ignored, explicit `--db` override, no hidden global state.
- **Backup (required, because primary data)**: scheduled bundle export to a destination outside the workspace, cadence and destination as recorded configuration. This depends on the gear-memory P2 export/import CLI, which is **planned, not built** — C1 cannot claim completion without a working export path. **Exports are retention-bounded** (default: expire within 35 days, mirroring the monorepo backup doctrine), because exported bundles are the one place erased content survives — see §4.4.
- **Multi-session concurrency**: several agent sessions may run on one workspace in parallel. WAL serializes writers; the design requirement is _attribution_: every L0/L1 row carries its `session_id`, sequence numbers are per-session, and provenance never interleaves across sessions.
- Retrieval starts at the rungs that exist: catalog queries now, FTS5 when rung 2 lands — as **external-content FTS directly over the payload tables**, no duplicate corpus. What generalizes from repo-memory ADR-0003's sidecar is the transactional discipline (same file, same transaction, same tombstones), not a second copy of the text. Vector is untouched by this spec (ladder rung 5; Stage-4 requirements of `../gear/04-gear-memory-substrate.md` apply if it ever becomes relevant).

### 4.3 Contracts: reference-only (option A, arbitrated 2026-07-17)

The established invariant — **"the contracts carry no text"** (repo-memory ADR-0003, the fact that shaped the whole FTS5 rung) — survives conversational memory:

- `ConversationEntry` (candidate v0.2 shape): session id, sequence, timestamp, entry kind (decision | evidence-ref | tool-digest | note), **content hash, content length, payload reference — no content field.**
- **Hash semantics**: content hashes are computed over the **stored** payload — post-S1-redaction when redaction occurred — so hashes always verify against what the store actually holds; the redaction itself is flagged in the entry's provenance.
- The text itself lives in **store-internal payload tables** (the `search_documents` sidecar pattern generalized to primary payload): same file, same transaction, same tombstones. The ingestion API transports text; contract objects never carry it.
- `MemoryEntry` (extended): fact type, source-span refs into `ConversationEntry` rows, dedup lineage (supersedes / duplicates). `ProvenanceRecord` and `EventLogEntry` reused as-is.
- Consequences: bundles/exports carry payload only when explicitly requested (and payload re-passes the S1 scan at export time); every contract consumer stays payload-free; erasure is provable at exactly one layer.
- Per the 2026-07-02 rule, these shapes open contracts v0.2 only when agent-factory actually emits them — declared producer intent, not a frozen schema.
- Downward-traceability invariant: every L1 fact resolves to its L0 evidence in one join; every recall result returns references and hashes, never floating prose.

### 4.4 Erasure — byte-level, not query-level

ADR 0006 tombstone doctrine applied to conversations, with the acceptance strengthened over R0:

- Deleting an L0 entry (or a whole session) tombstones it, invalidates every L1 fact whose source spans reference it, and deletes the payload rows in the same transaction; invalidated facts leave auditable tombstones and disappear from all retrieval surfaces.
- The store runs with `PRAGMA secure_delete=ON`; an erasure completes with a WAL checkpoint and a (batchable) `VACUUM`, so freed pages do not retain plaintext.
- **Exports are part of the erasure horizon.** Erased content survives in previously exported bundles until those expire (§4.2 retention bound) or are explicitly destroyed. The erasure command therefore reports which known exports still contain the erased chain, and full erasure is only complete when the last of them is gone. Store-and-WAL erasure is immediate; the export horizon is bounded by the export retention window.
- **Acceptance**: after erasure + compaction, (a) no query surface returns anything from the erased chain, (b) the erased plaintext is absent from the store and WAL file bytes — verified by fixture: insert a marker text, erase, byte-scan the files — and (c) the erasure report lists the exports still holding the chain, with their expiry dates.

### 4.5 Retention — an executable maximum

- L0 entries expire at a configurable maximum age (default proposal: 180 days). Default rule for derived facts: **L1 facts expire with their L0 evidence** — no fact outlives its evidence, so traceability never degrades into unsupported claims. (Alternative — keep the fact, mark evidence-expired — is a C1 decision if dogfooding shows the default too aggressive.)
- Purge is an explicit, idempotent CLI command suitable for scheduling; it uses the §4.4 erasure mechanics — retention IS erasure on a timer, never a second deletion path.
- Doctrine alignment: "retention is an executable maximum, not a promise" (monorepo `DATA-LIFECYCLE.md`) — adopted here even though this store is local.

## 5. Policy design (bolt side)

### 5.1 Capture

Explicit, evidence-oriented, selective: decisions taken, refusals and their reasons, evidence artifacts produced, tool-result digests above a size threshold. Every candidate entry passes the S1 secret scan before persistence. Cadence and thresholds are configuration with recorded defaults, not constants — and the capture policy in force is itself recorded as evidence, so the selectivity boundary of §4.1 stays auditable. No ambient full-transcript recording: capture is a deliberate act of the harness, inspectable in the session log.

### 5.2 Extraction (L1)

Fact extraction is an agent-side derivation: prompts, cadence, and model choice are bolt policy; the resulting fact records and their dedup lineage are gear storage (§2). It is LLM-driven and therefore non-deterministic — the T3 caveat of the decomposition, made binding here: C2's acceptance includes an explicit **quality gate** (measured dedup rate, contradiction checks against existing facts, spot-check fixtures) before extracted facts are trusted by recall. Extraction failures and low-confidence facts are recorded as such, never silently dropped. Concurrent sessions may extract in parallel; dedup lineage resolves collisions after the fact rather than requiring cross-session coordination.

### 5.3 Recall

Recall is budgeted (max entries, max tokens) and always returns references + excerpts inside the S2 untrusted-context envelope, letting the agent decide what to drill into. The two-tool restraint of the reference project (memory search + conversation search, T12) is the right surface size.

### 5.4 Compaction invariants (T2/T10/T11)

Whatever the concrete mechanism (Mermaid canvas or otherwise), these four invariants are the requirement:

1. **Externalize before summarizing** — full content is written to an addressable location before any summary replaces it in context.
2. **Summaries carry addresses** — every summarized item keeps a resolvable identifier back to the externalized content.
3. **One live summary slot** — exactly one summary artifact in the live context, replaced in place, never accumulated.
4. **Deletion leaves a pointer** — aggressively removed context is replaced by its summary artifact, so nothing becomes unreachable.

Two-tier thresholds (mild replace / aggressive delete) as in T11, both configurable.

## 6. Evaluation (dogfooding)

Two-conditions protocol with the E21 **controls**, not just its shape: same task set run with and without memory; **blind grading against recorded ground truth; randomized presentation order; judge-bias controls (multiple passes, cross-family judge preferred); zeros kept as findings**; dual accounting (task quality **and** tokens consumed — memory value is quality at bounded cost). Dimensions from T17: fact-recall correctness across sessions, wide-context retrieval. One-shot benchmark per the 2026-07-02 decision; the wrench Eval Lab remains demand-gated.

## 7. Increment ladder (each gated, in order)

1. **C1 — gear storage**: `sessions.sqlite3` store behind the existing `Store` trait; contract fixtures; S1 scanning at ingestion; erasure acceptance including the §4.4 byte-level fixture and export report; retention purge command; export path with retention bound (P2 dependency). Opens `gear.memory` v0.2 with the §4.3 shapes as actually emitted. L0/L1 shapes are both stored from C1 on; L1 rows only appear once C2's extractor emits them.
2. **C2 — bolt capture/extraction/recall**: harness hooks producing C1 entries; the §5.2 extraction pipeline with its quality gate; recall through the S2 envelope; capture policy recorded as evidence.
3. **C3 — compaction**: the §5.4 invariants implemented over live context, with the §6 benchmark as its acceptance.

C1 has no dependency on C2/C3 semantics beyond §4.3; C2/C3 must not start before C1's contract shapes are real (no abstraction without a producer).

## 8. Topology note (Big Bang, discovered 2026-07-17)

The libre-ai org was frozen into the `libre-ai/libre-ai` monorepo on 2026-07-16 (Big Bang: global freeze, reconstruction, single cutover; no git history imported). In this spec, "agent-factory" and "context-kit/memory" therefore name **layer roles, not live repos**: per the monorepo `REPOSITORY-MAP`, agent-factory becomes a future orchestrator/harness package behind its own dedicated Specification Lock, and context-kit is archive-only — no context crate exists without a newly approved package. The C1–C3 increments land in the monorepo under its work-package discipline once those packages open; this spec is a design input to that future lock, not a bypass of it.

Two precisions added in R1:

- **This is the memory chapter of a composite lock, not the lock.** The monorepo blocks orchestrator integration until "a separate human-approved execution-plan, control-protocol and agent-harness Specification Lock exists" (`work-packages.v1.json`, global constraints). This spec feeds the _memory_ slice of that lock and deliberately does not cover execution plans, control protocol, harness mechanics, or budgets.
- When that lock opens, this content maps onto the monorepo's `SPECIFICATION-STANDARD.md` sections; ADR citations here are control-plane series (see header note) to avoid collision with the monorepo's own ADR series.

The §2 layer split is unaffected — it is exactly the boundary the monorepo map preserves (Bolt orchestration vs Gear context/storage).

## 9. Alignment

- **Layer model (ADR 0033)** and Q1/Q3 arbitration: policy in bolt, storage in gear, enrichment of existing repos, extraction only via the ADR 0022 five-condition rule.
- **ADR 0006**: ladder order untouched; single-engine posture kept _per data family_ (§4.2); tombstones extended to conversational chains with byte-level acceptance.
- **Repo-memory ADR-0003**: the no-text-in-contracts invariant and the sidecar pattern are generalized, not overridden (§4.3).
- **Security posture**: S1 extends the gear-loader ingestion-boundary precedent (regex + entropy scanning); S2 applies the odysseus E22 untrusted-context doctrine to recall.
- **Q4 standing constraint**: no persona consolidation anywhere in this design; the justification is locality + no-consolidation (§1), not data ownership.
- **Bounded-context rule**: one store per workspace; no cross-workspace or cross-context recall surface.

## 10. Review record

- 2026-07-17 — three-lens adversarial review (control-plane coherence; security/RGPD/design; Big Bang fit), findings verified against sources before acceptance. Confirmed: 2 blocking (text-in-contracts contradiction; absent security section), 5 major (data-class mixing/backup, query-level-only erasure, no retention, composite-lock framing, local/hosted boundary), 4 minor. All applied in R1. Refuted skeptic claims (Sessions-row conflation with the product app; gating-power misread; gear/bolt vocabulary already covered by §8) recorded in session, deliberately not in this spec. Contract posture arbitrated to **option A** (reference-only) by Constantin.
- 2026-07-17 — R2, delegated challenge pass on R1's new material: confirmed 2 major (erasure acceptance ignored exported bundles — the R1 backup and erasure fixes collided; L1 extraction had no owner, no quality gate, no increment) and 3 minor (hash-of-redacted-payload semantics, FTS duplicate-corpus wording, S2 scope on drill-down). Applied in R2; spec ratified under the challenge-then-continue instruction (decision-log). Code remains gated on the monorepo package locks (§8).

## 11. Sources

- `tencentdb-agent-memory-decomposition.md` — T1/T2/T10/T11/T12/T17 rows and deep dives; sovereignty audit.
- Decision-log rows: 2026-07-17 (arbitration Q1–Q3; Q4 confirmation + increments; option A + R1), 2026-07-02 (contracts v0.2 producer rule, rung commutativity, one-shot evaluation), 2026-06-30 (progressive indexing ladder).
- `../gear/04-gear-memory-substrate.md` — substrate constraints this design inherits.
- Repo memory (archived legacy, local checkout `libre-ai/context-kit/memory`): `docs/adr/0003` (FTS5 sidecar, no-text-in-contracts), P0 contracts, SqliteStore.
- gear-loader `SECURITY.md` (archived legacy, local checkout `libre-ai/context-kit/loader`): secret/PII scanning classes reused by S1.
- `odysseus-decomposition.md` — E22 untrusted-context envelope doctrine (S2).
- Monorepo (`libre-ai/libre-ai`): `docs/transformation/REPOSITORY-MAP.md`, `docs/transformation/work-packages.v1.json` (composite-lock constraint), `docs/specifications/DATA-LIFECYCLE.md` + monorepo ADR-0002 (hosted-execution regime, out of scope here).
