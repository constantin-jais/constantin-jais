# ADR 0011 — Bolt P0 Remains Inside cos-matic

Status: Proposed
Date: 2026-06-30

## Context

Rumble products need agentic orchestration primitives: implementation handoffs, validation, planning, gates, refusals, evidence references, retry lineage, and audit events.

If each Rumble implements these locally, the ecosystem will accumulate incompatible task/run states, approval semantics, retry behavior, and audit formats. That creates security and compliance risk: an action could be executed without a consistent handoff, gate, evidence trail, or refusal path.

At the same time, creating a separate Bolt runtime repository too early would invite a different failure mode: Bolt could become a generic agent platform, workflow builder, product UX, registry, storage substrate, or runtime console. Those responsibilities belong elsewhere:

- Rumble owns product UX and user-facing workflow meaning;
- Wrench owns extraction, inspection, validation, and evidence reports;
- Gear owns artifacts, memory, provenance, manifests, and durable references;
- Biscuit/shared auth owns delegated authorization semantics.

The current concrete P0 need is not a runtime service. It is a deterministic, planning-only orchestration grammar that `cos-matic` can validate and prove.

## Decision

Keep Bolt P0 inside `cos-matic`.

`cos-matic` is the current Bolt implementation target for:

- `ImplementationHandoff` receipt and validation;
- planning-only `PlanningRun` lifecycle;
- typed gates;
- structured refusals;
- Wrench/Gear evidence references;
- idempotency and attempt lineage;
- minimal audit events;
- sovereignty and prompt-injection safety gates.

Do not create a separate `bolt-runner` repository until a durable boundary appears that cannot be honestly held inside `cos-matic`.

A new Bolt repository becomes justified only if at least one of these is required by real product demand:

- long-lived workers or server process;
- distributed queue, leases, scheduling, or cancellation;
- stable network API used by multiple Rumbles;
- durable run database with migrations and operational ownership;
- runtime isolation/sandboxing for multi-agent execution;
- credentials brokering beyond local harness policy;
- independent release or operations cadence from `cos-matic`.

## Consequences

- Rumbles get one canonical grammar for handoff, validation, planning, gates, refusal, evidence, retry, and audit.
- `cos-matic` remains useful and hardened without becoming a product platform.
- Bolt P0 stays planning-only; execution requires a future explicit human gate and separate lifecycle decision.
- Wrench and Gear integrations stay reference-based, preventing Bolt from absorbing inspection or storage responsibilities.
- The ecosystem can later extract a `bolt-runner` from proven pressure instead of inventing it from architectural anxiety.

## Acceptance Tests

- A valid planning-only `ImplementationHandoff` is accepted for planning by `cos-matic`.
- A handoff with `allow_execution=true` is refused.
- A handoff with high/critical risk and no valid waiver is refused.
- Same `handoff_id + payload_hash` is idempotent.
- Same `handoff_id` with a different hash conflicts.
- A dry-run plan produces no implementation side effect.
- Wrench reports and Gear artifacts are consumed by ref/hash/status, not copied as raw bodies.
- A sovereignty violation blocks planning unless an explicit valid waiver exists.
- No Rumble MVP defines an incompatible local run/gate/retry lifecycle.

## References

- `../session-design-principles.md`
- `../contracts/implementation-handoff.v0.1.md`
- `../../harness/README.md`
- `../../harness/01-bolt-cosmatic-hardening.md`
