# Source-Grounded Product Slice — rumble-lm

Status: Draft proposal.

## Purpose

This note defines the visible P0 product for `rumble-lm` as a collective source-grounded session experience.

`rumble-lm` may learn from source notebook, RAG, evaluation, speech, prototyping, and LLM-app patterns, but it must not become:

- a generic chatbot;
- a full LMS;
- a clone of an external product;
- a durable ingestion system;
- a durable memory system;
- an authorization-token subsystem.

Rumble LM owns the user workflow: prepare a session, run collective activities, validate grounding, synthesize outcomes, and export evidence.

---

## Session Control Objectives

Every specification or design session for `rumble-lm` must leave behind explicit contracts that prevent local reinvention while keeping product teams fast.

1. **Avoid dangerous duplication.** Each session identifies which lower-layer capability is being centralized and what `rumble-lm` must not reimplement locally.
2. **Strengthen products without over-platforming.** Wrench, Gear, Bolt, and Biscuit are introduced only through concrete product needs shared by Rumble products, not as an abstract platform mandate.
3. **Produce contracts before code.** Each session should output boundaries, domain/service models, ADR candidates, and acceptance tests before implementation starts.
4. **Keep sovereignty as a hard filter.** No mandatory US SaaS, no blocking-license dependency, no opaque storage, and no PII in logs.
5. **Turn starred repositories into design capital.** Starred repositories challenge decisions, benchmark patterns, expose risks, and justify shared bricks; they are not a raw backlog.

### Duplication Ledger for This Slice

| Centralized subject | Owner | Rumble LM consumes | Rumble LM must not duplicate |
| --- | --- | --- | --- |
| Canonical source extraction | Wrench Loader | import requests, extraction warnings, normalized chunks | parsers/crawlers/OCR/transcription pipelines as durable product code |
| Source refs, chunks, provenance, retrieval | Gear Memory | `SourceRef`, `SourceChunkRef`, retrieval handles, provenance | vector DB, long-term memory, global knowledge graph |
| Generation orchestration and gates | Bolt | structured draft generation, refusals, gate evidence | agent runtime, model router, autonomous planner |
| Delegated rights | Biscuit/shared auth | attenuated operation tokens | product-specific delegation tokens or ad hoc signed authority |
| Export artifacts and evidence | Gear artifact/depot capability | artifact ref, checksum, manifest, revocation metadata | opaque file store with unverifiable exports |
| Citation support evidence | Wrench validator/inspect capability | support levels, explanations, warnings | hidden scoring of sources or untraceable citation heuristics |

---

## Product Thesis

`rumble-lm` is a facilitation product where the primary object is not a chat thread but a **session**.

A session has:

1. a bounded objective;
2. a selected source set;
3. facilitator-approved activities;
4. participant responses governed by explicit visibility rules;
5. cited claims;
6. aggregate learning/facilitation signals;
7. a validated synthesis;
8. an audience-scoped export.

The product promise is:

> A facilitator can turn trusted sources into a live collective session whose generated activities and summaries remain inspectable, cited, privacy-aware, and exportable.

---

## P0 Product Scope

### P0 Loop

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

### P0 Features

| Capability | P0 decision | Boundary |
| --- | --- | --- |
| Source import | Facilitator can add files/URLs/text/transcripts as session sources. | Rumble initiates; Wrench extracts; Gear stores/indexes refs. |
| Source set | Versioned session-scoped selection of source refs. | Rumble stores selection and snapshots, not source truth. |
| Session | First-class product object with Draft/Prepared/Live/Closed/Synthesized/Exported/Archived states. | Rumble-owned. |
| Activities | Quiz, vote, reflection, discussion, summary checkpoint. | Rumble-owned workflow objects. |
| Generation | Generate draft activities/summaries from objective + source set + constraints. | Bolt orchestrates; Rumble validates and publishes. |
| Citation | Every generated source-grounded claim has citation candidates and must be validated or marked unsupported. | Rumble UX + Wrench advisory validation. |
| Responses | Participants submit while an activity run is open. | Rumble-owned, with explicit visibility snapshots. |
| Aggregate results | Participation counts, distribution, common themes, confusion/consensus signals. | Aggregate-only by default; no hidden individual profiling. |
| Synthesis | Facilitator validates an audience-specific summary. | Rumble-owned; generation may be Bolt-mediated. |
| Export | Markdown, HTML/PDF, JSON bundle. | Rumble selects audience/data classes; Gear stores artifact/ref/checksum. |

### P0 Non-Goals

- Open-ended chat with arbitrary questions outside session context.
- Global personal tutor mode.
- Course catalog, grades, assignments, certificates, enrollment management, or LMS administration.
- Internal crawling, parsing, transcription, embedding, or durable search substrate.
- Persistent learner profile, hidden skill graph, or cross-session behavioral scoring.
- Direct provider lock-in or silent third-party transmission.

---

## Dependency Contract

### Wrench Loader

`rumble-lm` consumes Wrench Loader for canonical extraction.

Rumble sends:

- source payload or reference;
- source type and policy context;
- workspace/session identifiers;
- requested extraction mode.

Wrench returns:

- normalized content metadata;
- chunk refs or chunk payloads for Gear persistence;
- provenance: origin, hash/revision if available, extraction timestamp, extractor version;
- extraction warnings and quality signals.

Rumble must not implement durable parsers, crawlers, OCR, transcription, or content-normalization pipelines except temporary adapters awaiting Wrench integration.

### Gear Memory

`rumble-lm` consumes Gear Memory for source refs, chunk refs, retrieval handles, provenance, and indexed context.

Rumble stores only:

- `SourceSet` membership;
- pinned source revisions;
- display snapshots;
- citation references;
- session-specific derived state.

Gear owns:

- `SourceRef`;
- `SourceChunkRef`;
- provenance records;
- retrieval/index handles;
- memory/search substrate.

Rumble must not become a vector database, long-term memory, or cross-session knowledge graph.

### Bolt

`rumble-lm` consumes Bolt for bounded generation orchestration and gates.

Rumble sends a structured request:

- session objective;
- audience;
- source set revision;
- allowed activity types;
- output schema;
- citation requirement;
- privacy constraints;
- model/provider policy context.

Bolt returns:

- generated draft activities or summaries;
- citation candidates;
- generation metadata;
- refusals or gate failures;
- warnings.

Bolt must not publish, validate on behalf of a facilitator, or own product state.

### Biscuit

`rumble-lm` consumes Biscuit as the shared delegated authorization primitive.

Rumble must not invent product-specific delegation tokens. It may mint or request attenuated Biscuit tokens for scoped calls into Wrench, Gear, Bolt, and export access.

---

## Delegated Rights Model

### Principles

- All delegated rights are workspace-scoped and time-bounded.
- Delegation is attenuated: downstream services receive only the rights needed for one operation.
- Tokens carry session/source/artifact constraints, not broad user authority.
- Revocation references are auditable.
- Participant anonymity settings are not bypassed by service delegation.

### Example Delegations

| Flow | Delegated token scope | Holder | Caveats |
| --- | --- | --- | --- |
| Source import | `can_import_source(workspace, session, source_set_revision)` | Wrench Loader | expiry, source type, max size, no export right |
| Source persistence | `can_write_source_ref(workspace, session, source_set_revision)` | Gear Memory | provenance required, no participant response access |
| Generation | `can_read_source_chunks(workspace, source_set_revision)` + `can_generate_draft(session)` | Bolt/generation adapter | citation-required, provider policy, no publish right |
| Citation validation | `can_validate_citation_candidate(session, target)` | Wrench validator | advisory result only, no facilitator approval right |
| Export artifact | `can_write_artifact(workspace, session, export_id, audience)` | Gear artifact store | included data classes, checksum required, TTL/revocation ref |
| Participant join | `can_submit_response(session, activity_run, participant_scope)` | Participant client/session | expiry, activity open, visibility snapshot |

### Required Biscuit Facts / Caveats Candidates

- `workspace(<id>)`
- `session(<id>)`
- `role(<actor>, "facilitator"|"participant"|"admin")`
- `source_set_revision(<session>, <revision>)`
- `activity_run(<id>)`
- `audience("facilitator"|"participants"|"admin_audit"|"machine_readable")`
- `visibility_mode(<mode>)`
- `expires_at(<timestamp>)`
- `revocation_id(<id>)`
- `provider_policy(<policy_ref>)`
- `data_classes_allowed([...])`

---

## Grounding Rules

### Claim Classes

Generated text must classify claims as:

| Claim class | Rule |
| --- | --- |
| Source-derived | Requires validated citation or explicit unsupported marker. |
| Facilitator-authored | Requires facilitator attribution; citation optional unless presented as source-derived. |
| Participant-derived | Must respect response visibility and audience. |
| System/process | Can cite session metadata or audit state where relevant. |
| Unsupported | Allowed only if visibly marked and not used to satisfy grounding gates. |

### Citation Validation

A citation is publishable only when:

1. it points to a stable source/chunk revision;
2. quoted text is inspectable by the facilitator;
3. support level is not `Weak`, `Contradicted`, or `NotReviewed` for mandatory grounding;
4. stale citations are re-reviewed after source set changes;
5. facilitator validation is recorded.

Wrench validation may provide support-level evidence, but human validation remains the product gate in P0.

---

## Anti-Chatbot Product Guardrails

`rumble-lm` may expose an assistant-like interaction only inside bounded actions such as “generate activities”, “explain this citation blocker”, or “draft a summary section”.

It must not provide a persistent unconstrained chat surface as the main experience.

Required UI guardrails:

- every generation action is attached to a session object;
- every request has source set, objective, audience, and output schema;
- generated outputs land as drafts requiring review;
- no direct answer is presented as authoritative without citation state;
- follow-up questions should become activities, summary edits, or facilitator notes, not an infinite chat transcript.

---

## Anti-LMS Product Guardrails

`rumble-lm` is not responsible for full learning administration.

Out of P0 scope:

- course catalog;
- learner enrollment lifecycle beyond session participation;
- gradebook;
- certificates;
- homework/assignments;
- long-term learner records;
- competency tracking across sessions.

Allowed P0 learning signals:

- aggregate quiz correctness when enabled;
- aggregate confusion/checkpoint results;
- common questions/themes;
- consensus/divergence by activity;
- facilitator-visible session recap.

---

## RGPD and Security Risks

| Risk | Severity | Control |
| --- | --- | --- |
| Hidden individual profiling through repeated responses or quiz scores | High | No cross-session learner profile in P0; aggregate analytics by default; scores only when explicitly enabled and disclosed. |
| Re-identification in “anonymous” summaries | High | Visibility snapshots; privacy gate before summary/export; aggregate-only mode; no retroactive deanonymization. |
| Private response leakage in logs/audit | High | Audit metadata excludes raw responses; structured reason codes only. |
| Unsupported generated claims | High | Citation gate; unsupported markers; facilitator validation. |
| Source personal/confidential data copied into exports | High | Export preview with included data classes; audience policy; source excerpt filtering. |
| Admin overreach into sensitive session content | Medium | Separate metadata/content permission; audited break-glass if later required. |
| Third-party model data transfer | High | Provider policy enforced before Bolt/generation; no silent provider fallback; deployment-configured residency/BYOK. |
| Delegated token abuse | High | Biscuit attenuation, expiry, revocation refs, workspace/session caveats, least privilege. |
| Durable memory creep inside Rumble | Medium | Store refs/snapshots only; source truth and retrieval handles remain Gear-owned. |

---

## Acceptance Tests for P0 Grounding

### Source Import and Provenance

Given a facilitator imports a supported source
When Wrench extraction succeeds and Gear returns source/chunk refs
Then Rumble shows the source in the session source set
And the source has provenance, revision/hash where available, and extraction warnings.

### Generation Requires Source Set

Given a facilitator requests source-grounded generation
When no ready source set exists
Then the request is refused with an actionable `source_set_required` blocker.

### Generated Activities Are Drafts

Given a ready source set
When activities are generated
Then activities are stored as `Draft`
And citation candidates are attached
And no participant can see them before facilitator publication.

### Citation Gate Blocks Preparation

Given a generated source-grounded activity contains a claim with no validated citation
When the facilitator prepares the session
Then preparation is blocked
And the blocker identifies the target claim and recovery actions.

### Weak Citation Cannot Satisfy Grounding

Given Wrench marks citation support as `Weak` or `Contradicted`
When the facilitator tries to validate it as mandatory grounding
Then the UI requires replacement, edit, or explicit unsupported marking.

### Source Revision Stales Citations

Given an activity cites source set revision 1
When the source is removed or replaced in revision 2
Then dependent citations become `Stale`
And publication/preparation gates fail until re-reviewed.

### Summary Support Validation

Given a generated summary includes source-derived claims
When the facilitator validates the summary
Then every source-derived claim has a validated citation or visible unsupported marker
And participant-derived content respects visibility policy.

### Export Evidence

Given a participant-facing export is generated
When the export is opened
Then it includes audience, included data classes, source/citation references, artifact ref, checksum, and generation/validation timestamps.

### No Hidden Profiling

Given participants submit quiz and reflection responses across a session
When the facilitator views analytics
Then the default dashboard shows aggregate counts/distributions/themes only
And no cross-session individual score/profile is created.

### Delegated Rights

Given Rumble delegates a source import to Wrench
When the token is inspected by policy tests
Then it is scoped to workspace/session/source operation, has expiry, and cannot read participant responses or export artifacts.

---

## Inspiration Pattern Analysis

External references are used only as discovery input. The durable product spec should retain ecosystem language and boundaries.

Useful patterns:

- source notebook pattern: source list, grounded generation, visible citations;
- RAG pattern: retrieval must be explainable, bounded, and validated;
- evaluation pattern: automated checks produce evidence but do not replace human publication gates;
- local speech/media pattern: useful later for transcripts or audio accessibility, but belongs behind Wrench/media adapters;
- prototyping UI pattern: useful for demos, but not a production architecture boundary;
- LLM app catalog pattern: useful to identify recurring workflows, not as a dependency source.

Rejected patterns:

- open-ended chat as primary navigation;
- invisible model memory;
- unreviewed “answer engine” behavior;
- demo-framework-driven architecture;
- learner scoring/profiling as a default analytics model.

---

## ADR Candidates

1. **ADR: `rumble-lm` P0 is synchronous source-grounded live sessions.**
   - Decision: P0 centers on live sessions, activities, citations, aggregate signals, synthesis, and export.
   - Consequence: async course/LMS features are deferred.

2. **ADR: Rumble LM stores source references, not source truth.**
   - Decision: Wrench Loader + Gear Memory own extraction, source refs, chunks, provenance, and retrieval handles.
   - Consequence: Rumble keeps session source-set membership and snapshots only.

3. **ADR: Source-grounded generation is mediated by Bolt and citation-gated by Rumble.**
   - Decision: Bolt orchestrates drafts; Rumble owns facilitator validation and publication.
   - Consequence: no generated draft becomes participant-visible automatically.

4. **ADR: Biscuit is the only delegated authorization primitive.**
   - Decision: all service-to-service delegation uses attenuated Biscuit tokens.
   - Consequence: no per-product signed URLs/tokens except as adapters backed by Biscuit policy.

5. **ADR: No hidden individual profiling in MVP.**
   - Decision: analytics are aggregate by default; individual scores require explicit mode, notice, and retention policy.
   - Consequence: product success is collective learning/facilitation, not learner surveillance.

6. **ADR: Citation support validation is evidence, not authority.**
   - Decision: Wrench can advise support level; facilitator validation remains required for publication/export in P0.
   - Consequence: automated validation reduces risk but does not assume correctness.

7. **ADR: Exports are Gear artifacts with audience-scoped manifests.**
   - Decision: Rumble owns export semantics; Gear owns artifact refs, checksums, and retention/revocation metadata.
   - Consequence: exported evidence is verifiable and portable.

---

## Open Follow-Ups

- Define exact `SourceGroundedGenerationRequest` schema shared with Bolt.
- Define first Biscuit authorizer facts/caveats for Rumble→Wrench/Gear/Bolt delegation.
- Decide whether citation support validation starts as Wrench Inspect or a dedicated Wrench validator.
- Decide retention defaults for raw responses, summaries, exports, and audit events.
- Decide if speech/transcript ingestion is P0 only through pre-existing text transcripts or via Wrench media extraction.
