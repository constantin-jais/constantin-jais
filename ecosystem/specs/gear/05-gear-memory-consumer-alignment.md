# Gear Memory Consumer Alignment

Status: Draft / P0 integration map.

Purpose: make explicit what Gear Memory centralizes for each Rumble and Bolt, without forcing products into a premature platform.

## 1. Integration Rule

Each consumer adopts the smallest useful Gear Memory contract first:

1. use `SourceRef` and `ProvenanceRecord` when content can ground another workflow;
2. add `MemoryEntry` when retrieval/indexing is needed;
3. add graph edges or `CodeMap` only when cross-reference/code lookup is needed;
4. add vector search only after full-text/graph behavior is accepted and deletion tests pass.

Products must not store raw PII, secrets, tokens, or private source excerpts in Gear event/debug metadata.

## 2. Consumer Matrix

| Consumer | What Gear Memory centralizes | Product keeps | P0 seam | Anti-duplication effect |
| --- | --- | --- | --- | --- |
| `rumble-note` | explicit note export source refs, memory entries, retrieval, stale/delete/anonymize propagation | block editor, note graph UX, privacy choices, handoff intent | `NoteContextExport` → `SourceRef` + `MemoryEntry` | avoids local search/provenance/index deletion logic in Note |
| `rumble-lm` | session source refs, citation retrieval refs, source-set provenance | facilitation UX, activities, learner/session semantics, citation validation UX | source set references `SourceRef`; recap/export references `ArtifactRef` via Depot | avoids per-session bespoke source cache and citation provenance store |
| `rumble-canvas` | spec/handoff source references, indexed context, trace-to-source lookup | spec semantics, approvals, waivers, packaging UX | `SpecPackage`/handoff artifact can later become `SourceRef` for grounding | avoids local memory/search layer for approved spec context |
| `rumble-feed-mind` | feed item source refs, curated source graph, stale/revoked propagation | feed subscriptions, curation rules, explanations, ranking UX | feed item → `SourceRef`; curated bundle → Depot `ArtifactRef`; artifact-as-source if reused | avoids each target product re-ingesting feed provenance |
| `rumble-crew` | evidence refs, safe runtime log refs, code maps for task context | board UX, task lifecycle, recovery decisions, approvals | task context/evidence points at `SourceRef`, `ArtifactRef`, `CodeMap` | avoids task-local evidence stores and ad hoc code graph lookups |
| Bolt / `cos-matic` | retrieval of current/stale references, code maps, provenance for planning | planning, gates, sequencing, execution/refusal decisions | plan input carries Gear refs; plan output may cite refs | avoids Bolt becoming a memory DB or parser |
| Wrench | storage target for canonical extractions and parser output | extraction, parsing, validation, inspection evidence | Wrench emits source/codemap/provenance payloads for Gear | avoids Gear absorbing parser or validator logic |

## 3. Product-Specific P0 Contracts

### 3.1 Rumble Note

P0 behavior:

- Note indexes only explicit exports or explicit local projections.
- Blocks marked `private`, `no_handoff`, or `sensitive` are excluded unless user explicitly includes them.
- Deleted/anonymized blocks propagate to Gear Memory by source state change.

Acceptance:

- Given a `NoteContextExport`, Gear indexes only included block refs.
- Given a private block not explicitly included, no `SourceRef` is created for that block.
- Given a deleted block, linked memory entries become deleted/stale and are removed from searchable payloads.

### 3.2 Rumble LM

P0 behavior:

- A session source set references `SourceRef` IDs, not copied raw documents.
- Generated or facilitator-facing citations resolve to source refs, hashes, and provenance.
- LM validates support and pedagogy in product/Wrench layers; Gear only retrieves references.

Acceptance:

- Given an LM activity with sources, every source has state/hash/provenance.
- Given a source becomes stale, LM displays stale citation context and requires refresh/revalidation before new generation.
- Given a source is deleted/anonymized, LM cannot retrieve raw searchable content from Gear.

### 3.3 Rumble Canvas

P0 behavior:

- Approved spec packages and handoffs remain product/Depot artifacts.
- Gear Memory may index package context as source material when reused for planning or downstream Rumbles.
- Traceability links remain Canvas semantics; Gear stores reference edges only if exported.

Acceptance:

- Given a handoff references prior source context, Bolt receives Gear refs, not embedded private content.
- Given a spec package is superseded, indexed source context becomes stale or points at the new source per product policy.

### 3.4 Rumble Feed Mind

P0 behavior:

- Feed items are `SourceRef` inputs.
- Curated bundles are Depot artifacts.
- Reused curated bundles can become `SourceRef` of type `artifact` for LM/Note/Canvas grounding.
- Rule explanations remain product/Wrench evidence, not Gear decisions.

Acceptance:

- Given a feed item is removed or source access revoked, derived memory entries stop normal retrieval.
- Given a curated export is reused by LM, the source chain preserves feed item → bundle artifact → artifact-as-source provenance.

### 3.5 Rumble Crew

P0 behavior:

- Evidence and runtime logs are references with safe metadata, not raw secret-bearing logs.
- Code context is retrieved through `CodeMap` and `SourceRef`.
- Crew decides task state and recovery; Gear only supplies evidence/source state.

Acceptance:

- Given a task references runtime evidence, Gear metadata contains no raw credentials or source excerpts.
- Given code changed after task context was built, Crew sees stale code map state before asking Bolt to plan/execute.

### 3.6 Bolt / Cos-matic

P0 behavior:

- Bolt consumes Gear Memory retrieval results as context refs.
- Bolt never writes product meaning into Gear indexes.
- Bolt decisions can be provenance inputs, but Gear does not decide.

Acceptance:

- Given a planning request, Bolt can cite retrieved source/code refs and stale warnings.
- Given stale or revoked context, Bolt refuses or gates execution according to Bolt policy; Gear only reports state.

## 4. Shared Acceptance Tests

- No Rumble stores a product-local long-term search/vector index for shared source material without logging an ADR/waiver.
- Every cross-product source handoff uses `SourceRef` or `ArtifactRef`, not raw private content by default.
- Every indexed item can be exported and replayed offline with ID, state, hash, provenance, and tombstones.
- Deletion/anonymisation wins over stale active content in every consumer sync replay.
- Compact agent-readable payloads contain canonical references and are not treated as storage truth.

## 5. ADR Follow-up

- Link this document from product service/API specs when those specs introduce Gear Memory calls.
- Add product-specific ADRs only when a product deviates from the P0 seam above.
