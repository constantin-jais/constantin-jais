# GitHub Stars Stack Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first complete stack-fit audit table for the 80 public GitHub starred repositories.

**Architecture:** This is a documentation/data artifact, not runtime code. The design spec defines the taxonomy; the implementation produces one stable Markdown table under `ecosystem/specs/shared/` so future diffs can review each repository classification.

**Tech Stack:** Markdown, GitHub public repository metadata captured on 2026-06-30, existing Rumble/Bolt/Wrench/Gear ecosystem docs.

## Global Constraints

- Do not copy upstream code or product language.
- Do not add dependencies during the audit.
- Do not treat popularity as a stack-fit criterion.
- Do not classify a repository as `rebuild` unless it maps to an existing ecosystem need.
- Do not accept AGPL, SSPL, BSL, proprietary, or unclear-license projects as direct dependencies.
- Every classification uses the axes Security, Quality, Performance, Completeness, in that order.
- The output must represent all 80 public starred repositories exactly once.

---

### Task 1: Create The Audit Table

**Files:**
- Create: `ecosystem/specs/shared/github-stars-stack-audit.md`
- Reference: `docs/superpowers/specs/2026-06-30-github-stars-stack-audit-design.md`
- Reference: `ecosystem/overview.md`
- Reference: `ecosystem/specs/shared/shared-capabilities.md`

**Interfaces:**
- Consumes: the taxonomy from `2026-06-30-github-stars-stack-audit-design.md`
- Produces: a Markdown table with columns `repo`, `disposition`, `layer`, `fit`, `risk`, `license`, `language`, `ecosystem_need`, `recommended_action`

- [ ] **Step 1: Create the Markdown artifact**

Create `ecosystem/specs/shared/github-stars-stack-audit.md` with:

```markdown
# GitHub Stars Stack Audit

Date: 2026-06-30
Source: `https://api.github.com/users/constantin-jais/starred?per_page=100`
Scope: 80 public starred repositories returned by the GitHub API.

## Method

This table applies the taxonomy from `docs/superpowers/specs/2026-06-30-github-stars-stack-audit-design.md`.
Disposition values: `adopt`, `rebuild`, `knowledge`, `reject`, `quarantine`.
Layer values: `rumble`, `bolt`, `wrench`, `gear`, `cross-layer`, `outside`.

## Audit Table

| repo | disposition | layer | fit | risk | license | language | ecosystem_need | recommended_action |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
```

- [ ] **Step 2: Add exactly 80 repository rows**

Use the GitHub metadata captured on 2026-06-30. Each row must contain one repository and one primary verdict.

- [ ] **Step 3: Verify row count**

Run:

```bash
grep -E '^\| [^|]+/[^|]+ \|' ecosystem/specs/shared/github-stars-stack-audit.md | wc -l
```

Expected output:

```text
80
```

- [ ] **Step 4: Verify no ambiguous primary verdicts**

Run:

```bash
rg -n ' or |maybe|probably|TBD|TODO|FIXME|\?\?' ecosystem/specs/shared/github-stars-stack-audit.md
```

Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add ecosystem/specs/shared/github-stars-stack-audit.md docs/superpowers/plans/2026-06-30-github-stars-stack-audit.md
git commit -m "docs: audit github stars for stack fit" -- ecosystem/specs/shared/github-stars-stack-audit.md docs/superpowers/plans/2026-06-30-github-stars-stack-audit.md
```

### Task 2: Verify The Audit Against The Design

**Files:**
- Read: `docs/superpowers/specs/2026-06-30-github-stars-stack-audit-design.md`
- Read: `ecosystem/specs/shared/github-stars-stack-audit.md`

**Interfaces:**
- Consumes: completed audit table from Task 1
- Produces: verification evidence for final response

- [ ] **Step 1: Verify hard blocker visibility**

Run:

```bash
rg -n 'AGPL-3.0|GPL-3.0|NOASSERTION|quarantine|reject' ecosystem/specs/shared/github-stars-stack-audit.md
```

Expected: matches for non-permissive or unclear licenses and hard-risk rows.

- [ ] **Step 2: Verify high-value follow-up rows exist**

Run:

```bash
rg -n 'eclipse-biscuit/biscuit|Goldziher/ai-rulez|xberg-io/xberg|siyuan-note/siyuan|elder-plinius/L1B3RT4S' ecosystem/specs/shared/github-stars-stack-audit.md
```

Expected: five matches.

- [ ] **Step 3: Verify git state**

Run:

```bash
git status --short
git show --stat --oneline --name-only HEAD
```

Expected: the new commit contains only the plan and audit table. Pre-existing unrelated WIP may remain visible in `git status --short`.
