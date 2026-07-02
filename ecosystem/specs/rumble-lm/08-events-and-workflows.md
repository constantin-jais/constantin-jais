# Events and Workflows — rumble-lm

Status: Draft.

## Event Principles

- Events must be human- and agent-readable.
- Events must not contain secrets or raw sensitive response content.
- Events should include actor snapshot, workspace ID, session ID when applicable, target type/id, timestamp, and schema version.
- Audit-relevant events are append-only.

## Event Payload Base

```json
{
  "schema": "rumble_lm.event.v0.1",
  "eventName": "session.created",
  "workspaceId": "...",
  "sessionId": "...",
  "actor": { "id": "...", "kind": "human", "displayName": "..." },
  "target": { "type": "session", "id": "..." },
  "metadata": {},
  "createdAt": "2026-06-30T00:00:00Z"
}
```

## Core Events

| Event | Producer | Consumers | Audit | Notes |
| --- | --- | --- | --- | --- |
| `session.created` | SessionService | UI, audit, analytics | Yes | New draft session |
| `session.updated` | SessionService | UI, audit | Yes | Metadata/settings changed |
| `session.prepared` | SessionService | UI, live readiness | Yes | Prepared revision locked |
| `session.started` | LiveSessionService | Live UI, participants | Yes | Live mode begins |
| `session.paused` | LiveSessionService | Live UI | Yes | Optional pause |
| `session.closed` | LiveSessionService | Summary/results | Yes | Response collection ends |
| `session.synthesized` | SummaryService | Export UI | Yes | Validated summary exists |
| `session.archived` | SessionService | Lists, retention | Yes | Read-only archive |
| `source.import_requested` | SourceSetService | Import worker | Yes | No raw content in event |
| `source.import_completed` | ImportPipeline | Source UI, generation | Yes | Includes source refs/status |
| `source.import_failed` | ImportPipeline | Source UI | Yes | Includes reason code |
| `source_set.updated` | SourceSetService | Activity/citation invalidation | Yes | Revision change |
| `source_set.locked` | SourceSetService | Generation/citation review | Yes | Prepared source revision |
| `activity.generation_requested` | ActivityService | Bolt/generation | Yes | Includes constraints |
| `activity.generated` | Generation adapter | Activity UI | Yes | Drafts created |
| `activity.updated` | ActivityService | UI, audit | Yes | Prompt/settings changed |
| `activity.validated` | ActivityService | Readiness checks | Yes | Citation requirements satisfied |
| `activity.published` | ActivityService | Participant/live views | Yes | Available for run |
| `activity.started` | LiveSessionService | Participant UI | Yes | Activity run open |
| `activity.closed` | LiveSessionService | Results | Yes | No more responses |
| `participant.joined` | ParticipantService | Live presence | Limited | Avoid PII if anonymous |
| `participant.left` | ParticipantService | Live presence | Limited |  |
| `response.submitted` | ResponseService | Results/live counts | Yes | No raw content in audit metadata |
| `response.anonymized` | Privacy workflow | Audit/results | Yes | Privacy action |
| `citation.candidate_created` | Generation adapter | Citation review | Yes |  |
| `citation.validated` | CitationService | Readiness, export | Yes | Human validation evidence |
| `citation.rejected` | CitationService | Readiness blockers | Yes |  |
| `citation.stale` | SourceSetService | Citation review | Yes | Source changed/removed |
| `summary.generation_requested` | SummaryService | Bolt/generation | Yes |  |
| `summary.generated` | Generation adapter | Summary editor | Yes | Draft created |
| `summary.validated` | SummaryService | Export | Yes | Human validation evidence |
| `summary.published` | SummaryService | Participants | Yes | Audience-specific |
| `export.requested` | ExportService | Artifact pipeline | Yes |  |
| `export.generated` | ExportService | UI, artifact store | Yes | Includes artifact ref/checksum |
| `export.failed` | ExportService | UI, observability | Yes | Reason code |
| `export.revoked` | ExportService | UI, audit | Yes | If supported |

## Workflow: Prepare Session

### Trigger

Facilitator clicks `Prepare` from setup.

### Steps

1. Validate required metadata.
2. Validate source set state if activities are source-grounded.
3. Validate at least one published or publishable activity.
4. Check citation resolution for all mandatory source-grounded claims.
5. Record prepared revision.
6. Emit `session.prepared`.

### Gates

- Missing objective blocks.
- No activities blocks.
- Unresolved source-grounded citations block unless explicitly marked unsupported/facilitator-authored.

### Rollback

If transition fails, session remains `Draft` and blockers are returned.

### Evidence

Readiness checklist, citation statuses, actor/timestamp.

## Workflow: Import Sources

### Trigger

Facilitator uploads or references a source.

### Steps

1. Create import request.
2. Gear Loader extracts text/metadata/chunks.
3. Gear stores source/chunk refs and provenance.
4. Rumble updates source set revision.
5. Existing citations are checked for staleness.

### Gates

- Workspace source policy.
- File size/type limits.
- Extraction quality threshold warning, not always blocker.

### Retry

Failed source can be retried or replaced independently.

### Evidence

Import status, source hash/provenance, extraction warnings.

## Workflow: Generate Activities

### Trigger

Facilitator requests source-grounded agenda/activities.

### Steps

1. Build generation request with objective, audience, source set revision, constraints.
2. Bolt/generation adapter returns structured drafts and citation candidates.
3. Validate response schema.
4. Store drafts as `Activity` in `Draft` state.
5. Emit `activity.generated` and `citation.candidate_created`.

### Gates

- Source set must be ready.
- Generated content must conform to schema.
- No publication without citation resolution.

### Evidence

Generation metadata, source set revision, output schema version.

## Workflow: Run Live Activity

### Trigger

Facilitator starts an activity from the live console.

### Steps

1. Check session is `Live`.
2. Check activity is `Published` or otherwise valid to run.
3. Ensure no other activity run is open.
4. Create `ActivityRun`.
5. Broadcast live state.
6. Accept responses until closed.

### Gates

- Activity must not have unresolved readiness blockers.
- Participant access policy must be configured.

### Retry/Rollback

If broadcast fails after run creation, facilitator can close or retry broadcast. Run creation is audited.

### Evidence

Activity run timestamps, actor, response counts.

## Workflow: Submit Response

### Trigger

Participant submits an answer.

### Steps

1. Validate participant session.
2. Validate activity run is open.
3. Validate payload against response schema.
4. Apply idempotency rule.
5. Snapshot visibility/anonymity mode.
6. Store response.
7. Emit `response.submitted` without raw content in audit metadata.
8. Update live aggregate counts.

### Gates

- Activity open.
- Schema valid.
- Participant allowed.

### Evidence

Response record, submission timestamp, visibility snapshot.

## Workflow: Generate and Validate Summary

### Trigger

Facilitator requests a post-session summary.

### Steps

1. Select audience and included data.
2. Build context from activities, aggregate results, allowed responses, citations, source set.
3. Generate draft summary.
4. Flag unsupported claims and privacy risks.
5. Facilitator edits and validates.
6. Emit `summary.validated` and `session.synthesized` if first validated summary.

### Gates

- Session must be `Closed` or later.
- Participant-facing summary must pass privacy policy.
- Source-derived claims require citation resolution.

### Evidence

Summary revision, generation metadata, validation actor/timestamp.

## Workflow: Export Session

### Trigger

Facilitator/Admin requests export.

### Steps

1. Select format, audience, and included data.
2. Check export policy and privacy rules.
3. Build export package from allowed session snapshot.
4. Store artifact in Gear candidate store.
5. Record checksum/artifact ref.
6. Emit `export.generated`.

### Gates

- Unvalidated participant-facing summary may block participant export.
- Private response data excluded unless explicitly allowed.

### Evidence

Export metadata, included data classes, artifact ref/checksum, actor/timestamp.

## Replay Behavior

- Audit/event log can reconstruct lifecycle and major user actions.
- Raw session state should not rely solely on replay in MVP.
- Response content and exports are stored in primary tables/artifact store, not embedded in event payloads.
