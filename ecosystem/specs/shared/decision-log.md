# Decision Log

| Date | Decision | Reason | Status |
| --- | --- | --- | --- |
| 2026-06-30 | Five active Rumble products are in scope: `rumble-canvas`, `rumble-cos`, `rumble-crew`, `rumble-lm`, `rumble-note`. | The doctrine must only list real active products. | Accepted |
| 2026-06-30 | External inspirations are private discovery context, not public spec content. | Keep product identity original and avoid cloning language. | Accepted |
| 2026-06-30 | `overview.md` is the specification control plane. | One visible place must track doctrine, roadmap, shared bricks, and decisions. | Accepted |
| 2026-06-30 | `rumble-canvas` is specified first. | It can become the internal method/tool for producing other product specs. | Proposed |
| 2026-06-30 | `rumble-canvas` uses dual-format spec content. | Structured fields are needed for validation, agents, tests, and Bolt handoff; Markdown remains the human-readable projection/export. | Accepted |
| 2026-06-30 | `TraceabilityLink` is first-class in `rumble-canvas` MVP. | Specs must connect intent → journeys → screens → actions → services/tests/capabilities to be inspectable and agent-compatible. | Accepted |
| 2026-06-30 | `Waiver` is first-class in `rumble-canvas` MVP, with a minimal extensible model. | Exceptions to rules, missing requirements, blocking risks, or validation gates must be auditable, approvable, expirable, traceable, and consumable by Wrench/Bolt. | Accepted |
| 2026-06-30 | `rumble-canvas` uses minimal `ActorReference`, `WorkspaceMembership`, and `RoleAssignment` before a full shared identity model. | Canvas needs attribution, permissions, reviews, and waiver approvals now; account/tenant/SSO/local-first identity remain shared architecture decisions. | Accepted |
| 2026-06-30 | High/critical waivers require distinct human Owner + Reviewer approval in Canvas MVP. | Sensitive exceptions must not be self-approved; Bolt/Wrench can rely on explicit approval evidence. | Accepted |
| 2026-06-30 | First Canvas-to-Bolt handoff format is `canvas.bolt_handoff.v0.1`, kind `planning_request`. | Bolt needs deterministic structured input; MVP must preserve package identity, traceability, waivers, risks, capabilities, requested outputs, and forbid automatic execution. | Accepted |
| 2026-06-30 | Rumble products integrate with Bolt through planning-only `ImplementationHandoff`; MVP Bolt target is `cos-matic`. | Canvas must not execute directly; it submits approved packages with decisions, waivers, risks, traceability links, and constraints, while `cos-matic` returns plans, gates, status, or auditable refusals. | Accepted |
| 2026-06-30 | `rumble-lm` MVP is a synchronous live session product with post-session read-only recap. | Keeps the product focused on facilitation and avoids becoming a full LMS or asynchronous chatbot. | Accepted |
| 2026-06-30 | `rumble-lm` activities are first-class objects with lifecycle, citations, responses, and analytics. | Activities need validation, publication, live execution, response collection, and auditability. | Accepted |
| 2026-06-30 | `rumble-lm` requires citation resolution for generated source-grounded claims. | Grounding and facilitator validation are the core product guardrails against unsupported generated content. | Accepted |
| 2026-06-30 | `rumble-lm` MVP does not center on individual scoring. | The product prioritizes collective learning signals, engagement, misconceptions, and consensus/divergence over learner ranking. | Accepted |
| 2026-06-30 | `rumble-lm` treats `Learner` as a persona, not an ACL role, for MVP. | Keeps the permission model simple: Admin, Facilitator, Participant. | Accepted |
| 2026-06-30 | Interactive Rumble products converge on Rust core + Dioxus UI by default. | Avoid frontend fragmentation and keep local-first/native/web products aligned with the Rust-first harness; `rumble-cos` remains Astro as a public content site exception. | Accepted |
| 2026-06-30 | `rumble-crew` MVP may request real execution through `cos-matic` when workspace `execution_mode=trusted_execution`. | Crew must be operationally useful, while preserving the boundary: Rumble requests/governs; Bolt executes. | Accepted |
| 2026-06-30 | `rumble-crew` uses explicit completion policy for auto-close. | Default stays review-first, but low-risk auto-closable tasks may close after trusted run success when blockers/approvals/stale context are absent. | Accepted |
| 2026-06-30 | `rumble-crew` local evidence storage is temporary and extractable toward Gear. | Gear remains target owner for artifact/provenance; Rumble fallback must include refs, hashes, migration status, and extraction path. | Accepted |
| 2026-06-30 | `rumble-crew` allows privileged raw runtime logs under strict controls. | Debugging trusted execution needs raw logs, but access must be disabled by default, audited, non-indexed, TTL-limited, and redaction-aware. | Accepted |
| 2026-06-30 | `rumble-crew` failed runs require human recovery decision by default. | Run failure is not always task failure; humans decide rerun, reassign, fail, or cancel. | Accepted |
