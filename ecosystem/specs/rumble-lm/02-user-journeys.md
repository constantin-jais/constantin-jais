# User Journeys — rumble-lm

Status: Draft.

## MVP Journey Map

The MVP proves one complete loop:

```text
create session → import sources → generate/select activities → validate citations → run live → collect responses → synthesize → export/archive
```

Core product rule: every generated activity or synthesis claim derived from sources must remain traceable to citations or be explicitly marked as facilitator-authored / unsupported by sources.

---

## Journey: Create a Session

### Trigger

A facilitator needs to prepare a learning or facilitation session for a group.

### Actor

Facilitator.

### Preconditions

- Facilitator has access to a workspace.
- Workspace policy allows session creation.

### Happy Path

1. Facilitator creates a new session.
2. Facilitator enters title, objective, expected audience, expected duration, and session mode.
3. System creates the session in `Draft` status.
4. Facilitator chooses response visibility defaults: named, anonymous, or configurable per activity.
5. System shows the preparation checklist: sources, activities, live settings, export settings.

### Alternate Paths

- Facilitator creates from a previous session template.
- Facilitator creates a session without sources but cannot generate source-grounded activities yet.
- Admin creates an empty session and assigns a facilitator.

### Failure Paths

- Missing required title or objective.
- Facilitator lacks permission.
- Workspace policy requires retention/export settings before participants can be invited.

### Recovery Path

- Save as incomplete draft.
- Display missing fields and policy blockers.

### Data Created or Updated

- `Session` created.
- Initial `SessionSettings` created.
- Audit event recorded.

### Events Emitted

- `session.created`
- `session.settings_updated`

### Audit Requirements

Record actor, workspace, timestamp, initial settings, and session owner.

### Acceptance Criteria

- Given a facilitator with create permission, when required fields are provided, then a `Draft` session exists.
- Given missing objective, when creating the session, then creation is blocked or saved as incomplete draft with visible missing fields.

---

## Journey: Import Sources

### Trigger

The facilitator wants activities and synthesis to be grounded in specific material.

### Actor

Facilitator.

### Preconditions

- Session exists in `Draft` or `Prepared` status.
- Source type is allowed by workspace policy.

### Happy Path

1. Facilitator adds files, URLs, text, notes, or transcripts.
2. System sends sources to the import pipeline.
3. Imported content is normalized into source records, chunks, metadata, and provenance.
4. System presents import status, errors, and extracted structure.
5. Facilitator reviews source titles and removes irrelevant sources.
6. System creates or updates the session `SourceSet`.

### Alternate Paths

- Facilitator manually adds a short source excerpt.
- Source import is asynchronous and session remains editable while processing.
- Some sources succeed while others fail.

### Failure Paths

- Unsupported file type.
- Source is inaccessible.
- Extracted text is empty or too low quality.
- Source violates workspace policy.

### Recovery Path

- Show failed source with reason.
- Allow retry, replacement, or manual text entry.
- Keep successful sources available.

### Data Created or Updated

- `SourceSet`
- `Source`
- `SourceChunk`
- `Provenance` metadata

### Events Emitted

- `source.import_requested`
- `source.import_completed`
- `source.import_failed`
- `source_set.updated`

### Audit Requirements

Record actor, source metadata, import time, provenance, source hash when available, and deletion/removal events.

### Acceptance Criteria

- Given a supported source, when import succeeds, then the source is available for activity generation with provenance.
- Given a failed source, when import ends, then the facilitator sees an actionable error and successful sources remain usable.

---

## Journey: Generate or Select Activities

### Trigger

The facilitator needs a structured session agenda with interactive activities.

### Actor

Facilitator.

### Preconditions

- Session has an objective.
- At least one source is imported for source-grounded generation.
- Session is in `Draft` or `Prepared` status.

### Happy Path

1. Facilitator requests activities for the session objective, audience, duration, and selected source set.
2. System proposes a sequence of activities: quiz, vote, reflection, discussion, and summary checkpoint.
3. Each generated activity includes objective, prompt, expected duration, response mode, source references, and citation candidates.
4. Facilitator edits, reorders, accepts, or rejects activities.
5. Accepted activities remain in `Draft` until citations are validated.

### Alternate Paths

- Facilitator creates activities manually.
- Facilitator generates only one activity type.
- Facilitator duplicates and adapts an existing activity.

### Failure Paths

- Sources are insufficient for requested objective.
- Generation returns unsupported claims.
- Too many activities for requested duration.

### Recovery Path

- Suggest narrower objective or fewer activities.
- Mark weakly grounded activity as requiring review.
- Allow manual activity creation with explicit unsupported status.

### Data Created or Updated

- `Activity`
- `ActivityCitationCandidate`
- `ActivityOrder`

### Events Emitted

- `activity.generation_requested`
- `activity.generated`
- `activity.updated`
- `activity.rejected`

### Audit Requirements

Record generation request, model/tool metadata where applicable, source set revision, accepted/rejected activity IDs, and facilitator edits.

### Acceptance Criteria

- Given imported sources, when activities are generated, then each source-derived activity has citation candidates.
- Given an unsupported generated claim, when facilitator reviews, then it can be rejected, edited, or marked as not source-grounded.

---

## Journey: Validate Citations and Prepare Session

### Trigger

The facilitator wants to publish activities for live use.

### Actor

Facilitator.

### Preconditions

- Activities exist.
- Source-grounded activities have citation candidates.

### Happy Path

1. Facilitator opens citation review.
2. System displays each source-derived prompt or answer beside cited excerpts.
3. Facilitator confirms, replaces, weakens, or rejects citations.
4. Activities with valid required citations become publishable.
5. Facilitator locks the agenda and moves session to `Prepared`.

### Alternate Paths

- Facilitator marks an activity as facilitator-authored without source grounding.
- Facilitator hides citations from participants but keeps them available for audit and export.
- Facilitator publishes a partial agenda.

### Failure Paths

- Citation does not support the claim.
- Source was removed after generation.
- Activity has no valid grounding but is labeled as source-grounded.

### Recovery Path

- Replace citation.
- Regenerate activity from valid sources.
- Change activity wording.
- Remove source-grounded label.

### Data Created or Updated

- `Citation`
- `Activity.status`
- `Session.status`
- `SessionAgenda`

### Events Emitted

- `citation.validated`
- `citation.rejected`
- `activity.published`
- `session.prepared`

### Audit Requirements

Record who validated citations, when, against which source revision.

### Acceptance Criteria

- Given a source-grounded activity without validated citation, when facilitator prepares the session, then publication is blocked or the activity is explicitly marked unsupported.
- Given all required checks pass, when facilitator prepares, then session enters `Prepared` status.

---

## Journey: Run Live Session

### Trigger

It is time to facilitate the session with participants.

### Actor

Facilitator; Participant.

### Preconditions

- Session is `Prepared`.
- Participants have join access.
- At least one activity is publishable.

### Happy Path

1. Facilitator starts live mode.
2. System changes session to `Live` and opens participant join.
3. Participants join and see session objective and participation rules.
4. Facilitator starts an activity.
5. Participants submit responses while collection is open.
6. Facilitator views live progress and aggregate results.
7. Facilitator closes the activity and moves to the next.

### Alternate Paths

- Participant joins late and lands on current activity.
- Facilitator skips an activity.
- Facilitator pauses live mode.
- Facilitator edits an unpublished upcoming activity during live mode.

### Failure Paths

- Participant connection drops.
- Facilitator accidentally starts wrong activity.
- Live updates lag or fail.
- Participation link is invalid or expired.

### Recovery Path

- Participant can reconnect and resume if activity is still open.
- Facilitator can pause, stop, or reopen an activity if policy allows.
- System preserves submitted responses idempotently.

### Data Created or Updated

- `ParticipantSession`
- `ActivityRun`
- `Response`
- `Presence` or live participation signal

### Events Emitted

- `session.started`
- `participant.joined`
- `activity.started`
- `response.submitted`
- `activity.closed`
- `session.paused`

### Audit Requirements

Record lifecycle transitions, activity timing, response submission metadata, and visibility/anonymity settings active at submission time.

### Acceptance Criteria

- Given a live activity, when a participant submits once, then exactly one response is recorded or the duplicate is safely idempotent.
- Given an anonymity setting, when responses are viewed, then identity visibility follows the setting captured at submission time.

---

## Journey: Produce Sourced Summary

### Trigger

The live session is closed and the facilitator needs a useful follow-up artifact.

### Actor

Facilitator.

### Preconditions

- Session is `Closed`.
- Responses and activity results are available.

### Happy Path

1. Facilitator requests a session summary.
2. System synthesizes learning outcomes, key points, questions, disagreements, vote results, misconceptions, and action items.
3. Summary includes citations to sources and references to activities/responses where appropriate.
4. Unsupported synthesis claims are flagged for facilitator review.
5. Facilitator edits and validates the summary.
6. Session moves to `Synthesized`.

### Alternate Paths

- Facilitator writes summary manually.
- Summary excludes individual responses.
- Summary is generated per audience: facilitator-only and participant-facing.

### Failure Paths

- Not enough responses.
- Citations are missing or weak.
- Summary exposes private participant data.

### Recovery Path

- Generate a limited summary with clear gaps.
- Remove or anonymize sensitive content.
- Ask facilitator to validate questionable claims.

### Data Created or Updated

- `Summary`
- `SummaryCitation`
- `LearningSignal`

### Events Emitted

- `summary.generation_requested`
- `summary.generated`
- `summary.updated`
- `summary.validated`

### Audit Requirements

Record source set revision, response set revision, generated draft metadata, facilitator edits, and validation timestamp.

### Acceptance Criteria

- Given a source-derived summary claim, when summary is validated, then the claim has a citation or is marked as facilitator-authored/unsupported.
- Given participant-private responses, when summary is generated, then visibility policy is enforced.

---

## Journey: Export and Archive

### Trigger

The facilitator or admin needs a durable post-session artifact.

### Actor

Facilitator; Admin.

### Preconditions

- Session is `Synthesized` or `Closed` for raw export.
- Export is allowed by workspace and session policy.

### Happy Path

1. Actor chooses export format and audience.
2. System prepares export package: agenda, activities, aggregate results, summary, citations, and metadata.
3. Actor previews export.
4. System records export and makes it available for download or sharing.
5. Actor archives the session when no further changes are expected.

### Alternate Paths

- Export only summary.
- Export machine-readable session artifact.
- Admin exports audit bundle.

### Failure Paths

- Export would include private data not allowed for audience.
- Summary is unvalidated.
- Export generation fails.

### Recovery Path

- Show privacy blockers.
- Allow reduced export.
- Retry export generation.

### Data Created or Updated

- `Export`
- `Artifact`
- `Session.status` optionally `Archived`

### Events Emitted

- `export.requested`
- `export.generated`
- `export.failed`
- `session.archived`

### Audit Requirements

Record actor, format, included data classes, recipient scope, timestamp, and artifact checksum where available.

### Acceptance Criteria

- Given an export audience, when export is generated, then included data respects visibility and retention policy.
- Given an archived session, when a user opens it, then content is read-only unless a new revision/follow-up session is created.
