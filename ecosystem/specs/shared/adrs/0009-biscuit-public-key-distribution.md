# ADR 0009 — Biscuit public key distribution

Status: Proposed  
Date: 2026-06-30  
Related ADR: `0001-biscuit-shared-delegated-authorization.md`

## Context

All services that accept Biscuit delegated tokens must verify signatures. Private signing keys must stay with the issuer/auth service only, while Rumble/Bolt services need current and previous public keys during rotation.

The mechanism must be self-hostable, compatible with local/EU deployments, and avoid a mandatory external SaaS dependency.

## Decision

Use a versioned Biscuit public keyset as the shared distribution shape.

P0 supports two delivery modes:

1. **Static config/env keyset** for local-first, development, and simple self-hosted deployments.
2. **Self-hosted well-known endpoint** for multi-service deployments:

```text
GET /.well-known/biscuit-public-keys
```

The endpoint returns public keys only, never private material.

Example shape:

```json
{
  "format": "biscuit-public-keyset.v0.1",
  "issuer": "shared-auth",
  "generated_at": "2026-06-30T10:00:00Z",
  "keys": [
    {
      "key_id": "biscuit-ed25519-2026q3",
      "algorithm": "Ed25519",
      "public_key": "base64-or-hex-public-key",
      "status": "active",
      "not_before": "2026-06-30T10:00:00Z",
      "not_after": null
    },
    {
      "key_id": "biscuit-ed25519-2026q2",
      "algorithm": "Ed25519",
      "public_key": "base64-or-hex-public-key",
      "status": "retiring",
      "not_before": "2026-04-01T00:00:00Z",
      "not_after": "2026-07-07T00:00:00Z"
    }
  ]
}
```

## Rules

- Services must support at least two accepted public keys during rotation.
- Key IDs are safe to log; public keys may be logged only in explicit debug/admin contexts, not normal request logs.
- Unknown `key_id` or key material fails closed.
- Well-known endpoint is optional in P0; static keyset remains valid for local and small deployments.
- Hosted/multi-service deployments should cache keysets with short TTL and fail closed for sensitive actions if no valid keyset is available.
- Private keys are never distributed through Gear, Rumble, Bolt, Wrench, config exports, logs, or audit events.

## Consequences

### Positive

- Rotation is possible without invalidating every active token immediately.
- Local-first and self-hosted modes remain simple.
- No dependency on US cloud KMS/JWKS SaaS is introduced.

### Negative

- Services need keyset parsing/cache logic.
- Emergency compromise requires coordinated key disablement plus revocation.

## Alternatives considered

### Single env var public key only

Rejected as the only mechanism. It is simple but makes rotation brittle.

### Hosted JWKS provider

Rejected as default. It introduces unnecessary SaaS/platform dependency and JWT-shaped assumptions.

### Gear as key registry

Rejected for P0. Gear may store safe audit refs, but should not become auth/key infrastructure.

## Acceptance criteria

- Verifiers accept active and retiring keys during the rotation window.
- Verifiers reject unknown or retired keys after TTL plus clock skew.
- Static keyset and well-known keyset use the same data shape.
- No private key material appears in logs, config exports, or Gear metadata.
