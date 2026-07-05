# Personas and Roles — rumble-canvas

## Scope

This document defines the MVP personas and roles for `rumble-canvas`.

`rumble-canvas` is a product-conception workspace. Its roles must support one core loop:

> clarify intent → structure specs → review decisions → approve handoff → feed the harness

---

## Personas

### Persona: Solo Builder

#### Goal

Turn a rough product idea into a structured, implementable specification without needing a full product team.

#### Motivations

- Avoid vague prompts and unclear implementation requests.
- Make scope explicit before coding.
- Produce reusable specs and acceptance criteria.
- Identify when a feature should become a shared harness capability.

#### Pain Points

- Ideas are scattered across notes, chats, docs, and code.
- Product decisions are implicit and easy to ecosystemt.
- Agents can implement too early from ambiguous instructions.
- Data model and permission details are often discovered too late.

#### Success Condition

The solo builder can export a coherent spec package and request a Bolt handoff without losing context.

---

### Persona: Product Lead

#### Goal

Align stakeholders around product scope, roles, screens, workflows, and acceptance criteria.

#### Motivations

- Reduce ambiguity before engineering starts.
- Make trade-offs visible.
- Keep product decisions auditable.
- Prevent scope creep.

#### Pain Points

- Meetings produce loose notes but not implementation-ready specs.
- Stakeholders disagree on what was decided.
- Product requirements and technical feasibility drift apart.

#### Success Condition

The product lead can turn discussion into reviewed decisions and a validated screen/action matrix.

---

### Persona: Tech Lead

#### Goal

Ensure the product spec is implementable, secure, testable, and correctly mapped to Rumble/Bolt/Wrench/Gear responsibilities.

#### Motivations

- Detect architecture boundary leaks early.
- Identify missing data, permissions, and service contracts.
- Convert accepted scope into safe implementation plans.

#### Pain Points

- Specs often ignore failure modes, permissions, migrations, and observability.
- Product flows sometimes hide infrastructure or orchestration requirements.
- Agents may duplicate shared capabilities if not guided.

#### Success Condition

The tech lead can review the spec, mark risks, and approve or block implementation handoff.

---

### Persona: Reviewer

#### Goal

Challenge completeness, clarity, risk, and alignment before a spec becomes executable.

#### Motivations

- Catch contradictions and missing cases.
- Ensure acceptance criteria are testable.
- Protect security, privacy, and architecture boundaries.

#### Pain Points

- Reviews are often unstructured.
- Comments become detached from decisions.
- Approval status is unclear.

#### Success Condition

The reviewer can leave structured comments, request changes, and approve specific sections.

---

### Persona: Agent Operator

#### Goal

Use accepted specs to request safe planning or implementation from the harness.

#### Motivations

- Avoid manual prompt rewriting.
- Ensure agents receive precise, bounded context.
- Track what was sent to Bolt and under which approval.

#### Pain Points

- Agent prompts are often non-repeatable.
- It is unclear which spec version was executed.
- There is no clean boundary between planning and execution.

#### Success Condition

The operator can produce a handoff package and request a Bolt plan without automatic execution.

---

## Roles

### Role: Owner

#### Goal

Own the spec workspace, its settings, permissions, and final approval authority.

#### Permissions

- Create a spec workspace.
- Rename/archive/delete a spec workspace.
- Invite or remove users.
- Assign roles.
- Edit all spec sections.
- Approve final spec package.
- Accept low/medium waivers.
- Co-approve high/critical waivers with a distinct human Reviewer.
- Request Bolt handoff.
- Export all workspace data.

#### Visible Data

- All workspace content.
- All comments, decisions, assumptions, and open questions.
- All audit and activity entries.
- All handoff packages.

#### Editable Data

- Product charter.
- Roles.
- Journeys.
- Screens/actions.
- Domain model.
- Shared capability candidates.
- Workspace settings.

#### Allowed Actions

- `create_spec_workspace`
- `update_workspace_settings`
- `invite_member`
- `change_member_role`
- `archive_workspace`
- `delete_workspace`
- `edit_spec_section`
- `accept_decision`
- `resolve_open_question`
- `approve_spec_package`
- `propose_waiver`
- `accept_low_medium_waiver`
- `co_approve_high_critical_waiver`
- `request_bolt_handoff`
- `export_spec_package`

#### Forbidden Actions

- Bypass audit logs.
- Execute agent implementation directly without Bolt handoff.
- Delete immutable handoff history.

#### Edge Cases

- Last owner cannot be removed unless ownership is transferred.
- Deletion may require export/archive confirmation.
- Handoff package history must remain auditable even if workspace is archived.

#### Trust / Security Expectations

- All destructive actions are confirmed.
- Final approval is logged.
- Handoff requests are tied to a spec version.

---

### Role: Editor

#### Goal

Create and modify product spec content.

#### Permissions

- Edit spec sections.
- Create decisions as proposed decisions.
- Create assumptions and open questions.
- Create shared capability candidates.
- Comment and respond to comments.
- Export drafts if allowed by workspace settings.

#### Visible Data

- All non-restricted spec content.
- Comments and review status.
- Shared capability candidates.

#### Editable Data

- Draft sections.
- Proposed decisions.
- Open questions.
- Comments.

#### Allowed Actions

- `edit_spec_section`
- `create_proposed_decision`
- `create_assumption`
- `create_open_question`
- `create_capability_candidate`
- `comment_on_section`
- `mark_section_ready_for_review`

#### Forbidden Actions

- Final approval.
- Member/role management.
- Workspace deletion.
- Bolt handoff request unless explicitly delegated.

#### Edge Cases

- Editing an approved section should create a new draft revision.
- Conflicting edits must preserve both versions or require resolution.

#### Trust / Security Expectations

- Edits are attributed.
- Major changes are visible in activity log.

---

### Role: Reviewer

#### Goal

Validate or challenge spec quality before approval.

#### Permissions

- Read spec sections.
- Add structured comments.
- Request changes.
- Approve sections.
- Flag architecture/security/product risks.
- Co-approve high/critical waivers when independent from the waived target.

#### Visible Data

- Spec content under review.
- Open questions.
- Proposed decisions.
- Change history relevant to reviewed sections.

#### Editable Data

- Review comments.
- Review status.
- Risk flags.

#### Allowed Actions

- `comment_on_section`
- `request_changes`
- `approve_section`
- `flag_risk`
- `co_approve_high_critical_waiver`
- `suggest_capability_candidate`

#### Forbidden Actions

- Edit spec content directly unless also Editor.
- Approve final package unless also Owner.
- Request Bolt handoff.

#### Edge Cases

- A reviewer cannot approve their own section if separation-of-duty is enabled.
- Requested changes block final approval until resolved or waived by Owner.

#### Trust / Security Expectations

- Review decisions are logged with rationale.
- Risk waivers require Owner confirmation.

---

### Role: Viewer

#### Goal

Read the product spec and understand scope/status.

#### Permissions

- View approved sections.
- View exported packages.
- View public comments if allowed.

#### Visible Data

- Approved or shared spec content.
- Published decisions.
- High-level status.

#### Editable Data

None.

#### Allowed Actions

- `view_spec`
- `download_export_if_allowed`

#### Forbidden Actions

- Edit.
- Comment unless explicitly allowed.
- Review.
- Approve.
- Request handoff.

#### Edge Cases

- Draft visibility may be restricted.
- Sensitive sections may be hidden.

#### Trust / Security Expectations

- Viewer access must not expose restricted discussions or private sources.

---

### Role: Agent

#### Goal

Assist with analysis, drafting, inspection, or handoff preparation under human control.

#### Permissions

- Read explicitly provided context.
- Suggest spec text.
- Suggest missing cases.
- Suggest shared capability candidates.
- Produce draft outputs.

#### Visible Data

- Only context included in the current task/run.
- No implicit access to all workspace data unless authorized.

#### Editable Data

None directly in MVP. Agent outputs are suggestions until accepted by a human.

#### Allowed Actions

- `suggest_spec_section`
- `suggest_open_question`
- `suggest_decision`
- `suggest_capability_candidate`
- `prepare_handoff_draft`

#### Forbidden Actions

- Directly approve decisions.
- Directly edit accepted sections.
- Directly execute implementation.
- Access data outside assigned context.

#### Edge Cases

- Agent-generated content must be marked as such until accepted.
- Agent suggestions may require citation to source material.

#### Trust / Security Expectations

- Human approval is required for accepted changes.
- Agent runs are logged.
- Prompt/context used for a suggestion should be reproducible where possible.

---

### Role: System

#### Goal

Maintain integrity, state transitions, auditability, and automated checks.

#### Permissions

- Enforce role permissions.
- Create activity log entries.
- Compute section completeness status.
- Detect missing required fields.
- Track revisions.
- Trigger non-destructive checks.

#### Visible Data

System has operational access only as required by deployment architecture.

#### Editable Data

- Derived status fields.
- Audit/activity log.
- Completeness reports.

#### Allowed Actions

- `record_activity`
- `compute_completeness`
- `validate_required_fields`
- `create_revision`
- `mark_handoff_package_immutable`

#### Forbidden Actions

- Change product content without actor attribution.
- Approve specs.
- Execute implementation.

#### Trust / Security Expectations

- System actions are deterministic and auditable.
- Derived state can be recomputed from source state where possible.

---

## MVP Permission Matrix

| Action | Owner | Editor | Reviewer | Viewer | Agent | System |
| --- | --- | --- | --- | --- | --- | --- |
| Create workspace | Yes | No | No | No | No | No |
| Edit draft spec | Yes | Yes | No | No | Suggest only | No |
| Comment | Yes | Yes | Yes | No | Suggest only | No |
| Request changes | Yes | No | Yes | No | Suggest only | No |
| Approve section | Yes | No | Yes | No | No | No |
| Approve final package | Yes | No | No | No | No | No |
| Propose waiver | Yes | Yes | Yes | No | Suggest only | No |
| Accept low/medium waiver | Yes | No | No | No | No | No |
| Co-approve high/critical waiver | Yes | No | Yes | No | No | No |
| Request Bolt handoff | Yes | Delegated only | No | No | No | No |
| Export package | Yes | If allowed | No | If allowed | No | No |
| Manage members | Yes | No | No | No | No | No |
| Record audit event | No | No | No | No | No | Yes |

---

## Shared Capability Candidates

| Candidate | Reason | Proposed placement |
| --- | --- | --- |
| Actor reference | All auditable products need human/agent/system attribution. | Shared auth/profile adapter later; Canvas MVP owns minimal snapshot. |
| Workspace membership | Collaboration, ownership, and invitations recur across Rumble products. | Shared Rumble + app-specific adapters. |
| Role assignment | Permission checks need actor-to-role mapping, separate from product role definitions. | Shared Rumble + app-specific adapters. |
| Role | All products need role/permission semantics. | Shared Rumble + app-specific adapters. |
| Permission matrix | Reused across Rumble products. | Shared Rumble or Gear policy adapter. |
| Comment/thread | Reviews and collaboration recur in multiple products. | Shared Rumble. |
| Activity log | Audit and agent readability recur everywhere. | Gear event log. |
| Agent suggestion | Agent output requiring human acceptance appears across products. | Bolt for runs; Rumble shared for presentation. |
| Approval | Needed for sections, handoffs, publication, execution. | Bolt for gates; Rumble UX for interaction. |

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should `Agent` be a role in the same permission model as humans or a separate actor type? | High | Accepted for MVP: agent is both `actor_type=agent` and assignable role, but cannot approve or execute. |
| Should `Reviewer` approvals be section-level only or also package-level? | Medium | Open |
| Should comments be allowed for Viewers in public review mode? | Low | Open |
| Should delegated Bolt handoff be allowed for Editors in MVP? | Medium | Open |
