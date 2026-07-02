# ADR 0002 — Rumble LM source-grounded session P0

Status: Proposed  
Date: 2026-06-30  
Decision owner: Rumble LM product architecture  
Related spec: `../../rumble-lm/14-source-grounded-product-slice.md`

## Context

`rumble-lm` needs to use patterns from source notebooks, RAG applications, LLM evaluation, speech/media tooling, prototyping frameworks, and LLM app catalogs without becoming a generic chatbot, a full LMS, or a clone product.

The ecosystem doctrine requires Rumble products to own product experience while consuming lower-layer capabilities:

- Wrench extracts, validates, and produces evidence.
- Gear stores, indexes, references, packages, verifies, and provides provenance.
- Bolt plans, sequences, gates, and orchestrates generation.
- Biscuit provides shared delegated authorization.

If `rumble-lm` implements ingestion, memory, orchestration, artifact storage, or delegation locally, it duplicates security-sensitive and architecture-critical responsibilities.

## Decision

`rumble-lm` P0 is a synchronous collective source-grounded session product.

The P0 loop is:

```text
create session
→ attach/import sources through Wrench/Gear
→ generate or author activities
→ validate citation support
→ run one live activity at a time
→ collect participant responses
→ display aggregate results
→ generate and validate synthesis
→ export audience-scoped artifact
```

Core decisions:

1. The primary product object is `Session`, not `ChatThread`.
2. Activities are first-class workflow objects with lifecycle, citation state, response schema, and live runs.
3. Generated source-grounded claims require validated citations or explicit unsupported markers.
4. Gear Loader owns canonical extraction; Rumble only initiates imports and stores source-set refs/snapshots.
5. Gear Memory owns `SourceRef`, `SourceChunkRef`, provenance, and retrieval handles.
6. Bolt mediates structured generation and gates, but cannot publish or validate product content.
7. Biscuit is the delegated-rights primitive for Rumble-to-Wrench/Gear/Bolt calls and scoped participant/export operations.
8. Exports are audience-scoped Gear artifacts with refs, manifests, checksums, and revocation/retention metadata.
9. Analytics are aggregate by default; hidden individual profiling and cross-session learner scoring are forbidden in MVP.
10. Starred repositories are used as design capital, benchmarks, and risk comparators, not as a dependency backlog.

## Boundaries

| Responsibility | Owner | Rumble LM behavior |
| --- | --- | --- |
| Session UX, activities, citation review, live participation, synthesis validation | Rumble LM | Owns product workflow and user-facing meaning. |
| Canonical source extraction | Gear Loader | Consumes extraction outputs and warnings. |
| Source refs/chunks/provenance/retrieval | Gear Memory | Stores refs/snapshots only. |
| Draft generation orchestration and gates | Bolt | Sends structured requests; receives drafts/refusals/evidence. |
| Delegated rights | Biscuit shared contract | Uses attenuated scoped tokens; no local token format. |
| Export artifact integrity | Gear artifact/depot capability | Produces audience/data-class intent; stores artifact refs/checksums. |
| Citation support evidence | Wrench validator/inspect capability | Uses advisory support levels; facilitator remains final gate. |

## Consequences

### Positive

- The product remains visible and useful: source-backed sessions, not abstract platform plumbing.
- Dangerous duplication is avoided across Rumble products.
- Grounding becomes testable through source refs, citation states, support levels, and export evidence.
- RGPD risk is reduced by aggregate analytics, visibility snapshots, and no PII in logs.
- Future shared capabilities are justified by product need rather than premature platform design.

### Negative / Costs

- P0 depends on clear contracts with Wrench, Gear, Bolt, and Biscuit before implementation.
- Some features may need stubs until lower-layer capabilities are ready.
- Facilitators must review citations; full automation is explicitly not the P0 trust model.
- Provider policy and retention defaults remain deployment-sensitive decisions.

## Alternatives considered

### Generic source chatbot

Rejected. It makes chat the product object, weakens facilitation workflows, and risks unsupported answer-engine behavior.

### Full LMS

Rejected. Course catalogs, enrollment lifecycle, grades, certificates, assignments, and long-term learner records are outside P0 and would create profiling/RGPD burden.

### Product-local ingestion and vector memory

Rejected. This duplicates Wrench/Gear responsibilities and creates opaque storage and deletion/anonymization risks.

### Product-local delegation tokens

Rejected. Delegation is security-sensitive and must use the shared Biscuit contract.

### Fully automated citation authority

Rejected for P0. Wrench can provide evidence and support-level advice, but publication/export validation remains a facilitator-owned product gate.

## Sovereignty and compliance filters

- No mandatory US SaaS.
- No production dependency with blocking license.
- No opaque source, response, summary, export, or audit storage.
- No raw source excerpts, participant responses, bearer tokens, Biscuit tokens, or secrets in logs.
- Provider routing is deployment-policy controlled; no silent third-party transmission.

## Required follow-up

- Define `SourceGroundedGenerationRequest` contract with Bolt.
- Define citation support validation result contract with Wrench.
- Define export `ArtifactManifest` requirements with Gear.
- Define LM-specific Biscuit facts/caveats and authorizer conformance tests.
- Decide retention defaults for responses, summaries, exports, and audit events.
- Decide whether the first implementation uses real lower-layer services or contract stubs.

## Acceptance criteria

- A source-grounded generation request without ready source set is refused.
- Generated activities are drafts and are never participant-visible before facilitator publication.
- Preparation is blocked when mandatory source-grounded claims lack validated citations or unsupported markers.
- Weak, contradicted, rejected, or stale citations cannot satisfy grounding gates.
- Participant-facing summaries and exports enforce response visibility snapshots.
- Default analytics expose aggregate signals only and create no cross-session individual profile.
- Delegated tokens are attenuated by workspace/session/action/audience/data-class where relevant.
- Exports include audience, included data classes, artifact ref, checksum, source/citation references, and validation timestamps.
