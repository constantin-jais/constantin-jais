# Product Charter — rumble-canvas

## Mission

`rumble-canvas` helps a person or team transform unclear product intent into validated, implementation-ready specifications.

It turns conversations, assumptions, constraints, and decisions into structured deliverables: product charters, roles, journeys, screens, actions, domain models, service boundaries, data models, and acceptance tests.

## Product Thesis

Software teams often industrialize implementation before they industrialize conception. `rumble-canvas` exists to make conception explicit, reviewable, agent-readable, and executable.

The product is not a prompt-to-UI toy. It is a specification and alignment workspace that feeds the agentic harness.

## Target Users

### Primary Users

| User | Need |
| --- | --- |
| Product builder | Clarify a product idea and convert it into implementable specs. |
| Founder / solo maker | Turn rough strategy into concrete screens, actions, and data models. |
| Product manager | Align stakeholders around scope, roles, journeys, and acceptance criteria. |
| Tech lead | Validate that specs are implementable, bounded, and correctly mapped to architecture layers. |

### Secondary Users

| User | Need |
| --- | --- |
| Designer | Understand screens, flows, states, and interaction requirements. |
| Developer | Implement from precise contracts instead of vague prompts. |
| Agent operator | Convert validated specs into safe execution plans through Bolt. |
| Reviewer | Challenge scope, security, data, and architecture before implementation. |

## Jobs To Be Done

1. When I have a vague product idea, I want to clarify the mission, users, and non-goals so that scope does not drift.
2. When stakeholders discuss a feature, I want decisions and assumptions captured so that we do not lose context.
3. When designing a product, I want every screen to list actions by role so that implementation and permissions are clear.
4. When preparing agentic implementation, I want specs to identify which work belongs in Rumble, Bolt, Wrench, or Gear.
5. When several products need the same capability, I want the system to flag it as a shared brick candidate.
6. When a spec is ready, I want to hand it to the harness as an implementation-ready artifact with acceptance tests.

## Product Promise

`rumble-canvas` produces specs that are:

- understandable by humans;
- readable by agents;
- explicit about scope and non-scope;
- mapped to architecture layers;
- testable through acceptance criteria;
- safe to use as input for implementation planning.

## Non-Goals

`rumble-canvas` is not:

- a generic design canvas;
- a full project-management tool;
- an autonomous implementation agent;
- a raw data-ingestion pipeline;
- a code editor;
- a replacement for Bolt execution gates;
- a generic whiteboard without structured output.

## Product Boundaries

### Owns

- Product-conception workflows.
- Spec authoring and review UX.
- Conversation-to-decision mapping.
- Role/screen/action modeling.
- Product deliverable generation.
- Shared capability detection from product needs.

### Does Not Own

- Execution planning and safe writes: Bolt / `cos-matic`.
- Raw document extraction: Wrench.
- Persistent memory substrate and provenance primitives: Gear.
- Artifact distribution and registry policy: Gear.

## Success Metrics

### Product Quality

- A user can produce a complete MVP spec for a small product without leaving the workspace.
- Every MVP screen has actions by role.
- Every critical action has acceptance criteria.
- Every shared capability candidate is logged instead of silently duplicated.

### Harness Utility

- A validated spec can be converted into a Bolt implementation plan.
- Wrench/Gear/Bolt needs are identified directly from product specs.
- Agentic implementation starts with fewer ambiguous prompts.

### User Value

- Reduced time from idea to implementable scope.
- Fewer missing permission/data/state requirements during implementation.
- Clearer stakeholder alignment before development.

## MVP Scope

The MVP should support one workspace and one product spec at a time.

### MVP Capabilities

1. Create a product canvas.
2. Define product charter: mission, users, jobs, non-goals, success metrics.
3. Define roles and permissions at a first-pass level.
4. Define user journeys.
5. Define screens and actions by role.
6. Define domain entities and lifecycle states.
7. Log assumptions, decisions, and open questions.
8. Identify shared capability candidates.
9. Export specs as Markdown.
10. Prepare a handoff package for Bolt planning.

### MVP Deliverables

- Product charter.
- Personas/roles spec.
- Journey map.
- Screen/action matrix.
- Domain model draft.
- Shared capability report.
- Open questions list.
- Markdown export.

## Post-MVP Scope

- Multi-product workspace.
- Collaborative editing and comments.
- Spec diffing and review workflows.
- Visual screen map.
- Service/API model generation.
- Data model generation.
- Acceptance test generation.
- Direct Bolt handoff with approval gates.
- Inspector integration for spec quality checks.
- Reusable templates for product families.

## Dependencies on Bolt/Wrench/Gear

### Bolt

`rumble-canvas` asks Bolt to:

- convert accepted specs into execution plans;
- enforce approval gates;
- create agent tasks;
- track implementation runs;
- report execution status back to the product.

### Wrench

`rumble-canvas` asks Wrench to:

- ingest background material when users provide documents or URLs;
- inspect specs for completeness, contradictions, and architectural boundary leaks;
- validate generated artifacts when relevant.

### Gear

`rumble-canvas` uses Gear for:

- storing sources, specs, decisions, and artifacts;
- preserving provenance;
- local-first or self-hostable persistence;
- exporting and distributing implementation-ready packages.

## Core Domain Concepts

| Concept | Definition | Shared candidate? |
| --- | --- | --- |
| Canvas | Workspace for one product-conception effort. | Maybe: product-specific. |
| Product spec | Structured set of product documents. | Yes: artifact. |
| Role | Actor with permissions and goals. | Maybe: shared Rumble. |
| Screen | User-facing state/surface with actions. | Product-specific but template reusable. |
| Action | User or system operation with business rules. | Maybe: shared spec primitive. |
| Decision | Accepted choice with rationale. | Yes: shared decision record. |
| Assumption | Unverified statement that may affect scope. | Maybe: shared product primitive. |
| Open question | Unresolved issue that blocks or risks implementation. | Maybe: shared product primitive. |
| Capability candidate | Need that may become a shared brick. | Yes: shared registry concept. |
| Handoff package | Accepted spec bundle prepared for Bolt. | Yes: artifact + Bolt input. |

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Becomes a visual design toy | High | Keep specs, decisions, and acceptance criteria as primary outputs. |
| Produces verbose but unusable docs | High | Every section must map to implementation decisions or tests. |
| Duplicates Bolt orchestration | High | Canvas can request plans; Bolt owns execution. |
| Over-specifies too early | Medium | Keep MVP flow iterative: draft → review → accept → handoff. |
| Shared capability extraction becomes premature | Medium | Mark candidates first; accept ownership only after repeated need or clear infra responsibility. |

## MVP Acceptance Criteria

- Given a new product idea, a user can create a canvas and fill a product charter.
- Given roles and screens, the system can produce a screen/action matrix.
- Given a product action, the user can define business rules and acceptance criteria.
- Given repeated or cross-layer needs, the system can log a shared capability candidate.
- Given an accepted spec, the user can export Markdown.
- Given an accepted spec, the user can request a Bolt planning handoff without executing automatically.

## Open Questions

| Question | Impact | Status |
| --- | --- | --- |
| Is the first target user solo builder or team? | High | Open |
| Is the canonical unit called `canvas`, `project`, or `spec workspace`? | High | Open |
| What is the minimum viable screen representation: list, table, graph, or visual map? | Medium | Open |
| Should Markdown be the canonical storage format or only an export format? | High | Open |
| How much AI assistance is allowed before human validation? | High | Open |
