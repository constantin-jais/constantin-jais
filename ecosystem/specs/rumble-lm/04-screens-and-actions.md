# Screens and Actions — rumble-lm

Status: Draft.

## Navigation Model

MVP navigation:

```text
Workspace Sessions
  → Session Setup
  → Sources
  → Activities
  → Citation Review
  → Live Console
  → Results
  → Summary
  → Export / Archive

Participant Entry
  → Join
  → Current Activity
  → Results / Recap when allowed
```

## Screen: Workspace Sessions

### Purpose

List, create, search, resume, archive, and inspect sessions in a workspace.

### Route / Entry Point

`/workspaces/:workspaceId/sessions`

### Allowed Roles

Admin, Facilitator.

### Displayed Data

- session title, objective, owner, status;
- scheduled or last activity date;
- participant count;
- source/activity readiness indicators;
- export/archive state.

### Actions by Role

- **Admin:** view metadata, filter by owner/status, archive/delete per policy, assign facilitator.
- **Facilitator:** create session, open own sessions, duplicate session, archive own sessions per policy.

### Empty State

Prompt to create first source-grounded session.

### Loading State

Skeleton list and filters disabled.

### Error State

Show retry and workspace access error.

### Offline State

Read cached session metadata only if local cache exists; no create/update.

### Permission Denied State

Explain missing workspace/session role.

### Telemetry / Events

`session_list.viewed`, `session.create_clicked`, `session.opened`.

### Service Calls

`GET /sessions`, `POST /sessions`, `POST /sessions/:id/archive`.

### Acceptance Criteria

- Users only see sessions permitted by workspace policy.
- Status and readiness indicators match session lifecycle state.

## Screen: Session Setup

### Purpose

Define objective, audience, mode, timing, visibility, and readiness checklist.

### Route / Entry Point

`/sessions/:sessionId/setup`

### Allowed Roles

Admin with content access, Facilitator.

### Displayed Data

- title, objective, audience, duration;
- lifecycle status;
- anonymity/visibility defaults;
- source/activity/citation/live/export checklist;
- blockers to `Prepared`.

### Actions by Role

- **Facilitator:** edit metadata, configure settings, move to prepared when checks pass, reopen preparation before live.
- **Admin:** edit governance settings only if policy allows; reassign facilitator.

### States

- Empty: new session form.
- Loading: disable save.
- Error: field-level validation.
- Offline: view cached draft, queue edits only if supported later.
- Permission denied: no edit controls.

### Service Calls

`GET /sessions/:id`, `PATCH /sessions/:id`, `POST /sessions/:id/prepare`.

### Acceptance Criteria

- Session cannot become `Prepared` while mandatory source-grounded activity citations are unresolved.
- Anonymity/visibility defaults are explicit before participant invitation.

## Screen: Source Import and Review

### Purpose

Add, process, inspect, and curate sources used for grounding.

### Route / Entry Point

`/sessions/:sessionId/sources`

### Allowed Roles

Facilitator; Admin with content access.

### Displayed Data

- source list and import status;
- type, title, provenance, hash when available;
- extraction quality warnings;
- source chunks preview;
- dependent activities/citations.

### Actions by Role

- **Facilitator:** add source, retry failed import, remove source, rename source, inspect chunks, lock source set.
- **Admin:** view/remove sources only per governance policy.

### States

- Empty: explain supported source types and grounding value.
- Error: unsupported type, extraction failed, policy blocked.
- Offline: no import; cached review only.

### Service Calls

`POST /sources/import`, `GET /sessions/:id/source-set`, `DELETE /sources/:sourceId`, `POST /source-sets/:id/lock`.

### Acceptance Criteria

- Failed sources do not block successful sources.
- Removing a source flags dependent citation candidates as invalid.

## Screen: Activity Builder

### Purpose

Create, generate, edit, order, validate, and publish session activities.

### Route / Entry Point

`/sessions/:sessionId/activities`

### Allowed Roles

Facilitator.

### Displayed Data

- agenda order;
- activity type, objective, prompt, duration, response mode;
- grounding mode and citation readiness;
- status: Draft, Validated, Published, Running, Closed.

### Actions by Role

- Generate activities from source set.
- Create manual activity.
- Edit prompt/options/duration/visibility.
- Reorder activities.
- Duplicate/delete activity before live.
- Send to citation review.
- Publish/unpublish before live.

### States

- Empty: choose activity type or generate from sources.
- Error: generation failed, insufficient sources, invalid response config.
- Offline: edit disabled for MVP.

### Service Calls

`POST /activities/generate`, `POST /activities`, `PATCH /activities/:id`, `POST /activities/reorder`, `POST /activities/:id/publish`.

### Acceptance Criteria

- Generated source-grounded activities include citation candidates.
- Running or closed activities cannot be structurally edited.

## Screen: Citation Review

### Purpose

Verify that generated claims are supported by cited source excerpts before publication or synthesis validation.

### Route / Entry Point

`/sessions/:sessionId/citations`

### Allowed Roles

Facilitator; Admin read-only if policy allows.

### Displayed Data

- claim/prompt/answer text;
- citation candidate excerpt and source location;
- support level;
- source revision;
- unresolved/rejected/validated status.

### Actions by Role

- Validate citation.
- Reject citation.
- Replace citation.
- Edit claim/prompt.
- Mark claim as facilitator-authored/unsupported.

### States

- Empty: no citations requiring review.
- Error: source missing, citation stale, chunk unavailable.

### Service Calls

`GET /citation-review`, `POST /citations/:id/validate`, `POST /citations/:id/reject`, `POST /citations/:id/replace`.

### Acceptance Criteria

- Source-grounded generated claims cannot be published with only rejected/missing citations.
- Validation records actor, timestamp, and source revision.

## Screen: Live Facilitator Console

### Purpose

Run the session, control activities, monitor participation, and close collection.

### Route / Entry Point

`/sessions/:sessionId/live`

### Allowed Roles

Facilitator.

### Displayed Data

- current status and timer;
- participant presence count;
- current/upcoming activities;
- response count and aggregate results;
- visibility/anonymity state;
- live warnings and connection health.

### Actions by Role

- Start session.
- Start/pause/close activity.
- Skip activity.
- Show/hide aggregate results.
- Moderate discussion.
- End session.

### States

- Empty: session not prepared.
- Error: live transport unavailable, activity invalid.
- Offline: cannot run live; show recovery guidance.

### Service Calls

`POST /sessions/:id/start`, `POST /activities/:id/start`, `POST /activities/:id/close`, `GET /live/:sessionId/state`.

### Acceptance Criteria

- Participants only submit to the currently open activity.
- Ending session closes all open activity runs.

## Screen: Participant Join and Activity View

### Purpose

Let participants join and respond with minimal friction and clear privacy context.

### Route / Entry Point

`/join/:sessionCode` or `/sessions/:sessionId/participant`

### Allowed Roles

Participant.

### Displayed Data

- session title/objective;
- facilitator name;
- current activity prompt;
- response controls;
- anonymity/visibility notice;
- submission status.

### Actions by Role

- Join session.
- Set display name if allowed.
- Submit response.
- Edit response before close if allowed.
- View aggregate results if published.

### States

- Waiting room: no activity open.
- Closed: session no longer accepts responses.
- Error: invalid code, permission denied, network failure.
- Reconnect: restore active participant state.

### Service Calls

`POST /participants/join`, `GET /participant/session-state`, `POST /responses`, `PATCH /responses/:id` if allowed.

### Acceptance Criteria

- Privacy notice is visible before first response.
- Duplicate submissions are idempotent according to activity settings.

## Screen: Results Dashboard

### Purpose

Review participation, activity outcomes, learning signals, and discussion themes.

### Route / Entry Point

`/sessions/:sessionId/results`

### Allowed Roles

Facilitator; Admin per policy.

### Displayed Data

- response/completion rates;
- quiz correctness distribution if enabled;
- vote distributions;
- reflection themes;
- open questions;
- citation/source confusion signals.

### Actions by Role

- Filter by activity.
- Mark notable insight.
- Exclude private/sensitive response from summary draft.
- Request summary generation.

### Acceptance Criteria

- Aggregate analytics do not reveal identities when anonymity is enabled.
- Results reflect closed activity state, not partial hidden data.

## Screen: Summary Editor

### Purpose

Generate, validate, edit, and publish sourced post-session summaries.

### Route / Entry Point

`/sessions/:sessionId/summary`

### Allowed Roles

Facilitator.

### Displayed Data

- summary draft;
- citations and unsupported claims;
- participant visibility warnings;
- revision history;
- audience selector.

### Actions by Role

- Generate summary.
- Edit summary.
- Validate citation.
- Remove sensitive/private content.
- Publish facilitator-only or participant-facing version.

### Acceptance Criteria

- Participant-facing summary cannot include private responses outside policy.
- Source-derived claims require citations or explicit unsupported/facilitator-authored markers.

## Screen: Export and Archive

### Purpose

Generate durable artifacts and archive the session.

### Route / Entry Point

`/sessions/:sessionId/export`

### Allowed Roles

Facilitator; Admin.

### Displayed Data

- available formats;
- audience and included data classes;
- privacy warnings;
- previous exports;
- archive/retention status.

### Actions by Role

- Generate export.
- Preview export.
- Revoke export if supported.
- Archive session.
- Create follow-up session.

### Acceptance Criteria

- Export generation records actor, format, audience, included data, and artifact reference.
- Archived sessions are read-only except policy-controlled restore/follow-up.

---

# Core Action Specifications

## Action: Prepare Session

### Actor

Facilitator.

### Intent

Move a draft session into a run-ready state.

### Preconditions

Session is `Draft`; required metadata exists; at least one publishable activity exists.

### Business Rules

- Source-grounded generated activities require validated citations or explicit unsupported/facilitator-authored marking.
- Participant visibility/anonymity rules must be configured.

### Side Effects

Session status becomes `Prepared`; source set/activity revisions are recorded.

### Events Emitted

`session.prepared`.

### Audit Log

Actor, timestamp, checks passed, unresolved waivers/unsupported claims if any.

### Acceptance Criteria

Preparation fails with actionable blockers when checks are missing.

## Action: Submit Response

### Actor

Participant.

### Intent

Contribute to an open activity.

### Preconditions

Session is `Live`; activity run is open; participant has joined.

### Business Rules

- Response must match activity response mode.
- Identity visibility is captured at submission time.
- Duplicate handling follows activity idempotency rule.

### Events Emitted

`response.submitted`.

### Audit Log

Participant/session reference, activity, timestamp, visibility mode; avoid logging sensitive response content outside response store.

### Acceptance Criteria

Response is accepted exactly once or safely updated when edits are allowed.

## Action: Validate Summary

### Actor

Facilitator.

### Intent

Approve a post-session synthesis for export or participant sharing.

### Preconditions

Session is `Closed`; summary draft exists.

### Business Rules

- Participant-facing version must pass privacy rules.
- Source-derived claims must have validated citations or explicit unsupported markers.

### Events Emitted

`summary.validated`, optionally `session.synthesized`.

### Acceptance Criteria

Validation is blocked by unresolved citation/privacy issues.

## Action: Generate Export

### Actor

Facilitator or Admin.

### Intent

Create a durable session artifact.

### Preconditions

Session is `Closed`, `Synthesized`, or `Exported`; export policy allows requested audience/format.

### Business Rules

- Include only data classes allowed for audience.
- Record export metadata and artifact reference.

### Events Emitted

`export.requested`, `export.generated` or `export.failed`.

### Acceptance Criteria

Export is reproducible enough to audit included data and source/session revisions.
