# Services and APIs — rumble-lm

Status: Draft.

## Service Boundary Doctrine

`rumble-lm` owns product workflow and user-facing session logic. It consumes shared capabilities for source ingestion, generation orchestration, validation, storage, audit, and artifacts.

## Rumble App Services

### SessionService

- **Owner layer:** Rumble.
- **Responsibilities:** create sessions, update settings, enforce lifecycle transitions, archive sessions.
- **Inputs:** workspace ID, actor, session metadata, settings.
- **Outputs:** session records and lifecycle state.
- **Auth:** facilitator/admin permissions.
- **Idempotency:** create may use client request ID; lifecycle transitions should be idempotent where safe.
- **Failure modes:** permission denied, invalid transition, missing readiness checks.
- **Observability:** lifecycle event logs, transition failures by reason.
- **Tests:** transition matrix, permission tests, readiness blockers.

### SourceSetService

- **Owner layer:** Rumble orchestration around Wrench/Gear.
- **Responsibilities:** attach sources to sessions, track source set revisions, react to import status.
- **Inputs:** source files/URLs/text refs, session ID.
- **Outputs:** source set status, source refs, provenance snapshots.
- **Auth:** facilitator can manage session sources; admin according to policy.
- **Failure modes:** import failed, source unavailable, policy denied.
- **Tests:** partial import success, stale citations after removal.

### ActivityService

- **Owner layer:** Rumble.
- **Responsibilities:** create/edit/reorder/publish activities; enforce activity lifecycle.
- **Inputs:** activity schema, source set refs, generation request.
- **Outputs:** activities and citation candidates.
- **Auth:** facilitator.
- **Failure modes:** invalid response schema, locked/running activity edit, unresolved citations.
- **Tests:** publish blockers, activity run edit restrictions.

### LiveSessionService

- **Owner layer:** Rumble with possible shared live transport later.
- **Responsibilities:** start/pause/close live session and activity runs; publish live state.
- **Inputs:** session ID, activity ID, actor.
- **Outputs:** live state, activity run state.
- **Auth:** facilitator controls; participant reads allowed live state.
- **Failure modes:** transport unavailable, invalid session status, duplicate run.
- **Tests:** one open run per session, reconnect behavior, close-all on session end.

### ResponseService

- **Owner layer:** Rumble.
- **Responsibilities:** validate and store participant responses.
- **Inputs:** participant ID, activity run ID, response payload.
- **Outputs:** accepted response and submission status.
- **Auth:** participant access to session/activity.
- **Idempotency:** submission key per activity/participant/client request.
- **Failure modes:** activity closed, invalid schema, duplicate not allowed, permission denied.
- **Tests:** schema validation, anonymous visibility snapshot, duplicate handling.

### CitationService

- **Owner layer:** Rumble with Wrench validation candidate.
- **Responsibilities:** manage citation candidates, validation/rejection/replacement, support-level tracking.
- **Inputs:** target claim, source chunk refs, facilitator decision.
- **Outputs:** citation status and blockers.
- **Auth:** facilitator validates; admin read per policy.
- **Failure modes:** stale source, missing chunk, weak support.
- **Tests:** source-grounded publication blocked without citation resolution.

### SummaryService

- **Owner layer:** Rumble consuming generation/validation capabilities.
- **Responsibilities:** generate, edit, validate, publish summaries.
- **Inputs:** session results, source set, citations, audience.
- **Outputs:** summary draft/revision.
- **Auth:** facilitator; participant reads published permitted summary.
- **Failure modes:** insufficient data, privacy violation, unresolved citations.
- **Tests:** privacy rules, citation requirements, revisioning.

### ExportService

- **Owner layer:** Rumble + Gear artifact candidate.
- **Responsibilities:** generate exports, record included data, produce artifact ref/checksum.
- **Inputs:** session ID, format, audience, included data config.
- **Outputs:** artifact reference or failure.
- **Auth:** facilitator/admin per policy.
- **Failure modes:** invalid audience, unvalidated summary, private data leak blocker.
- **Tests:** export data filtering, artifact metadata, audit event.

## Bolt Calls

### SourceGroundedGenerationRequest

- **Purpose:** request activity or summary draft generation from selected source set and objective.
- **Owner:** Bolt orchestrates generation plan; Rumble owns product request and final validation.
- **Input:** session ID, source set revision, objective, audience, activity types, constraints, output schema.
- **Output:** generated draft activities/summaries, citation candidates, generation metadata.
- **Auth:** facilitator request; Bolt cannot publish directly.
- **Gates:** human validation before publication.
- **Failure modes:** insufficient grounding, generation refused, invalid schema.

### ValidationGateRequest

- **Purpose:** ask for checks before publication/export.
- **Input:** activity/summary IDs, citations, policy context.
- **Output:** pass/fail/warnings with evidence.
- **Use:** optional MVP; likely post-MVP if Wrench validator is not ready.

## Wrench Calls

### ImportPipeline

- **Purpose:** extract canonical content from files/URLs/transcripts/text.
- **Input:** source payload or reference.
- **Output:** source metadata, chunks, provenance, extraction warnings.
- **Failure modes:** unsupported format, inaccessible source, low extraction quality.

### CitationSupportValidator

- **Purpose:** assess whether a citation supports a generated claim.
- **Input:** claim, quoted excerpt, surrounding context.
- **Output:** support level, explanation, warnings.
- **MVP:** advisory only; facilitator remains final validator.

## Gear Calls

### SourceStore / Memory

- **Purpose:** persist source refs, chunks, provenance, retrieval index.
- **Input:** normalized source content and metadata.
- **Output:** source refs, chunk refs, retrieval handles.

### EventLog

- **Purpose:** append audit/domain events.
- **Input:** event name, actor snapshot, target, metadata.
- **Output:** event ID, timestamp.

### ArtifactStore

- **Purpose:** store export artifacts and checksums.
- **Input:** export package content and metadata.
- **Output:** artifact ref, checksum, access metadata.

## API Endpoints MVP

### Sessions

- `GET /workspaces/:workspaceId/sessions`
- `POST /workspaces/:workspaceId/sessions`
- `GET /sessions/:sessionId`
- `PATCH /sessions/:sessionId`
- `POST /sessions/:sessionId/prepare`
- `POST /sessions/:sessionId/start`
- `POST /sessions/:sessionId/close`
- `POST /sessions/:sessionId/archive`

### Sources

- `GET /sessions/:sessionId/source-set`
- `POST /sessions/:sessionId/sources/import`
- `DELETE /sessions/:sessionId/sources/:sourceRef`
- `POST /sessions/:sessionId/source-set/lock`

### Activities

- `GET /sessions/:sessionId/activities`
- `POST /sessions/:sessionId/activities`
- `POST /sessions/:sessionId/activities/generate`
- `PATCH /activities/:activityId`
- `POST /sessions/:sessionId/activities/reorder`
- `POST /activities/:activityId/publish`
- `POST /activities/:activityId/start`
- `POST /activities/:activityId/close`

### Participants and Responses

- `POST /join/:sessionCode`
- `GET /participant/:participantSessionId/state`
- `POST /activity-runs/:activityRunId/responses`
- `PATCH /responses/:responseId` only before close if allowed

### Citations

- `GET /sessions/:sessionId/citations`
- `POST /citations/:citationId/validate`
- `POST /citations/:citationId/reject`
- `POST /citations/:citationId/replace`

### Summaries and Exports

- `POST /sessions/:sessionId/summary/generate`
- `PATCH /summaries/:summaryId`
- `POST /summaries/:summaryId/validate`
- `POST /summaries/:summaryId/publish`
- `POST /sessions/:sessionId/exports`
- `GET /exports/:exportId`

## Cross-Cutting Requirements

### Auth

Every write endpoint requires actor, workspace, and product-role checks. Participant response endpoints require session access and current activity state.

### Idempotency

Use client request IDs for:

- session creation;
- source import requests;
- response submission;
- export generation.

### Rate Limits

Apply per workspace and per session for generation, imports, live response submissions, and exports.

### Observability

Track:

- lifecycle transition failures;
- import failure reasons;
- generation requests and refusals;
- citation blocker counts;
- live transport health;
- export failures;
- privacy policy blockers.

### Error Shape

Errors should be agent-readable and user-actionable:

```json
{
  "code": "citation_required",
  "message": "This activity has source-grounded claims without validated citations.",
  "target": { "type": "activity", "id": "..." },
  "recovery": "Validate citations, edit the claim, or mark it as unsupported."
}
```
