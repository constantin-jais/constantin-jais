# 04 — Stack validation tooling

Status: P0 specification.

## Goal

Provide a small, local-only toolchain that helps agents and humans challenge a stack before implementation or provisioning.

The tooling must answer:

1. What stack is present or proposed?
2. What evidence exists locally?
3. What risks exist across security, quality, performance, completeness, and sovereignty?
4. Which next action is safe, local, and reversible?

## Operating mode

Default mode is **read-only or dry-run**.

Allowed:

- inspect files and manifests;
- run local checks explicitly configured in the repository;
- produce JSON/Markdown reports;
- recommend ADRs, fixtures, or follow-up spikes.

Forbidden without explicit human approval:

- provisioning cloud resources;
- creating remote apps, databases, buckets, queues, registries, or secrets;
- calling paid providers;
- uploading source manifests, prompts, logs, PII, or secrets;
- mutating git history or remote branches.

## Naming convention

- Tool IDs and JSON reports use `snake_case`, for example `project_status`.
- CLI commands use `kebab-case`, for example `bolt-cosmatic stack project-status`.

## Implementation scope

### P0 implemented

- `project_status`: repository status and local script signals.
- `stack_detect`: stack signal detection and suggested local gates.
- `stack_scorecard`: PASS/WARN/FAIL axes and GO/Conditional GO/SPIKE/WAIT/NO-GO recommendation.
- `dependency_audit`: local manifest signal scan for license/provider/sovereignty risks.
- `local_smoke`: explicit local command runner with refusal screening, timeout, redacted output, and JSON reports.

### P1 planned

- `local_smoke` endpoint/file/assertion checks beyond command exit codes.
- Direct wrappers for `cargo deny`, `cargo audit`, npm/bun audit, and secret scanners.
- Evidence-store integration for last-known verification references.
- Configurable scan bounds and allow/deny policies per repository.

## P0 tools

### `project_status`

Purpose: produce a concise repository status for humans and agents.

Inputs:

- repository path;
- optional list of expected check commands.

Outputs:

- branch and dirty state;
- modified/untracked file summary;
- detected project scripts;
- detected verification evidence when available; durable last-known evidence is P1 evidence-store work;
- warnings for pre-existing local changes;
- recommended next local action.

Refusals:

- refuse to claim green status without command output;
- refuse to summarize secrets or PII from file contents.

### `stack_detect`

Purpose: detect stack signals without installing or running unknown code.

Signals:

- Rust: `Cargo.toml`, workspace, crates, `deny.toml`, migrations;
- Web: `package.json`, `bun.lock`, Astro/Dioxus/Playwright configs;
- DB: SQLx, migrations, PostgreSQL, SQLite, pgvector hints;
- CI: GitHub/GitLab workflows;
- docs: ADRs, README, SECURITY, AGENTS.

Outputs:

- detected components;
- confidence level;
- suggested local verification commands;
- missing gates.

Refusals:

- do not infer maturity from file presence alone;
- do not install dependencies automatically.

### `stack_scorecard`

Purpose: score a proposed or detected stack against the decision axes.

Axes:

1. security;
2. quality;
3. performance;
4. completeness;
5. sovereignty.

Outputs:

- PASS/WARN/FAIL per axis;
- evidence references;
- missing evidence;
- GO / Conditional GO / SPIKE LOCAL / WAIT / NO-GO recommendation.

Refusals:

- refuse GO when evidence is missing for security or sovereignty;
- refuse production-readiness claims from dry-run-only evidence.

### `dependency_audit`

Purpose: consolidate dependency risk evidence from local manifests.

P0 checks:

- local manifest signal scan for license strings and provider SDK names;
- direct dependency on forbidden SaaS/provider SDKs in core paths;
- native TLS/OpenSSL signals in portable Rust paths;
- external font/CDN/tracking signals in web paths.

P1 checks:

- licenses via ecosystem tools such as `cargo deny` or equivalent;
- known vulnerabilities via `cargo audit`, npm/bun audit, or equivalent;
- direct integration with secret scanners such as `gitleaks`.

Outputs:

- dependency findings;
- license summary;
- sovereignty findings;
- waiver candidates, never automatic waivers.

Refusals:

- do not auto-upgrade;
- do not fetch private registries without approval;
- do not upload dependency manifests to SaaS scanners.

### `local_smoke`

Purpose: run small local checks that prove a slice starts and responds as expected.

Inputs:

- explicit command list;
- timeout.

P1 inputs:

- expected endpoints/files/assertions.

Outputs:

- commands executed;
- exit codes;
- captured redacted logs;
- smoke PASS/WARN/FAIL.

Refusals:

- refuse commands requiring remote secrets by default;
- refuse destructive commands;
- refuse to connect to production endpoints unless explicitly allowed.

## Later tools

| Tool | Scope | Gate |
| --- | --- | --- |
| `db_security_check` | Run local DB security checks over migrations/schema fixtures and optional read-only metadata. | PostgreSQL/SQL-backed slice exists. |
| `adr_generate` | Draft ADR text from accepted decisions and evidence. | Human keeps acceptance authority. |
| `deploy_dry_run` | Validate deployment prerequisites without resource creation. | Must prove no provisioning side effect. |

## Shared output envelope

Tools should eventually converge on this report shape:

```json
{
  "tool": "stack_scorecard",
  "version": "0.1",
  "mode": "local_only",
  "target": "repo-or-stack-id",
  "decision": "SPIKE_LOCAL",
  "findings": [
    {
      "axis": "sovereignty",
      "severity": "warn",
      "message": "Provider policy is not instantiated",
      "evidence": ["ecosystem/status.md#current-stack-challenge-decisions"]
    }
  ],
  "next_actions": ["write provider-policy ADR candidate"],
  "redactions_applied": true
}
```

## Acceptance for P0

P0 is complete when:

- each tool has a fixture-backed spec or test plan;
- every tool can run without network and without secrets;
- outputs are safe to paste into issues, PRs, or Bolt planning reports;
- missing evidence is reported as missing, not silently inferred;
- Wrench/Bolt/Gear ownership boundaries remain explicit.

## References

- `../shared/adrs/0034-stack-validation-local-only.md`
- `../shared/adrs/0035-agentic-p0-tooling-backlog.md`
- `../shared/decision-log.md`
- `../../status.md#current-stack-challenge-decisions`
- `../../remaining-work.md#p0b--stack-validation-and-local-only-gates`
