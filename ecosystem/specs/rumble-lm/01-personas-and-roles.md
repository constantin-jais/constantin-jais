# Personas and Roles — rumble-lm

Status: Draft.

## Product Positioning Guardrails

`rumble-lm` is a source-grounded collective session product. It must optimize for learning outcomes, facilitation reliability, group engagement, and post-session evidence. It must not behave as an unconstrained chatbot or as an isolated quiz generator.

## Personas

### Persona: Facilitator

A trainer, teacher, consultant, manager, or workshop lead who prepares and runs a session for a group.

- **Goal:** turn trusted sources into a structured session with activities, live participation, and an actionable synthesis.
- **Motivations:** save preparation time, keep participants engaged, keep claims grounded, leave with usable outputs.
- **Success signals:** session runs on time, participants respond, misconceptions are visible, summary is sourced and exportable.
- **Risks:** overtrusting generated activities, losing control during live facilitation, publishing unsupported summaries.

### Persona: Participant

A person joining a session to learn, react, vote, reflect, or contribute to a group synthesis.

- **Goal:** understand the material, contribute safely, see how the group is progressing.
- **Motivations:** clarity, low-friction participation, fair visibility, useful recap after the session.
- **Success signals:** can join quickly, understands each activity, can answer without confusion, sees a relevant follow-up.
- **Risks:** privacy concerns, unclear anonymity, fatigue from too many activities, unsupported AI claims.

### Persona: Learner

A participant in an explicitly pedagogical context.

- **Goal:** acquire or verify understanding of session material.
- **Motivations:** clear learning outcomes, immediate feedback, reliable citations, durable recap.
- **Success signals:** knows what was expected, identifies gaps, can revisit cited sources.
- **MVP note:** `Learner` is a persona, not a separate permission role unless a later product decision requires learner-specific access control.

### Persona: Admin

A workspace or organization operator responsible for access, retention, policy, and configuration.

- **Goal:** ensure sessions are compliant, auditable, secure, and manageable.
- **Motivations:** governance, data residency, role management, retention control, operational visibility.
- **Success signals:** clear permission model, audit trail, export/deletion controls, source provenance.

---

## System Roles

MVP roles are `Admin`, `Facilitator`, and `Participant`. `Learner` remains a persona layered on top of `Participant`.

## Role: Admin

### Goal

Manage workspace-level configuration, access, governance, retention, and auditability.

### Motivations

- Keep data and session artifacts under organizational control.
- Ensure participant data, sources, exports, and generated summaries follow policy.
- Support facilitators without owning each session's content.

### Permissions

- Create and manage workspace-level settings.
- Assign and revoke facilitator/admin roles.
- View session metadata and audit logs according to policy.
- Configure retention, export availability, and allowed source types.
- Archive or delete sessions when policy allows.

### Visible Data

- Workspace members and role assignments.
- Session metadata: title, owner, status, dates, retention state.
- Audit events and export records.
- Policy settings.
- Session content only when granted by workspace policy or session ownership rules.

### Editable Data

- Workspace settings.
- Role assignments.
- Retention and export policies.
- Session archival/deletion status when permitted.

### Allowed Actions

- Invite/remove users.
- Promote/demote facilitators.
- Configure data retention and export formats.
- Review audit history.
- Enforce archival or deletion.

### Forbidden Actions

- Silently alter participant responses.
- Modify facilitator-validated citations without an audit trail.
- Impersonate facilitators or participants.
- Publish generated content as validated without facilitator approval.

### Edge Cases

- Admin must support incident response without breaking participant privacy promises.
- Admin may need to recover a session when a facilitator leaves the workspace.
- Admin access to content may be restricted in sensitive sessions.

### Trust / Security Expectations

- Every administrative action is audited.
- Admin permissions are explicit and revocable.
- Admin cannot bypass source/citation validation rules invisibly.

## Role: Facilitator

### Goal

Prepare, run, close, synthesize, and export a source-grounded collective session.

### Motivations

- Convert sources into useful learning or facilitation activities.
- Keep participation flowing live.
- Understand group comprehension, disagreement, and open questions.
- Produce an evidence-backed recap.

### Permissions

- Create sessions.
- Import or select sources.
- Generate, edit, order, validate, publish, pause, and close activities.
- Invite participants.
- Configure anonymity and visibility rules for responses.
- Start and end live mode.
- Generate, edit, validate, and export summaries.

### Visible Data

- Session configuration and lifecycle status.
- Imported sources and extracted chunks.
- Generated activities and citation candidates.
- Participant roster or anonymous presence depending on settings.
- Live responses, aggregate results, discussion threads, summary drafts, exports.

### Editable Data

- Session title, objective, audience, agenda, and settings.
- Source set membership before lock/publish rules apply.
- Activity prompts, ordering, durations, citations, answer keys when relevant.
- Summary content before final export.

### Allowed Actions

- Create a draft session.
- Add sources and request source-grounded activity generation.
- Validate or reject generated activities.
- Run live activities and collect responses.
- Moderate visible discussion content.
- Close collection and produce a summary.
- Export approved session artifacts.

### Forbidden Actions

- Publish a source-grounded activity without visible citation review.
- Change submitted participant responses.
- Present unsupported generated claims as grounded facts.
- Reopen a closed session without creating an audited revision or follow-up.

### Edge Cases

- Facilitator edits an activity during live mode.
- A source is removed after activities have been generated from it.
- A generated citation is weak or points to the wrong passage.
- A participant requests deletion or anonymization after the session.

### Trust / Security Expectations

- Facilitator remains responsible for final validation.
- AI assistance is draft-producing, not authority-granting.
- Live moderation and summary edits are auditable.

## Role: Participant

### Goal

Join a session, respond to activities, see relevant context, and receive a useful follow-up.

### Motivations

- Participate with low friction.
- Know whether responses are anonymous or named.
- Understand what source material supports the activity.
- Receive a recap that reflects the session accurately.

### Permissions

- Join sessions they are invited to or that are open via configured access.
- View currently published activities.
- Submit responses while collection is open.
- View permitted aggregate results or discussion threads.
- Access post-session summary/export if allowed.

### Visible Data

- Session title, objective, facilitator name, activity instructions.
- Their own responses.
- Published aggregate results and summary according to visibility rules.
- Source excerpts/citations exposed by the facilitator.

### Editable Data

- Their profile/display name if allowed.
- Their own response before submission or before collection closes, depending on activity settings.

### Allowed Actions

- Join/leave session.
- Answer quiz, vote, reflection, discussion, or checkpoint activities.
- Ask or submit questions when enabled.
- Download or view follow-up artifacts when permitted.

### Forbidden Actions

- View unpublished activities.
- View other participants' private responses unless visibility rules allow it.
- Modify responses after collection is closed.
- Access sources or exports beyond session policy.

### Edge Cases

- Anonymous participation is enabled.
- Participant joins late.
- Participant loses connection during live mode.
- Participant wants their data deleted after session close.

### Trust / Security Expectations

- Anonymity and visibility rules are explicit before response submission.
- Participant data is not reused beyond stated session purposes.
- Responses and identity are protected according to workspace policy.
