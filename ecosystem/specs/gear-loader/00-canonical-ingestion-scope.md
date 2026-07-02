# Gear Loader — Canonical Ingestion Scope

Status: Proposed.
Date: 2026-06-30.

## Mission

`gear-loader` is the Gear canonical ingestion and extraction brick for the Rumble / Bolt / Wrench / Gear ecosystem.

It turns hostile or heterogeneous inputs into deterministic, auditable, source-grounded canonical content that Rumble products can use and Gear can store/index.

It is not a knowledge product, not durable memory, not a crawler brain, not a feed reader, and not an orchestration system.

## Upstream Inspirations, Clean-Room Use

The GitHub stars audit positions these projects as inspiration only:

| Inspiration                          | What to learn                                                                         | What not to copy                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `xberg-io/xberg`                     | Document-intelligence architecture, extraction report shape, modular loader idea.     | No direct product clone; no upstream contract naming as ecosystem contract.       |
| `xberg-io/html-to-markdown`          | Deterministic HTML cleanup and readable Markdown projection.                          | Do not make Markdown the only truth; keep structured blocks and provenance.       |
| `xberg-io/crawlberg`                 | URL capture, fetch policy, crawl frontier constraints, evidence around fetched pages. | Do not let Wrench decide what to crawl next; Bolt/Rumble owns intent/scheduling.  |
| `cjpais/Handy`                       | Offline speech-to-text option for audio/transcript ingestion.                         | Do not make STT a hidden cloud dependency; no unreviewed model/license import.    |
| `xberg-io/tree-sitter-language-pack` | Polyglot code parsing and syntax-aware chunking.                                      | Do not turn Loader into a code intelligence product; only extract/code-normalize. |

License rule: direct dependencies must remain MIT / Apache-2.0 / BSD / ISC / MPL-2.0 compatible. AGPL, SSPL, BSL, proprietary dependencies, and unverified model licenses are blocked.

## Product Demand

`gear-loader` is justified by repeated needs:

- `rumble-note`: import documents/sources without becoming an ingestion engine.
- `rumble-lm`: build source sets for sessions, activities, summaries, and citations.
- `rumble-feed-mind`: parse feeds and normalize fetched items before curation.
- `rumble-cos`: ingest reusable sources for articles/courses/resources.
- `rumble-canvas`: consume source-grounded specs and evidence packages.
- Bolt / `cos-matic`: call deterministic extraction as one step in a plan.
- `gear-memory`: receive normalized sources, chunks, hashes, provenance, and indexing hints.

## Scope by Priority

### P0 — canonical shared ingestion

P0 is the minimal surface needed to stop Rumble products from reimplementing ingestion.

| Format / input   | P0 decision                                                                                        | Reason                                                                                                                               |
| ---------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| HTML             | In scope.                                                                                          | Needed by URLs, feeds, COS, LM, Note. Normalize DOM, main content, links, metadata, and Markdown projection.                         |
| Markdown         | In scope.                                                                                          | Native agent-readable format, notes/specs/blog/source packages. Preserve frontmatter and headings.                                   |
| PDF              | In scope.                                                                                          | Common source format for learning/research. Extract text, pages, metadata; OCR only when explicitly enabled.                         |
| Office documents | In scope for `.docx`, `.pptx`, `.xlsx` text/tables metadata.                                       | Common user uploads. Prefer open parsers and safe archive handling. Legacy binary Office is P1/quarantine unless safe parser exists. |
| Feeds            | In scope for RSS/Atom/JSON Feed parsing and item normalization.                                    | `rumble-feed-mind`, Note and COS need reusable feed source normalization. Polling strategy remains Rumble/Bolt.                      |
| URLs             | In scope for single-URL fetch and bounded capture.                                                 | Needed by all source-grounded products. Respect fetch policy, robots policy setting, content-type allowlist, size/time limits.       |
| Code             | In scope for repository/file snippets as source extraction, syntax-aware chunking where available. | Needed for specs, agents, Canvas, Note. No deep code graph ownership.                                                                |
| Plain text       | In scope.                                                                                          | Baseline fallback and test fixture format.                                                                                           |

### P1 — valuable but gated

| Format / input              | P1 decision                                                | Reason                                                                                                        |
| --------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Audio / STT                 | P1 behind explicit consent and model/license review.       | Useful for LM sessions and notes, but high privacy and model risk. Prefer offline/local STT or sovereign STT. |
| Images / OCR                | P1 behind explicit OCR flag.                               | Useful for scanned PDFs/screenshots, but expensive and error-prone. Produce confidence and bounding evidence. |
| Archives                    | P1 for safe archive expansion.                             | Useful upload shape, but hostile-archive risk requires strict limits.                                         |
| EPUB                        | P1.                                                        | Useful for learning sources; not required for first shared pipeline.                                          |
| Video transcript extraction | P1 only via existing transcript files or local extraction. | Avoid platform lock-in and proprietary APIs.                                                                  |
| Sitemap / bounded crawl     | P1.                                                        | Should be a bounded extraction primitive, not an autonomous crawler.                                          |

### P2 — deferred / explicit non-P0

| Format / input                                | P2 decision                                                           | Reason                                                              |
| --------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Legacy binary Office (`.doc`, `.xls`, `.ppt`) | P2/quarantine unless converted in sandbox.                            | Parser attack surface and fidelity risk.                            |
| Email boxes                                   | P2.                                                                   | PII-heavy, product-specific retention and consent model.            |
| Full website crawling                         | P2 and Bolt/Rumble-driven.                                            | Loader may execute bounded fetches; it does not own crawl strategy. |
| Database dumps                                | Out of Loader P0/P1; likely Wrench Inspect / DB Inspect if inspected. | Different security domain.                                          |
| Proprietary SaaS connectors                   | Deferred.                                                             | Sovereignty/vendor-lock risk.                                       |

## Canonical Output

The canonical output is not “just Markdown”. Markdown is a projection. The contract is a structured envelope with content, blocks, chunks, metadata, provenance, risk findings, and evidence.

### `CanonicalSourceDocument v0.1`

```json
{
  "format": "wrench.canonical_source_document.v0.1",
  "document_id": "csd_01",
  "source": {
    "input_type": "file | url | feed_item | transcript | markdown | html | pdf | office | code | text",
    "uri": "optional",
    "filename": "optional",
    "media_type": "text/html",
    "size_bytes": 123,
    "content_hash": "sha256:<64 hex chars>",
    "retrieved_at": "2026-06-30T00:00:00Z"
  },
  "canonical": {
    "title": "optional",
    "language": "fr",
    "text": "plain text projection",
    "markdown": "markdown projection",
    "structure": [
      {
        "block_id": "blk_01",
        "type": "heading | paragraph | list | table | code | quote | image | audio_segment | feed_metadata",
        "text": "block text",
        "markdown": "optional block markdown",
        "source_span": {
          "page": 1,
          "byte_start": 0,
          "byte_end": 42,
          "selector": "optional DOM/CSS/XPath or structural selector"
        }
      }
    ],
    "chunks": [
      {
        "chunk_id": "chk_01",
        "block_ids": ["blk_01"],
        "text": "retrieval-ready text",
        "token_estimate": 120,
        "citation_label": "p.1 / h2 / item guid"
      }
    ]
  },
  "metadata": {
    "authors": [],
    "published_at": "optional",
    "license": "optional",
    "links": [],
    "feed": { "feed_url": "optional", "item_id": "optional" },
    "code": { "language": "optional", "symbols": [] }
  },
  "security": {
    "classification": "public | internal | personal_data | sensitive | secret_suspected",
    "prompt_injection": {
      "detected": false,
      "findings": []
    },
    "pii": {
      "detected": false,
      "categories": []
    },
    "secrets": {
      "detected": false,
      "findings": []
    },
    "active_content_removed": true
  },
  "quality": {
    "extraction_status": "ok | partial | failed | quarantined",
    "confidence": 0.92,
    "warnings": [],
    "unsupported_features": []
  },
  "provenance": {
    "tool": "wrench-loader",
    "tool_version": "0.1.0",
    "pipeline_id": "pipeline_html_default_v1",
    "started_at": "2026-06-30T00:00:00Z",
    "completed_at": "2026-06-30T00:00:01Z",
    "input_refs": [],
    "output_hash": "sha256:<64 hex chars>"
  }
}
```

### Output rules

- The canonical hash is computed over canonical JSON bytes with stable key ordering.
- Raw files are never embedded by default; they are referenced by hash/ref.
- Markdown and plain text are projections, not authority.
- Every chunk must trace back to block IDs and source spans where available.
- Extraction warnings are first-class; partial extraction is not silently treated as success.
- Security findings travel with the output so Gear/Rumble/Bolt do not lose context.

## Core API Contracts

### `ExtractionRequest v0.1`

```json
{
  "format": "wrench.extraction_request.v0.1",
  "request_id": "req_01",
  "actor_ref": "actor_01",
  "workspace_ref": "workspace_01",
  "input": {
    "kind": "file_ref | url | inline_text | feed_ref | artifact_ref",
    "ref": "opaque reference or URL"
  },
  "policy": {
    "allowed_media_types": [],
    "max_bytes": 25000000,
    "network": "disabled | single_url | bounded_crawl",
    "ocr": "disabled | enabled",
    "stt": "disabled | enabled",
    "pii_mode": "detect | redact | block",
    "secret_mode": "detect | redact | block",
    "prompt_injection_mode": "detect | quarantine_on_high"
  },
  "requested_outputs": [
    "canonical_document",
    "evidence_report",
    "gear_source_candidate"
  ]
}
```

### `GearSourceCandidate v0.1`

`gear-loader` may produce a candidate for Gear, but Gear owns the durable `SourceRef`.

```json
{
  "format": "wrench.gear_source_candidate.v0.1",
  "canonical_document_ref": "csd_01",
  "source_type": "file | url | feed_item | transcript | document | dataset | artifact",
  "origin_product": "wrench-loader",
  "content_hash": "sha256:<64 hex chars>",
  "provenance": {},
  "indexing_hints": {
    "language": "fr",
    "chunk_ids": [],
    "sensitive": false
  }
}
```

Gear may accept, reject, index, delete, anonymize, or mark stale. Loader must not assume persistence.

## Boundary: Wrench Loader vs Gear Memory vs Rumble vs Bolt

| Concern                                                 | Wrench Loader             | Gear Memory                    | Rumble products                   | Bolt / `cos-matic`          |
| ------------------------------------------------------- | ------------------------- | ------------------------------ | --------------------------------- | --------------------------- |
| Parse HTML/PDF/Office/feed/code/audio transcript        | Owns                      | No                             | Calls                             | May schedule/call           |
| Fetch a single URL under policy                         | Owns execution            | May store refs                 | Requests                          | May orchestrate             |
| Decide what sources matter to a user/session/feed       | No                        | No                             | Owns product meaning              | May plan workflow           |
| Poll feeds as a product workflow                        | Provides parser/extractor | Stores/indexes source refs     | `rumble-feed-mind` owns UX/config | May schedule recurring runs |
| Store durable source refs/chunks/indexes                | Produces candidates       | Owns                           | Uses                              | Uses refs                   |
| Semantic memory / retrieval API                         | No                        | Owns                           | Uses                              | Uses                        |
| Product notes/sessions/articles/curation                | No                        | No                             | Owns                              | No                          |
| Inspection readiness/evidence validation                | Produces loader evidence  | Stores report refs if accepted | Displays/acts                     | Gates/plans from evidence   |
| Decide publication, task execution, or learning summary | No                        | No                             | Owns final human/product decision | Owns orchestration gates    |

Strict rule: Wrench Loader extracts and normalizes; Gear Memory persists and retrieves; Rumble interprets and presents; Bolt sequences and gates.

## Security, Privacy, and Hostile Input Handling

Security outranks extraction completeness.

### Hostile files

- Process untrusted inputs in a sandboxed worker with no ambient secrets.
- Default network is disabled during file parsing.
- Enforce file size, page count, archive depth, decompressed size, wall-clock, CPU, and memory limits.
- Use content-type sniffing plus extension checks; mismatch becomes warning or quarantine.
- Strip or ignore active content: scripts, macros, remote references, embedded executables, external images unless explicitly allowed.
- Never execute document macros, embedded scripts, formulas, or external URL fetches found inside documents.
- Quarantine malformed, encrypted, password-protected, or parser-crashing files with evidence.

### Prompt injection

- Treat all extracted content as untrusted data.
- Detect common instruction-in-content patterns, but do not rely on detection as a complete defense.
- Mark suspicious spans with source locations.
- Output must separate `content` from `instructions`; Loader never converts extracted instructions into system/developer prompts.
- High-risk findings can set `extraction_status=quarantined` depending on request policy.

### PII and secrets

- Detect PII categories and secret-like material before storage handoff.
- Default behavior: detect and report. Product policy may request redact or block.
- Never write raw secrets to logs, metrics, evidence metadata, or provenance metadata.
- Redaction must preserve traceability via stable redaction markers and hashes where lawful.
- Support deletion/anonymization propagation by linking findings to block/chunk IDs.

### OCR and STT

- OCR/STT are disabled by default because they may process highly sensitive content and introduce confidence errors.
- Enabling OCR/STT requires explicit policy in `ExtractionRequest` and evidence of selected engine/model.
- Prefer local/offline or sovereign EU processing; no AWS/GCP/Azure/Supabase/Vercel or proprietary hidden service.
- STT/OCR output must include confidence, timestamps/bounding boxes where possible, language, model/tool ref, and warnings.
- Low-confidence OCR/STT chunks must not be citation-authoritative without warning.

## Evidence for Wrench Inspect / Bolt

`gear-loader` must produce machine-readable evidence. Wrench Inspect can validate it; Bolt can gate plans on it.

### `LoaderEvidenceReport v0.1`

```json
{
  "format": "wrench.loader_evidence_report.v0.1",
  "report_id": "ler_01",
  "request_id": "req_01",
  "canonical_document_id": "csd_01",
  "status": "passed | passed_with_warnings | failed | quarantined",
  "input_evidence": {
    "media_type": "text/html",
    "size_bytes": 123,
    "content_hash": "sha256:<64 hex chars>",
    "source_uri_hash": "optional"
  },
  "pipeline_evidence": {
    "tool_version": "0.1.0",
    "pipeline_id": "pipeline_html_default_v1",
    "deterministic": true,
    "sandboxed": true,
    "network_policy": "single_url"
  },
  "extraction_evidence": {
    "pages_seen": 0,
    "blocks_emitted": 10,
    "chunks_emitted": 4,
    "coverage_ratio": 0.95,
    "confidence": 0.92,
    "warnings": []
  },
  "security_evidence": {
    "active_content_removed": true,
    "prompt_injection_findings": [],
    "pii_findings": [],
    "secret_findings": [],
    "quarantine_reason": "optional"
  },
  "policy_evidence": {
    "blocked_by_policy": false,
    "policy_decisions": []
  },
  "outputs": {
    "canonical_hash": "sha256:<64 hex chars>",
    "gear_source_candidate_hash": "optional"
  }
}
```

Required evidence reports:

1. `LoaderEvidenceReport`: extraction status, hashes, parser/pipeline version, sandbox/network policy, warnings.
2. `SecurityFindingsReport`: prompt injection, PII, secrets, active content, quarantine reasons. May be embedded in `LoaderEvidenceReport` for MVP.
3. `CoverageReport`: pages/blocks/chunks emitted, skipped zones, unsupported features, confidence.
4. `ProvenanceReport`: input refs, output refs/hashes, actor/tool/time, policy used.
5. `CitationMap`: source spans to block/chunk/citation labels for LM/COS/Canvas source-grounded workflows.

## ADRs

Created decision records:

1. `../shared/adrs/0012-wrench-loader-canonical-json.md` — `CanonicalSourceDocument v0.1` as structured JSON, Markdown as projection.
2. `../shared/adrs/0013-wrench-loader-p0-input-set.md` — P0 input set includes HTML, Markdown, selectable-text PDF, Office Open XML, feeds, URLs, code, and text; audio/OCR are P1.
3. `../shared/adrs/0014-wrench-loader-gear-source-candidate.md` — `wrench-loader` produces `GearSourceCandidate`, not durable `SourceRef`.
4. `../shared/adrs/0015-wrench-loader-hostile-content-evidence.md` — hostile-content evidence is mandatory and travels with canonical output.
5. `../shared/adrs/0016-wrench-loader-feed-parsing-boundary.md` — feed parsing belongs in `wrench-loader` P0; feed polling/product triage remains `rumble-feed-mind`/Bolt.

## Acceptance Tests

### Contract tests

- Given a valid HTML file, when extracted, then `CanonicalSourceDocument v0.1` contains title, text, Markdown projection, blocks, chunks, hashes, and `LoaderEvidenceReport`.
- Given Markdown with frontmatter and headings, when extracted, then frontmatter is metadata and headings become structured blocks.
- Given a PDF with selectable text, when extracted, then chunks include page-level citation labels and coverage evidence.
- Given `.docx`, `.pptx`, and `.xlsx` fixtures, when extracted, then text/tables/slides are represented without executing macros or external references.
- Given RSS, Atom, and JSON Feed fixtures, when parsed, then feed and item metadata are normalized into source documents.
- Given a code file, when extracted, then code blocks include language and optional syntax-aware chunks without requiring code graph storage.

### Security tests

- Given an HTML page containing scripts and prompt-injection text, when extracted, then scripts are removed/ignored and injection spans are reported.
- Given a file containing API-key-like strings, when extracted, then secrets are detected and never appear in logs/evidence metadata.
- Given PII-containing text with `pii_mode=block`, when extracted, then output is blocked or quarantined with policy evidence.
- Given a zip bomb or over-limit archive, when processed, then Loader aborts safely and emits quarantine evidence.
- Given an Office document with macros or remote references, when extracted, then active content is not executed and evidence records removal/blocking.
- Given a parser crash fixture, when processed, then the worker fails closed and produces a failed/quarantined report.

### Boundary tests

- Given a successful extraction, when Gear is unavailable, then Loader still returns canonical output and evidence but does not pretend a `SourceRef` exists.
- Given a feed subscription, when polling interval/rules are requested, then Loader rejects ownership and accepts only parse/extract requests.
- Given a Rumble LM source set import, when extraction is partial, then Rumble receives warnings and cannot silently mark all citations validated.
- Given Bolt calls Loader, when evidence status is `quarantined`, then Bolt can gate/refuse the next step using the report.

### Determinism tests

- Given the same input bytes and same pipeline version, when extracted twice, then canonical hashes match.
- Given only retrieval timestamp differs for a URL fetch, when canonical content is unchanged, then content hash is stable and provenance timestamps differ.
- Given chunks are regenerated with the same chunker version, when source blocks are unchanged, then chunk IDs/order remain stable.

### OCR/STT P1 tests

- Given scanned PDF with `ocr=disabled`, when extracted, then Loader reports no text coverage and recommends OCR without running it.
- Given audio with `stt=enabled`, when transcribed, then transcript chunks include timestamps, confidence, engine ref, and privacy evidence.

## Recommendation

Recommendation: strengthen the existing `gear-loader` repository as the canonical ingestion repository, not create a new repo now.

Rationale:

- The ecosystem overview already names `gear-loader` as rich-document ingestion and canonical extraction.
- The need is shared by multiple Rumble products now; fragmentation would recreate the problem.
- A separate `wrench-feed-loader` should remain a future split only if feed parsing grows independent operational complexity.
- A separate `wrench-stt-loader` should remain a future split only if audio/STT becomes a major sandbox/model lifecycle domain.

Near-term implementation shape:

1. Keep one repo: `gear-loader`.
2. Add modular adapters internally: `html`, `markdown`, `pdf`, `office`, `feed`, `url`, `code`, later `ocr`, `stt`.
3. Publish contracts from the repo and mirror stable contracts in `constantin-jais/ecosystem/specs`.
4. Add `cargo deny` license policy before dependencies.
5. Build P0 from deterministic fixtures and evidence reports before optimizing extraction quality.

## Open Questions

| Question                                     | Impact | Proposed default                                                                         |
| -------------------------------------------- | ------ | ---------------------------------------------------------------------------------------- |
| Should Loader write directly to Gear Memory? | High   | No by default; return candidate/output. Direct write only via explicit integration mode. |
| Should raw input bytes be stored by Loader?  | High   | No durable storage; temporary sandbox only. Gear/Depot may store according to policy.    |
| Should feeds stay in Loader or split?        | Medium | Keep feed parsing in Loader P0; revisit after FeedMind MVP.                              |
| Which OCR/STT engine is acceptable?          | High   | Decide by ADR after license/model/RGPD review; prefer local/offline or sovereign EU.     |
| Is Markdown sufficient for all Rumbles?      | High   | No; Markdown is projection, structured JSON is canonical.                                |
