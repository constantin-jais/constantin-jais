# ADR 0001 — Biscuit as shared delegated authorization contract

Status: Accepted  
Date: 2026-06-30  
Decision owner: Shared Rumble architecture  
Related contract: `../contracts/delegated-authorization-biscuit.v0.1.md`

## Context

`rumble-canvas`, `rumble-crew`, `rumble-lm`, and later collaborative `rumble-note` all need delegated rights:

- handoff preparation/submission;
- Bolt run request/cancel/rerun;
- waiver and approval decisions;
- export creation/read/revocation;
- source access;
- participant/member management;
- privileged runtime log access for Crew.

If each product invents its own delegation token, the ecosystem duplicates high-risk security logic: tenant isolation, attenuation, expiry, revocation, key rotation, and audit logging.

The starred-stack audit identifies `eclipse-biscuit/biscuit` as `adopt`, layer `gear`, fit `5`, risk `low`, license `Apache-2.0`, ecosystem need `capability authorization`. This makes Biscuit a suitable design reference and candidate primitive under the sovereignty/license filter.

## Decision

Use Biscuit tokens as the shared internal delegated-authorization contract for Rumble products that delegate rights.

The P0 contract is `DelegatedAuthorizationBiscuit v0.1`.

Core decisions:

1. Tenant fact is `organization`, always required.
2. P0 facts include organization, workspace, actor with canonical actor kind, role snapshot, resource, action, purpose, expiry, delegation ID, revocation reference, policy reference, audit reference, and optional chain refs.
3. Shared actions cover handoff, run request/cancel/rerun, waiver approval, export, source access, participant/member management, raw log access, and audit export.
4. Products keep local authorizers and local product policy decisions.
5. Gear stores only safe references for policy/audit/revocation; it does not become an identity provider.
6. JWT is forbidden for internal delegation unless an external integration requires it and an exception ADR/waiver documents the reason.
7. Raw tokens, bearer headers, secrets, participant responses, source excerpts, and runtime log bodies are forbidden in logs/audit metadata.

## Architecture objectives satisfied

| Objective | ADR consequence |
| --- | --- |
| Avoid dangerous duplication | One shared delegation vocabulary and Biscuit lifecycle replaces per-product token formats. |
| Strengthen products without platform overreach | Products keep local authorization policies; Biscuit centralizes only reusable delegation mechanics. |
| Contracts before code | P0 contract, facts, examples, matrix, lifecycle, and acceptance tests are defined before implementation. |
| Sovereignty as hard filter | Apache-2.0 reference, self-hostable verification, no US SaaS dependency, no opaque storage, no PII in logs. |
| Starred list as design capital | `eclipse-biscuit/biscuit` is used to challenge/justify the authorization primitive, not as a blind backlog item. |

## Consequences

### Positive

- Cross-product delegation becomes inspectable and attenuable.
- Tokens can be narrowed by resource/action/purpose/payload hash without calling the issuer.
- Revocation and key rotation become shared security concerns instead of product afterthoughts.
- Product teams can reason about local permissions while reusing a common delegation substrate.
- Audit logs can correlate decisions using safe references without storing secrets.

### Negative / Costs

- Rumble services need Biscuit verifier libraries and authorizer tests.
- Developers must learn Biscuit facts/checks/policies and avoid treating tokens as JWT-like claim bags.
- Revocation lookup/cache and keyset distribution must be implemented consistently.
- Product-specific actions require governance to avoid vocabulary drift.

## Alternatives considered

### Per-product opaque tokens

Rejected. This duplicates security logic and makes cross-product delegation hard to audit.

### Internal JWT delegation

Rejected for internal delegation. JWTs can express claims but do not provide native attenuation by downstream services. JWT may be used only for external systems that require it, with documented exception.

### Full shared identity provider now

Rejected for P0. The immediate need is delegated authorization, not account lifecycle, SSO, or a complete identity platform. Gear may store safe refs but must not become an IdP.

### Product-local RBAC only

Rejected as insufficient for service-to-service and bounded delegation flows such as Canvas-to-Bolt handoff and Crew run requests.

## Required follow-up

- Keep shared conformance tests aligned with `../contracts/delegated-authorization-biscuit.v0.1.tests.md`.
- Add executable product adapter tests in Canvas, Crew, LM, and Note when delegation is implemented.
- Resolve proposed ADRs for key distribution and revocation storage before first production implementation.
- Define DB schema/migration for revocation references and policy references.
- Decide whether critical events require DB-enforced append-only storage or application-enforced append-only storage.

## Acceptance criteria

- A Canvas handoff token attenuated to `handoff:submit` cannot request `run:request`.
- A Crew run token cannot approve a gate unless `actor($id, "human")` is present and product policy allows it.
- An LM export token cannot read private responses unless explicit product policy and token facts allow it.
- A token without `organization` is rejected by all authorizers.
- A token whose organization differs from route/body/row scope is rejected.
- A revoked `revocation_ref` is rejected before product policy evaluation.
- Public-key rotation supports old and new verification keys until old-token TTL expiry.
- Structured logs contain delegation/audit refs, never raw Biscuit tokens or bearer headers.
