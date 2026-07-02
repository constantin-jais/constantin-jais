# ADR-0025 — Agentic P0 tooling backlog for stack validation

- Status: Accepted
- Date: 2026-07-02
- Related: `0024-stack-validation-local-only.md`, `../decision-log.md`, `../../harness/04-stack-validation-tooling.md`

## Context

The ecosystem needs repeatable stack validation before product teams or agents start implementing. The tools must improve evidence quality without becoming a broad automation platform or a provisioning shortcut.

The useful tools share the same shape: frequent, deterministic, local-first, testable, dry-run by default, and easy to refuse when inputs are unsafe.

## Decision

Start with five P0 tools:

| Tool | Responsibility | Must not do |
| --- | --- | --- |
| `project_status` | Summarize repository state: branch, dirty files, recent checks, known scripts, risks, and next local action. | Commit, push, reset, delete, or modify files. |
| `stack_detect` | Detect languages, package managers, frameworks, DB signals, CI, scripts, and likely verification commands. | Install dependencies or infer maturity from presence alone. |
| `stack_scorecard` | Score a target stack against security, quality, performance, completeness, and sovereignty. | Treat the score as approval without evidence links. |
| `dependency_audit` | Consolidate license, vulnerability, source/provider, and sovereignty signals from local manifests. | Upload manifests, auto-upgrade dependencies, or waive risks silently. |
| `local_smoke` | Run explicitly configured local smoke checks for endpoints, CLIs, builds, or UI. | Connect to remote production resources or require secrets by default. |

Later tools are accepted but not P0:

| Tool | Activation condition |
| --- | --- |
| `db_security_check` | PostgreSQL is active or a SQL-backed product slice is under review. |
| `adr_generate` | A decision has been accepted and needs a draft projection, not automatic acceptance. |
| `deploy_dry_run` | Deployment target is documented and the tool can prove no resource creation. |

Rejected for the current line:

- `setup_everything` or any do-everything bootstrapper;
- automatic cloud provisioning;
- real deploy automation;
- SaaS/provider activation that requires API keys;
- tools with broad write permissions or unclear ownership.

## Tool contract baseline

Every tool must document:

1. purpose and owner layer;
2. inputs and outputs;
3. read/write/network permissions;
4. refusal cases;
5. local verification command;
6. redaction rules for secrets and PII;
7. how its output can be consumed by Bolt/Wrench/Gear without moving ownership.

## Consequences

- Bolt may orchestrate these tools, but it must not absorb Wrench inspection, Gear storage, or product UX responsibilities.
- Wrench can inspect outputs and produce evidence reports.
- Gear can store artifacts/reports only through explicit ArtifactRef/ArtifactManifest flows.
- Tooling maturity is measured by evidence, not by breadth of automation.
