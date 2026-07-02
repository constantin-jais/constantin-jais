# P0 Stub Implementation Plan — rumble-lm

Status: Draft implementation plan, not code.  
Depends on: [`15-contracts-v0.1.md`](./15-contracts-v0.1.md), [`16-contract-review-pack.md`](./16-contract-review-pack.md).

## Purpose

This plan defines the smallest implementation slice allowed before real Wrench/Gear/Bolt/Biscuit integrations are ready.

The goal is to prove product workflow and contracts without creating permanent product-local ingestion, memory, orchestration, artifact, or authorization subsystems.

---

## Allowed Stub Principle

A stub is allowed only if it is:

- contract-shaped;
- deterministic;
- visibly marked as stubbed;
- replaceable by the lower-layer owner;
- forbidden from becoming durable hidden infrastructure.

Stub outputs must include:

```json
{
  "stubbed": true,
  "replaceWith": "gear-loader | gear-memory | bolt | biscuit | gear-depot",
  "contractVersion": "v0.1"
}
```

---

## Vertical P0 Slice

```text
1. Facilitator creates draft session
2. Facilitator attaches one source ref through SourceSetService
3. Stub Wrench/Gear returns source/chunk/provenance refs
4. Facilitator requests source-grounded activity generation
5. Stub Bolt returns draft activity + citation candidate
6. Facilitator validates citation
7. Facilitator publishes activity
8. Participant submits response while activity run is open
9. Facilitator closes session
10. Stub Bolt returns summary draft
11. Facilitator validates summary
12. Stub Gear returns export artifact ref/checksum/manifest
```

---

## Minimal Services

### SessionService

Owns:

- create session;
- update metadata/settings;
- prepare/start/close/synthesize/export/archive transitions;
- readiness blockers.

Must not own:

- ingestion;
- generation orchestration;
- source truth;
- artifact storage.

### SourceSetService

Owns:

- session source-set membership;
- pinned revision;
- stale citation marking when source set changes.

Stub dependency:

- `StubSourceIngestionAdapter` emits Wrench/Gear-shaped refs.

Exit condition:

- replace with Gear Loader + Gear Memory calls.

### ActivityService

Owns:

- activity drafts;
- edit/reorder/publish;
- citation blockers;
- output schema validation.

Stub dependency:

- `StubGenerationAdapter` emits Bolt-shaped generation response.

Exit condition:

- replace with Bolt `SourceGroundedGenerationRequest`.

### CitationService

Owns:

- citation candidate status;
- facilitator validation/rejection/replacement;
- stale detection.

Stub dependency:

- optional `StubCitationSupportValidator` emits Wrench-shaped support result.

Exit condition:

- replace with Wrench validator/inspect capability.

### LiveSessionService

Owns:

- start/close session live state;
- one open activity run in P0;
- server-side run state.

Must not own:

- shared live transport abstraction beyond local product need.

### ResponseService

Owns:

- participant response schema validation;
- idempotency;
- visibility snapshot;
- immutable-after-close rules.

Must not:

- create cross-session learner profiles;
- log raw response content.

### SummaryService

Owns:

- summary draft persistence;
- privacy/citation gate;
- facilitator validation;
- audience-specific publishing.

Stub dependency:

- `StubGenerationAdapter` for summary draft only.

### ExportService

Owns:

- audience and included data classes;
- privacy blocker preview;
- manifest request;
- export metadata.

Stub dependency:

- `StubArtifactAdapter` emits Gear artifact-shaped ref/checksum/manifest.

Exit condition:

- replace with Gear artifact/depot capability.

---

## Stub Adapters

| Stub | Replaces temporarily | Required output | Hard forbidden |
| --- | --- | --- | --- |
| `StubSourceIngestionAdapter` | Gear Loader + Gear Memory | `SourceRef`, `SourceChunkRef`, provenance hash, warnings | parsing arbitrary documents, durable indexing |
| `StubGenerationAdapter` | Bolt | draft activity/summary, citation candidate refs, refusal codes | publishing, model routing, hidden memory |
| `StubCitationSupportValidator` | Wrench validator | support level + explanation | final validation authority |
| `StubArtifactAdapter` | Gear artifact/depot | artifact ref, checksum, manifest, revocation ref | opaque file store, unverifiable export |
| `StubDelegationVerifier` | Biscuit runtime | accepted/rejected fixture-like facts | product-specific token format |

---

## Minimal Data Needed for Stub P0

Reuse existing model tables where possible:

- `sessions`
- `source_sets`
- `source_set_items`
- `activities`
- `citations`
- `activity_runs`
- `participants`
- `responses`
- `summaries`
- `exports`
- `audit_events`

Stub-specific metadata may be stored in `generated_metadata` or adapter metadata fields, with:

```json
{
  "stubbed": true,
  "replaceWith": "bolt",
  "contract": "rumble_lm.source_grounded_generation_response.v0.1"
}
```

No separate durable stub database is allowed.

---

## API Slice

Implement only:

- `POST /workspaces/:workspaceId/sessions`
- `POST /sessions/:sessionId/sources/import`
- `POST /sessions/:sessionId/activities/generate`
- `POST /citations/:citationId/validate`
- `POST /activities/:activityId/publish`
- `POST /sessions/:sessionId/prepare`
- `POST /sessions/:sessionId/start`
- `POST /activities/:activityId/start`
- `POST /activity-runs/:activityRunId/responses`
- `POST /activities/:activityId/close`
- `POST /sessions/:sessionId/close`
- `POST /sessions/:sessionId/summary/generate`
- `POST /summaries/:summaryId/validate`
- `POST /sessions/:sessionId/exports`

No open-ended `/chat` endpoint.

---

## Acceptance Gates Before Coding

Must be green:

```bash
python3 ecosystem/specs/rumble-lm/run_p0_contract.py
```

Must be reviewed or explicitly deferred-with-stub:

- Bolt generation contract;
- Wrench citation support contract;
- Gear source/export contract;
- Biscuit delegation profile.

---

## Runtime Acceptance Tests for First Stub P0

Given a facilitator creates a session and imports a source through the stub adapter
Then the source set contains Gear-shaped refs and Wrench-shaped provenance.

Given the facilitator generates activities
Then generated activities are drafts and cannot be participant-visible before publication.

Given a generated claim has no validated citation
Then prepare/publish is blocked.

Given a participant submits a response
Then raw response content is not present in audit logs.

Given a participant-facing export is requested
Then private responses and facilitator-only notes are excluded by default.

Given any stub output is produced
Then it contains `stubbed=true`, `replaceWith`, and contract version metadata.

---

## Exit Criteria from Stub Mode

Stub can be removed when:

- Gear Loader returns canonical source candidates accepted by SourceSetService;
- Gear Memory stores/returns source refs, chunk refs, provenance, and retrieval handles;
- Bolt accepts `SourceGroundedGenerationRequest` and returns draft/refusal contract;
- Wrench citation validator returns support evidence or the feature is explicitly deferred;
- Gear artifact/depot stores export artifact refs/checksums/manifests;
- Biscuit verifier enforces LM delegation profile.

Each replacement must keep the fixture contract proof green.

---

## Explicit Non-Goals

- No generic chatbot.
- No LMS features.
- No durable internal ingestion.
- No durable internal memory/search/vector DB.
- No product-owned model router.
- No product-specific internal delegation tokens.
- No individual learner profile.
- No raw PII/secrets/tokens in logs.
