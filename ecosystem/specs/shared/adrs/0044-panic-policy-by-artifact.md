# ADR 0044 — Panic policy by artifact class

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Amends: blanket release-profile guidance
Related: ADR 0038, ADR 0040

## Context

A global `panic = "abort"` reduces binary size but turns one unexpected task failure into total service loss and prevents a parser worker supervisor from reporting controlled evidence. One policy does not fit all artifacts.

## Decision

- Long-lived servers, multi-task runtimes and supervisors use unwind and catch failures only at explicit isolation boundaries.
- Hostile document parsing runs in a separate process; process exit is treated as typed failure.
- One-shot CLI and WASM artifacts may use abort after size/performance measurement and a local artifact declaration.
- Libraries do not prescribe the final panic strategy.
- No input validation path may depend on panic for rejection.

## Acceptance criteria

- target-version records the policy per artifact class;
- server tests prove one failed task does not terminate unrelated work;
- worker tests prove crash/timeout becomes fail-closed evidence;
- abort deviations include measurement and rollback.
