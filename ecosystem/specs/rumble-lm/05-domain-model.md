# Domain Model — rumble-lm

Status: Draft.

## Aggregate Boundaries

### Session Aggregate

Owns lifecycle, settings, agenda, live state, and archival state.

Includes:

- `Session`
- `SessionSettings`
- `SessionAgenda`
- `ActivityRun`

Does not own imported source truth or global identity.

### SourceSet Aggregate

Owns the session-specific selection and revision of sources.

Includes:

- `SourceSet`
- `SourceSetItem`
- references to `Source` and `SourceChunk`

Does not own source extraction internals; those belong to Wrench/Gear capabilities.

### Activity Aggregate

Owns activity prompt, options, lifecycle, grounding metadata, and response schema.

Includes:

- `Activity`
- `ActivityOption`
- `Citation`
- `ResponseSchema`

Does not own submitted responses once activity is closed, except through explicit moderation/deletion workflows.

### Response Aggregate

Owns participant submissions and immutable response metadata.

Includes:

- `Response`
- `ResponseRevision` optional later
- visibility snapshot

### Summary/Export Aggregate

Owns generated and validated post-session artifacts.

Includes:

- `Summary`
- `SummarySection`
- `Export`
- artifact references

## Entities

## Entity: Session

### Definition

A bounded learning/facilitation event.

### Key Fields

`id`, `workspaceId`, `title`, `objective`, `audience`, `status`, `facilitatorId`, `sourceSetId`, `settings`, timestamps.

### Lifecycle States

`Draft`, `Prepared`, `Live`, `Closed`, `Synthesized`, `Exported`, `Archived`.

### Relationships

Has one active `SourceSet`, many `Activities`, `Participants`, `Responses`, `Summaries`, and `Exports`.

### Invariants

- Cannot become `Live` unless `Prepared`.
- Cannot become `Prepared` with unresolved mandatory citation blockers.
- Cannot accept responses outside `Live` activity runs.
- Cannot mutate closed responses except anonymization/deletion workflows.

### Deletion / Archive

Archive is default. Hard delete follows workspace retention and participant-data policy.

## Entity: SessionSettings

### Definition

Configuration that affects participation, visibility, privacy, and export behavior.

### Key Fields

`defaultResponseVisibility`, `allowGuests`, `participantAccessMode`, `allowResponseEditBeforeClose`, `showAggregateResults`, `retentionPolicyRef`, `exportPolicyRef`.

### Invariants

Visibility settings active at submission time are snapshotted onto each `Response`.

## Entity: SourceSet

### Definition

A versioned set of sources used for a session.

### Key Fields

`id`, `sessionId`, `revision`, `status`, `sourceRefs`, `lockedAt`.

### Lifecycle States

`Open`, `Processing`, `Ready`, `Locked`, `Stale`.

### Invariants

- Activities and citations reference a specific source set revision.
- Removing/replacing a source makes dependent citation candidates stale.

## Entity: Source

### Definition

A file, URL, text, note, transcript, or document imported for grounding.

### Owner

Shared source primitive candidate: Wrench Loader + Gear Memory. Rumble stores session references and user-facing metadata.

### Key Fields

`id`, `type`, `title`, `contentRef`, `metadata`, `provenance`, `hash`, `importStatus`.

### Invariants

A source must have inspectable provenance before it can support validated citations.

## Entity: SourceChunk

### Definition

Addressable segment of a source.

### Key Fields

`id`, `sourceId`, `location`, `text`, `metadata`.

### Invariants

Location must be stable enough for citation review and export.

## Entity: Activity

### Definition

Interactive block in the session agenda.

### Key Fields

`id`, `sessionId`, `type`, `title`, `objective`, `prompt`, `status`, `order`, `responseMode`, `visibility`, `groundingMode`, `sourceSetRevision`.

### Lifecycle States

`Draft`, `Validated`, `Published`, `Running`, `Closed`, `Archived`.

### Activity Types

`Quiz`, `Vote`, `Reflection`, `Discussion`, `SummaryCheckpoint`.

### Invariants

- Running/closed activity cannot be structurally edited.
- Source-grounded generated activity cannot be published without citation resolution.
- Activity order must be unique within a session agenda.

## Entity: ActivityOption

### Definition

Selectable option for quiz/vote/rating activities.

### Key Fields

`id`, `activityId`, `label`, `value`, `isCorrect` optional, `order`, `citationRefs` optional.

### Invariants

Correctness is optional and only used when scoring/comprehension checks are enabled.

## Entity: ActivityRun

### Definition

Live execution instance of an activity.

### Key Fields

`id`, `activityId`, `sessionId`, `status`, `startedAt`, `closedAt`, `timer`, `openedBy`, `closedBy`.

### Invariants

Only one activity run should be current/open per session in MVP.

## Entity: Participant

### Definition

Session-scoped participant identity or guest reference.

### Key Fields

`id`, `sessionId`, `actorRef`, `displayName`, `joinMode`, `joinedAt`, `lastSeenAt`.

### Invariants

Participant display identity and anonymity are not equivalent; visibility rules decide what others can see.

## Entity: Response

### Definition

Submitted participant answer/contribution.

### Key Fields

`id`, `activityId`, `activityRunId`, `participantId`, `content`, `responseType`, `visibilitySnapshot`, `submittedAt`, `deletedAt`.

### Invariants

- Cannot exist without open activity run at submission time.
- Immutable after activity close except policy workflows.
- Content visibility follows `visibilitySnapshot`.

## Entity: Citation

### Definition

Evidence link between a claim and source material.

### Key Fields

`id`, `targetType`, `targetId`, `sourceId`, `sourceChunkId`, `quote`, `location`, `supportLevel`, `status`, `validatedBy`, `validatedAt`.

### Lifecycle States

`Candidate`, `Validated`, `Rejected`, `Stale`.

### Invariants

- `Validated` citations must reference current or explicitly pinned source revisions.
- Rejected/stale citations cannot satisfy grounding requirements.

## Entity: Summary

### Definition

Post-session synthesis for facilitator and/or participants.

### Key Fields

`id`, `sessionId`, `audience`, `content`, `status`, `revision`, `generatedAt`, `validatedBy`, `validatedAt`.

### Lifecycle States

`Draft`, `Validated`, `Published`, `Archived`.

### Invariants

- Participant-facing summaries enforce response visibility policy.
- Source-derived claims need validated citations or unsupported markers.

## Entity: Export

### Definition

Durable generated artifact.

### Key Fields

`id`, `sessionId`, `format`, `audience`, `includedData`, `artifactRef`, `checksum`, `generatedBy`, `generatedAt`, `revokedAt`.

### Invariants

Export includes a snapshot of data classes and policy at generation time.

## Value Objects

### ActorReference

Minimal actor snapshot: `actorId`, `kind`, `displayName`, `workspaceRoleSnapshot`.

### VisibilityMode

`Named`, `AnonymousToParticipants`, `AnonymousToFacilitator`, `PrivateToFacilitator`, `AggregateOnly`.

### GroundingMode

`SourceGrounded`, `FacilitatorAuthored`, `Unsupported`, `Mixed`.

### SupportLevel

`Strong`, `Partial`, `Weak`, `Contradicted`, `NotReviewed`.

### ExportAudience

`FacilitatorOnly`, `Participants`, `AdminAudit`, `MachineReadable`.

## Domain Events

- `session.created`
- `session.prepared`
- `session.started`
- `session.closed`
- `activity.generated`
- `activity.published`
- `activity.started`
- `response.submitted`
- `citation.validated`
- `summary.validated`
- `export.generated`

## Shared Capability Candidates

- Workspace and roles: shared Rumble/auth adapter.
- Source and provenance: Gear Memory.
- Import pipeline: Wrench Loader.
- Citation support validation: Wrench validator/inspector.
- Generation orchestration: Bolt.
- Event/audit log and artifact storage: Gear.
