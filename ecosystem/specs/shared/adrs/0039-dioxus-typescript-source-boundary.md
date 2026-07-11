# ADR 0039 — Dioxus 0.7.9 and the TypeScript source boundary

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Amends: ADR 0032
Related: ADR 0036, ADR 0037, ADR 0038

## Context

ADR 0032 elects Dioxus but does not close the language boundary tightly enough for Office hosts, browser tests and migration tooling. Unbounded JavaScript or TypeScript would allow durable product rules to drift outside the Rust contracts.

## Decision

1. Dioxus 0.7.9 is the Web/PWA and ecosystem SSG shell until a separate upgrade ADR.
2. JavaScript source (`.js`, `.jsx`, `.mjs`, `.cjs`) is forbidden unless generated and unversioned.
3. TypeScript is allowed only for browser-facing presentation, Playwright, generated clients, bounded Office host interop and disposable build tooling.
4. TypeScript must use `strict: true`, may not hand-own Rust API contracts and may not own authorization, persistence, jobs, provider routing or release truth.
5. Office interop, if ever enabled, is a specialized adapter under ADR 0038 and requires an interoperability waiver.

## Acceptance criteria

- source-extension gate rejects versioned JavaScript;
- generated TypeScript is traceable to a Rust-owned schema;
- UI tests prove keyboard, reduced-motion and 320/768/1440 behavior;
- provider keys, Biscuit tokens and session secrets remain inaccessible to browser code.
