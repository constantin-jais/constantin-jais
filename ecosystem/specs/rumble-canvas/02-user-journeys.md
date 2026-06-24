# User Journeys — rumble-canvas

## Scope

This document defines MVP journeys for `rumble-canvas`.

The first vertical slice is:

> create workspace → draft product charter → define roles/screens/actions → review → approve spec package → request Bolt handoff

---

## Journey: Create a Spec Workspace

### Trigger

A user wants to turn a product idea into an implementation-ready spec.

### Actor

Owner.

### Preconditions

- Actor is authenticated if the product is running in multi-user mode.
- Actor has permission to create a workspace.
- No workspace with the same slug exists in the same account/tenant.

### Happy Path

1. Owner opens the product home.
2. Owner selects “New spec workspace”.
3. Owner enters:
   - workspace name;
   - short product idea;
   - intended audience;
   - optional initial context.
4. System creates a spec workspace in draft state.
5. System creates default sections:
   - product charter;
   - roles;
   - journeys;
   - screens/actions;
   - domain model;
   - open questions;
   - shared capability candidates.
6. System records `spec_workspace_created`.
7. Owner lands on the Product Charter screen.

### Alternate Paths

- Owner starts from a Markdown import.
- Owner starts from a template.
- Owner starts from an existing workspace duplicated as a new draft.

### Failure Paths

- Workspace name is invalid.
- Slug already exists.
- Storage is unavailable.
- Actor lacks permission.

### Recovery Path

- Show validation errors inline.
- Allow retry.
- Preserve entered text locally when possible.
- If storage fails, offer local draft recovery.

### Data Created or Updated

- `SpecWorkspace`
- default `SpecSection` records
- initial `ActivityEvent`

### Events Emitted

- `spec_workspace_created`
- `spec_sections_initialized`

### Audit Requirements

- Actor ID.
- Timestamp.
- Workspace ID.
- Initial creation metadata.

### Acceptance Criteria

- Given a valid workspace name and idea, when Owner creates a workspace, then the workspace exists in draft state.
- Given a duplicate slug, when Owner submits, then the system blocks creation and shows a clear error.
- Given a storage failure, when Owner submits, then input is not silently lost.

---

## Journey: Draft Product Charter

### Trigger

A workspace exists and needs a clear mission, users, scope, and non-goals.

### Actor

Owner or Editor.

### Preconditions

- Workspace exists.
- Actor can edit draft spec sections.
- Product Charter section is not locked by final approval.

### Happy Path

1. Actor opens Product Charter.
2. Actor fills:
   - mission;
   - target users;
   - jobs-to-be-done;
   - product promise;
   - non-goals;
   - product boundaries;
   - MVP scope;
   - success metrics.
3. System validates required fields.
4. Actor saves draft.
5. System creates a revision.
6. System updates completeness status.
7. Actor marks section ready for review.

### Alternate Paths

- Actor asks an Agent to suggest a draft from initial context.
- Actor imports context from a source.
- Actor leaves optional sections incomplete.

### Failure Paths

- Required fields missing.
- Conflicting edits.
- Agent suggestion cannot be generated.
- Imported context is unreadable.

### Recovery Path

- Show missing fields.
- Preserve unsaved work.
- Present conflict resolution.
- Log failed agent suggestion without blocking manual editing.

### Data Created or Updated

- `SpecSectionRevision`
- `CompletenessReport`
- optional `AgentSuggestion`
- optional `SourceReference`

### Events Emitted

- `spec_section_updated`
- `spec_section_marked_ready_for_review`
- `agent_suggestion_created` if applicable

### Audit Requirements

- Actor ID.
- Section ID.
- Revision ID.
- Change summary.
- Agent attribution if generated.

### Acceptance Criteria

- Given required fields are complete, when Actor marks ready for review, then section status becomes `ready_for_review`.
- Given required fields are missing, when Actor marks ready for review, then system blocks the transition and lists missing fields.
- Given an agent draft is accepted, then accepted content is attributed as human-accepted agent output.

---

## Journey: Define Roles, Screens, and Actions

### Trigger

The product charter is drafted and the team needs implementation-level clarity.

### Actor

Owner or Editor.

### Preconditions

- Workspace exists.
- Actor can edit spec sections.
- At least one target user exists in the charter.

### Happy Path

1. Actor opens Roles.
2. Actor defines product roles and permissions.
3. Actor opens Screens and Actions.
4. Actor creates MVP screens.
5. For each screen, Actor defines:
   - purpose;
   - allowed roles;
   - displayed data;
   - actions by role;
   - empty/error/offline states;
   - service calls if known;
   - acceptance criteria.
6. System detects actions reused across screens.
7. System prompts for shared capability candidates where relevant.
8. Actor saves screen/action matrix.
9. Actor marks section ready for review.

### Alternate Paths

- Actor starts from journeys and derives screens.
- Actor starts from screens and derives journeys.
- Agent suggests missing actions or states.

### Failure Paths

- Screen has no purpose.
- Action has no actor.
- Destructive action has no confirmation or audit rule.
- A role is referenced but not defined.

### Recovery Path

- Show structured validation warnings.
- Allow incomplete draft save.
- Block review readiness only for critical missing fields.

### Data Created or Updated

- `RoleDefinition`
- `ScreenDefinition`
- `ActionDefinition`
- `CapabilityCandidate`
- `CompletenessReport`

### Events Emitted

- `role_defined`
- `screen_defined`
- `action_defined`
- `capability_candidate_created`
- `spec_section_marked_ready_for_review`

### Audit Requirements

- Actor ID.
- Created/updated role/screen/action IDs.
- Capability candidate rationale.

### Acceptance Criteria

- Given a screen references a role, that role must exist.
- Given an action is destructive, it must define confirmation, audit, and rollback/recovery behavior.
- Given a repeated cross-product-looking action, the system allows logging a shared capability candidate.

---

## Journey: Review and Approve a Spec Section

### Trigger

A section is ready for review.

### Actor

Reviewer or Owner.

### Preconditions

- Section status is `ready_for_review`.
- Actor has review permission.
- Section has at least one revision.

### Happy Path

1. Reviewer opens review queue.
2. Reviewer reads the section.
3. Reviewer checks completeness, ambiguity, risks, and boundary leaks.
4. Reviewer adds comments where needed.
5. Reviewer either:
   - approves the section; or
   - requests changes with reasons.
6. System records review decision.
7. If approved, section status becomes `approved`.
8. If changes requested, section status becomes `changes_requested`.

### Alternate Paths

- Reviewer flags architecture risk.
- Reviewer suggests a shared capability candidate.
- Owner waives a risk with rationale.

### Failure Paths

- Actor lacks review permission.
- Section was modified during review.
- Required fields are incomplete.

### Recovery Path

- Ask reviewer to refresh if section changed.
- Block approval if required fields are missing.
- Allow comments without approval.

### Data Created or Updated

- `ReviewDecision`
- `CommentThread`
- `RiskFlag`
- `SpecSection.status`

### Events Emitted

- `review_comment_created`
- `section_approved`
- `section_changes_requested`
- `risk_flagged`

### Audit Requirements

- Reviewer ID.
- Review decision.
- Rationale.
- Section revision reviewed.

### Acceptance Criteria

- Given a section changed after review started, reviewer must approve the latest revision or explicitly acknowledge the change.
- Given changes are requested, final package approval is blocked until resolved or waived.
- Given a section is approved, its approved revision is tracked.

---

## Journey: Approve Spec Package

### Trigger

All MVP sections are complete enough for implementation planning.

### Actor

Owner.

### Preconditions

- Required sections are approved or explicitly waived.
- Blocking open questions are resolved or deferred.
- Critical risks are resolved or accepted with rationale.
- Actor has final approval permission.

### Happy Path

1. Owner opens Spec Package Review.
2. System displays readiness checklist:
   - charter;
   - roles;
   - journeys;
   - screens/actions;
   - domain model;
   - open questions;
   - shared capability candidates;
   - risks.
3. Owner reviews unresolved issues.
4. Owner approves package.
5. System creates immutable `SpecPackage` version.
6. System records `spec_package_approved`.
7. Package becomes available for export or Bolt handoff.

### Alternate Paths

- Owner approves with non-blocking open questions.
- Owner exports draft package without final approval.
- Owner reopens an approved section before package approval.

### Failure Paths

- Required section missing.
- Blocking question unresolved.
- Requested changes unresolved.
- Actor lacks permission.

### Recovery Path

- Show readiness checklist with blockers.
- Deep-link to blocking sections/questions.
- Allow explicit waiver only for configured blocker types.

### Data Created or Updated

- `SpecPackage`
- `SpecPackageItem`
- `ApprovalRecord`
- `ActivityEvent`

### Events Emitted

- `spec_package_approved`
- `spec_package_created`

### Audit Requirements

- Owner ID.
- Package version.
- Included section revisions.
- Waivers and rationale.

### Acceptance Criteria

- Given required sections are not approved, package approval is blocked.
- Given package is approved, included section revisions cannot be silently changed.
- Given waivers exist, they are included in the package audit record.

---

## Journey: Request Bolt Handoff

### Trigger

An approved spec package should be transformed into an implementation plan.

### Actor

Owner or delegated Editor.

### Preconditions

- Spec package is approved.
- Actor has handoff permission.
- Bolt integration is configured.
- No automatic implementation execution is enabled in MVP.

### Happy Path

1. Actor opens approved Spec Package.
2. Actor selects “Prepare Bolt handoff”.
3. System summarizes:
   - package version;
   - included sections;
   - open questions;
   - risks;
   - shared capability candidates;
   - requested planning scope.
4. Actor confirms planning-only handoff.
5. System creates `ImplementationHandoff` using `canvas.bolt_handoff.v0.1`.
6. System validates payload hash, planning scope, traceability, waivers, and execution policy.
7. System sends handoff request to Bolt.
8. Bolt acknowledges receipt.
9. System records handoff status as `submitted` or `acknowledged` with `bolt_reference`.
10. Actor sees handoff status and link/reference.

### Alternate Paths

- Actor exports handoff package without sending to Bolt.
- Bolt returns validation errors.
- Actor scopes handoff to one slice only.

### Failure Paths

- Bolt unavailable.
- Package is not approved.
- Actor lacks permission.
- Handoff payload validation fails.

### Recovery Path

- Keep handoff draft.
- Allow retry.
- Show validation errors.
- Never execute implementation automatically.

### Data Created or Updated

- `ImplementationHandoff`
- `HandoffPayload`
- `ActivityEvent`

### Events Emitted

- `implementation_handoff_created`
- `implementation_handoff_validated`
- `implementation_handoff_validation_failed`
- `bolt_handoff_submitted`
- `bolt_handoff_failed`

### Audit Requirements

- Actor ID.
- Spec package version.
- Payload format `canvas.bolt_handoff.v0.1`.
- Payload hash/reference.
- Bolt response.
- Planning-only flag and `allow_execution=false`.

### Acceptance Criteria

- Given an unapproved package, handoff is blocked.
- Given Bolt is unavailable, handoff draft remains available for retry/export.
- Given handoff succeeds, the system records the exact package version, payload format, payload hash, and Bolt reference.
- Given MVP mode, Bolt handoff cannot trigger automatic implementation execution.
- Given the payload lacks `planning_only=true` or has `allow_execution=true`, handoff validation fails.

---

## Shared Capability Candidates Found

| Candidate | From journey | Proposed placement | Status |
| --- | --- | --- | --- |
| Spec workspace | Create workspace | Discuss: Rumble shared vs product-specific | Candidate |
| Spec section | Draft/review sections | Rumble shared spec primitive | Candidate |
| Revision | Draft/review/package | Gear event log or Rumble domain | Candidate |
| Comment thread | Review | Shared Rumble | Candidate |
| Review decision | Review | Rumble shared + audit log | Candidate |
| Approval record | Package approval / handoff | Bolt gate + Rumble UX | Candidate |
| Spec package | Package approval | Gear artifact | Candidate |
| Implementation handoff | Bolt handoff | Rumble-to-Bolt boundary object; MVP target `cos-matic` | Accepted for Canvas MVP |
| Capability candidate | Screens/actions | Shared registry concept | Candidate |
