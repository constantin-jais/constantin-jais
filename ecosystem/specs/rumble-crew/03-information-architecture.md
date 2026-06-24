# Information Architecture — rumble-crew

## Scope

This document defines the MVP information architecture for `rumble-crew`.

The IA must make agentic work inspectable without turning the product into:

- a generic project management suite;
- a runtime console;
- an orchestration planner;
- a workflow-builder.

Primary objects are task-centric. Runs, approvals, blockers, and evidence exist to explain task state and support human decisions.

---

## IA Challenge / Product Guardrails

### Guardrail 1: Task-first, not project-management-first

`rumble-crew` may show boards, filters, and queues, but its differentiator is agentic supervision:

- runtime identity;
- blockers;
- approvals;
- evidence;
- audit timeline;
- task/run separation.

Avoid MVP features whose main value is generic PM:

- roadmaps;
- epics;
- sprint velocity;
- capacity planning;
- estimates/burndown;
- advanced dependencies;
- generic custom fields.

### Guardrail 2: Run detail is an inspection view, not a runtime console

Run detail must answer:

- what run is this?;
- what task does it support?;
- what state did Bolt report?;
- what gate/evidence/failure did it produce?;
- what can the human decide next?

It must not expose:

- raw credentials;
- full tool internals by default;
- arbitrary command execution;
- orchestration editing;
- runtime step sequencing controls.

### Guardrail 3: Skill cards guide assignment; they do not execute

Skill cards help humans choose a capability. They are not buttons that bypass Bolt.

---

## Navigation Model

### Top-Level Navigation

| Entry | Purpose | MVP |
| --- | --- | --- |
| Board | Operational task overview. | Yes |
| Review Queue | Approvals and evidence requiring human decision. | Yes |
| Agents & Skills | Available agent profiles and skill cards. | Yes |
| Timeline | Audit/collaboration event stream. | Yes |
| Settings | Workspace, members, policies, integrations. | Yes, minimal |
| Reports | Exports and metrics. | Post-MVP except audit export entry |

### Recommended MVP Left Navigation

```text
Workspace
├── Board
├── Review Queue
│   ├── Approvals
│   └── Evidence
├── Agents & Skills
├── Timeline
└── Settings
    ├── Members
    ├── Approval Policy
    └── Integrations
```

### Contextual Navigation

From a task card or task detail, users can navigate to:

- task detail;
- current run detail;
- blocker detail;
- approval detail;
- evidence detail;
- related timeline slice;
- agent profile;
- skill card.

---

## Primary Spaces

## Space: Board

### Purpose

Show the current operational state of agentic work.

### Default Columns

| Column | Task statuses | Notes |
| --- | --- | --- |
| Created | `created` | Needs assignment/context. |
| Ready / Assigned | `assigned`, `ready` | Ready means runnable once approvals are satisfied. |
| In Progress | `in_progress` | May show current `RunStatus`. |
| Blocked | `blocked` | Prioritize resolver and blocker type. |
| Review | `in_review` | Evidence/completion decision needed. |
| Done | `done` | Closed with accepted evidence/approval. |
| Failed / Cancelled | `failed`, `cancelled` | Optional collapsed lane. |

### Board Card Must Show

- task title;
- task status;
- assignee human/agent;
- selected skill card if agent-assigned;
- latest run status;
- blocker badge/count;
- approval pending badge;
- evidence status;
- risk level;
- last activity time.

### Board Must Not Show By Default

- raw logs;
- secrets;
- internal orchestration steps;
- broad PM metadata unrelated to agentic supervision.

---

## Space: Review Queue

### Purpose

Centralize human decisions needed to move work forward safely.

### Queue Sections

| Section | Objects | User question |
| --- | --- | --- |
| Approvals | `Approval.status=requested` | “Can this proceed?” |
| Evidence | `Evidence.status=submitted` | “Is this sufficient?” |
| Blockers requiring human | `Blocker.status=open` | “What input/decision is needed?” |
| Failed runs | `RunRef.status=failed` | “Retry, reassign, fail, or cancel?” |

### Priority Ordering

1. High/critical risk approvals.
2. Blocking blockers.
3. Stale approvals near expiry.
4. Submitted completion evidence.
5. Failed runs without recovery decision.

---

## Space: Task Detail

### Purpose

Canonical page for one unit of work.

### Sections

```text
Task Detail
├── Header: title, status, risk, primary action
├── Goal & Context
├── Assignment
│   ├── human/agent assignee
│   ├── skill card
│   └── runtime/run summary
├── Blockers
├── Approvals
├── Evidence
├── Comments
└── Timeline
```

### Default Primary Action Logic

| Condition | Primary action |
| --- | --- |
| `created` with no assignee | Assign |
| assigned but missing context | Add context |
| ready and agent-assigned | Request run |
| waiting for approval | Review approval |
| blocked | Resolve blocker |
| evidence submitted | Review evidence |
| failed run | Decide recovery |
| done/cancelled | View timeline/export |

---

## Space: Run Detail

### Purpose

Inspect one execution attempt as projected from Bolt.

### Sections

```text
Run Detail
├── Run summary
├── Linked task
├── Runtime reference
├── Status projection
├── Gate requests
├── Evidence produced
├── Failure context
└── Safe activity/log references
```

### Hard Boundary

Run Detail may show what Bolt reports, but it must not allow users to edit Bolt's plan or execute arbitrary runtime actions.

Allowed actions are limited to Rumble-mediated decisions:

- approve/reject gate;
- request cancellation;
- request rerun;
- open evidence;
- open task timeline.

---

## Space: Agents & Skills

### Purpose

Help users understand what agent profiles/capabilities are available for task assignment.

### Sections

```text
Agents & Skills
├── Agent Profiles
│   ├── status
│   ├── description
│   ├── default runtime ref
│   └── compatible skills
└── Skill Cards
    ├── input requirements
    ├── output expectations
    ├── required approvals
    ├── risks
    └── compatible runtime refs
```

### MVP Limit

No marketplace, no billing, no arbitrary install flow. Skill cards are workspace-visible metadata, optionally sourced from Bolt integration.

---

## Space: Timeline

### Purpose

Provide an auditable, human-readable history of task and workspace activity.

### Timeline Modes

| Mode | Scope |
| --- | --- |
| Workspace timeline | All visible activity in workspace. |
| Task timeline | Activity for one task. |
| Run timeline | Projection events for one run. |
| Review timeline | Approvals/evidence/blockers decisions. |

### Event Grouping

- task lifecycle;
- assignment;
- run projection;
- blocker;
- approval;
- evidence;
- comments;
- system/integration sync.

---

## Space: Settings

### MVP Settings

| Section | Purpose | MVP fields |
| --- | --- | --- |
| Members | Manage workspace access. | role, status, invitation/removal. |
| Approval Policy | Configure limited approval rules. | start/scope/risk/completion defaults. |
| Integrations | Configure Bolt target. | provider, availability, safe connection status. |
| Data & Audit | Exports and retention overview. | audit export request, retention labels. |

### Explicitly Post-MVP

- complex workflow builder;
- custom field schema builder;
- organization-wide policy inheritance;
- fine-grained DSL for approvals.

---

## Object Hierarchy

```text
Workspace
├── Board
│   └── BoardColumn
├── Task
│   ├── TaskAssignment
│   ├── RunRef
│   ├── Blocker
│   ├── Approval
│   ├── Evidence
│   ├── CommentThread
│   └── ActivityEvent
├── AgentProfile
├── SkillCard
├── RuntimeRef
└── AuditExport
```

## Object Ownership Summary

| Object | Source of truth | Notes |
| --- | --- | --- |
| Workspace | Rumble Crew | Shared Rumble candidate. |
| Board | Rumble Crew | View over tasks. |
| Task | Rumble Crew | Product collaboration state. |
| RunRef | Projection of Bolt | Local reference, not execution owner. |
| RuntimeRef | Bolt/Gear reference | Safe snapshot only. |
| AgentProfile | Rumble projection/local metadata | May be sourced from Bolt later. |
| SkillCard | Rumble projection/local metadata | Candidate for Bolt/shared registry. |
| Approval | Rumble decision + Bolt gate sync | Human UX in Rumble; enforcement in Bolt. |
| Evidence | Rumble review + external artifact | Gear likely stores artifact/provenance. |
| ActivityEvent | Rumble projection / Gear candidate | Audit/timeline. |

---

## Search and Browse Model

## Search Scope

MVP search should cover:

- task title;
- task description/goal;
- assignee;
- agent profile;
- skill card;
- blocker summary;
- approval summary;
- evidence summary;
- event type.

MVP search should not index raw sensitive logs by default.

## Filters

| Filter | Values |
| --- | --- |
| Task status | `created`, `assigned`, `ready`, `in_progress`, `blocked`, `in_review`, `done`, `failed`, `cancelled` |
| Run status | `queued`, `claimed`, `running`, `waiting_for_approval`, `succeeded`, `failed`, `cancelled`, `unknown` |
| Assignee type | human, agent, role |
| Agent profile | selectable |
| Skill card | selectable |
| Risk | low, medium, high, critical |
| Needs attention | blocker, approval, evidence review, failed run |
| Updated | date range |

## Saved Views

MVP may include system views only:

- My tasks;
- Agent tasks;
- Blocked;
- Needs approval;
- Evidence review;
- Failed runs.

User-defined complex saved views are post-MVP.

---

## Empty State Strategy

| Space | Empty state |
| --- | --- |
| Board | Explain agentic task loop and offer “Create task”. |
| Review Queue | “No human decisions needed.” |
| Agents & Skills | Prompt to add/sync first agent profile or skill card. |
| Timeline | “No activity yet.” |
| Run Detail | If no run exists, explain task may need assignment/run request. |
| Settings/Integrations | Show Bolt integration status and setup CTA. |

---

## Loading / Degraded State Strategy

| Condition | UX requirement |
| --- | --- |
| Bolt unavailable | Show last known run status as stale/unknown; do not fabricate progress. |
| Evidence artifact unavailable | Show evidence record with artifact unavailable marker. |
| Timeline loading partial | Show partial history with loading marker, not empty state. |
| Permission-limited data | Show redacted/hidden markers when object existence can be disclosed. |
| Integration sync failed | Show sync error with retry/action path for authorized users. |

---

## Information Scent Rules

Every task card/detail should answer quickly:

1. What is the task trying to achieve?
2. Who or what is assigned?
3. Is work actually running, blocked, or waiting for a human?
4. What evidence exists?
5. What is the next safe action?

If a screen cannot answer one of these, the IA is incomplete.

---

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Should failed/cancelled tasks be visible as board columns or archived filters by default? | Medium | Proposed: collapsed lane or filter. |
| Should Review Queue be separate from Board or a board view? | Medium | Proposed: separate top-level entry for decision focus. |
| Should Agents & Skills be visible to all contributors? | Medium | Proposed: visible metadata, permission-sensitive details redacted. |
| Should raw logs ever appear in Run Detail? | High | Proposed: only safe summaries/references in MVP. |
