# Rumble Delivery Maturity v0.1

Status: Draft / P0 contract  
Owner: Bolt harness (`cos-matic`) consumes; Rumble products claim; Wrench/Gear provide evidence.  
Purpose: make the long-term ambition of commercializable, multi-platform Rumble products inspectable without turning product ambition into startup-style prioritization.

## Principle

Rumble projects are dojos today and serious products in the long term.

Commercializable maturity is a **quality target**, not a monetization or traction heuristic. A Rumble is allowed to stay experimental, but when it claims a delivery level the claim must be backed by dated evidence.

```text
ambition → claimed maturity → evidence → gates → next increment
```

## Maturity levels

| Level | Name | Meaning |
| --- | --- | --- |
| `R0` | `spec` | Intention, boundaries, learning role, and non-goals are explicit. |
| `R1` | `contract` | Core contracts, fixtures, schemas, or validation tests exist. |
| `R2` | `portable-core` | Durable product logic exists in a portable Rust core with tests. |
| `R3` | `local-workflow` | A CLI or local reference workflow proves the core end-to-end. |
| `R4` | `service-api` | A self-hostable API/service exposes the workflow with auth/config boundaries. |
| `R5` | `web-ui` | A usable web UI exists without duplicating durable business logic. |
| `R6` | `desktop` | Desktop packaging exists through the shared release rail. |
| `R7` | `mobile` | Mobile experience exists without reimplementing the core. |
| `R8` | `sync-offline` | Backup/export/local-first/sync story is explicit and tested where relevant. |
| `R9` | `reproducible-release` | Builds, checksums, provenance, artifacts, and install floors are reproducible. |
| `R10` | `commercializable` | External-user quality: onboarding, docs, security, supportability, data lifecycle, release, and operations are credible. |

## Axes

A level claim also reports axis maturity. The global claim cannot exceed the weakest mandatory axis for that level.

Required axes:

- `spec`
- `contracts`
- `core`
- `security`
- `ux`
- `persistence`
- `orchestration`
- `inspection`
- `release`
- `operations`
- `commercial_readiness`
- `learning_yield`

## Platform readiness

Platform readiness is tracked separately from global maturity so ambition remains visible without pretending every platform is ready.

Allowed platform states:

- `none`
- `planned`
- `proof`
- `usable`
- `trusted`

Platforms:

- `cli`
- `api`
- `web`
- `desktop`
- `mobile`
- `self_hosted`
- `cloud_eu`

## Evidence categories

A maturity claim may reference:

- docs/spec files;
- contracts/schemas;
- fixtures;
- test commands;
- proof JSON files;
- Wrench reports;
- Gear artifact/provenance refs;
- ADRs/decision-log entries;
- release artifacts.

Evidence must be references, not embedded raw secrets, raw logs, or private user data.

## Forbidden shortcuts

The harness must reject claims that take unsafe shortcuts.

Examples:

| Shortcut | Reason |
| --- | --- |
| claiming `R5` web UI without `R2` portable core | UI must not become the durable product core. |
| claiming `R7` mobile without a non-duplicated core | Mobile must not fork business logic. |
| claiming `R9` without Gear-style checksums/provenance | Release maturity requires verifiability. |
| claiming `R10` with unresolved BYOK/secrets/logging policy | Commercializable quality requires explicit security posture. |
| claiming high level while hiding open questions | Ambition must not mask incompleteness. |

## Learning yield

Because Rumbles are dojos, every claim may report what the project taught the stack:

- shared capability generated;
- contract extracted;
- Wrench/Gear/Bolt primitive strengthened;
- open question closed;
- shortcut prevented;
- evidence produced.

This keeps learning visible even before commercial maturity.

## Extraction pressure

A Rumble may report capabilities that are appearing in more than one product. The harness should warn when repeated product-local needs may deserve shared ownership.

Example:

```text
Provider/BYOK policy appears in rumble-feed-mind and rumble-lm → shared security policy candidate.
```

## P0 validation scope

P0 validation is intentionally small:

- validate schema shape;
- ensure claimed/current/target levels are known;
- ensure level ordering is coherent;
- reject forbidden shortcut fixtures;
- reject unsafe evidence keys;
- require blockers for non-passing claims;
- require `learning_yield` for Rumble dojo claims.

Runtime command execution belongs to later `cos-matic maturity` integration.

## Future CLI shape

```bash
cosmatic maturity report --workspace ecosystem.toml
cosmatic maturity promote --project rumble-lm --to R2 --check
```

Expected report:

```text
rumble-lm
current: R1 contract
target: R3 local-workflow
next: R2 portable-core
blocked_by:
- no portable-core compile check
- retention defaults unresolved
- CitationValidation contract missing
```
