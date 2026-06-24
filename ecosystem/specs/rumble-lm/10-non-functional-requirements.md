# Non-Functional Requirements — rumble-lm

Status: Draft.

## Availability and Reliability

- Live session control must remain responsive for facilitator actions.
- Participant submissions must be durable once accepted.
- Source import and generation can be asynchronous and retried.
- Export generation can be asynchronous for large sessions.

### MVP Targets

- Session list/setup pages: normal web app responsiveness.
- Live activity state updates: perceived latency under 1–2 seconds for typical small sessions.
- Response submission: acknowledge success/failure clearly within 2 seconds under normal conditions.
- Import/generation/export: show progress and allow safe retry.

## Performance

### Expected MVP Scale

- Small to medium sessions: 5–100 participants.
- Activities per session: 3–20.
- Sources per session: 1–20.
- Responses per activity: up to participant count, with spikes during live moments.

### Requirements

- Paginate/filter sessions and exports.
- Aggregate response results server-side.
- Avoid returning raw individual responses to participants unless explicitly allowed.
- Index by workspace, session, activity, participant, and event time.
- Do not embed large sources in session payloads; use source refs/chunks.

## Offline Behavior

MVP is online-first for live sessions.

- Facilitator can view cached session metadata if available.
- Participant live participation requires network.
- Source import, generation, live response submission, and export require network.
- Offline-first authoring/sync is post-MVP and depends on shared storage decisions.

## Sync and Conflict Handling

- Single active facilitator editing session is assumed for MVP.
- Concurrent edits should use optimistic locking/revision checks on activities, summaries, and source sets.
- Live activity state is server-authoritative.
- Participant response duplicates are handled by idempotency keys and activity settings.

## Accessibility

- Participant flow must be keyboard navigable.
- Activity prompts and controls must have semantic labels.
- Timer-based activities must not rely only on color or motion.
- Results visualizations need text alternatives.
- Contrast and focus states must support live classroom/workshop settings.
- Error messages must be readable and actionable.

## Internationalization

- UI text should be externalized from day one.
- Session content can be multilingual.
- Citation locations and source metadata should not assume one locale.
- Date/time display follows user/workspace locale.

## Observability

Track metrics and logs for:

- session lifecycle transitions;
- import success/failure and duration;
- generation success/failure/refusal;
- citation blockers;
- live connection health;
- response submission latency/failure;
- export generation success/failure;
- permission denials;
- privacy/export blockers.

Logs must exclude secrets and raw sensitive content.

## Auditability

- Lifecycle transitions are auditable.
- Citation validation is auditable.
- Summary validation/publication is auditable.
- Export generation/revocation is auditable.
- Response content is not duplicated into audit logs.

## Portability and Self-Hosting

- Core product must run without mandatory proprietary SaaS.
- Source storage, event log, and artifact storage should have self-hostable options.
- Generation backends must be configurable by deployment policy.
- Exports should use open formats where possible: Markdown, HTML, JSON, PDF.

## Backup and Restore

Backups must include:

- sessions and settings;
- source set references and provenance snapshots;
- activities/options/runs;
- participants and responses according to retention policy;
- citations;
- summaries;
- export metadata and artifact references;
- audit events.

Restore requirements:

- Restored sessions keep lifecycle state.
- Restored exports remain traceable to artifact refs or marked unavailable.
- Restored summaries/citations are not silently regenerated.

## Disaster Recovery

- RPO/RTO are deployment-specific.
- Minimum product requirement: backups and restore procedure must be documented before production use.
- Live session disruption should fail safely: stop accepting ambiguous duplicate submissions or reconcile through idempotency.

## Security

- Enforce authorization server-side.
- Protect browser writes with CSRF mitigations when cookie-authenticated.
- Sanitize rich text and rendered source excerpts.
- Use rate limits for participant join/response flows.
- Store generated metadata without provider secrets.

## Privacy

- Privacy notices before response submission.
- Configurable retention.
- Anonymization/deletion workflows.
- Aggregate analytics by default.
- Participant-facing exports filtered by audience.

## Cost Constraints

- Generation and import should be bounded by source size/session limits.
- Avoid unbounded live fan-out costs in MVP.
- Export artifacts should have retention/expiry policy.
- Analytics should be computed incrementally or on demand for MVP scale.

## Quality Gates Before Implementation

- Lifecycle state machine accepted.
- Permission matrix accepted.
- Citation gating rules accepted.
- Data retention defaults decided.
- MVP live scale target decided.
- Source ingestion owner decided or stubbed.
