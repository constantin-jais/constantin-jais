# Domain Model — rumble-canvas

## Scope

This document defines the MVP domain model for `rumble-canvas`.

The model must support:

- structured product conception;
- section drafting and review;
- role/screen/action specification;
- shared capability detection;
- spec packaging;
- planning-only handoff to Bolt.

---

## Aggregate Overview

```text
SpecWorkspace
├── WorkspaceMembership
│   └── RoleAssignment
├── SpecSection
│   └── SpecSectionRevision
├── RoleDefinition
├── JourneyDefinition
├── ScreenDefinition
│   └── ActionDefinition
├── DomainEntityDraft
├── DecisionRecord
├── Assumption
├── OpenQuestion
├── CommentThread
│   └── Comment
├── ReviewDecision
├── RiskFlag
├── Waiver
├── CapabilityCandidate
├── TraceabilityLink
├── SpecPackage
│   └── SpecPackageItem
└── ImplementationHandoff
```

## Aggregate Boundary

### Primary Aggregate: `SpecWorkspace`

`SpecWorkspace` is the root aggregate for product-conception work.

It owns the lifecycle of draft sections, roles, journeys, screens, decisions, comments, reviews, packages, and handoffs.

### External References

The workspace may reference external/substrate objects without owning them:

| Reference | Owner layer | Notes |
| --- | --- | --- |
| `SourceReference` | Gear Memory / Gear Loader | Context imported from files, URLs, notes, transcripts. |
| `ArtifactReference` | Gear Depot / Gear Memory | Exported spec package, handoff payload, generated report. |
| `BoltRunReference` | Bolt | Planning run created after handoff. |
| `UserReference` | Identity layer / app | Human actor. |
| `AgentReference` | Bolt / runtime registry | Agent actor or assistant. |

---

## Value Object: ActorReference

### Definition

A normalized reference to the actor responsible for an action, decision, review, waiver, or generated suggestion.

`ActorReference` is intentionally not the full identity model. It is the minimum spec-level attribution contract until shared identity/auth is decided.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `actor_id` | string/UUID | Yes | Stable local or external identifier. |
| `actor_type` | enum | Yes | `human`, `agent`, `system`, `external`. |
| `display_name` | string | No | Snapshot for readability. |
| `source` | enum/string | No | `local_profile`, `workspace_member`, `bolt_agent`, `system`, `external`. |

### Invariants

- Every auditable action must store an actor reference.
- Agent and system actors cannot be treated as human approvers unless an explicit human proxy is recorded.
- Actor references are snapshots for audit; identity resolution may happen through a later shared auth/profile layer.

---

## Entity: WorkspaceMembership

### Definition

A membership grants one actor access to one `SpecWorkspace`.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `actor` | ActorReference | Yes | Member actor. |
| `status` | enum | Yes | `invited`, `active`, `suspended`, `removed`. |
| `created_by` | ActorId | Yes | Inviter or system creator. |
| `created_at` | timestamp | Yes | Audit. |
| `updated_at` | timestamp | Yes | Audit. |

### Invariants

- A workspace must always have at least one active human Owner assignment.
- Removed or suspended memberships cannot perform workspace actions.
- Agent memberships are allowed only for scoped assistance and cannot own the workspace in MVP.

### Events

- `workspace_member_invited`
- `workspace_member_activated`
- `workspace_member_suspended`
- `workspace_member_removed`

---

## Entity: RoleAssignment

### Definition

A role assignment attaches a product role to a workspace membership.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `membership_id` | UUID | Yes | Parent membership. |
| `role` | enum | Yes | `owner`, `editor`, `reviewer`, `viewer`, `agent`, `system`. |
| `scope` | enum/string | No | `workspace`, `section`, `package`, or a target object reference. Defaults to workspace. |
| `status` | enum | Yes | `active`, `revoked`. |
| `assigned_by` | ActorId | Yes | Actor granting the role. |
| `assigned_at` | timestamp | Yes | Audit. |
| `revoked_at` | timestamp | No | Audit. |

### Invariants

- Permission checks derive from active role assignments, not only from persona labels.
- The last active human Owner role assignment cannot be revoked without transferring ownership.
- Reviewer self-approval can be blocked by policy when `created_by == reviewer_id`.
- Agent role assignments cannot approve packages, accept waivers, or request execution.

### Events

- `role_assignment_created`
- `role_assignment_revoked`

### Shared Capability Candidate

Strong shared Rumble/auth-adapter candidate. Canvas owns the product-level role semantics; enforcement may later move to a shared policy layer.

---

## Entity: SpecWorkspace

### Definition

A bounded product-conception space for one product, feature, or implementation slice.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `name` | string | Yes | Human-readable. |
| `slug` | string | Yes | Unique per owner/account. |
| `description` | text | No | Short product idea. |
| `status` | enum | Yes | `draft`, `in_review`, `approved`, `handoff_requested`, `archived`. |
| `owner_id` | UserId | Yes | Current owner. |
| `created_at` | timestamp | Yes | Audit. |
| `updated_at` | timestamp | Yes | Audit. |
| `archived_at` | timestamp | No | Archive lifecycle. |

### Lifecycle States

| State | Meaning |
| --- | --- |
| `draft` | Content is being created. |
| `in_review` | One or more sections are under review. |
| `approved` | At least one spec package is approved. |
| `handoff_requested` | Approved package has been submitted to Bolt planning. |
| `archived` | Workspace is no longer active. |

### Invariants

- A workspace must have exactly one current owner.
- A workspace cannot be hard-deleted if it has approved packages or handoffs, unless an explicit retention policy allows it.
- A workspace cannot request Bolt handoff without an approved `SpecPackage`.
- `slug` must be unique within its account/local profile scope.

### Events

- `spec_workspace_created`
- `spec_workspace_updated`
- `spec_workspace_archived`
- `spec_workspace_deleted`
- `workspace_owner_transferred`

### Shared Capability Candidate

`SpecWorkspace` may generalize into a shared `Workspace` or `ProjectSpace` primitive. Placement is still open.

---

## Entity: SpecSection

### Definition

A named part of a product spec, such as Product Charter, Roles, Journeys, Screens/Actions, or Domain Model.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `key` | string | Yes | Example: `product-charter`. |
| `title` | string | Yes | Human-readable. |
| `status` | enum | Yes | `empty`, `draft`, `ready_for_review`, `changes_requested`, `approved`, `waived`. |
| `current_revision_id` | UUID | No | Latest revision. |
| `approved_revision_id` | UUID | No | Approved revision, if any. |
| `required_for_package` | boolean | Yes | Whether package approval needs this section. |
| `created_at` | timestamp | Yes | Audit. |
| `updated_at` | timestamp | Yes | Audit. |

### Invariants

- A section belongs to one workspace.
- A section can only be `approved` if it has an `approved_revision_id`.
- Editing an approved section creates a new draft revision and must not mutate the approved revision.
- A required section cannot be `waived` without an accepted `Waiver` targeting the section.

### Events

- `spec_section_created`
- `spec_section_updated`
- `spec_section_marked_ready_for_review`
- `spec_section_approved`
- `spec_section_changes_requested`
- `spec_section_waived`

### Shared Capability Candidate

Strong candidate for shared Rumble: structured sections with status, revisions, and review.

---

## Entity: SpecSectionRevision

### Definition

An immutable version of a spec section’s content.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `section_id` | UUID | Yes | Parent section. |
| `revision_number` | integer | Yes | Monotonic per section. |
| `content_format` | enum | Yes | `dual`. Structured fields are canonical; Markdown is projection/export. |
| `structured_content` | json | Yes | Machine-readable source of truth for validation, agents, services, and tests. |
| `markdown_content` | text | No | Human-readable projection/prose/export content. |
| `created_by` | ActorId | Yes | Human/system/agent attribution. |
| `created_at` | timestamp | Yes | Audit. |
| `source_attribution` | json | No | Agent/source attribution when applicable. |

### Invariants

- Revisions are immutable after creation.
- Revision numbers are monotonic per section.
- Agent-generated content must be marked until human accepted.
- Approved packages reference specific revision IDs, never mutable section content.

### Events

- `spec_section_revision_created`
- `agent_content_accepted`

### Shared Capability Candidate

May belong to Gear as append-only event/log primitive or shared Rumble as document revision primitive.

---

## Entity: RoleDefinition

### Definition

A product actor with goals, permissions, visible data, editable data, allowed actions, and forbidden actions.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Unique per workspace. |
| `description` | text | No | Role purpose. |
| `actor_type` | enum | Yes | `human`, `agent`, `system`, `external`. |
| `permissions` | json | No | Draft permission model. |
| `visible_data` | json/text | No | Product-facing visibility. |
| `editable_data` | json/text | No | Product-facing edit rights. |
| `forbidden_actions` | json/text | No | Explicit constraints. |

### Invariants

- Role name must be unique within a workspace.
- A role referenced by a screen/action cannot be deleted without resolving references.
- `Agent` roles cannot approve final decisions unless explicitly modeled as a human-approved proxy, which is out of MVP scope.

### Events

- `role_defined`
- `role_updated`
- `role_deleted`

### Shared Capability Candidate

Role definitions are shared at UX/spec level, but enforcement belongs to application auth/policy adapters.

---

## Entity: JourneyDefinition

### Definition

A user or system journey from trigger to outcome, including happy path, alternatives, failures, recovery, events, and acceptance criteria.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Human-readable. |
| `primary_actor_role_id` | UUID | No | Main role. |
| `trigger` | text | No | Starting condition. |
| `preconditions` | json/text | No | Required state. |
| `happy_path` | json/text | No | Ordered steps. |
| `alternate_paths` | json/text | No | Variants. |
| `failure_paths` | json/text | No | Failures. |
| `recovery_path` | json/text | No | Recovery. |
| `acceptance_criteria` | json/text | No | Testable criteria. |

### Invariants

- A journey marked ready for review must have at least trigger, actor, happy path, and acceptance criteria.
- If a journey emits events, those events should be represented in the event/workflow spec later.

### Events

- `journey_defined`
- `journey_updated`

---

## Entity: ScreenDefinition

### Definition

A user-facing product surface with purpose, allowed roles, displayed data, states, service calls, and actions.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Human-readable. |
| `route_or_entry` | string | No | Route, modal, command, or navigation entry. |
| `purpose` | text | Yes | Why screen exists. |
| `allowed_role_ids` | UUID[] | No | Roles that can access. |
| `displayed_data` | json/text | No | Visible information. |
| `states` | json | No | Empty/loading/error/offline/permission states. |
| `service_calls` | json/text | No | Known app/API calls. |
| `acceptance_criteria` | json/text | No | Screen-level tests. |

### Invariants

- A screen ready for review must have a purpose.
- Referenced roles must exist.
- If a screen exposes destructive actions, those actions must define audit and recovery rules.

### Events

- `screen_defined`
- `screen_updated`
- `screen_deleted`

### Shared Capability Candidate

Screen/action modeling is initially `rumble-canvas` specific. It may become a shared spec primitive if other Rumbles use it directly.

---

## Entity: ActionDefinition

### Definition

An operation available on a screen or journey, performed by a role or system, with business rules and acceptance criteria.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `screen_id` | UUID | No | Parent screen when UI action. |
| `name` | string | Yes | Human-readable. |
| `actor_role_id` | UUID | No | Role performing action. |
| `intent` | text | No | Why action exists. |
| `input` | json/text | No | Required input. |
| `preconditions` | json/text | No | Required state. |
| `business_rules` | json/text | No | Domain rules. |
| `validation_rules` | json/text | No | Input validation. |
| `side_effects` | json/text | No | Data/system effects. |
| `events_emitted` | string[] | No | Event names. |
| `audit_required` | boolean | Yes | Default false. |
| `destructive` | boolean | Yes | Default false. |
| `idempotency` | text | No | Retry semantics. |
| `rollback_retry` | text | No | Recovery. |
| `acceptance_criteria` | json/text | No | Action-level tests. |

### Invariants

- An action ready for review must have actor, intent, preconditions when relevant, business rules, and acceptance criteria.
- Destructive actions must define confirmation, audit, and rollback/recovery behavior.
- Actions referencing roles must reference existing roles.

### Events

- `action_defined`
- `action_updated`
- `action_deleted`

### Shared Capability Candidate

Action definitions may become the bridge between product specs and Bolt planning. Naming and placement remain open.

---

## Entity: DecisionRecord

### Definition

An accepted choice with rationale, scope, trade-offs, and consequences.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `title` | string | Yes | Decision summary. |
| `status` | enum | Yes | `proposed`, `accepted`, `rejected`, `superseded`. |
| `context` | text | No | Why decision exists. |
| `options` | json/text | No | Options considered. |
| `decision` | text | No | Accepted choice. |
| `rationale` | text | Yes when accepted | Why chosen. |
| `consequences` | text | No | Expected impact. |
| `decided_by` | ActorId | No | Required when accepted. |
| `decided_at` | timestamp | No | Required when accepted. |

### Invariants

- Accepted decisions require rationale and actor attribution.
- Superseded decisions must reference the replacement decision.
- Decisions that affect architecture should be exportable as ADR candidates.

### Events

- `decision_proposed`
- `decision_accepted`
- `decision_rejected`
- `decision_superseded`

### Shared Capability Candidate

Strong candidate. Needs split between product decisions, architecture ADRs, and Bolt operational decisions.

---

## Entity: Assumption

### Definition

A statement believed true but not yet verified.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `statement` | text | Yes | Assumption. |
| `risk_level` | enum | No | `low`, `medium`, `high`. |
| `validation_plan` | text | No | How to verify. |
| `status` | enum | Yes | `open`, `validated`, `invalidated`, `deferred`. |

### Invariants

- High-risk assumptions should block package approval unless validated, deferred, or covered by an accepted `Waiver`.

### Events

- `assumption_created`
- `assumption_validated`
- `assumption_invalidated`
- `assumption_deferred`

---

## Entity: OpenQuestion

### Definition

An unresolved question affecting product, architecture, implementation, data, security, or scope.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `question` | text | Yes | The unresolved issue. |
| `impact` | enum | Yes | `low`, `medium`, `high`, `blocking`. |
| `owner` | ActorId/Role | No | Responsible resolver. |
| `status` | enum | Yes | `open`, `answered`, `deferred`, `waived`. |
| `answer` | text | No | Required when answered; waived questions must reference an accepted `Waiver`. |

### Invariants

- Blocking open questions prevent package approval unless answered, deferred, or covered by an accepted `Waiver`.
- Answered questions should link to resulting decisions when applicable.

### Events

- `open_question_created`
- `open_question_answered`
- `open_question_deferred`
- `open_question_waived`

### Shared Capability Candidate

Likely shared Rumble primitive across specs, articles, learning sessions, and agent tasks.

---

## Entity: CommentThread and Comment

### Definition

A discussion attached to a section, entity, decision, risk, or candidate.

### Fields: CommentThread

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `target_type` | string | Yes | Section, screen, action, etc. |
| `target_id` | UUID | Yes | Target object. |
| `status` | enum | Yes | `open`, `resolved`. |

### Fields: Comment

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `thread_id` | UUID | Yes | Parent thread. |
| `author_id` | ActorId | Yes | Author. |
| `body` | text | Yes | Comment text. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Comments are append-only after a short edit window, if edit is allowed.
- Resolving a thread must be attributed.

### Events

- `comment_thread_created`
- `comment_created`
- `comment_thread_resolved`

### Shared Capability Candidate

Strong shared Rumble candidate.

---

## Entity: ReviewDecision

### Definition

A reviewer’s decision about a section or package.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `target_type` | enum | Yes | `section`, `package`. |
| `target_id` | UUID | Yes | Reviewed object. |
| `revision_id` | UUID | No | Required for section review. |
| `decision` | enum | Yes | `approved`, `changes_requested`, `rejected`. |
| `rationale` | text | No | Required for rejection/changes. |
| `reviewer_id` | ActorId | Yes | Reviewer. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Section approval must target a specific revision.
- Requested changes block package approval until resolved or covered by an accepted `Waiver`.
- Separation-of-duty may prevent approving self-authored sections in stricter modes.

### Events

- `review_decision_created`
- `section_approved`
- `section_changes_requested`

---

## Entity: RiskFlag

### Definition

A product, security, architecture, data, or implementation risk attached to an object.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `target_type` | string | No | Optional target. |
| `target_id` | UUID | No | Optional target. |
| `category` | enum | Yes | `product`, `security`, `privacy`, `architecture`, `data`, `performance`, `delivery`. |
| `severity` | enum | Yes | `low`, `medium`, `high`, `blocking`. |
| `description` | text | Yes | Risk description. |
| `mitigation` | text | No | Mitigation. |
| `status` | enum | Yes | `open`, `mitigated`, `accepted`, `waived`. |

### Invariants

- Blocking risks prevent package approval unless mitigated, accepted, or covered by an accepted `Waiver`.
- A waived risk must keep the risk record and point to the accepted `Waiver` for audit.

### Events

- `risk_flagged`
- `risk_mitigated`
- `risk_accepted`
- `risk_waived`

---

## Entity: Waiver

### Definition

A controlled exception that permits a spec, package, validation, risk, question, review decision, or handoff to proceed despite an unmet rule, incomplete requirement, or accepted risk.

`Waiver` is first-class in the MVP, but intentionally minimal and extensible.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `target_type` | enum/string | Yes | Example: `section`, `package`, `open_question`, `risk_flag`, `review_decision`, `traceability_link`, `handoff`, `validation_check`. |
| `target_id` | UUID/string | Yes | Target object or validation identifier. |
| `status` | enum | Yes | `proposed`, `accepted`, `rejected`, `expired`, `revoked`. |
| `reason` | text | Yes | Why the exception is justified. |
| `risk_level` | enum | Yes | `low`, `medium`, `high`, `critical`. |
| `risk_category` | enum | Yes | `security`, `quality`, `performance`, `compliance`, `product`, `ux`, `delivery`. |
| `owner_id` | ActorId | Yes | Person/accountable actor carrying the risk. |
| `approver_id` | ActorId | No | Required when accepted, unless policy allows owner self-approval. |
| `expires_at` | timestamp | No | Required for high/critical waivers unless explicitly exempted by policy. |
| `conditions` | text/json | No | Constraints under which the waiver is valid. |
| `compensating_controls` | text/json | No | Mitigations or manual checks replacing the waived rule. |
| `created_at` | timestamp | Yes | Audit. |
| `decided_at` | timestamp | No | Set when accepted/rejected/revoked. |

### Invariants

- Only `accepted` waivers can unblock package approval, handoff, or validation gates.
- Accepted waivers require `reason`, `owner_id`, `approver_id`, and explicit risk classification.
- Low/medium waivers may be approved by an active human Owner.
- High/critical waivers require a human Owner plus a distinct active human Reviewer approval; security, privacy, or compliance waivers require a reviewer with relevant review responsibility.
- High/critical waivers require either `expires_at` or a documented condition explaining why no expiry applies.
- Expired or revoked waivers no longer unblock their target.
- Waivers must not delete or hide the underlying issue; they record an explicit exception.
- Waivers should be connected through `TraceabilityLink` when the exception affects downstream screens, actions, services, tests, or capabilities.

### Events

- `waiver_proposed`
- `waiver_accepted`
- `waiver_rejected`
- `waiver_expired`
- `waiver_revoked`

### Shared Capability Candidate

Strong shared Rumble review/governance primitive. Bolt may consume accepted waivers as gate exceptions, but Canvas owns the product-spec exception record in MVP.

---

## Entity: CapabilityCandidate

### Definition

A product need that may become a reusable Rumble, Bolt, Wrench, or Gear brick.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `name` | string | Yes | Candidate name. |
| `description` | text | Yes | What capability does. |
| `origin_type` | string | No | Section/screen/action/journey. |
| `origin_id` | UUID | No | Origin object. |
| `needed_by` | string[] | No | Products or flows. |
| `proposed_owner_layer` | enum | No | `rumble-shared`, `bolt`, `wrench`, `gear`, `unknown`. |
| `status` | enum | Yes | `candidate`, `discuss`, `accepted`, `rejected`. |
| `rationale` | text | Yes | Why it may be shared. |

### Invariants

- Candidate must include description and rationale.
- Accepted candidates require owner layer.
- Candidates exported to ecosystem registry must keep origin reference.

### Events

- `capability_candidate_created`
- `capability_candidate_updated`
- `capability_candidate_exported`
- `capability_candidate_accepted`
- `capability_candidate_rejected`

### Shared Capability Candidate

This is itself a shared process primitive for the ecosystem.

---

## Entity: TraceabilityLink

### Definition

A typed relationship between two spec objects that explains how product intent flows toward implementation and validation.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `source_type` | enum/string | Yes | Example: `job`, `journey`, `screen`, `action`, `domain_entity`, `service`, `test`, `capability_candidate`. |
| `source_id` | UUID/string | Yes | Source object reference. |
| `target_type` | enum/string | Yes | Target object type. |
| `target_id` | UUID/string | Yes | Target object reference. |
| `relation_type` | enum | Yes | `justifies`, `implements`, `requires`, `tests`, `produces`, `extracts_to_candidate`, `included_in`. |
| `rationale` | text | No | Why the link exists. |
| `confidence` | enum | No | `manual`, `agent_suggested`, `system_inferred`. |
| `status` | enum | Yes | `active`, `stale`, `rejected`. |
| `created_by` | ActorId | Yes | Actor attribution. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- A traceability link must reference existing objects or explicit external references.
- Agent-suggested links are not authoritative until accepted by a human or system rule.
- If either linked object is deleted/archived, the link becomes `stale` rather than silently disappearing.
- Package readiness may require minimum traceability coverage.

### Events

- `traceability_link_created`
- `traceability_link_updated`
- `traceability_link_marked_stale`
- `traceability_link_rejected`

### Shared Capability Candidate

`TraceabilityLink` is a strong candidate for a shared spec primitive. It may start in `rumble-canvas` and later move to shared Rumble or Gear-backed graph/indexing.

---

## Entity: SpecPackage

### Definition

An immutable bundle of approved spec section revisions and related metadata.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `version` | string/integer | Yes | Package version. |
| `status` | enum | Yes | `draft`, `approved`, `exported`, `handoff_submitted`, `handoff_failed`. |
| `approved_by` | ActorId | No | Required when approved. |
| `approved_at` | timestamp | No | Required when approved. |
| `package_hash` | string | No | Integrity. |
| `artifact_reference_id` | string | No | Gear artifact reference if exported/stored. |

### Invariants

- Approved packages are immutable.
- Approved packages reference section revision IDs, not mutable section IDs alone.
- Package approval is blocked by unresolved required sections, blocking questions, or blocking risks unless covered by accepted non-expired waivers.

### Events

- `spec_package_created`
- `spec_package_approved`
- `spec_package_exported`
- `spec_package_handoff_submitted`

### Shared Capability Candidate

Strong Gear artifact candidate with Rumble-specific package UX.

---

## Entity: SpecPackageItem

### Definition

A reference to a specific spec section revision included in a package.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `package_id` | UUID | Yes | Parent package. |
| `section_id` | UUID | Yes | Section. |
| `revision_id` | UUID | Yes | Included immutable revision. |
| `required` | boolean | Yes | Whether required for package. |

### Invariants

- `revision_id` must belong to `section_id`.
- Package item cannot be changed after package approval.

---

## Entity: ImplementationHandoff

### Definition

A planning-only request to Bolt based on an approved spec package.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Stable identifier. |
| `workspace_id` | UUID | Yes | Parent workspace. |
| `package_id` | UUID | Yes | Approved package. |
| `status` | enum | Yes | `draft`, `validated`, `submitted`, `acknowledged`, `failed`, `cancelled`. |
| `payload_format_version` | string | Yes | `canvas.bolt_handoff.v0.1` for MVP. |
| `payload_kind` | string | Yes | `planning_request`. MVP never uses `execution_request`. |
| `bolt_target` | string | Yes | MVP value: `cos-matic`. |
| `planning_scope` | text/json | Yes | Slice or full package, including target objects and exclusions. |
| `payload` | json | Yes | Canonical structured handoff payload sent/exported to Bolt. |
| `payload_hash` | string | Yes | Integrity hash of canonical payload. |
| `execution_policy` | json | Yes | Must include `planning_only: true` and `allow_execution: false` in MVP. |
| `validation_status` | enum | Yes | `not_checked`, `valid`, `invalid`. |
| `validation_errors` | json | No | Bolt/Rumble validation errors. |
| `bolt_reference` | string | No | Bolt plan/run reference after acknowledgement. |
| `created_by` | ActorId | Yes | Actor. |
| `created_at` | timestamp | Yes | Audit. |

### Invariants

- Handoff requires an approved package.
- Handoff payload must conform to `canvas.bolt_handoff.v0.1` until a newer version is explicitly accepted.
- MVP Bolt implementation target is `cos-matic`.
- MVP handoff is planning-only: `payload_kind` must be `planning_request`, `execution_policy.planning_only` must be `true`, and `execution_policy.allow_execution` must be `false`.
- Handoff cannot trigger implementation execution directly.
- Handoff payload must include package identity, included revision IDs, planning scope, decisions, traceability links, active waivers, open risks/questions, capability candidates, and requested Bolt outputs.
- `cos-matic` may return a plan, required gates, status, validation errors, refusal, or failure context.
- Failed or refused handoff must preserve payload and validation errors for retry/export/audit.

### Events

- `implementation_handoff_created`
- `implementation_handoff_validated`
- `implementation_handoff_validation_failed`
- `bolt_handoff_submitted`
- `bolt_handoff_acknowledged`
- `bolt_plan_returned`
- `bolt_gates_required`
- `bolt_handoff_refused`
- `bolt_handoff_failed`

### Canonical Payload — `canvas.bolt_handoff.v0.1`

```json
{
  "format": "canvas.bolt_handoff.v0.1",
  "kind": "planning_request",
  "bolt_target": "cos-matic",
  "source": {
    "product": "rumble-canvas",
    "workspace_id": "uuid",
    "handoff_id": "uuid",
    "created_by": "actor-id",
    "created_at": "timestamp"
  },
  "package": {
    "package_id": "uuid",
    "version": "string",
    "package_hash": "sha256",
    "artifact_reference_id": "optional-string",
    "items": [
      {
        "section_id": "uuid",
        "revision_id": "uuid",
        "section_key": "product-charter",
        "required": true
      }
    ]
  },
  "planning_scope": {
    "mode": "full_package | slice",
    "target_objects": [
      { "type": "action", "id": "uuid" }
    ],
    "excluded_objects": [],
    "goal": "text"
  },
  "spec_context": {
    "charter_summary": {},
    "decisions": [],
    "roles": [],
    "journeys": [],
    "screens": [],
    "actions": [],
    "domain_entities": [],
    "acceptance_criteria": []
  },
  "traceability_links": [],
  "active_waivers": [],
  "open_questions": [],
  "risks": [],
  "capability_candidates": [],
  "constraints": {
    "sovereignty": "self-hostable; no hidden external dependency",
    "data_residency": "EU/local-first where applicable",
    "non_goals": []
  },
  "requested_outputs": [
    "implementation_plan",
    "task_breakdown",
    "risk_review",
    "test_plan",
    "shared_capability_extraction_review"
  ],
  "execution_policy": {
    "planning_only": true,
    "allow_execution": false,
    "requires_human_approval_for_execution": true
  }
}
```

### Shared Capability Candidate

Belongs at the seam between Rumble and Bolt. Rumble owns request UX and payload assembly; Bolt owns validation, planning, gates, runs, and any later execution lifecycle. For the MVP, the concrete Bolt target is `cos-matic`.

---

## Missing Concepts / Challenges

These concepts are not fully modeled yet and should be discussed before data model finalization.

| Missing concept | Why it matters | Candidate placement | Priority |
| --- | --- | --- | --- |
| Identity / Account / Local Profile | Partially covered by `ActorReference`; full identity remains shared auth/profile. | Shared auth/profile layer; not Canvas-specific. | High |
| Workspace membership | Accepted as minimal `WorkspaceMembership` + `RoleAssignment` in Canvas MVP. | Canvas first; shared Rumble or auth adapter later. | High |
| SourceReference | Needed when specs cite notes, files, URLs, transcripts. | Gear Memory + Gear Loader. | High |
| ArtifactReference | Needed for exports, packages, handoffs. | Gear Depot / Gear Memory. | High |
| CompletenessReport | Needed for readiness checklist and review. | Rumble shared or Wrench Inspect. | Medium |
| Waiver | Accepted as first-class MVP entity for controlled exceptions. | Rumble Canvas first; likely shared Rumble governance primitive, consumed by Bolt gates. | High |
| Notification | Needed for review and collaboration. | Shared Rumble/service. | Medium |
| Presence / collaboration state | Needed for real-time team editing. | Shared Rumble, post-MVP. | Low for MVP |
| Template | Needed to create specs faster. | Rumble shared. | Medium |
| Export format | Markdown vs structured JSON vs both affects storage and handoff. | Gear artifact + Rumble export. | High |
| Spec quality inspection | Could be deterministic checks or AI-assisted. | Wrench Inspect. | Medium |
| Traceability link | Accepted as first-class MVP entity: links product intent → implementation → validation. | Rumble Canvas first; maybe shared spec primitive. | High |

---

## Recommended Domain Decisions

### Decision Candidate 1: Use `SpecWorkspace` for Canvas, not generic `Workspace` yet

Reason:

- Keeps Canvas product model precise.
- Avoids prematurely defining a cross-product tenant model.
- We can later extract a generic `Workspace` if multiple products converge.

### Decision Candidate 2: Treat `SpecPackage` as a Gear artifact candidate

Reason:

- It needs integrity, immutability, export, provenance, and handoff.
- Rumble owns package UX, Gear likely owns artifact semantics.

### Decision Candidate 3: Treat `ImplementationHandoff` as a Rumble-to-Bolt boundary object

Reason:

- Canvas creates the request.
- Bolt owns planning, gates, runs, and execution lifecycle.
- MVP must remain planning-only.

### Decision 4: Make `TraceabilityLink` explicit before services/data model

Status: Accepted.

Reason:

- Without traceability, specs become prose.
- We need to connect goals → journeys → screens → actions → services → tests.
- This may become the most important differentiator of the product.

### Decision 5: Make `Waiver` first-class, minimal, and extensible

Status: Accepted.

Reason:

- A waiver is an explicit permission to proceed despite an unmet rule, incomplete requirement, or accepted risk.
- It must be auditable, approvable, expirable, and consumable by Wrench/Bolt instead of being buried in Markdown.
- The MVP keeps the model small: target, status, reason, risk classification, owner, approver, expiry, conditions, controls.

### Decision 6: Use minimal Actor/Membership/RoleAssignment for Canvas MVP

Status: Accepted.

Reason:

- Canvas needs attribution, permissions, collaboration, reviews, and waiver approvals before the full cross-product identity model is known.
- `ActorReference` records who did what without owning identity/auth.
- `WorkspaceMembership` and `RoleAssignment` are enough to enforce Owner/Editor/Reviewer/Viewer/Agent/System permissions in MVP.
- This keeps full account, tenant, SSO, and local-first identity sync decisions outside Canvas scope for now.

### Decision 7: Use `canvas.bolt_handoff.v0.1` as the first Bolt handoff format

Status: Accepted.

Reason:

- Bolt needs structured, deterministic input rather than Markdown-only context.
- The MVP handoff must preserve package identity, immutable revisions, decisions, traceability, waivers, risks, capabilities, and requested outputs.
- The format is explicitly planning-only and forbids automatic implementation execution.
- The concrete Bolt target for MVP is `cos-matic`, which may return a plan, required gates, status, validation errors, refusal, or failure context.

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should `TraceabilityLink` be a first-class entity in MVP? | High | Accepted. |
| Should `Waiver` be a first-class entity instead of text fields on risks/questions/sections? | Medium | Accepted: first-class minimal/extensible MVP. |
| Should `SpecSectionRevision.content` be Markdown, JSON, or dual-format? | High | Accepted: dual-format. |
| Is `RoleDefinition` only descriptive in specs or should it compile into enforceable permissions later? | High | Partially accepted: Canvas MVP uses `RoleAssignment` for workspace permissions; product `RoleDefinition` remains spec content. |
| Are `DecisionRecord` and ADR the same object or different projections? | Medium | Open |
| Should `CompletenessReport` be stored or recomputed? | Medium | Open |
| Should agent suggestions be modeled as `AgentSuggestion` first-class entity? | Medium | Open |
| What is the first Bolt handoff format? | High | Accepted: `canvas.bolt_handoff.v0.1` planning request targeting `cos-matic` for MVP. |
