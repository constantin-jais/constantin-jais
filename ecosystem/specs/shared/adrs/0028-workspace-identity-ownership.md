# ADR 0028 — Workspace/Identity capability ownership

Status: Proposed
Date: 2026-07-02
Decision owner: Constantin (ecosystem architecture)
Related: shared-capabilities registry (overview §6, "Workspace / project space" — Candidate, "Discuss: shared Rumble vs Gear"); decision-log 2026-06-30 (canvas minimal ActorReference/WorkspaceMembership/RoleAssignment); D11 (Draft→Accepted criteria)

## Context

The `Workspace/Identity` capability — who an actor is, which workspace they belong to, and what they may do there — is needed **now** by more than one product:

- `rumble-canvas` already ships a minimal model (`ActorReference`, `WorkspaceMembership`, `RoleAssignment`, decided 2026-06-30, specced in `rumble-canvas/05b-domain-decisions.md`).
- `rumble-crew` specs an 8-role × 9-permission matrix over a workspace.
- `rumble-lm` implements Host/Participant capabilities and mints Biscuit tokens over a session workspace.

The capability is the **hard prerequisite of the flagship**: canvas MVP is collaborative and multi-actor from day one, so it cannot ship without a workspace/identity boundary. Yet the capability has stayed `Candidate` since 2026-06-30, and each product is reinventing a local variant — the exact "paralysis pushes each product to reimplement" the committee review flagged.

A new pressure has appeared: `portal-core` now describes itself as "thin shared identity, permission, and tenant boundary primitives for Portal". This risks a **third** identity model drifting in, in the design-substrate layer, where it does not belong.

The unresolved question (overview open question #3, "minimum shared identity/auth model") is **ownership**, not need. This ADR frames the ownership decision and recommends one, so canvas design can proceed.

## The ownership options

The capability has two separable halves that may live in different layers:

- **Identity/authorization primitives** — `ActorReference` (human/agent/service), tenant boundary, `RoleAssignment`, and the tie-in with the `delegated-authorization-biscuit` contract.
- **Workspace container** — the membership boundary that owns users, permissions, content, runs, and settings for a product space.

| #   | Owner                                                                                   | Rationale                                                                                                                                                                                               | Cost / risk                                                                                                                                                                                          |
| --- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A   | **Shared Rumble crate** (new `rumble-workspace` or a shared-domain crate)               | Workspace is a user-facing product primitive (overview naming rule: `workspace` is a "Rumble shared" name). Products consume one contract; canvas/crew/lm stop reinventing.                             | Requires a shared Rumble code home that does not exist yet (today there is no shared Rumble crate; each product is its own repo).                                                                    |
| B   | **Gear** (`gear-*`, e.g. a `gear-identity` substrate)                                   | Identity/tenant/permission are substrate-like (stored, indexed, verified) and dual-client (products AND agents need them) — consistent with D15 ("gear = runtime substrate, one contract two clients"). | Risks Gear absorbing product meaning (workspace membership is product UX, not pure substrate) — a boundary the doctrine warns against.                                                               |
| C   | **Split**: identity primitives in Gear, workspace container as a shared Rumble contract | Cleanest by the doctrine boundary tests: substrate stays in Gear, product primitive stays in Rumble.                                                                                                    | Two homes to coordinate; more contract surface.                                                                                                                                                      |
| D   | **portal-core** (status quo drift)                                                      | It already claims identity primitives.                                                                                                                                                                  | **Rejected**: portal is the _design substrate_ (D14). Identity in the token/theme layer couples authorization to the UI kit and violates layer isolation. This ADR exists partly to stop this drift. |

## Recommendation

**Option C (split), sequenced behind a shared Rumble home.** Rationale, on the doctrine's own axes:

- **Boundary correctness**: identity/tenant/delegation are substrate (Gear) — they are stored, verified, and consumed by both agents and product runtimes (D15's "one contract, two clients"). The _workspace container_ (membership, roles-in-a-space, settings) is a user-facing product primitive and belongs to shared Rumble (overview naming rule).
- **Unblocks the flagship without over-building**: canvas MVP needs the _contract_, not a running identity service. Promote canvas's minimal `ActorReference`/`WorkspaceMembership`/`RoleAssignment` into the shared contract `workspace-identity.v0.1` (this PR, Draft), and let canvas/crew/lm implement against it. A full SSO/local-first identity service is explicitly deferred (anti-gold-plating: no product has an external user yet).
- **Stops the portal-core drift**: `portal-core` must not own identity. Its "identity primitives" line should be narrowed to _label/locale/token identity for theming_, not actor/tenant authorization.

Deferred, on purpose (not part of Accepted scope): the shared Rumble code home (a `rumble-workspace` crate or equivalent) — that is a repo-creation decision that should ride the canvas MVP, not precede it.

## Consequences

- The `workspace-identity.v0.1` contract (this PR) becomes the single reference; the shared-capabilities registry row moves from `Candidate` to `Accepted` **on acceptance of this ADR**, with owner = "Gear (identity primitives) + shared Rumble (workspace container)".
- `portal-core`'s scope statement is corrected in a follow-up (coordinated with the portal work stream) to remove actor/tenant authorization.
- Canvas, crew, and lm reconcile their local models to the shared contract at their next increment; divergence becomes a review finding.
- This is the first application of the D11 criteria (≥2 implementations + ≥1 cross-repo test + adoption ADR) to a shared capability.

## Status note

Proposed, not Accepted: the ownership split (B vs C) and the deferral of the shared Rumble home are Constantin's call. Merging this ADR as Accepted ratifies Option C; amending it to Option A or B before merge is the intended fork.
