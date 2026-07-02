# ADR 0026 — Sovereignty Posture: Core Truth vs. Operational Substrate

Status: Accepted
Date: 2026-07-02
Decision owner: Ecosystem Architecture
Related decision: D2 (decision-log)

## Context

GitHub is the current operational substrate for CI/orchestration, releases, and collaborative workflows. However, the Rumble/Bolt/Wrench/Gear ecosystem must remain sovereign: data, specs, code, and decisions must be exportable and runnable on self-hosted infrastructure.

A clear boundary between "core truth" (self-hostable, governance-owned, auditable export target) and "operational substrate" (assumed trusted for delivery but not required for history) ensures that GitHub lock-in does not become architectural debt.

## Decision

Define the sovereignty posture as follows:

**Core Truth** (must remain fully exportable and self-hostable):

- Specifications and architecture decisions (`ecosystem/specs/shared/`).
- Product code and test suites (all `rumble-*`, `gear-*`, `wrench-*`, `bolt-*` repos).
- Versioned contracts (`contracts/*.md`).
- Configuration and manifest files (`maturity.json`, NIST mappings, policy definitions).
- Audit event logs and decision records.

Mirrored/archived copy must be maintained outside GitHub (S3, Tarball, or alternative Git host) on a recurring schedule (weekly recommended).

**Operational Substrate** (GitHub-assumed, non-blocking):

- CI/orchestration pipeline definitions (GitHub Actions).
- Release processes and artifact hosting.
- Collaboration infrastructure (Pull Requests, Issues, Discussions).
- Real-time dashboard/monitoring integrations.

These are implementation details; switching CI providers does not require changes to product code or specs.

## Architecture objectives satisfied

| Objective                       | ADR consequence                                                                   |
| ------------------------------- | --------------------------------------------------------------------------------- |
| No platform lock-in             | Core truth is portable; operational substrate is swappable.                       |
| Regulatory and audit confidence | Exportable decision history and code audit trails.                                |
| Self-hosted option              | Teams can run the entire system from a tarball and an internal Git host.          |
| Disaster recovery               | External snapshot ensures history survives GitHub downtime or account compromise. |

## Consequences

### Positive

- Ecosystem remains portable to alternative Git hosts or internal infrastructure.
- GDPR/compliance audits have a clear export target.
- Team can maintain a verifiable backup independent of GitHub's SLA/terms.
- Code/decision history is decoupled from real-time collaboration features.

### Negative / Costs

- Weekly snapshots require storage infrastructure and automation.
- Bidirectional sync between GitHub and external archive is not automatic; one-way archive suffices but drift monitoring is needed.
- Documentation must clarify what is backed up and what is CI-only.

## Alternatives considered

### Single source of truth in GitHub, periodic exports

Rejected as insufficient. GitHub Terms of Service can change; dependencies are opaque.

### Complete GitHub independence; self-hosted only

Rejected. Would sacrifice development velocity and ecosystem contribution ease for negligible risk reduction.

### Encrypted GitHub backups via third-party service

Rejected. Still depends on GitHub durability and terms; external archive is simpler and more portable.

## Required follow-up

- Define snapshot scope and automation target (S3 bucket, Tarball repo, or internal Git host).
- Implement `ecosystem/tools/state-snapshot.sh` to archive specs, decisions, maturity, and readiness data weekly.
- Document snapshot retention policy and verification (checksums, reproducibility).
- Add snapshot verification job to CI (ensures archive stays synchronized).
- Update CLAUDE.md and onboarding docs to reference the backup location and disaster recovery process.

## Acceptance criteria

- Weekly snapshot contains `ecosystem/specs/`, all `*-jais` source code, and `maturity.json`.
- Snapshot is independently verifiable via checksums.
- Snapshot tarball can be extracted and entire spec suite is readable without GitHub access.
- Documentation clearly states GitHub Terms of Service do not restrict archival or re-hosting.
