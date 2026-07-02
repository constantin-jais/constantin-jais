# ADR 0013 — Gear Loader P0 Input Set

Status: Accepted
Date: 2026-06-30

## Context

Multiple Rumbles need shared ingestion now, but high-risk modalities such as OCR/STT and legacy binary formats can introduce privacy, licensing, and sandboxing risk.

## Decision

P0 input set:

- HTML;
- Markdown;
- PDF with selectable text;
- `.docx`, `.pptx`, `.xlsx` text/table/slide extraction;
- RSS, Atom, JSON Feed parsing;
- single URL fetch under policy;
- code file/repository snapshot extraction;
- plain text.

P1 gated inputs:

- OCR/images/scanned PDFs;
- audio/STT;
- archives;
- EPUB;
- bounded crawl.

P2/deferred:

- legacy binary Office unless sandbox-converted;
- email boxes;
- full website crawling;
- database dumps;
- proprietary SaaS connectors.

## Consequences

- Rumbles stop duplicating common ingestion.
- Security-sensitive media remains explicit and reviewable.
- Feed parsing is shared without turning Loader into a feed product.

## Acceptance Tests

- P0 fixtures extract deterministically with evidence reports.
- OCR/STT requests fail closed unless explicitly enabled.
- Legacy binary Office and over-limit archives quarantine rather than parse unsafely.
