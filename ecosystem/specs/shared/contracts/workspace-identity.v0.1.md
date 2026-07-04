# Contract — WorkspaceIdentity v0.1

Status: **Accepted 2026-07-04** (ADR 0028). Ratified by promoting the schema from the `rumble-canvas` D11 #1 implementation (the real, tested shape) to the control plane; the registry row moves `Candidate → Accepted`.
Schema: `workspace-identity.v0.1.schema.json` (present, JSON Schema draft 2020-12).

> **Reconciliation note (2026-07-04).** The ratified schema is canvas's implemented shape (fields `actor_type`, `source`, and the `id`/`joined_at`/`created_at`/`revoked_at` fields that carry the revocation-cascade invariant). Explicit changes made in promoting it to the control plane, none silent: (1) `actor_kind` prose aligned to the implemented `actor_type`; (2) upgraded from draft-07 to draft 2020-12 with `$id` and `$defs`; (3) **`tenant_id` made required** at the fact-set root to enforce the multi-tenant invariant (axis #1); (4) `minLength: 1` added to every identifier string (`workspace_id`, `tenant_id`, `actor_id`, `id`, `role`); (5) `additionalProperties: false` added to every object type (`ActorReference`, `WorkspaceMembership`, `RoleAssignment`) so unknown fields are rejected. Two canvas follow-ups this makes explicit, each a small increment, not a contract change: (a) canvas must emit `tenant_id` (its domain does not yet — until then, canvas objects will not validate against this stricter schema, which is intended: the contract is the target); (b) canvas's local `specs/shared/contracts/workspace-identity.v0.1.schema.json` re-syncs to this copy (adopting the same required/minLength/additionalProperties strictness and draft 2020-12) so a single schema governs. A richer `Workspace` type (`name`, `settings`) stays a v0.2 concern per Non-goals.

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

- **ActorReference** — `{ actor_id, actor_type: human | agent | service | external, display_name?, source? }`. No PII beyond a display name; no credentials. Stable across products. (The field is `actor_type` in the ratified schema and canvas code — the earlier `actor_kind` prose was aligned to the implementation on 2026-07-04.)
- **Workspace** — `{ workspace_id, tenant_id, name, settings }`. The container that owns members, content, runs, and settings.
- **WorkspaceMembership** — `{ workspace_id, actor_ref, status: active | invited | revoked }`. Ties an actor to a workspace.
- **RoleAssignment** — `{ workspace_id, actor_ref, role, permissions: [permission_primitive] }`. `role` is a product-named bundle; `permissions` is restricted to the closed primitive vocabulary below (ADR 0028 amendment 1) — never free-form strings.

## Permission primitives (closed vocabulary, v0.1)

`read` · `comment` · `write` · `approve` · `invite` · `administer` · `delegate`

Product roles are named bundles of these primitives, mapped explicitly:

- crew's 8×9 matrix: each of the 9 permission columns maps to exactly one primitive (or a bundle); the mapping table lives in crew's spec and is validated against this list.
- lm's `Host` ⊇ `{read, comment, write, approve, invite, administer}`; `Participant` ⊇ `{read, comment, write}`.
- canvas roles map at reconciliation (2026-07 wave, ADR 0028 amendment 3).

Adding a primitive is a v0.2 change (new contract version + ADR), not a product-local extension. `approve` and `delegate` are never grantable to `agent`/`service`/`external` actors (see Invariants).

## Invariants

- `tenant_id` is mandatory on every `Workspace` and travels into every Biscuit authority block (multi-tenant isolation; never cross-tenant).
- An `ActorReference` of kind `agent`/`service`/`external` can never hold an approval-granting role (enforced at the authorizer, mirrored from crew's spec and lm's Host/Participant split).
- Revocation of a membership cascades to any delegation issued under it (ties to the revocation-registry deferral in ADR 0036 / delegated-authorization-biscuit).
- No secrets, passwords, or tokens are stored in these types; authorization facts only.

## Adoption path (D11 criteria)

1. Canvas maps its minimal `ActorReference`/`WorkspaceMembership`/`RoleAssignment` onto this contract (implementation #1). **Done** (canvas `crates/domain` types + `integration_test_workspace_identity`); remaining canvas increment = emit `tenant_id` and re-sync the local schema to this one (Reconciliation note above).
2. lm maps Host/Participant onto `RoleAssignment` (implementation #2). **Pending** — lm has no identity impl in `crates/*/src` yet; this is the next lm increment toward M1.
3. One cross-repo fixture proves a Biscuit token minted against a `WorkspaceIdentity` fact set authorizes a canvas→handoff request. Canvas's `token_sealer` + D11 fixture cover the mint side; the end-to-end proof lands with M2 (cos-matic real verification).
4. On acceptance, the registry row moves `Candidate → Accepted`. **Done 2026-07-04.**

## Non-goals (anti-gold-plating)

- No SSO/OIDC, no password/credential handling, no session management.
- No local-first identity sync.
- No org/billing/account hierarchy above `tenant_id`.

These are added only when a product with a real external user demands them, not before.
