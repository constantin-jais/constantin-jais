# ADR 0043 — Named sovereignty exceptions for Clever and GitHub

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Amends: ADR 0026, ADR 0034
Related: provider-byok-policy.v0.1

## Context

A blanket hosted-service prohibition conflicts with the selected EU operating boundary, while an implicit exception would hide lock-in and data-transfer risk.

## Decision

The following named exceptions are accepted:

- Clever Cloud for compute and PostgreSQL;
- Cellar through an S3-compatible, provider-neutral storage port;
- Clever AI as the sole default hosted AI boundary, behind an OpenAI-compatible/provider-neutral port;
- GitHub as canonical public forge and distribution surface.

Mistral API and direct OpenAI, Anthropic, Google, AWS or Azure model calls are not fallback candidates. Other hosted providers remain blocked unless a new ADR or a narrowly scoped captive-public interoperability waiver is accepted.

Controls:

- no customer document, prompt body, secret or long-lived credential in GitHub;
- no implicit provider fallback;
- kill switch and local/self-hostable path for AI features;
- explicit region, retention, deletion and subcontractor evidence before provisioning;
- export/restore path for SQL, objects, repositories and release evidence;
- provider SDKs do not enter portable domain cores.

## Consequences

This ADR authorizes code, contracts and dry-runs. Account creation, paid provisioning and deployment remain separate human operations.
