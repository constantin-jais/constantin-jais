# Screens and Actions — rumble-canvas

## Scope

This document defines the first MVP screens and role-based actions.

The goal is to specify enough of the product to support the first vertical slice:

> create workspace → draft charter → define roles/screens/actions → review → package → handoff

---

## Screen: Home

### Purpose

Let the user create or resume spec workspaces.

### Route / Entry Point

`/`

### Allowed Roles

- Authenticated user / local profile.

### Displayed Data

- Recent spec workspaces.
- Workspace status.
- Last edited timestamp.
- Sync/storage status if applicable.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner-capable user | Create workspace, open workspace, duplicate workspace, archive workspace. |
| Viewer | Open accessible workspace. |
| System | Compute recent list and status. |

### Empty State

No workspaces yet.

Primary action: `Create spec workspace`.

### Loading State

Show skeleton list and storage status.

### Error State

If workspaces cannot load, show retry and local recovery option when available.

### Offline State

Show locally available workspaces and indicate that remote sync/handoff is unavailable.

### Permission Denied State

If user cannot create workspace, show read-only available workspaces.

### Accessibility Notes

- Workspace list navigable by keyboard.
- Status indicators must have text labels.

### Telemetry / Events

- `home_viewed`
- `create_workspace_clicked`

### Service Calls

- `WorkspaceService.listWorkspaces()`
- `WorkspaceService.createWorkspace()`

### Acceptance Criteria

- Given no workspaces exist, user sees a clear create action.
- Given workspaces exist, user can open one.
- Given storage fails, user sees a retry and no data is silently lost.

---

## Screen: New Spec Workspace

### Purpose

Capture the minimum information needed to initialize a spec workspace.

### Route / Entry Point

`/new`

### Allowed Roles

- Owner-capable user.

### Displayed Data

Form fields:

- workspace name;
- short product idea;
- intended audience;
- optional initial context;
- optional template.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Create workspace, cancel. |
| Agent | Suggest clearer product idea from entered context. |
| System | Validate fields, create default sections. |

### Empty State

Empty form with short guidance.

### Loading State

Show creation progress; disable duplicate submission.

### Error State

- Invalid name.
- Duplicate slug.
- Storage unavailable.

### Offline State

Allow local-only draft workspace if supported; otherwise explain limitation.

### Permission Denied State

User cannot create workspace.

### Accessibility Notes

- Form labels required.
- Errors associated with fields.

### Telemetry / Events

- `new_workspace_viewed`
- `spec_workspace_created`
- `spec_workspace_creation_failed`

### Service Calls

- `WorkspaceService.validateWorkspaceInput()`
- `WorkspaceService.createWorkspace()`

### Acceptance Criteria

- Given valid input, workspace is created in `draft` status.
- Given duplicate slug, creation is blocked with a clear error.
- Given user double-clicks submit, only one workspace is created.

---

## Screen: Workspace Overview

### Purpose

Show current spec status, blockers, and recommended next actions.

### Route / Entry Point

`/workspaces/:workspaceId`

### Allowed Roles

- Owner
- Editor
- Reviewer
- Viewer

### Displayed Data

- Product/workspace name.
- Mission summary.
- Section status list.
- Completeness report.
- Open blockers.
- Recent decisions.
- Shared capability candidate count.
- Last activity.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Edit settings, approve package if ready, request handoff if package approved. |
| Editor | Continue drafting, mark sections ready for review. |
| Reviewer | Open review queue, review ready sections. |
| Viewer | Read approved content. |
| Agent | Suggest next missing section or completeness improvements. |
| System | Compute completeness and blockers. |

### Empty State

Workspace has no meaningful content yet.

Primary action: `Start product charter`.

### Loading State

Show section skeletons and status placeholders.

### Error State

If status cannot be computed, show sections but mark completeness unavailable.

### Offline State

Allow viewing/editing local draft sections if available; disable remote handoff.

### Permission Denied State

If user lacks workspace access, show no content and explain access requirement.

### Accessibility Notes

- Completion status must not rely only on color.
- Blockers should be navigable as links.

### Telemetry / Events

- `workspace_overview_viewed`
- `next_action_clicked`

### Service Calls

- `WorkspaceService.getWorkspace()`
- `SpecStatusService.computeCompleteness()`
- `ActivityService.listRecentActivity()`

### Acceptance Criteria

- Given required sections are incomplete, overview lists next missing sections.
- Given blockers exist, overview links to blocking questions/reviews.
- Given package is approved, handoff action is visible to authorized users.

---

## Screen: Product Charter

### Purpose

Define the product’s mission, users, jobs, promise, non-goals, boundaries, MVP, and success metrics.

### Route / Entry Point

`/workspaces/:workspaceId/charter`

### Allowed Roles

- Owner
- Editor
- Reviewer
- Viewer with approved-content access

### Displayed Data

- Mission.
- Target users.
- Jobs-to-be-done.
- Product promise.
- Non-goals.
- Boundaries.
- Success metrics.
- MVP scope.
- Post-MVP scope.
- Risks.
- Review status.
- Comments.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Edit, save, request review, approve section, waive blocker. |
| Editor | Edit, save, request review, respond to comments. |
| Reviewer | Comment, request changes, approve section, flag risk. |
| Viewer | Read approved revision. |
| Agent | Suggest draft, suggest missing non-goals, suggest risks. |
| System | Validate required fields, create revision, compute completeness. |

### Empty State

Explain that the charter prevents scope drift and anchors all later sections.

Primary action: `Start charter`.

Secondary action: `Suggest outline`.

### Loading State

Show form skeleton and latest revision status.

### Error State

- Required fields missing when marking ready for review.
- Save conflict.
- Storage error.

### Offline State

Allow local draft save if possible; show unsynced state.

### Permission Denied State

Read-only or no access depending on role.

### Accessibility Notes

- Long text areas must have clear labels.
- Review comments must be reachable by keyboard.

### Telemetry / Events

- `charter_viewed`
- `charter_saved`
- `charter_marked_ready_for_review`
- `charter_reviewed`

### Service Calls

- `SpecSectionService.getSection(charter)`
- `SpecSectionService.saveRevision()`
- `ReviewService.requestReview()`
- `ReviewService.approveSection()`

### Acceptance Criteria

- Given required charter fields are complete, Editor can mark section ready for review.
- Given required fields are missing, readiness is blocked with field-level feedback.
- Given Reviewer requests changes, section status becomes `changes_requested`.

---

## Screen: Roles

### Purpose

Define product actors, permissions, visible data, editable data, and forbidden actions.

### Route / Entry Point

`/workspaces/:workspaceId/roles`

### Allowed Roles

- Owner
- Editor
- Reviewer
- Viewer with approved-content access

### Displayed Data

- Role list.
- Permission summary.
- Visible/editable data per role.
- Role-related open questions.
- Review comments.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Add/edit/delete role, request review, approve section. |
| Editor | Add/edit role, define permissions, request review. |
| Reviewer | Comment, request changes, approve section, flag missing permission cases. |
| Viewer | Read approved roles. |
| Agent | Suggest roles from charter, suggest permission gaps. |
| System | Validate referenced roles, detect orphan screen actions. |

### Empty State

No roles defined.

Primary action: `Add role`.

Secondary action: `Suggest roles from charter`.

### Loading State

Show role card skeletons.

### Error State

- Duplicate role name.
- Role referenced by screens cannot be deleted without migration.
- Missing required fields.

### Offline State

Allow local draft role edits if possible.

### Permission Denied State

Read-only or no access.

### Accessibility Notes

- Permission matrix must be screen-reader friendly.
- Role cards must expose status text.

### Telemetry / Events

- `roles_viewed`
- `role_created`
- `role_updated`
- `role_deleted`

### Service Calls

- `RoleService.listRoles()`
- `RoleService.createRole()`
- `RoleService.updateRole()`
- `RoleService.deleteRole()`
- `SpecValidationService.validateRoleReferences()`

### Acceptance Criteria

- Given a screen action references a role, that role cannot be deleted without resolving references.
- Given duplicate role name, save is blocked.
- Given roles are complete, section can be marked ready for review.

---

## Screen: Screens and Actions

### Purpose

Define each MVP screen, allowed roles, displayed data, states, and actions by role.

### Route / Entry Point

`/workspaces/:workspaceId/screens-actions`

### Allowed Roles

- Owner
- Editor
- Reviewer
- Viewer with approved-content access

### Displayed Data

- Screen list.
- Screen purpose.
- Route/entry point.
- Allowed roles.
- Displayed data.
- Actions by role.
- States: empty, loading, error, offline, permission denied.
- Service calls.
- Acceptance criteria.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Add/edit/delete screen, add/edit actions, request review, approve section. |
| Editor | Add/edit screen, add/edit actions, request review. |
| Reviewer | Comment, request changes, approve section, flag missing states or permissions. |
| Viewer | Read approved screen/action matrix. |
| Agent | Suggest missing states, detect destructive actions, suggest capability candidates. |
| System | Validate roles, detect missing action rules, detect repeated candidates. |

### Empty State

No screens defined.

Primary action: `Add first screen`.

Secondary action: `Derive screens from journeys`.

### Loading State

Show screen table skeleton.

### Error State

- Screen has no purpose.
- Action has no actor.
- Referenced role does not exist.
- Destructive action lacks audit/confirmation rule.

### Offline State

Allow draft edits when local storage is available.

### Permission Denied State

Read-only or no access.

### Accessibility Notes

- Matrix must support keyboard navigation.
- Tables need row/column headers.

### Telemetry / Events

- `screens_actions_viewed`
- `screen_created`
- `action_created`
- `capability_candidate_suggested`

### Service Calls

- `ScreenService.listScreens()`
- `ScreenService.createScreen()`
- `ScreenService.updateScreen()`
- `ActionService.createAction()`
- `ActionService.updateAction()`
- `SpecValidationService.validateScreenActionMatrix()`

### Acceptance Criteria

- Given an action is destructive, readiness is blocked until confirmation/audit/recovery rules are defined.
- Given a role reference is missing, readiness is blocked.
- Given repeated action patterns are detected, user can log a shared capability candidate.

---

## Screen: Shared Capability Candidates

### Purpose

Track product needs that may become reusable Rumble/Portal/Bolt/Wrench/Gear bricks.

### Route / Entry Point

`/workspaces/:workspaceId/shared-capabilities`

### Allowed Roles

- Owner
- Editor
- Reviewer
- Viewer with approved-content access

### Displayed Data

- Candidate name.
- Description.
- Origin section/action.
- Needed by products if known.
- Proposed owner layer.
- Status.
- Rationale.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Create/edit candidate, accept/reject local candidate, export to shared registry. |
| Editor | Create/edit candidate, add rationale. |
| Reviewer | Comment, challenge placement, request rename. |
| Viewer | Read approved candidates. |
| Agent | Suggest candidates from repeated patterns. |
| System | Link candidates to origin sections/actions. |

### Empty State

No candidates identified yet.

Primary action: `Add capability candidate`.

Secondary action: `Scan spec for candidates`.

### Loading State

Show candidate list skeleton.

### Error State

- Missing name.
- Missing rationale.
- Invalid owner layer.

### Offline State

Allow local candidate drafting.

### Permission Denied State

Read-only or no access.

### Accessibility Notes

- Status and owner layer must be text-visible.

### Telemetry / Events

- `capabilities_viewed`
- `capability_candidate_created`
- `capability_candidate_exported`

### Service Calls

- `CapabilityCandidateService.listCandidates()`
- `CapabilityCandidateService.createCandidate()`
- `CapabilityCandidateService.updateCandidate()`
- `CapabilityCandidateService.exportCandidate()`

### Acceptance Criteria

- Given a candidate is created, it must include a rationale and proposed owner layer.
- Given a candidate is exported, the origin workspace and section are recorded.
- Given owner layer is unclear, status remains `Discuss`.

---

## Screen: Review

### Purpose

Review sections, request changes, approve sections, and prepare final package approval.

### Route / Entry Point

`/workspaces/:workspaceId/review`

### Allowed Roles

- Owner
- Reviewer
- Editor with read access

### Displayed Data

- Sections by status.
- Open comments.
- Requested changes.
- Risks.
- Blocking open questions.
- Readiness checklist.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Review, approve, waive risk, approve package if ready. |
| Reviewer | Review section, comment, request changes, approve section, flag risk. |
| Editor | View requested changes, respond, update draft. |
| Agent | Suggest review checklist issues. |
| System | Compute readiness checklist. |

### Empty State

No sections ready for review.

Primary action for Editor/Owner: `Continue drafting`.

### Loading State

Show review queue skeleton.

### Error State

- Readiness cannot be computed.
- Section changed during review.

### Offline State

Review comments may be drafted locally, but approvals require sync if audit persistence is unavailable.

### Permission Denied State

No access or read-only depending on role.

### Accessibility Notes

- Review queue must be navigable by status.
- Comments must have author/time metadata.

### Telemetry / Events

- `review_queue_viewed`
- `section_approved`
- `section_changes_requested`
- `risk_flagged`

### Service Calls

- `ReviewService.listReviewItems()`
- `ReviewService.comment()`
- `ReviewService.requestChanges()`
- `ReviewService.approveSection()`
- `SpecStatusService.computeReadiness()`

### Acceptance Criteria

- Given a section is changed after approval, its approval is invalidated or a new revision is created as draft.
- Given requested changes exist, final package approval is blocked unless waived.
- Given reviewer flags a risk, it appears in package readiness.

---

## Screen: Packages and Handoff

### Purpose

Create immutable spec packages, export Markdown, and request planning-only Bolt handoff.

### Route / Entry Point

`/workspaces/:workspaceId/packages`

### Allowed Roles

- Owner
- delegated Editor
- Viewer for approved exports if allowed

### Displayed Data

- Approved package versions.
- Included sections and revision IDs.
- Export status.
- Handoff status.
- Open risks/questions included in package.

### Actions by Role

| Role | Actions |
| --- | --- |
| Owner | Create package, approve package, export Markdown, request Bolt handoff. |
| Delegated Editor | Export draft if allowed, request handoff if delegated. |
| Viewer | Download approved export if allowed. |
| Agent | Prepare handoff draft. |
| System | Mark package immutable, hash payload, record audit. |

### Empty State

No package created.

Primary action: `Create package from approved sections`.

### Loading State

Show package creation progress.

### Error State

- Required sections missing.
- Blocking open questions unresolved.
- Bolt unavailable.
- Export failed.

### Offline State

Allow local Markdown export if possible; disable remote Bolt handoff.

### Permission Denied State

Read-only or no access.

### Accessibility Notes

- Package contents should be navigable as a list.
- Handoff status must be text-readable.

### Telemetry / Events

- `package_created`
- `package_approved`
- `package_exported`
- `implementation_handoff_validated`
- `implementation_handoff_validation_failed`
- `bolt_handoff_requested`
- `bolt_handoff_failed`

### Service Calls

- `PackageService.createPackage()`
- `PackageService.approvePackage()`
- `PackageService.exportMarkdown()`
- `HandoffService.prepareBoltHandoff()`
- `HandoffService.submitToBolt()`

### Acceptance Criteria

- Given blockers exist, package approval is blocked or requires explicit waiver.
- Given package is approved, included revisions are immutable.
- Given Bolt handoff fails, the handoff draft remains retryable/exportable.
- Given MVP mode, handoff is planning-only and cannot trigger implementation execution.
- Given a handoff is prepared, it uses `canvas.bolt_handoff.v0.1` and includes package hash, traceability links, active waivers, risks, capability candidates, requested outputs, and execution policy.

---

## Cross-Screen Action Requirements

### Action: Save Draft

- Must create or update a revision.
- Must attribute actor.
- Must preserve local input on failure where possible.
- Must not invalidate approved package versions.

### Action: Mark Ready for Review

- Must validate required fields.
- Must set section status to `ready_for_review`.
- Must notify reviewers if notifications exist.

### Action: Approve Section

- Must record reviewer, revision, timestamp, and rationale if required.
- Must approve a specific revision.
- Must be invalidated or superseded if section changes.

### Action: Request Bolt Handoff

- Requires approved spec package.
- Must use `canvas.bolt_handoff.v0.1` with kind `planning_request`.
- Must include package identity, immutable revision IDs, planning scope, traceability links, active waivers, open risks/questions, capability candidates, constraints, requested outputs, and execution policy.
- Must be planning-only in MVP.
- Must set `execution_policy.planning_only=true` and `execution_policy.allow_execution=false`.
- Must record payload reference/hash.
- Must never silently execute implementation.

## Shared Capability Candidates

| Candidate | Reason | Proposed placement |
| --- | --- | --- |
| Workspace shell | Many Rumbles need workspace-like navigation and status. | Shared Rumble. |
| Section editor with review | Reusable for specs, articles, courses, notes. | Shared Rumble. |
| Screen/action matrix | May be Canvas-specific but useful as spec primitive. | Rumble Canvas first, later shared if reused. |
| Readiness checklist | Reusable before handoff/publication/execution. | Bolt gates + Rumble UX. |
| Package/export flow | Reusable for artifacts. | Gear artifact + Rumble UX. |
| Handoff service | Specific bridge to Bolt. | Bolt API + Rumble adapter. |
