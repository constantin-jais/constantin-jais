# Conformance Tests — DelegatedAuthorizationBiscuit v0.1

Status: Draft / P0 shared conformance suite.  
Contract: `delegated-authorization-biscuit.v0.1.md`.

## Purpose

These tests define the minimum behavior any Rumble/Bolt service must satisfy before accepting Biscuit delegated authorization tokens.

They are product-neutral. Product adapters may add stricter tests, but must not weaken these.

## Anti-Duplication Gate

#### Product-specific delegation token is challenged

Given a Rumble product proposes a new delegated token, signed URL, JWT, or opaque capability for internal delegation  
When architecture review runs  
Then the proposal must answer why `delegated-authorization-biscuit.v0.1.md` cannot satisfy the use case  
And undocumented product-local delegation formats are rejected.

#### External token exception is documented

Given an external system requires JWT, signed URL, OAuth token, or another non-Biscuit mechanism  
When the integration is accepted  
Then an ADR or waiver documents the external constraint, boundary, TTL, logging rules, and why the token is not reused for internal delegation.

## Test Categories

### Tenant isolation

#### Missing organization is rejected

Given a validly signed Biscuit token without `organization($org)`  
When any protected endpoint authorizes the request  
Then authorization fails before product policy grants access.

#### Organization mismatch is rejected

Given a token with `organization("org_a")`  
And the route/body/database row belongs to `org_b`  
When the request is authorized  
Then authorization fails  
And the audit event records a safe `organization_mismatch` reason without logging the raw token.

### Required facts

#### Minimal P0 facts are mandatory

Given a token missing one of `organization`, `actor`, `resource`, `action`, `purpose`, `expires_at`, `delegation_id`, or `revocation_ref`  
When the request is authorized  
Then authorization fails closed.

#### Stable opaque identifiers only

Given a token containing email-like, bearer-like, or private-key-like values in facts  
When token validation runs in strict mode  
Then validation fails or emits a blocking security finding according to deployment policy.

### Action attenuation

#### Canvas handoff token cannot request execution

Given a Canvas token with `action("handoff:submit")`  
And an attenuation block restricted to the same action and one payload hash  
When the caller requests `run:request`  
Then authorization fails.

#### Payload hash binding is enforced

Given an attenuated token containing `payload_hash("sha256:abc")`  
When the submitted payload hash is `sha256:def`  
Then authorization fails.

#### Source token cannot export

Given a token with `action("source:read")` for one `source_ref`  
When the caller requests `export:create`  
Then authorization fails.

### Actor type restrictions

#### Agents cannot approve

Given `actor($id, "agent")`  
When the actor requests `approval:decide` or `waiver:approve`  
Then authorization fails even if a product role snapshot is present.

#### Runtime service accounts cannot manage members

Given `actor($id, "runtime_service")`  
When the actor requests `member:manage` or `participant:manage`  
Then authorization fails.

### Expiration

#### Expired token is rejected

Given a token with a Biscuit expiry check before current service time  
When authorization runs  
Then authorization fails.

#### Excessive TTL is rejected for high-risk actions

Given a token for `run:request`, `approval:decide`, `waiver:approve`, or `log:raw:read`  
And `expires_at - issued_at` exceeds product maximum TTL  
When authorization runs  
Then authorization fails.

### Revocation

#### Revoked reference is rejected before product policy

Given a token with `revocation_ref("rev_123")`  
And `rev_123` exists in revocation storage  
When authorization runs  
Then the request is rejected before local allow policies are evaluated.

#### Bulk actor revocation is effective

Given all active delegations for `actor("act_1", "human")` are revoked  
When a previously valid token for that actor is used  
Then authorization fails.

#### Revocation lookup failure fails closed for sensitive actions

Given revocation storage is unavailable  
When authorizing `run:request`, `approval:decide`, `waiver:approve`, `log:raw:read`, or `export:create`  
Then authorization fails closed unless an explicitly documented emergency policy says otherwise.

### Key rotation

#### Dual public key window works

Given verifiers are configured with old and new public keys  
And an old-key token is unexpired  
When authorization runs during the rotation window  
Then signature verification succeeds subject to policy/revocation checks.

#### Old key is rejected after TTL window

Given the old public key has been retired after max token TTL plus clock skew  
When an old-key token is presented  
Then signature verification fails.

#### Unknown key ID is rejected

Given a token signed by a key ID outside the accepted keyset  
When authorization runs  
Then authorization fails.

### Logging and audit safety

#### Raw token is never logged

Given a request contains `Authorization: Bearer <biscuit>`  
When authorization succeeds or fails  
Then logs and audit events contain no raw token, bearer header, cookie, or private key material.

#### Safe references are logged

Given a token contains `delegation_id`, `revocation_ref`, `policy_ref`, and `audit_ref`  
When authorization runs  
Then logs may include those safe references, action, resource type/id, decision result, and error class.

#### Sensitive payloads are excluded

Given an LM response, Note block, source excerpt, or Crew raw runtime log is involved  
When an authorization audit event is recorded  
Then the event stores references/hashes only, not raw content.

### Product adapter smoke tests

#### Canvas

Given a delegated Editor token for `handoff:submit`  
And the package is approved and immutable  
When submitting to Bolt in planning-only mode  
Then authorization succeeds.  
When execution policy allows execution  
Then validation fails even if authorization succeeds.

#### Crew

Given an Agent Supervisor token for `run:request`  
And workspace `execution_mode=trusted_execution`  
When all Crew execution preconditions are true  
Then authorization may succeed.  
Given `execution_mode=disabled`  
Then authorization fails.

#### LM

Given a Facilitator token for `export:create`  
And export policy includes private responses without required visibility permission  
When export is requested  
Then product policy denies the export.

#### Note collaborative later

Given a collaborative Note token for `source:read` over an explicit package manifest  
When a consumer requests full workspace access  
Then authorization fails.
