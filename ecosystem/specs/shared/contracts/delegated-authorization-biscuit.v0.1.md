# Contract — DelegatedAuthorizationBiscuit v0.1

Status: Accepted by ADR 0041.
Owner: Shared Libre AI authorization contract; product adapters enforce locally; Gear stores safe policy/audit references only.
Contract index: `README.md`.  
Conformance tests: `delegated-authorization-biscuit.v0.1.tests.md`.  
Prototype plan: `delegated-authorization-biscuit.v0.1.prototype.md`.  
ADRs: `../adrs/0001-biscuit-shared-delegated-authorization.md`, `../adrs/0009-biscuit-public-key-distribution.md`, `../adrs/0010-biscuit-revocation-storage.md`, `../adrs/0041-biscuit-canonical-authorization.md`.
Reference implementation inspiration: `eclipse-biscuit/biscuit` (Apache-2.0, Rust, capability authorization). This spec uses Biscuit concepts; it does not copy repository content.

## Purpose

Biscuit tokens are the shared delegation contract for Libre AI products. They express bounded, attenuable rights across Spec Studio, Agent Board, Sessions and later collaborative Notebook.

The goal is to prevent each product from inventing its own delegation token, approval token, run token, export token, or source-access token.

## Non-Negotiable Rules

- Tenant is always `organization`.
- No home-made JWT for internal delegation unless an external integration forces it and the exception is documented.
- A Biscuit token carries facts and checks; product authorization policies stay in local authorizers.
- Tokens must include tenant, actor, expiry, delegation purpose, and revocation reference.
- Services must never log raw tokens or secrets. Logs may include hashes, block IDs, revocation refs, and decision IDs.
- Products apply product-specific decisions locally, but the delegation vocabulary remains shared.
- Gear may store safe references to policy, audit, revocation, artifacts, and events. Gear is not a full identity provider.

## Boundary

| Concern | Owner |
| --- | --- |
| Human account identity, login, SSO, local account lifecycle | Future identity/auth adapter, not this contract |
| Delegated right vocabulary and token shape | Shared Biscuit contract |
| Product role-to-action mapping | Each product |
| Runtime execution | Bolt / `cos-matic` |
| Source/artifact/audit references | Gear Memory / Gear Depot / Gear EventLog candidates |
| Policy decisions for a specific request | Local service authorizer |
| Private signing keys | Single issuer/auth service only |

## Rights Vocabulary

Rights are expressed with `action($name)` facts/checks. Shared names are intentionally cross-product and coarse enough to avoid product forks.

Priority meanings:

- **P0**: required for first shared contract adoption or already needed by active products.
- **P1**: expected soon or sensitive enough to reserve now.
- **P2**: future/collaborative expansion; should not drive P0 implementation.

| Right | Priority | Meaning | Typical resources |
| --- | --- | --- | --- |
| `handoff:prepare` | P0 | Prepare a product-to-Bolt handoff payload. | spec package, task bundle |
| `handoff:submit` | P0 | Submit a validated planning handoff to Bolt. | implementation handoff |
| `run:request` | P0 | Request a bounded Bolt run/execution attempt. | task, agent assignment |
| `approval:decide` | P0 | Decide a gate/approval request. | gate, evidence review |
| `export:create` | P0 | Create an export artifact/package. | session, package, audit bundle |
| `export:read` | P0 | Read/download an export artifact. | artifact ref |
| `source:read` | P0 | Access a source or source excerpt within scope. | `SourceRef`, source chunk |
| `source:attach` | P0 | Attach/import a source reference to a workspace/session/task. | `SourceRef` |
| `member:manage` | P0 | Manage workspace membership and roles. | workspace |
| `participant:manage` | P0/P1 | Invite/remove/update participant/member access where sessions expose participants. | workspace, session |
| `waiver:propose` | P1 | Propose a controlled exception. | waiver target |
| `waiver:approve` | P1 | Approve a waiver within product policy. | waiver |
| `run:cancel` | P1 | Cancel or request cancellation for a run. | run ref, task |
| `run:rerun` | P1 | Request rerun for a failed/superseded run. | run ref, task |
| `export:revoke` | P1 | Revoke export availability or mark artifact revoked. | artifact ref |
| `log:raw:read` | P1 | Read privileged runtime raw logs. | runtime log ref |
| `audit:export` | P1 | Export audit timeline/report metadata. | workspace, session, task |

Product-specific actions may exist, but must either map to one of these shared actions or be proposed as a v0.2 shared action if reused by more than one product.

## P0 Biscuit Token Facts

Token facts use stable opaque IDs, never emails, names, raw content, source excerpts, credentials, or raw tokens.

| Fact | Required | Example | Notes |
| --- | --- | --- | --- |
| `organization($org_id)` | Yes | `organization("org_01H...")` | Tenant boundary. Token without it is invalid. |
| `workspace($workspace_id)` | Usually | `workspace("ws_canvas_123")` | Required for workspace-scoped delegation. |
| `actor($actor_id, $actor_kind)` | Yes | `actor("act_123", "human")` | Canonical actor kind is the second argument: `human`, `agent`, `runtime_service`, `system`. Do not introduce a separate `actor_type()` fact in P0. |
| `role($role_name)` | Optional | `role("owner")` | Snapshot role; authorizer still checks current product state when needed. |
| `resource($type, $id)` | Yes | `resource("handoff", "hnd_123")` | Use `"*"` only for admin/system maintenance with short TTL and approval. |
| `action($action_name)` | Yes | `action("handoff:submit")` | From shared vocabulary. |
| `purpose($purpose_name)` | Yes | `purpose("canvas_to_bolt_planning")` | Explains why delegation exists. |
| `issued_at($ts)` | Yes | `issued_at("2026-06-30T10:00:00Z")` | ISO-8601 string or Biscuit date literal depending library support. |
| `expires_at($ts)` | Yes | `expires_at("2026-06-30T10:15:00Z")` | Also enforced by `check if time($t), $t < ...`. |
| `delegation_id($id)` | Yes | `delegation_id("del_123")` | Safe audit correlation ID, not a secret. |
| `revocation_ref($ref)` | Yes | `revocation_ref("rev_123")` | Stable DB/Gear reference for revocation lookup. |
| `policy_ref($ref)` | Optional | `policy_ref("pol_canvas_handoff_v1")` | Safe policy version/reference. |
| `audit_ref($ref)` | Optional | `audit_ref("evt_123")` | Gear/product event reference, no raw token. |
| `parent_delegation($id)` | Optional | `parent_delegation("del_parent")` | Delegation chain without storing token material. |
| `chain_depth($n)` | Optional | `chain_depth(1)` | Authorizers should cap depth for sensitive actions. |
| `artifact_ref($id)` | Optional | `artifact_ref("art_123")` | For export/handoff/evidence. |
| `source_ref($id)` | Optional | `source_ref("src_123")` | For source access. |
| `run_ref($id)` | Optional | `run_ref("run_123")` | For Bolt run operations. |

## Minimal Authority Block Example

Canvas Owner delegates a planning handoff submission for one approved package.

```datalog
organization("org_01H8");
workspace("ws_canvas_42");
actor("act_owner_7", "human");
role("owner");
resource("implementation_handoff", "hnd_99");
artifact_ref("pkg_artifact_31");
action("handoff:submit");
purpose("canvas_to_bolt_planning");
issued_at("2026-06-30T10:00:00Z");
expires_at("2026-06-30T10:15:00Z");
delegation_id("del_handoff_99");
revocation_ref("rev_del_handoff_99");
policy_ref("policy:canvas-handoff-submit:v1");
audit_ref("event:implementation_handoff_validated:evt_123");

check if time($time), $time < 2026-06-30T10:15:00Z;
```

## Attenuation Example

An intermediate service attenuates the handoff token before calling Bolt so it can only submit a planning request and cannot be reused for execution.

```datalog
// Added attenuation block
check if organization("org_01H8");
check if workspace("ws_canvas_42");
check if resource("implementation_handoff", "hnd_99");
check if action("handoff:submit");
check if purpose("canvas_to_bolt_planning");
check if time($time), $time < 2026-06-30T10:05:00Z;

// Bind to one payload hash; this is safe to log, unlike the token.
payload_hash("sha256:8f3...");
check if payload_hash("sha256:8f3...");

// Explicitly prevent accidental broad runtime delegation in authorizers by absence:
// no action("run:request") fact/check is introduced.
```

A product authorizer must still inject local context facts such as current workspace state, package approval, actor membership, and policy version.

## Glossary

| Term | Meaning | Safe to store/log? |
| --- | --- | --- |
| `delegation_id` | Stable ID for the delegated authorization grant. | Yes. |
| `revocation_ref` | Lookup reference used to revoke one delegation or a revocation scope. | Yes. |
| `policy_ref` | Version/reference of the policy used when issuing or evaluating delegation. | Yes. |
| `audit_ref` | Product/Gear event reference correlating a decision or issuance. | Yes. |
| `root_block_id` | Biscuit authority/root block identifier or hash used for revocation/debug. | Yes, if not token material. |
| `block_id` | Biscuit block identifier or hash for authority/attenuation blocks. | Yes, if not token material. |
| `artifact_ref` | Safe reference to Gear Depot or product export artifact. | Yes. |
| `source_ref` | Safe reference to Gear Memory/product source record. | Yes; not source content. |
| `run_ref` | Safe reference to a Bolt run/projection. | Yes. |
| raw Biscuit token | Base64/bytes bearer credential. | Never. |

## Authorizer Contract

Every product or Bolt service receiving a Biscuit token must:

1. Verify signature with an accepted public key.
2. Reject if root block ID or revocation reference is revoked.
3. Inject service context facts: `time`, `request_organization`, `request_workspace`, requested `resource`, requested `action`, request hash/version, and product state needed for local policy.
4. Run closed-world policies ending in `deny if true`.
5. Enforce organization equality between token, route/body, and database row scope.
6. Log only safe references: `delegation_id`, root/block IDs, `revocation_ref`, `policy_ref`, action, resource type/id, decision, and error class.

### Token facts vs authorizer context facts

| Kind | Examples | Rule |
| --- | --- | --- |
| Token facts/checks | `organization`, `workspace`, `actor`, `role`, `resource`, `action`, `purpose`, `expires_at`, `delegation_id`, `revocation_ref`, `artifact_ref`, `source_ref`, `run_ref` | Signed/attenuated delegation scope; must not encode mutable product truth as final authority. |
| Authorizer context facts | `time`, `request_organization`, `request_workspace`, `request_resource`, `request_action`, `handoff_validated`, `member_has_current_permission`, `workspace_execution_mode`, `privacy_gate_passed` | Injected by the receiving service from route/body/DB/current policy; used for local decisions. |

Dynamic product decisions belong in authorizer context facts, not in the token. A role snapshot in a token is only advisory unless the local authorizer deliberately accepts it for a low-risk action.

Example local policy skeleton:

```datalog
allow if
  organization($org),
  request_organization($org),
  workspace($ws),
  request_workspace($ws),
  actor($actor, "human"),
  action("handoff:submit"),
  resource("implementation_handoff", $handoff),
  handoff_validated($handoff),
  member_has_current_permission($actor, $ws, "handoff:submit");

deny if true;
```

## Rights x Products Matrix

| Shared right | Canvas | Crew | LM | Note collaborative later |
| --- | --- | --- | --- | --- |
| `handoff:prepare` | P0 | Later, task bundle planning | Later, session/export handoff | Later |
| `handoff:submit` | P0 planning-only to Bolt | P1 for task bundle / recovery planning | P1 for source-grounded activity/report planning | Later |
| `run:request` | Not MVP; Canvas must not execute directly | P0 trusted execution request | P1 generation/evaluation run if routed through Bolt | Later agent assistance |
| `run:cancel` | Not MVP | P0 | P1 | Later |
| `run:rerun` | Not MVP | P0 | P1 | Later |
| `waiver:propose` | P0 | P1 | P1 | Later |
| `waiver:approve` | P0, human separation for high/critical | P1 for gates/evidence exceptions | P1 for privacy/citation/export blockers | Later |
| `approval:decide` | Section/package/handoff approval | P0 gates/evidence | P1 publication/export gates | Later collaboration approvals |
| `export:create` | P0 spec package | P0 audit/evidence exports | P0 session summaries/audit exports | P1 note workspace export |
| `export:read` | P0 | P0 | P0 participant/admin scoped | P1 |
| `export:revoke` | P1 artifact availability | P1 evidence/log bundles | P0/P1 depending export backend | P1 |
| `source:read` | P0 package/source refs | P0 task context/evidence refs | P0 session sources | P0 note/source refs |
| `source:attach` | P0 spec package inputs | P0 evidence/task context | P0 imports | P0 note projections |
| `participant:manage` | Optional; prefer `member:manage` | Optional; prefer `member:manage` | P0 session join/invite | P0 collaborators |
| `member:manage` | P0 workspace roles | P0 workspace roles | P0 admin/facilitator policy | P0 |
| `log:raw:read` | Not MVP | P0 privileged only | Not P0 | Not P0 |
| `audit:export` | P0 | P0 | P0 | P1 |

## Expiration, Attenuation, Revocation, Key Rotation

### Expiration

- Every token must contain `expires_at` and a Biscuit `check if time($time), $time < ...`.
- Default TTLs:
  - UI-to-product delegation: 5–30 minutes.
  - Product-to-Bolt handoff submission: 5–10 minutes.
  - Runtime/event ingestion delegation: 5–15 minutes or mTLS/service channel equivalent.
  - Download/export access: short-lived URL/token; artifact retention is separate.
- Long-lived delegation is forbidden for P0. Use re-issuance with audit instead.

### Attenuation

- Downstream services may add checks for narrower resource, action, payload hash, source/artifact ref, TTL, or organization/workspace.
- Attenuation must never introduce broader actions or new tenant scope.
- Chain depth should be capped by product policy; sensitive approvals should reject delegated chains beyond depth 1 unless explicitly allowed.

### Revocation

Store revocation records by safe references, not raw tokens:

```text
revoked_delegations(
  revocation_ref,
  root_block_id,
  optional_delegation_id,
  organization_id,
  actor_id,
  revoked_at,
  reason_code,
  expires_at
)
```

Authorizers check revocation before running product policy. A short cache TTL (30–60s) is acceptable. Bulk revocation must support at least organization, actor, workspace, and policy version scopes.

### Key Rotation

- Use Ed25519 signing keys.
- Private signing key is available only to the issuer/auth service.
- Verifiers support a key set with `key_id`/version metadata and at least two active public keys during rotation.
- Rotation flow:
  1. Publish new public key to verifiers.
  2. Enable verifier support for old and new keys.
  3. Switch issuer to new private key.
  4. Wait for max token TTL plus clock skew.
  5. Retire old public key.
- Emergency key compromise requires: disable issuer, revoke affected key version, invalidate active delegation refs, and record security event without exposing token material.

## Safe Audit and Gear References

Gear and products may store:

- `delegation_id`, `revocation_ref`, `policy_ref`, `audit_ref`;
- Biscuit root/block IDs or hashes;
- public key `key_id`/version;
- resource/action/purpose/organization/workspace IDs;
- decision result and error class;
- payload hashes, artifact refs, source refs, run refs.

Gear and products must not store in audit metadata:

- raw Biscuit token base64/bytes;
- private keys;
- bearer headers;
- cookies/session IDs;
- source excerpts, participant responses, runtime log bodies, or credentials.

## Security Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Token logged and replayed | Critical | Structured logging denylist, `skip(token)`, log refs only, short TTL. |
| Cross-tenant access | Critical | Mandatory `organization`, route/body/DB equality checks, RLS where possible. |
| Product forks delegation model | High | Shared vocabulary/contract; new reused rights proposed as v0.2. |
| Token grants too broad scope | High | Resource/action/purpose required, attenuation by payload hash and TTL. |
| Stale role snapshot used as truth | High | Authorizer checks current membership/role for high-risk actions. |
| Agent/runtime approves human gate | High | `actor($id, "human")` is required for approvals unless explicit future ADR. |
| Revocation lookup unavailable | High | Fail closed for high-risk actions; short local cache only for positive revoked refs. |
| Key rotation breaks all sessions | Medium | Dual public-key window and short max TTL. |
| Gear becomes identity provider | Medium | Gear stores references/audit only, no login/credential lifecycle. |
| Export/download tokens outlive policy | High | Short-lived delegated access plus artifact-level revocation metadata. |

## Acceptance Tests

- Given a token without `organization`, authorization fails.
- Given route organization differs from token organization, authorization fails.
- Given a raw Biscuit token appears in logs, logging tests fail.
- Given `actor($id, "agent")`, `waiver:approve` and `approval:decide` fail.
- Given a revoked `revocation_ref`, authorization fails before product policy.
- Given an attenuated Canvas token for `handoff:submit`, `run:request` fails.
- Given a handoff payload hash differs from the attenuated hash, submission fails.
- Given old and new public keys during rotation, unexpired old-key tokens verify until TTL expiry.
- Given raw log access in Crew, the audit event records only `log_ref`, actor, purpose, and visibility level, not log body.
