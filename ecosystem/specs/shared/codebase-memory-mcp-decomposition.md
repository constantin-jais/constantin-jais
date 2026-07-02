# codebase-memory-mcp — Element Decomposition and Stack Mapping

Date: 2026-07-02
Source project: `DeusData/codebase-memory-mcp` v0.8.1 (MIT) — <https://github.com/DeusData/codebase-memory-mcp>
Decision: **inspiration only** — no installation, no runtime dependency, no code reuse. See the 2026-07-02 entry in `decision-log.md`.
Scope: personal forge ecosystem only. Professional workspaces are out of scope.

## Why this document

`codebase-memory-mcp` is a mature code-intelligence MCP server (single static C binary, persistent SQLite knowledge graph, 24k stars, peer-describable design in [arXiv 2603.27277](https://arxiv.org/abs/2603.27277)). Several of its elements land exactly on declared ecosystem territory (`gear-memory` code maps and indexing, Wrench parsing, Bolt impact analysis, Rumble Note visualization). Per ADR `adrs/0022-starred-repos-strengthen-existing-repos.md`, external projects strengthen existing repositories; this document decomposes the tool element by element so each concept lands on the right layer — or is explicitly rejected — instead of being adopted wholesale.

All verdicts below are **proposed** and gate any implementation increment: review and validation come first.

## Method

Taxonomy reused from `github-stars-stack-audit.md`:

- Disposition: `adopt` (use as-is), `rebuild` (reimplement the concept on our stack), `knowledge` (reference material only), `reject`, `quarantine`.
- Layer: `rumble`, `bolt`, `wrench`, `gear`, `cross-layer`, `outside`.

Since the standing decision is inspiration-only, no element is `adopt`; the useful split is `rebuild` (concept worth reimplementing, with a target increment) vs `knowledge` (worth understanding, no increment) vs `reject`.

## Reference facts (verified 2026-07-02)

- Single static C binary (~88% C), zero runtime dependencies, 100% local, no telemetry; MIT; bundled `nomic-embed-code` weights Apache-2.0. Sovereignty audit: PASS.
- Indexing: tree-sitter across 158 languages; "Hybrid LSP" type resolution for 9 (incl. Rust, Kotlin, TypeScript); six-phase pipeline; Linux kernel indexed in ~4 min on a laptop.
- Storage: one SQLite file, WAL, deferred index creation, in-memory graph buffer flushed in bulk.
- Graph: 12 node labels, 32 edge types (26 intra-repo + 6 cross-repo), confidence scoring on inferred edges.
- Measured value (paper, Table 6): answer quality 0.83 vs 0.92 for a grep/read explorer (90%), 2.1× fewer tool calls, ~10× fewer tokens, sub-ms queries vs 10–30 s exploration.
- Known limits (authors'): static structure only (no runtime/reflection/dynamic dispatch), macro-heavy code is hard, Cypher subset gaps, aggregation caps that silently undercount (200-row / 100k-row ceilings).

## Element map

| #   | Element                                                                                                                                                                                                          | What it is / solves                              | Layer          | Disposition                             | Recommended action                                                                                                                                                                                                                                |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1  | Six-phase ingest pipeline (Structure → Extraction → Resolution → Enrichment → Flush → Post-index), in-memory buffer, bulk INSERT with deferred indexes                                                           | Fast, restartable indexing at kernel scale       | gear           | rebuild (pattern)                       | Reuse the buffer→bulk-flush and deferred-index pattern in the `gear-memory` SQLite ingest path.                                                                                                                                                   |
| E2  | Hybrid LSP type resolution (9 languages)                                                                                                                                                                         | Call-graph precision beyond syntax               | wrench         | knowledge                               | Defer. Parsing is Wrench territory; the harness already exposes an LSP tool in session. Study §3.4 of the paper when Wrench builds `CodeMap` producers.                                                                                           |
| E3  | Tree-sitter parsing, 158 vendored grammars                                                                                                                                                                       | Polyglot syntax extraction                       | wrench         | rebuild (later)                         | Already tracked: stars audit rows `xberg-io/tree-sitter-language-pack` (adopt, wrench) and decision D-2026-06-30 "tree-sitter `CodeMap`" ladder stage. No new action here.                                                                        |
| E4  | Single-file SQLite + WAL store, integrity guards, `PRAGMA` hygiene                                                                                                                                               | Durable, inspectable local graph storage         | gear           | **rebuild (P1)**                        | First `gear-memory` increment: `SQLiteStore` behind the existing `Store` trait. Deep dive below.                                                                                                                                                  |
| E5  | Graph schema: 12 node labels, 32 edge types, confidence on inferred edges                                                                                                                                        | Rich, queryable code model                       | gear           | knowledge → v0.2 candidates             | Gap analysis vs `gear.memory.v0.1` contracts below; no contract change now.                                                                                                                                                                       |
| E6  | Structured queries: `search_graph` (label/name/degree + FTS), `trace_path`/`trace_call_path` (bounded BFS), `get_graph_schema` (stats)                                                                           | Token-cheap structural answers                   | gear           | **rebuild (P1)**                        | Deterministic subset in `gear-memory`: `symbol_search`, `symbol_neighbors`, `trace_bfs`, `stats`.                                                                                                                                                 |
| E7  | `get_code_snippet` by qualified name                                                                                                                                                                             | Precise source retrieval without file dumps      | gear           | **rebuild (P1)**                        | Cheap once symbols carry `SourceRange`; include in the P1 query surface.                                                                                                                                                                          |
| E8  | `query_graph` — read-only openCypher subset                                                                                                                                                                      | Ad-hoc graph queries                             | gear           | knowledge                               | Defer post-P1. Their own caveats (silent undercount at caps, missing syntax) argue for named deterministic queries first.                                                                                                                         |
| E9  | `get_architecture` (languages, packages, routes, hotspots, clusters)                                                                                                                                             | One-call codebase overview                       | gear / bolt    | knowledge                               | Defer; depends on E10 analytics. Revisit once P1 data exists.                                                                                                                                                                                     |
| E10 | Community detection (Louvain → Leiden), complexity/bottleneck metrics                                                                                                                                            | Module boundaries and hotspots from the graph    | gear           | knowledge                               | Defer. Derived analytics, not contract data. Note: deterministic seeding required if ever rebuilt.                                                                                                                                                |
| E11 | `detect_changes` (git diff → affected symbols + risk class) + `FILE_CHANGES_WITH` co-change mining                                                                                                               | Impact analysis for changes                      | bolt           | rebuild (later)                         | Strong fit for Bolt planning gates (cos-matic): map a diff to affected `CodeMap` symbols before planning. Dedicated increment after P1.                                                                                                           |
| E12 | `search_code` (grep-like over indexed files, FTS5)                                                                                                                                                               | Text search inside the index                     | gear           | reject (as tool) / knowledge (as stage) | The harness already greps. But SQLite FTS5 is the natural "full-text" rung of the D-2026-06-30 progressive-indexing ladder — keep as design note, not P1.                                                                                         |
| E13 | Bundled int8 code embeddings + `semantic_query`, `SIMILAR_TO` / `SEMANTICALLY_RELATED` edges                                                                                                                     | Vector recall without API/infra                  | gear           | knowledge                               | Defer to the last ladder rung ("vector search must not become opaque truth"). Sovereignty fine (Apache-2.0, local). Rust candidates when due: `fastembed-rs`/`candle`; benchmark vs `USearch` (already audit-flagged). Note: post-paper addition. |
| E14 | Cross-repo intelligence (`CROSS_HTTP_CALLS`, `CROSS_GRPC_CALLS`, …)                                                                                                                                              | Links between separately indexed projects        | cross-layer    | quarantine (concept)                    | Mirrors the bounded-context contamination risk: cross-context edges must never drive cross-context design. If ever rebuilt, per-context stores with explicit, reviewed link ingestion only.                                                       |
| E15 | `manage_adr` (ADR CRUD as MCP tool)                                                                                                                                                                              | Decision records next to the graph               | outside        | reject                                  | ADRs stay as files in git under review; a runtime mutation tool weakens the audit trail. Keep the idea "ADR referenced from architecture output" as knowledge.                                                                                    |
| E16 | `ingest_traces` (runtime traces validate inferred edges)                                                                                                                                                         | Ground static edges in observed behavior         | bolt           | knowledge                               | Defer. Relevant to future Bolt observability/evidence work; contradicts nothing today.                                                                                                                                                            |
| E17 | Team-shared artifact: `.codebase-memory/graph.db.zst` committed + `.gitattributes` merge policy                                                                                                                  | Clone-and-go warm index                          | gear           | knowledge                               | Boundary per existing decisions: `gear-memory` may export/import bundles; artifact custody (checksums, retention, distribution) is `gear-depot`. No increment now.                                                                                |
| E18 | Auto-index on git changes + agent SessionStart hooks                                                                                                                                                             | Always-fresh index                               | bolt / harness | knowledge                               | Defer; couples to E11. Explicit re-index beats hidden daemons for now (locality, inspectability).                                                                                                                                                 |
| E19 | Interactive graph visualization UI (localhost httpd, 3D graph)                                                                                                                                                   | Human exploration of the knowledge graph         | rumble         | rebuild (need captured)                 | Captured as a `rumble-note` need: knowledge-graph/mapping-point visualization over notes, code maps, and linked context. See `Rumble-Note` `ROADMAP.md`. No implementation here.                                                                  |
| E20 | Distribution posture: static binary, SLSA 3, cosign, VirusTotal, `THIRD_PARTY_NOTICES`, `install --plan` receipts, MCP Registry listing                                                                          | Verifiable supply chain for a local tool         | gear           | knowledge                               | Feed `gear-cable`/`gear-depot` release-floor specs (checksums/signature planning already in their scope). Machine-readable install receipts are a pattern worth keeping.                                                                          |
| E21 | Evaluation method: language benchmark + 159-language evaluation plan (D1–D5 dimensions per Sillito et al., blind 3-pass LLM judge, dual token metrics, zeros-kept edge histograms, symmetric question authoring) | Honest measurement of graph vs plain exploration | wrench         | **rebuild (method)**                    | High value for `wrench-inspect` Eval Lab and as the `gear-memory` dogfooding benchmark: same-questions/two-conditions protocol, zeros as findings, judge bias controls. Deep dive below.                                                          |
| E22 | Security engineering internals: SQLite authorizer blocking `ATTACH`/`DETACH`, localhost-only strict HTTP/1.1 server, allocator unification, ASan/LSan in CI, fuzz-hardened query parser                          | Hardening patterns for local substrates          | gear           | knowledge                               | Design lessons for any Gear substrate touching SQLite or exposing localhost surfaces.                                                                                                                                                             |

## Deep dives (implementation-relevant)

### E4 — SQLite store design (P1 target)

What their design demonstrates, transposed to `gear-memory` (`Store` trait stays the contract; `FileStore` remains):

- one SQLite file per store root, `PRAGMA journal_mode=WAL`, `user_version` as schema version;
- contract tables mirroring `gear.memory.v0.1` (`source_refs`, `memory_entries`, `provenance_records`, `event_log_entries`, `code_maps`) plus normalized `code_symbols` / `code_edges` with indexes on name, kind, from, to;
- `validate()` before every insert — no invalid contract ever persisted;
- bulk ingest through a buffer with deferred index creation (E1 lesson) once volumes justify it;
- their silent-undercount caps are the anti-pattern: our queries return explicit truncation metadata, never silently clipped results.

### E5 — Graph schema gap analysis (`gear.memory.v0.1` vs their 32 edge types)

Covered today: `CALLS`→`Calls`, `IMPORTS`→`Imports`, `TESTS`→`Tests`, `CONFIGURES`→`Configures`, `DEFINES`/`DEFINES_METHOD`→`Defines`, `CONTAINS_*`→`BelongsTo`.

| Their edge                           | v0.2 candidate?                                   | Rationale                                                                                        |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `IMPLEMENTS`, `INHERITS`             | yes                                               | OO/trait relations are the biggest expressiveness gap for real code maps (Rust trait impls).     |
| `HTTP_CALLS` (+confidence)           | yes, with `confidence: Option<f32>` on `CodeEdge` | Cross-service linking was their differentiator; confidence keeps inferred edges honest.          |
| `ASYNC_CALLS`                        | as attribute, not kind                            | Variant of `Calls`; a kind explosion is the wrong shape.                                         |
| `USES_TYPE`, `USAGE`                 | yes (`UsesType`)                                  | Type-usage queries ("who touches this type") are common structural questions.                    |
| `THROWS`, `READS`, `WRITES`          | defer                                             | Data-flow extraction cost is high; no consumer yet.                                              |
| `DECORATES`, `HANDLES`               | defer                                             | Framework-specific; wait for a Wrench producer that emits them.                                  |
| `FILE_CHANGES_WITH`                  | no (analytics, not contract)                      | Derived from git history, recomputable; belongs to E11 outputs, not `CodeMap` truth.             |
| `MEMBER_OF` (communities)            | no (analytics, not contract)                      | Louvain/Leiden output is derived data; persisting it as contract truth would freeze a heuristic. |
| `SIMILAR_TO`, `SEMANTICALLY_RELATED` | no for now                                        | Gated by the progressive-indexing decision: vector must not become opaque truth.                 |
| `CROSS_*`                            | no                                                | E14 quarantine: bounded-context isolation.                                                       |

Node kinds: their `Method`, `Class`, `Enum` are `CodeSymbolKind` v0.2 candidates; their `Project`/`Package`/`Folder` containers are already covered by `CodeMapScope`. Our provenance-flavored edges (`Documents`, `GeneratedFrom`, `Cites`, `DerivedFrom`, `Supersedes`) have no equivalent on their side — that is `gear-memory`'s identity; keep them.

### E6 — Query surface (P1 target)

Their query tools reduced token cost ~10× because agents ask structural questions structurally. P1 subset, all deterministic (stable `ORDER BY`, explicit bounds):

- `symbol_search(name_pattern, kind?)`
- `symbol_neighbors(symbol_id, direction, kind?)`
- `trace_bfs(symbol_id, max_depth)` — bounded, stable neighbor ordering
- `stats()` — counts per table/kind + schema version, zeros kept (E21 lesson)

Rejected from P1: Cypher (E8), degree filters, FTS (E12) — named queries first, generic query language only if real usage demands it.

### E21 — Evaluation method (dogfooding benchmark)

Worth rebuilding as method, not code:

- two conditions on identical questions (graph tools vs grep/read exploration), blind grading against source as ground truth;
- five question dimensions anchored in Sillito et al.'s developer-question catalogue (find symbols / trace relations / exact source / architecture / domain patterns);
- dual token metrics (answering-phase and full-session), tool-call counts, zero-result rates;
- edge/node histograms with zeros kept — a zero is a finding, not an omission;
- judge-bias controls: randomized answer order, multiple passes, cross-family judge preferred.

First forge use: measure `gear-memory` P1 against plain exploration on one forge repo — same protocol, tiny scale.

## Alignment with existing ecosystem decisions

- **Progressive indexing ladder** (decision 2026-06-30, Proposed: catalog → full-text → graph → tree-sitter `CodeMap` → optional vector): this decomposition lands P1 on the graph rung with FTS deferred; their design shows all rungs can share one SQLite file. Open question 1 below.
- **ADR-0022** (starred repos strengthen existing repos): honored — every verdict targets an existing repo; no new repository.
- **Boundary "Wrench parses, Gear stores and indexes"**: E1/E2/E3 stay Wrench; `gear-memory` ingests conformant bundles only.
- **Stars-audit cross-references**: `Egonex-AI/Understand-Anything` (rebuild → Gear Memory code maps), `unum-cloud/USearch` (vector benchmark), `xberg-io/tree-sitter-language-pack` (wrench parsing), `tursodatabase/agentfs` (gear substrate requirements) — this decomposition refines those rows with a concrete reference design.
- **Bounded-context isolation**: E14 quarantined; per-context indexing is the rule if cross-repo linking is ever considered.

## First increment proposal (pending validation)

`gear-memory` P1 = E4 + E6 + E7 (+ E1 flush pattern), sequenced after the in-flight Stage 0 branch (`feat/stage0-store-and-erasure`) merges. Storage decision (rusqlite `bundled` vs redb) and its rationale go to a `gear-memory` ADR (`docs/adr/0002-…`), which also records `codebase-memory-mcp` as design reference — not upstream — and reconciles ADR-0001's stale upstream wording. Detailed implementation plan exists in session notes; nothing starts before this document is reviewed.

## Rumble Note need capture (E19)

Captured in `Rumble-Note` `ROADMAP.md` (Later): knowledge-graph / mapping-point visualization over notes, code maps, and linked context — local-first, read-only over Gear-provided references, no product decision implied by this document.

## Open questions (for review)

1. Ladder order: does P1 on the graph rung before any FTS rung amend the progressive-indexing decision, or is rung order free within one SQLite engine?
2. Should `CodeEdge` gain `confidence: Option<f32>` in v0.2, or stay boolean-truth edges with inferred links kept out of contracts?
3. E11 owner: Bolt planning gate (cos-matic) or `wrench-inspect` evidence collector?
4. E17 boundary: is a committed compressed bundle export a `gear-memory` feature or purely `gear-depot` custody?
5. E21: adopt the two-condition benchmark as a standing `wrench-inspect` Eval Lab protocol, or one-shot dogfooding evidence for P1 only?

## Sources

- README and `docs/llms.txt` — <https://github.com/DeusData/codebase-memory-mcp>
- Paper: _Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP_ — <https://arxiv.org/abs/2603.27277> (§3.1–§3.8 architecture, Tables 1–3 schema/pipeline, §4.1/Table 6 evaluation, §5.4 limitations)
- `docs/BENCHMARK.md` (v0.3.0, 35 languages / 63 repos, 91.8%) and `docs/EVALUATION_PLAN.md` (159-language plan, D1–D5, judge protocol)
- Release notes v0.7.0 → v0.8.1 (Hybrid LSP rollout, Leiden communities, hardening)
- Model weights license — <https://huggingface.co/nomic-ai/nomic-embed-code> (Apache-2.0)
