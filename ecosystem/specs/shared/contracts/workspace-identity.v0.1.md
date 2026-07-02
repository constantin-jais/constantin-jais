# Contract — WorkspaceIdentity v0.1

Status: Draft / decision material for ADR 0028.
Schema: `workspace-identity.v0.1.schema.json` (to be authored once ADR 0028 ownership is Accepted).

## Purpose

`WorkspaceIdentity` consolidates the minimal actor/workspace/permission model that `rumble-canvas`, `rumble-crew`, and `rumble-lm` each reinvent today into a single shared contract. It exists so products stop shipping divergent identity models and so the `delegated-authorization-biscuit` contract has a stable set of facts to authorize over.

It is **not** a running identity service, an SSO integration, or a local-first sync protocol. Those remain deferred until a product has a real external user.

## Boundary (per ADR 0028, recommended split)

| Concern                                                                  | Owner                                                             |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| `ActorReference` identity, tenant boundary, `RoleAssignment` semantics   | Gear (identity substrate)                                         |
| `Workspace` container, `WorkspaceMembership`, membership UX and settings | Shared Rumble (product primitive)                                 |
| Delegation over these facts (A→B, ≤3 levels, attenuation)                | `delegated-authorization-biscuit.v0.1`                            |
| Theming/label/locale identity                                            | `portal-core` (design substrate — NOT actor/tenant authorization) |

## Core types (minimal, promoted from `rumble-canvas/05b-domain-decisions.md`)

- **ActorReference** — `{ actor_id, actor_kind: human | agent | service | external, display_name }`. No PII beyond a display name; no credentials. Stable across products.
- **Workspace** — `{ workspace_id, tenant_id, name, settings }`. The container that owns members, content, runs, and settings.
- **WorkspaceMembership** — `{ workspace_id, actor_ref, status: active | invited | revoked }`. Ties an actor to a workspace.
- **RoleAssignment** — `{ workspace_id, actor_ref, role, permissions: [string] }`. Product-specific roles mapped to shared permission primitives where possible.

## Invariants

- `tenant_id` is mandatory on every `Workspace` and travels into every Biscuit authority block (multi-tenant isolation; never cross-tenant).
- An `ActorReference` of kind `agent`/`service`/`external` can never hold an approval-granting role (enforced at the authorizer, mirrored from crew's spec and lm's Host/Participant split).
- Revocation of a membership cascades to any delegation issued under it (ties to the revocation-registry deferral in ADR 0036 / delegated-authorization-biscuit).
- No secrets, passwords, or tokens are stored in these types; authorization facts only.

## Adoption path (D11 criteria)

1. Canvas maps its minimal `ActorReference`/`WorkspaceMembership`/`RoleAssignment` onto this contract (implementation #1).
2. lm maps Host/Participant onto `RoleAssignment` (implementation #2).
3. One cross-repo fixture proves a Biscuit token minted against a `WorkspaceIdentity` fact set authorizes a canvas→handoff request.
4. On acceptance, the registry row moves `Candidate → Accepted`.

## Non-goals (anti-gold-plating)

- No SSO/OIDC, no password/credential handling, no session management.
- No local-first identity sync.
- No org/billing/account hierarchy above `tenant_id`.

These are added only when a product with a real external user demands them, not before.
