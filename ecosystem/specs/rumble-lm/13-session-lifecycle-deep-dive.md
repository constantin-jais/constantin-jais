# Session Lifecycle and Initial Domain Model — rumble-lm

Status: Draft.

## Product Thesis

A `rumble-lm` session is not a chat thread. It is a bounded collective event with sources, activities, responses, citations, synthesis, exports, and auditable lifecycle transitions.

## MVP Session Lifecycle

```text
Draft → Prepared → Live → Closed → Synthesized → Exported → Archived
```

`Exported` may happen multiple times after `Closed` or `Synthesized`. `Archived` is terminal for normal editing.

### Status: Draft

The session exists but is not ready to run.

- **Allowed:** edit objectives/settings, import sources, generate/edit activities, invite draft collaborators.
- **Blocked:** participant live collection, final export as validated session, participant-facing summary.
- **Exit criteria:** required metadata exists; at least one publishable activity exists; grounding/citation checks are resolved or explicitly waived/marked unsupported.

### Status: Prepared

The session agenda is ready for live use.

- **Allowed:** invite participants, preview participant view, adjust non-structural settings, start live mode.
- **Controlled:** source set and validated activities are treated as a prepared revision.
- **Blocked:** publishing source-grounded activities with unvalidated citations.
- **Exit criteria:** facilitator starts session.

### Status: Live

Participants can join and submit responses to currently open activities.

- **Allowed:** start/close/pause activities, collect responses, view live progress, moderate discussion.
- **Controlled:** editing a currently running activity is blocked; editing upcoming unpublished activities is allowed with audit.
- **Blocked:** changing anonymity/visibility rules for already submitted responses.
- **Exit criteria:** facilitator ends live collection.

### Status: Closed

Live participation is complete and response collection is frozen.

- **Allowed:** view results, generate summary, raw export if policy allows.
- **Blocked:** new participant responses, mutation of submitted responses.
- **Exit criteria:** summary is generated and facilitator validates or rejects it.

### Status: Synthesized

A post-session synthesis exists and has been validated by the facilitator.

- **Allowed:** export, share, archive, create follow-up session.
- **Controlled:** summary edits create revisions.
- **Blocked:** silent modification of validated summary.
- **Exit criteria:** at least one export is generated or session is archived.

### Status: Exported

One or more durable artifacts have been generated.

- **Allowed:** generate additional exports, archive, create follow-up.
- **Controlled:** each export records included data, audience, format, checksum/provenance where available.

### Status: Archived

Session is retained as read-only according to policy.

- **Allowed:** read according to permissions, export if policy allows, restore only by admin/facilitator policy.
- **Blocked:** normal edits, live restart, response mutation.

## State Transitions

| From | To | Actor | Required Checks | Event |
| --- | --- | --- | --- | --- |
| none | Draft | Facilitator/Admin | create permission | `session.created` |
| Draft | Prepared | Facilitator | metadata complete; activities publishable; citation state resolved | `session.prepared` |
| Prepared | Draft | Facilitator | no live run started | `session.reopened_for_preparation` |
| Prepared | Live | Facilitator | participant access configured; at least one activity available | `session.started` |
| Live | Prepared | Facilitator | pause, no destructive reset | `session.paused` |
| Live | Closed | Facilitator | close all open activities | `session.closed` |
| Closed | Synthesized | Facilitator | summary validated; privacy checks pass | `session.synthesized` |
| Closed | Exported | Facilitator/Admin | export policy pass | `export.generated` |
| Synthesized | Exported | Facilitator/Admin | export policy pass | `export.generated` |
| Closed/Synthesized/Exported | Archived | Facilitator/Admin | retention policy pass | `session.archived` |

## Activity Types MVP

### Quiz

- **Purpose:** verify comprehension.
- **Response mode:** single choice, multiple choice, short answer.
- **Grounding:** required for generated questions/answers.
- **Scoring:** optional lightweight correctness signal; not the product core.

### Vote

- **Purpose:** measure priority, opinion, confidence, or consensus.
- **Response mode:** single/multiple choice, rating, rank.
- **Grounding:** required when options are generated from sources; optional when facilitator-authored.
- **Scoring:** none.

### Reflection

- **Purpose:** collect individual interpretation, application, or concern.
- **Response mode:** free text.
- **Grounding:** prompt may be source-grounded; responses are participant-authored.
- **Scoring:** none.

### Discussion

- **Purpose:** structure collective exchange around a question or tension.
- **Response mode:** thread, prompt, or facilitator-led discussion notes.
- **Grounding:** prompt should cite source context when derived from source material.
- **Scoring:** none.

### Summary Checkpoint

- **Purpose:** ask participants to reformulate key points or signal confusion.
- **Response mode:** free text, confidence, or selected statement.
- **Grounding:** expected points can be source-grounded.
- **Scoring:** optional aggregate comprehension signal, not individual grading by default.

## Scoring Decision

MVP should not center on individual scoring. The product should expose learning and facilitation signals:

- participation rate;
- completion rate per activity;
- quiz correctness when explicitly enabled;
- confidence distribution;
- consensus/divergence;
- recurring themes;
- misconceptions or unresolved questions;
- source sections that triggered most confusion or discussion.

## Initial Domain Model

### Entity: Session

- **Definition:** bounded learning/facilitation event.
- **Owner:** Rumble product layer.
- **Fields:** `id`, `workspaceId`, `title`, `objective`, `audience`, `durationEstimate`, `status`, `facilitatorId`, `sourceSetId`, `settings`, `createdAt`, `preparedAt`, `startedAt`, `closedAt`, `archivedAt`.
- **Relationships:** has one active `SourceSet`; has many `Activities`, `Participants`, `Responses`, `Summaries`, `Exports`.
- **Invariants:** cannot be `Live` without at least one publishable activity; cannot be `Synthesized` without validated summary; submitted responses are immutable after close except for deletion/anonymization workflows.
- **Archive/delete:** archive is read-only; deletion follows retention and participant data policy.
- **Events:** `session.created`, `session.prepared`, `session.started`, `session.closed`, `session.synthesized`, `session.archived`.
- **Shared candidates:** workspace, audit/event log, actor reference, role assignment.

### Entity: SourceSet

- **Definition:** revisioned set of sources used by a session.
- **Owner:** Rumble product layer consuming Wrench/Gear source primitives.
- **Fields:** `id`, `sessionId`, `revision`, `sourceIds`, `status`, `createdAt`, `lockedAt`.
- **Relationships:** contains many `Sources`; referenced by `Activities`, `Citations`, and `Summaries`.
- **Invariants:** generated activities reference a specific source set revision; removing a source invalidates dependent citation candidates unless replaced.
- **Archive/delete:** source removal preserves provenance/audit; hard deletion follows policy.
- **Events:** `source_set.updated`, `source_set.locked`.
- **Shared candidates:** source, provenance, import pipeline.

### Entity: Source

- **Definition:** imported or manually entered material used for grounding.
- **Owner:** Gear/Wrench primitives with Rumble session usage.
- **Fields:** `id`, `workspaceId`, `type`, `title`, `contentRef`, `metadata`, `provenance`, `hash`, `importStatus`, `createdAt`.
- **Relationships:** belongs to source sets; has many `SourceChunks`; cited by `Citations`.
- **Invariants:** source-derived claims must reference source revision/chunk; source import status must be successful for generation.
- **Events:** `source.import_requested`, `source.import_completed`, `source.import_failed`.
- **Shared candidates:** Gear Loader, Gear Memory source/provenance.

### Entity: SourceChunk

- **Definition:** addressable excerpt or segment of a source.
- **Owner:** Gear/Wrench primitive.
- **Fields:** `id`, `sourceId`, `position`, `text`, `location`, `metadata`, `embeddingRef` optional.
- **Relationships:** cited by `Citation`.
- **Invariants:** location must allow a user or agent to inspect cited context.
- **Shared candidates:** document chunking, source index, provenance.

### Entity: Activity

- **Definition:** interactive session block presented to participants.
- **Owner:** Rumble product layer.
- **Fields:** `id`, `sessionId`, `type`, `title`, `objective`, `prompt`, `status`, `order`, `durationEstimate`, `responseMode`, `visibility`, `groundingMode`, `sourceRefs`, `createdBy`, `validatedBy`, `createdAt`.
- **Lifecycle:** `Draft` → `Validated` → `Published` → `Running` → `Closed` → `Archived`.
- **Relationships:** belongs to session; has many citations, responses, activity runs.
- **Invariants:** source-grounded generated activity cannot become `Published` without citation validation or explicit unsupported/facilitator-authored marking; running activity cannot be structurally edited.
- **Events:** `activity.generated`, `activity.validated`, `activity.published`, `activity.started`, `activity.closed`.
- **Shared candidates:** source-grounded generation, approval/gate, event log.

### Entity: Participant

- **Definition:** actor participating in a session.
- **Owner:** Rumble product layer with shared actor reference.
- **Fields:** `id`, `sessionId`, `actorRef` optional, `displayName`, `joinMode`, `role`, `joinedAt`, `leftAt`.
- **Relationships:** submits responses; may have presence states.
- **Invariants:** participant identity visibility follows session/activity settings captured at response time.
- **Events:** `participant.joined`, `participant.left`.
- **Shared candidates:** actor reference, workspace membership, presence.

### Entity: Response

- **Definition:** participant submission for an activity.
- **Owner:** Rumble product layer.
- **Fields:** `id`, `activityId`, `participantId`, `content`, `responseType`, `visibility`, `submittedAt`, `submissionRevision`, `deletedAt` optional.
- **Relationships:** belongs to activity and participant; contributes to summary/analytics.
- **Invariants:** immutable after activity close except deletion/anonymization workflows; duplicate submissions obey activity idempotency rules.
- **Events:** `response.submitted`, `response.deleted`, `response.anonymized`.
- **Shared candidates:** event log, privacy policy, analytics signals.

### Entity: Citation

- **Definition:** verified link between a claim/activity/summary and source evidence.
- **Owner:** Rumble product layer consuming Gear/Wrench source addressing.
- **Fields:** `id`, `targetType`, `targetId`, `sourceId`, `sourceChunkId`, `quote`, `location`, `supportLevel`, `validatedBy`, `validatedAt`, `status`.
- **Relationships:** points to source chunks; attached to activities and summaries.
- **Invariants:** validated citation must reference an existing source revision/chunk; rejected citation cannot be used as support.
- **Lifecycle:** `Candidate` → `Validated` or `Rejected`.
- **Events:** `citation.candidate_created`, `citation.validated`, `citation.rejected`.
- **Shared candidates:** provenance, traceability link, source-grounded generation.

### Entity: Summary

- **Definition:** post-session synthesis for facilitator, participants, or export.
- **Owner:** Rumble product layer.
- **Fields:** `id`, `sessionId`, `audience`, `content`, `status`, `citationIds`, `responseRefs`, `generatedAt`, `validatedBy`, `validatedAt`, `revision`.
- **Relationships:** belongs to session; cites sources; references aggregate response data.
- **Invariants:** participant-facing summary must pass privacy rules; source-derived claims need citations or unsupported/facilitator-authored markers.
- **Lifecycle:** `Draft` → `Validated` → `Published` → `Archived`.
- **Events:** `summary.generated`, `summary.validated`, `summary.published`.
- **Shared candidates:** artifact, source-grounded generation, audit log.

### Entity: Export

- **Definition:** generated session artifact for download, sharing, handoff, or archive.
- **Owner:** Rumble product layer, stored as Gear artifact candidate.
- **Fields:** `id`, `sessionId`, `format`, `audience`, `includedData`, `artifactRef`, `checksum`, `generatedBy`, `generatedAt`, `expiresAt` optional.
- **Relationships:** belongs to session; may include summary, activities, citations, aggregate results, audit bundle.
- **Invariants:** export content must respect visibility, retention, and privacy policy at generation time.
- **Events:** `export.requested`, `export.generated`, `export.failed`, `export.revoked`.
- **Shared candidates:** Gear artifact, export pipeline, provenance.

## Analytics MVP

MVP analytics should help facilitation and learning without becoming invasive profiling.

### Session-Level Signals

- participant count;
- join/leave timing;
- response rate per activity;
- completion rate;
- activity timing versus planned duration;
- unanswered activities.

### Learning/Facilitation Signals

- quiz correctness distribution when quiz has answer keys;
- confidence distribution;
- repeated misconceptions;
- recurring themes in reflections;
- consensus/divergence in votes;
- open questions;
- source excerpts with high confusion or discussion.

### Privacy Guardrails

- Aggregate by default for facilitator analytics.
- Individual analytics only when clearly configured and disclosed.
- No hidden learner profiling in MVP.
- Retention and export of analytics follow workspace/session policy.

## Shared Capability Needs

| Need | Candidate Owner | Reason |
| --- | --- | --- |
| Source ingestion | Gear Loader | Import and normalize files, URLs, transcripts, notes. |
| Source storage/index/provenance | Gear Memory | Keep addressable sources, chunks, metadata, and retrieval context. |
| Source-grounded generation | Bolt + Wrench + Gear Memory | Generate activities/summaries from source sets with traceability. |
| Citation verification | Wrench Inspector or validator capability | Check whether cited passage supports generated claim. |
| Workspace/roles | Shared Rumble + auth adapter | Common collaboration and permission boundary. |
| Live participation/presence | Shared Rumble or Gear transport | Reusable live session primitive across collaborative products. |
| Event/audit log | Gear | Immutable-ish activity history for trust and agent readability. |
| Export artifact | Gear Depot/Gear Memory | Durable session output with provenance/checksum. |
| Approval/gate | Bolt + Rumble UX | Human validation before publishing generated activities/summaries. |
| Analytics signals | Rumble shared initially | Product-facing engagement and learning signals with privacy constraints. |

## MVP Open Questions

| Question | Impact | Proposed Default | Status |
| --- | --- | --- | --- |
| Is participation synchronous only? | High | MVP is synchronous live, with post-session read-only access. | Proposed |
| Do participants need accounts? | High | MVP supports invited/authenticated and lightweight guest participation per workspace policy. | Proposed |
| Are activities first-class objects? | High | Yes, first-class with lifecycle and citations. | Proposed |
| Are citations mandatory? | High | Mandatory for source-grounded generated claims; not for explicitly facilitator-authored unsupported content. | Proposed |
| Is scoring central? | Medium | No; only lightweight optional quiz correctness and aggregate learning signals. | Proposed |
| Can a session be reopened? | Medium | Not after `Closed`; create follow-up or audited revision. | Proposed |
| Are responses anonymous? | High | Configurable per session/activity, captured immutably at submission time. | Proposed |
