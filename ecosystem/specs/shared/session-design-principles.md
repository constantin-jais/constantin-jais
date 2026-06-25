# Session Design Principles

These principles guide every ecosystem design session for Rumble, Bolt, Wrench, Gear, and shared security/auth bricks.

## 1. Avoid Dangerous Duplication

Each session must identify what the discussed capability centralizes so Rumble products do not reimplement security-sensitive, evidence-sensitive, or infrastructure-sensitive logic locally.

Examples:

- DB security inspection belongs in `wrench-db-inspect`, not in every Rumble.
- Delegated authorization token semantics belong in the shared Biscuit contract, not per-product token formats.
- Durable artifact/provenance storage belongs in Gear contracts, not ad hoc product blobs.

## 2. Strengthen Products Without Overloading Them

Shared bricks must make `rumble-lm`, `rumble-note`, `rumble-canvas`, `rumble-feed-mind`, and `rumble-crew` safer and more reliable without forcing a premature abstract platform.

A shared capability is justified when it removes duplicated risk or provides reusable evidence. It is not justified merely because multiple products could theoretically use it later.

## 3. Produce Contracts Before Code

Each session should produce implementation-ready design capital before runtime code:

- responsibility boundaries;
- data/API/report models;
- ADR candidates or accepted decisions;
- acceptance tests and fixtures;
- explicit non-goals and scope-leak tests.

Code should follow these contracts, not invent hidden product/platform semantics.

## 4. Keep Sovereignty as a Hard Filter

Design choices must preserve sovereign, inspectable, self-hostable operation:

- no mandatory US SaaS for core truth;
- no blocking licenses for direct dependencies;
- no opaque storage for security/audit/provenance truth;
- no secrets, tokens, raw credentials, raw embeddings, or PII in ordinary logs/reports;
- EU/local-first/data-residency compatibility where applicable.

If an exception is considered, it must be explicit, justified, time-bounded, and reviewable.

## 5. Turn Starred Repositories Into Design Capital

Starred repositories are not a backlog. They are used to:

- challenge architecture decisions;
- benchmark patterns;
- identify risks and anti-patterns;
- justify why a capability should be adopted, rebuilt, studied, rejected, or quarantined;
- improve contracts and tests.

Public ecosystem specs must describe the ecosystem’s own intent and boundaries rather than cloning external product language.
