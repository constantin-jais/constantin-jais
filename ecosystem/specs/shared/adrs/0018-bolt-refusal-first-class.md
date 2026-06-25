# ADR 0018 — Bolt Refusal Is First-Class

Status: Accepted
Date: 2026-06-30

## Context

Unsafe handoffs, stale context, quarantined evidence, missing rights, invalid waivers, and sovereignty violations must not be silently repaired or downgraded. A hidden repair would make planning unauditable and could hide risk from Rumble users.

## Decision

Bolt P0 returns structured `RefusalReport` for unsafe or incomplete inputs. Refusal is a normal output, not an exception fallback.

A refusal includes:

- stable reason code;
- severity;
- safe findings;
- target refs/paths;
- remediation hints;
- no raw PII, secrets, credentials, or evidence bodies.

## Consequences

- Rumbles can display actionable negative outcomes.
- Bolt gates stay deterministic and inspectable.
- Wrench/Gear evidence remains by reference.

## Acceptance Tests

- Stale Gear context produces a refusal or gate, not a silent refresh.
- Quarantined Wrench evidence blocks planning.
- Missing Biscuit right blocks protected actions.
- Refusal output contains safe summaries only.
