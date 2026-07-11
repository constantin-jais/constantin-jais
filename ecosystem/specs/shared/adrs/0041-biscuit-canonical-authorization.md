# ADR 0041 — Biscuit as canonical delegated authorization

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Ratifies: delegated-authorization-biscuit.v0.1
Related: ADR 0001, ADR 0009, ADR 0010

## Context

The shared Biscuit contract is detailed but remains Draft while product implementations can diverge. Delegated authorization needs one vocabulary and fail-closed verifier behavior before cross-service adoption.

## Decision

Biscuit with Ed25519 is the canonical internal delegation format. The authority block uses opaque identifiers and the shared facts `organization`, `workspace`, `actor`, `resource`, `action`, `purpose`, `delegation_id`, `revocation_ref`, issuance and expiry. Product state remains authorizer context, not token truth.

Requirements:

- closed-world authorizers end in explicit deny;
- organization equality is enforced across token, route/body and repository scope;
- every token has an expiry check;
- attenuation can only narrow scope;
- public-key rotation supports an overlap window;
- revocation failure closes high-risk operations;
- raw tokens and private keys never enter logs, traces, fixtures or evidence.

Browser login sessions remain separate from delegated Biscuit capabilities.

## Acceptance criteria

Contract suites include allow/deny, cross-tenant, expiry, attenuation, revocation and dual-key rotation cases. Logging tests fail on bearer material.
