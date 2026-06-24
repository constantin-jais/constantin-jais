# Acceptance Tests — rumble-lm

Status: Draft.

## Test Strategy

Acceptance tests should prove the complete MVP loop:

```text
create session → import sources → generate/select activities → validate citations → run live → collect responses → synthesize → export/archive
```

Tests are organized by product behavior, permissions, domain invariants, API contracts, privacy, and resilience.

## Scenario Tests

### Scenario: Create and Prepare Source-Grounded Session

Given a facilitator has workspace permission
And a draft session has title and objective
And at least one source has imported successfully
And a generated activity has validated citations
When the facilitator prepares the session
Then the session status becomes `Prepared`
And `session.prepared` is recorded
And the prepared revision references the source set revision.

### Scenario: Preparation Blocked by Missing Citations

Given a draft session contains a source-grounded generated activity
And the activity has no validated citation or unsupported marker
When the facilitator attempts to prepare the session
Then preparation is blocked
And the response includes a citation blocker with recovery guidance.

### Scenario: Source Import Partial Failure

Given a facilitator imports three sources
When two imports succeed and one fails
Then the two successful sources are available in the source set
And the failed source shows an actionable reason
And successful sources are not rolled back.

### Scenario: Activity Generation Creates Citation Candidates

Given a ready source set
When the facilitator generates quiz and reflection activities
Then draft activities are created
And source-derived prompts/options have citation candidates
And no generated activity is published automatically.

### Scenario: Run Live Activity

Given a session is `Prepared`
And it contains a published activity
When the facilitator starts the session and starts the activity
Then session status is `Live`
And exactly one activity run is open
And participants can see the current activity.

### Scenario: Participant Submits Response

Given a participant joined a live session
And an activity run is open
When the participant submits a valid response
Then the response is stored
And visibility settings are snapshotted
And the audit event does not include raw response content.

### Scenario: Duplicate Response Submission

Given an activity allows one response per participant
And a participant submits a response with an idempotency key
When the same request is retried
Then no duplicate response is created
And the participant receives the original accepted result.

### Scenario: Close Session and Freeze Responses

Given a session is `Live`
When the facilitator closes the session
Then all open activity runs are closed
And no new participant responses are accepted
And response records become immutable except privacy workflows.

### Scenario: Generate Participant-Facing Summary

Given a session is `Closed`
And participant responses include private free text
When the facilitator generates a participant-facing summary
Then private response content is excluded or anonymized
And unsupported source-derived claims are flagged.

### Scenario: Validate Summary

Given a summary draft contains source-derived claims
When all claims have validated citations or explicit unsupported markers
And privacy blockers are resolved
Then the facilitator can validate the summary
And the session becomes `Synthesized`.

### Scenario: Export Session

Given a session is `Synthesized`
When the facilitator exports a participant-facing Markdown artifact
Then the export includes only allowed data classes
And records format, audience, actor, timestamp, included data, and artifact reference.

### Scenario: Archive Session

Given a session is `Exported`
When the facilitator archives it
Then the session becomes read-only
And normal edits are blocked
And a follow-up session can be created instead.

## Permission Tests

### Facilitator Permissions

- Can create, edit, prepare, run, close, summarize, and export own/assigned sessions.
- Cannot silently change submitted responses.
- Cannot publish source-grounded generated content without citation resolution.

### Participant Permissions

- Can join only allowed sessions.
- Can view only current/published participant state.
- Can submit only while activity run is open.
- Cannot see private responses from others.
- Cannot access facilitator-only summaries or exports.

### Admin Permissions

- Can manage workspace policy and roles.
- Can view session metadata.
- Content access depends on policy.
- Cannot impersonate facilitator/participant.
- Admin actions are audited.

## Domain Invariant Tests

- A session cannot transition `Draft` → `Live` directly.
- A session cannot become `Prepared` without at least one publishable activity.
- Only one activity run can be open per session in MVP.
- A running/closed activity cannot be structurally edited.
- A response cannot be submitted after activity close.
- A validated citation references an existing source/chunk revision.
- Rejected/stale citations do not satisfy grounding requirements.
- Participant-facing summaries enforce visibility policy.
- Exports record included data and audience.

## API Contract Tests

### `POST /sessions/:id/prepare`

- Returns success when readiness checks pass.
- Returns structured blocker errors when checks fail.
- Is idempotent if session is already prepared with same revision.

### `POST /sessions/:id/sources/import`

- Accepts supported source types.
- Rejects unsupported source types with actionable error.
- Emits import request event.

### `POST /activities/generate`

- Requires source set for source-grounded generation.
- Returns activities matching schema.
- Stores generation metadata without secrets.

### `POST /activity-runs/:id/responses`

- Validates participant/session/activity state.
- Validates response payload schema.
- Handles duplicate idempotency key safely.

### `POST /summaries/:id/validate`

- Blocks unresolved privacy/citation issues.
- Emits validation event on success.

### `POST /sessions/:id/exports`

- Enforces audience policy.
- Returns artifact reference and export metadata.

## Security / RGPD Tests

- Anonymous-to-participants mode hides identities from participant views.
- Aggregate-only mode prevents individual response display.
- Response content is absent from audit log metadata.
- Participant-facing export excludes facilitator-only notes.
- Deletion/anonymization workflow removes or masks participant identity according to policy.
- Permission denied responses do not reveal hidden session content.
- Join links expire or follow configured access policy.
- CSRF-protected writes reject missing/invalid CSRF token when cookie-authenticated.

## Screen Smoke Tests

- Workspace session list loads permitted sessions.
- Session setup displays readiness checklist and blockers.
- Source import displays success/failure per source.
- Activity builder shows citation readiness.
- Citation review can validate/reject/replace citations.
- Live facilitator console starts/closes an activity.
- Participant view submits a response and shows confirmation.
- Results dashboard displays aggregates according to visibility.
- Summary editor blocks unsafe publish.
- Export screen generates an allowed artifact.

## Migration Tests

- Adding a new activity type does not break existing activities.
- Adding new visibility mode preserves existing visibility snapshots.
- Summary revisions remain readable after schema changes.
- Export metadata remains inspectable after artifact-store changes.

## Observability Tests

- Failed preparation logs blocker reason without sensitive content.
- Failed import logs reason code and source ref, not raw content.
- Failed response submission logs state/reason, not response content.
- Export failure logs format/audience/reason, not private content.

## MVP Definition of Done

- End-to-end scenario passes for one source-grounded live session.
- Permission tests pass for Admin, Facilitator, Participant.
- Citation gating prevents unsupported generated content from being silently published.
- Participant response privacy is enforced in results, summary, and export.
- Export artifact is generated with traceable metadata.
