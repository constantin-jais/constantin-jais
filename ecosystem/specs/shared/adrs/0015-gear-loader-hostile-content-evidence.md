# ADR 0015 — Gear Loader Hostile-Content Evidence Is Mandatory

Status: Accepted
Date: 2026-06-30

## Context

Inputs can contain scripts, macros, prompt-injection text, PII, secrets, corrupted structures, remote references, and parser bombs. If extraction warnings stay in logs or are lost before Rumble/Bolt/Gear consume the content, unsafe context may be treated as trustworthy.

## Decision

Every Loader run emits `LoaderEvidenceReport v0.1`, including extraction status, sandbox/network policy, content hashes, coverage, active-content handling, prompt-injection findings, PII findings, secret findings, warnings, and quarantine reasons.

Security evidence travels with canonical output and Gear source candidates. Logs and metadata must not contain raw PII, secrets, tokens, credentials, or private source excerpts.

## Consequences

- Rumbles can display warnings and require human validation.
- Bolt can gate or refuse downstream steps.
- Gear can store/index only safe references and preserve provenance.
- Wrench Inspect can validate extraction readiness.

## Acceptance Tests

- Given scripts/macros/remote references, evidence records removal/blocking and no execution occurs.
- Given secret-like strings, findings are reported without raw secret leakage in logs/metadata.
- Given prompt-injection spans, evidence marks them as untrusted content, not instructions.
