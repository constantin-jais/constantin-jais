# ADR 0040 — Machine-readable language, adapter and compromise contract

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Related: ADR 0033, ADR 0038, ADR 0039, ADR 0043, ADR 0044

## Context

The v0.1 target-version records layers and frameworks but cannot express language ownership, specialized adapters, provider exceptions, clean-room rules or panic policy. Harness generation can therefore be green while omitting accepted architecture constraints.

## Decision

The target-version machine contract evolves additively to v0.2. It must record:

- durable/core and browser language ownership;
- forbidden source-language extensions;
- specialized-adapter classes and required isolation;
- clean-room provenance rules;
- named infrastructure/forge exceptions and compromise references;
- Biscuit vocabulary/version;
- panic policy per artifact class.

Unknown fields remain rejected. Every named compromise references an accepted ADR. The human target-version and machine artifact change together.

## Acceptance criteria

- Draft 2020-12 schema validates the target artifact;
- deleting any required authority field fails validation;
- no session-local secret, account identifier or absolute path is serialized;
- spec-contract CI validates v0.2 directly.
