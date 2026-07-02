# Bolt HumanApproval v0.1

Status: Draft / P0 contract.
Date: 2026-07-02.

## Purpose

Represent a human approval as a safe, hash-anchorable contract that Bolt can consume during planning gates without enabling execution.

## Boundary

- Bolt consumes the approval as an `evidence_refs[]` projection.
- The approval subject is a `handoff_package` identified by handoff ref and package/payload SHA-256.
- The signature block is mandatory and carries `public_key_ref` plus the signature value; public keys are resolved from `bolt.approval_key_registry.v0.1`.
- P0 validates shape, decision, expiry, subject hash/ref, and verifies the Ed25519 signature over a canonical field string using the active registry key.
- Unknown, revoked, not-yet-valid, or expired `ApprovalKeyRef` entries are refusal conditions; rotation is represented by parallel key refs with `rotated_from` / `rotated_to` metadata.
- P0 still refuses `allow_execution=true`; approval verification is a planning gate, not execution enablement.

## Fixture

- `fixtures/human-approval/human-approval.valid.json`
- `fixtures/human-approval/human-approval-invalid-hash.invalid.json`
- `fixtures/human-approval/human-approval-invalid-signature.invalid.json`
- `approval-key-registry.v0.1.schema.json`
- `fixtures/approval-key-registry/approval-key-registry.valid.json`
- `fixtures/approval-key-registry/approval-key-registry-duplicate-ref.invalid.json`
- `fixtures/approval-key-registry/approval-key-registry-unknown-state.invalid.json`
