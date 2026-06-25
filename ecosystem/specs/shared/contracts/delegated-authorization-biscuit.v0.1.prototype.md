# Prototype Plan — DelegatedAuthorizationBiscuit v0.1

Status: Draft / pre-implementation spike.  
Contract: `delegated-authorization-biscuit.v0.1.md`.  
Conformance tests: `delegated-authorization-biscuit.v0.1.tests.md`.

## Purpose

Define the smallest technical spike needed before integrating Biscuit into any Rumble product.

This is intentionally not a product implementation. It validates token shape, attenuation, authorizer behavior, revocation lookup, key rotation, and log redaction.

## Scope

P0 spike should prove:

1. Authority block can encode the P0 facts.
2. Attenuation can restrict action/resource/payload hash/TTL.
3. Authorizer denies by default and enforces organization/workspace equality.
4. Agent/runtime actor kinds cannot approve human gates.
5. Revoked references fail before local policy.
6. Old/new public keys work during a rotation window.
7. Structured logs never contain raw Biscuit tokens.

## Preferred implementation shape

### Rust-first spike

Use a small Rust crate when the ecosystem has a suitable workspace:

```text
crates/shared-biscuit-auth-spike/
  Cargo.toml
  src/lib.rs
  tests/conformance.rs
```

Candidate dependencies:

- Biscuit Rust library from `eclipse-biscuit/biscuit` ecosystem, after version/license review.
- `tracing` for structured logs.
- No hosted service dependency.

### Alternative TypeScript spike

Use TypeScript only if the first consumer is a Dioxus/Hono-adjacent service needing WASM validation:

```text
packages/shared-biscuit-auth-spike/
  package.json
  src/index.ts
  test/conformance.test.ts
```

Candidate dependency:

- `@biscuit-auth/biscuit-wasm`, after supply-chain and runtime review.

## Fixtures

Create fixtures only with fake opaque IDs:

- `canvas-handoff-submit.valid.biscuit.fixture` or generated test token;
- `canvas-handoff-submit.attenuated.payload-hash.valid`;
- `crew-run-request.valid`;
- `agent-approval.invalid`;
- `missing-organization.invalid`;
- `revoked-ref.invalid`;
- `old-key.valid-until-ttl`.

Fixtures must never contain real organization IDs, user IDs, source excerpts, participant data, secrets, or live tokens.

## Minimal API to prove

```text
verify_delegation(token, request_context, verifier_config) -> DelegationDecision
```

Where `DelegationDecision` contains only safe fields:

```json
{
  "allowed": false,
  "reason_code": "revoked | expired | missing_fact | policy_denied | signature_invalid | allowed",
  "organization_id": "org_fake",
  "workspace_id": "ws_fake",
  "actor_id": "act_fake",
  "actor_kind": "human",
  "action": "handoff:submit",
  "resource_type": "implementation_handoff",
  "resource_id": "hnd_fake",
  "delegation_id": "del_fake",
  "revocation_ref": "rev_fake",
  "policy_ref": "policy_fake",
  "key_id": "biscuit-ed25519-test"
}
```

No raw token field is allowed in this output.

## Non-goals

- No full identity provider.
- No account/session login implementation.
- No product DB integration beyond fake revocation lookup.
- No real Bolt execution.
- No storage of raw tokens.
- No SaaS KMS/JWKS dependency.

## Spike exit criteria

- All shared conformance tests pass.
- Test logs are scanned for token-like fixture material and fail on leakage.
- Key rotation fixture proves old/new acceptance and retired-key rejection.
- Revocation tests prove single-ref and actor/workspace bulk revocation.
- Product teams can copy adapter patterns without copying product-specific token formats.

## Recommended sequence

1. Build token/fact fixture generator.
2. Implement verifier with static test keyset.
3. Add authorizer policy skeleton with `deny if true`.
4. Add in-memory revocation lookup and fail-closed mode.
5. Add keyset with active/retiring/retired statuses.
6. Add logging redaction tests.
7. Map Canvas handoff and Crew run request as first product smoke tests.
