# Information Architecture — rumble-canvas

## Scope

This document defines the MVP information architecture for `rumble-canvas`.

The IA must keep the product focused on structured product conception, not generic whiteboarding.

---

## Primary Object Hierarchy

```text
Account / Local profile
└── Spec Workspace
    ├── Product Charter
    ├── Personas and Roles
    ├── User Journeys
    ├── Screens and Actions
    ├── Domain Model
    ├── Shared Capability Candidates
    ├── Decisions
    ├── Assumptions
    ├── Open Questions
    ├── Review Comments
    ├── Spec Packages
    └── Implementation Handoffs
```

## Primary Spaces

### 1. Home

Purpose:

- list existing spec workspaces;
- create a new workspace;
- resume recent work;
- show local/remote sync status if applicable.

Primary objects:

- `SpecWorkspace`

---

### 2. Spec Workspace Overview

Purpose:

- show product identity;
- show spec completion;
- show blockers;
- navigate to sections;
- surface next recommended actions.

Primary objects:

- `SpecWorkspace`
- `CompletenessReport`
- `OpenQuestion`
- `RiskFlag`
- `ReviewDecision`

---

### 3. Product Charter

Purpose:

- define mission, users, jobs, non-goals, boundaries, and success metrics.

Primary objects:

- `SpecSection`
- `SpecSectionRevision`

---

### 4. Roles

Purpose:

- define human, agent, and system actors;
- define permissions and visible/editable data.

Primary objects:

- `RoleDefinition`
- `PermissionRule`

---

### 5. Journeys

Purpose:

- describe product workflows from trigger to outcome;
- capture happy paths, alternate paths, failures, recovery, events, and acceptance criteria.

Primary objects:

- `JourneyDefinition`
- `EventDefinition`

---

### 6. Screens and Actions

Purpose:

- define screens;
- list actions by role;
- specify states, service calls, validation, and acceptance criteria.

Primary objects:

- `ScreenDefinition`
- `ActionDefinition`
- `RoleDefinition`

---

### 7. Domain Model

Purpose:

- define entities, value objects, lifecycle states, invariants, relationships, and deletion/archive rules.

Primary objects:

- `DomainEntity`
- `ValueObject`
- `StateTransition`

---

### 8. Decisions and Questions

Purpose:

- centralize accepted decisions, assumptions, open questions, and waivers.

Primary objects:

- `DecisionRecord`
- `Assumption`
- `OpenQuestion`
- `RiskFlag`

---

### 9. Shared Capability Candidates

Purpose:

- list needs that may become shared Rumble/Portal/Bolt/Wrench/Gear bricks;
- discuss naming and placement;
- export candidates to ecosystem registry.

Primary objects:

- `CapabilityCandidate`

---

### 10. Review

Purpose:

- review sections;
- request changes;
- approve sections;
- flag risks;
- prepare final package approval.

Primary objects:

- `ReviewDecision`
- `CommentThread`
- `CompletenessReport`

---

### 11. Packages and Handoff

Purpose:

- create immutable spec package versions;
- export Markdown;
- prepare planning-only Bolt handoff.

Primary objects:

- `SpecPackage`
- `ImplementationHandoff`
- `ArtifactReference`

---

### 12. Settings

Purpose:

- manage workspace metadata;
- manage members and roles;
- configure exports and integrations;
- configure review rules.

Primary objects:

- `WorkspaceSettings`
- `Member`
- `IntegrationConfig`

---

## MVP Navigation Model

```text
Home
└── Workspace
    ├── Overview
    ├── Charter
    ├── Roles
    ├── Journeys
    ├── Screens & Actions
    ├── Domain Model
    ├── Decisions & Questions
    ├── Shared Capabilities
    ├── Review
    ├── Packages & Handoff
    └── Settings
```

## Status Model

### Workspace Status

| Status | Meaning |
| --- | --- |
| `draft` | Workspace is being specified. |
| `in_review` | At least one section is ready for review. |
| `approved` | A spec package has been approved. |
| `handoff_requested` | A package has been submitted to Bolt planning. |
| `archived` | Workspace is no longer active. |

### Section Status

| Status | Meaning |
| --- | --- |
| `empty` | Section exists but has no meaningful content. |
| `draft` | Section is being edited. |
| `ready_for_review` | Section is complete enough for review. |
| `changes_requested` | Reviewer requested changes. |
| `approved` | Section revision is approved. |
| `waived` | Section is intentionally skipped with rationale. |

### Package Status

| Status | Meaning |
| --- | --- |
| `draft` | Package is being assembled. |
| `approved` | Package version is approved and immutable. |
| `exported` | Package was exported. |
| `handoff_submitted` | Package was sent to Bolt for planning. |
| `handoff_failed` | Bolt submission failed and can be retried. |

## Search and Browse Model

MVP search should support:

- workspace name;
- section title;
- role name;
- screen name;
- action name;
- decision text;
- open question text;
- capability candidate name.

Post-MVP search may include semantic search via Gear Memory.

## Empty State Strategy

Every empty state should do three things:

1. Explain what the section is for.
2. Offer a first manual action.
3. Optionally offer an agent-assisted draft action.

Example:

> No roles defined yet. Start by adding the people, agents, or systems that interact with this product.

Primary action: `Add role`  
Secondary action: `Suggest roles from charter`

## Error State Strategy

Errors must be actionable and non-destructive.

- Validation errors should be inline.
- Storage errors should preserve local draft input.
- Permission errors should explain the missing permission.
- Bolt/Wrench/Gear integration errors should never silently discard a handoff or artifact.

## Offline State Strategy

MVP should not assume constant network access for drafting.

Minimum expectations:

- local draft preservation;
- visible sync/export status;
- no silent data loss;
- handoff unavailable while offline unless exported as file.

## Shared Capability Candidates

| Candidate | Reason | Proposed placement |
| --- | --- | --- |
| Spec workspace navigation shell | Could apply to other structured Rumble workspaces. | Shared Rumble. |
| Section status model | Reusable for specs, courses, notes, publication workflows. | Shared Rumble. |
| Package status model | Reusable for artifacts and handoffs. | Gear artifact + Rumble UX. |
| Search primitive | All Rumbles need object search. | Gear Memory. |
| Empty/error/offline state conventions | Product-wide UX consistency. | Shared Rumble design system. |
