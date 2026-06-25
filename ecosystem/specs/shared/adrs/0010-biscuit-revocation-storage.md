# ADR 0010 — Biscuit revocation storage and audit references

Status: Proposed  
Date: 2026-06-30  
Related ADR: `0001-biscuit-shared-delegated-authorization.md`

## Context

Biscuit tokens are signed and attenuable, but revocation still requires services to recognize unsafe or obsolete delegations before normal expiry.

Revocation must cover:

- one delegation/token root;
- all delegations for an actor;
- all delegations for a workspace or organization;
- all delegations tied to a compromised/obsolete policy version;
- emergency key compromise.

The design must not store raw tokens or make Gear a full identity provider.

## Decision

Use hybrid local enforcement with safe shared references.

P0 shape:

- Each service that authorizes a delegated action must have a local or locally reachable revocation lookup.
- Revocation records store safe IDs and hashes only, never raw Biscuit tokens.
- Gear/Rumble may store `revocation_ref`, `delegation_id`, `policy_ref`, root/block IDs, and audit event references for correlation.
- Gear is not the synchronous authorization oracle for every request in P0.

Minimal table shape:

```text
revoked_delegations(
  revocation_ref text primary key,
  root_block_id text null,
  delegation_id text null,
  organization_id text not null,
  workspace_id text null,
  actor_id text null,
  policy_ref text null,
  key_id text null,
  revoked_at timestamp not null,
  expires_at timestamp not null,
  reason_code text not null,
  audit_ref text null
)
```

Optional bulk-scope table or materialized records may be added:

```text
revocation_scopes(
  scope_type text,   -- organization | workspace | actor | policy_ref | key_id
  scope_id text,
  revoked_at timestamp,
  expires_at timestamp,
  reason_code text,
  audit_ref text
)
```

## Runtime rules

- Check revocation before local allow policies.
- Sensitive actions fail closed if revocation lookup is unavailable:
  - `run:request`;
  - `approval:decide`;
  - `waiver:approve`;
  - `log:raw:read`;
  - `export:create`;
  - `member:manage` / `participant:manage`.
- A short in-memory cache is allowed:
  - positive revoked hits: cache until `expires_at` or short cap;
  - negative hits: max 30–60 seconds;
  - cache must be bypassable after emergency revocation if deployment supports invalidation.
- Cleanup may remove revocation rows after max token TTL and retention requirements, except security audit summaries may remain as safe references.

## Audit rules

Audit can store:

- `revocation_ref`;
- `delegation_id`;
- root/block IDs or hashes;
- `organization_id`, `workspace_id`, `actor_id`;
- `policy_ref`, `key_id`;
- `reason_code`, timestamps, and actor who revoked.

Audit must not store:

- raw Biscuit token;
- bearer headers;
- cookies/session IDs;
- private keys;
- source excerpts;
- participant responses;
- raw runtime logs.

## Consequences

### Positive

- Products can enforce revocation without central platform coupling.
- Gear remains a safe reference/audit substrate, not an IdP.
- Emergency revocation paths are explicit.

### Negative

- Multiple services need consistent revocation synchronization or migration discipline.
- Fail-closed behavior can temporarily block sensitive actions during revocation-store outage.

## Alternatives considered

### No revocation, short TTL only

Rejected. Short TTL helps but is insufficient for raw log access, execution requests, compromised keys, and removed members.

### Gear as central online revocation oracle

Rejected for P0. This would turn Gear into critical auth infrastructure and increase coupling.

### Store raw tokens for blacklist lookup

Rejected. Raw token storage creates replay/secrets risk and violates logging/storage constraints.

## Acceptance criteria

- A revoked `revocation_ref` denies access before product allow policies.
- Bulk actor/workspace/organization revocation denies previously valid tokens.
- Sensitive actions fail closed when revocation lookup cannot be trusted.
- Revocation audit events contain safe refs only.
- Cleanup cannot remove records needed to reject still-unexpired tokens.
