# Phase 2 runtime metadata contracts v0.1

Status: Draft / implemented locally on Phase 2 branches.

## Ownership

| Contract | Owner | Consumers |
|---|---|---|
| `authorization-registries.v0.1.schema.json` | Bolt/control plane | Bolt authorizers and operator tooling |
| `parser-runtime-attestation.v0.1.schema.json` | Gear Loader | Wrench evidence and Bolt gates |
| `progress-snapshot.v0.1.schema.json` | Portal | Product UI adapters |
| `job-runtime.v0.1.schema.json` | Product-local runtime (first implementation: Sessions) | Portal projections and metadata publishers |

Products retain lifecycle ownership. Portal does not lease or retry jobs. Wrench evaluates evidence but does not execute workers. Bolt consumes authorization registries but never stores private signing material.

## Safe fields

These contracts carry opaque tenant/resource references, bounded counters, timestamps, public Ed25519 keys, stable reason/message codes and sandbox booleans. Job events and claims are metadata-only.

The following are forbidden:

- private keys, bearer material, credentials or provider secrets;
- prompts, source text, document bodies, parser output or arbitrary log text;
- public object URLs or unbounded error messages;
- claims of network/filesystem isolation from an `unconfined` sandbox.

## Lifecycle invariants

- Key registries use Ed25519 public keys and explicit `active`, `retiring` or `revoked` state. Revocation entries identify a delegation reference, root block ID, or both.
- A runtime attestation describes enforced limits only. `macos-seatbelt` requires process, network, filesystem and hard-kill booleans to be true. Linux is intentionally absent until equivalent runtime proof exists.
- Progress revisions and monotonic transitions are validated in Portal code; a snapshot contains translation keys, never raw status text.
- Job records are organization/workspace scoped. Leased records have an owner and expiry. Outbox claims are expiring, attempt-counted and acknowledged by opaque claim ID.

## Non-goals

- Token serialization, private-key distribution or online key discovery.
- Product workflow definitions or a shared job service.
- Database credentials, migration execution or Clever provisioning.
- Linux/Clever sandbox certification.
- UI layout or Dioxus component styling.

## Acceptance tests

1. Every schema passes Draft 2020-12 validation.
2. Positive fixtures are synthetic and contain no secret/content fields.
3. Negative fixtures reject private authorization material, false sandbox claims, raw progress messages, progress overflow and job payloads.
4. Semantic validation rejects `completed_units > total_units`, job attempts above budget and claims for absent events.
5. Implementations retain stricter runtime checks: Biscuit time windows/replay, UTF-8 spans, progress transition monotonicity, PostgreSQL RLS and outbox lease ownership.
