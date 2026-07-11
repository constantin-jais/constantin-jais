# Build Notes Policy

Build notes are not a publishing obligation.

A build note is written only when there is a useful public learning attached to a concrete artifact. The goal is to make decisions, trade-offs, failures, and maturity changes understandable without creating a separate blogging treadmill.

## When to write one

Write a build note for events such as:

- an alpha release;
- a demo milestone;
- a maturity promotion or demotion;
- a major architectural trade-off;
- a meaningful failure, rollback, or incident;
- a dogfooding result that changed the stack.

Do not write a build note just because time passed.

## Where notes live

- **GitHub Releases** own release-specific notes: what shipped, how to try it, checksums/artifacts when relevant, known limitations, and next steps.
- **ADRs** own durable technical decisions: context, options, decision, consequences, and rollback path.
- **Issues / PRs** own implementation discussion and evidence: failing cases, fixtures, test output, review history, and acceptance criteria.
- **rumble-libre-ia** may publish public essays only when the lesson is useful outside one repository.

## Minimal format

```md
## What changed?

## Why?

## Evidence

## What is still missing?
```

Evidence can be a release, commit, PR, issue, CI run, fixture, screenshot, terminal output, or documented demo.

## Non-goals

- no forced cadence;
- no marketing-only posts;
- no duplicated notes across repositories;
- no note without evidence;
- no replacement for ADRs, release notes, issues, or README usage docs.

## Rule of thumb

If the note does not help an external reader understand a concrete change, trade-off, failure, or maturity claim, do not write it yet.
