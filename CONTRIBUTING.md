# Contributing to constantin-jais

Thanks for taking the time to contribute.

This project is still early. The most valuable contributions are small, reproducible, and easy to review.

## What helps most right now

- trying the quickstart and reporting friction;
- improving confusing or incomplete documentation;
- adding realistic fixtures;
- improving examples and example outputs;
- adding tests around existing behavior;
- improving error messages;
- documenting known limits.

## Before opening a pull request

Please open an issue first for changes involving:

- architecture or public API changes;
- new dependencies;
- new product scope;
- security-sensitive behavior;
- storage, authentication, authorization, or provider changes;
- behavior that may affect determinism, reproducibility, privacy, or self-hosting.

Small documentation fixes, fixture additions, typo fixes, and focused tests can be opened directly as pull requests.

## Project focus

This repository focuses on ecosystem documentation, forge health, and cross-repository status.

## Project principles

Contributions should preserve these principles:

- deterministic behavior;
- no silent failures;
- explicit boundaries between components;
- self-hostable by default;
- permissive open-source dependencies;
- no unnecessary vendor lock-in;
- clear errors over implicit fallback behavior;
- tests or fixtures for existing behavior before changing it.

## Development

This repository is primarily documentation, specs, or planning material.

Before opening a pull request:

- check links you touched;
- validate fixtures or schemas when scripts are present;
- run the relevant GitHub workflow locally if the repository documents one;
- explain any check you could not run.

For the ecosystem spec contracts, the canonical validation entry point is:

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

Only use that command when the path exists in this repository.

## Pull request guidelines

A good pull request should:

- be small enough to review comfortably;
- explain the problem being solved;
- describe the chosen approach;
- include tests or fixtures when behavior changes;
- avoid unrelated formatting or refactoring;
- document user-facing behavior changes;
- call out any command you could not run.

## Fixtures and examples

Fixtures and examples should be:

- small and explicit;
- deterministic;
- safe to run locally;
- free from secrets or personal data;
- documented enough to explain why the case matters.

Prefer adding a new fixture over changing an existing one unless the existing behavior is wrong.

## Dependency policy

Avoid adding dependencies unless they are clearly justified.

New dependencies must be:

- permissive open source where possible: MIT, Apache-2.0, BSD, ISC, or MPL-2.0 preferred;
- compatible with self-hosting and local development;
- justified in the issue or pull request;
- accepted by the repository license and supply-chain checks when present;
- free from default telemetry, hidden network calls, and unnecessary SaaS coupling.

Discuss before adding:

- LGPL, GPL, or other copyleft dependencies;
- AGPL dependencies;
- source-available or non-OSI licenses such as SSPL or BSL;
- opaque SDKs;
- dependencies that introduce external providers, storage, auth, analytics, telemetry, or hosted services.

Avoid:

- unnecessary vendor lock-in;
- proprietary services by default;
- telemetry by default;
- dependencies that make self-hosting harder;
- services that store project or user data outside expected residency boundaries.

When a dependency is required, explain why a small local implementation is not enough.

## Reporting issues

When reporting a bug, please include:

- expected behavior;
- actual behavior;
- steps to reproduce;
- relevant logs or error messages;
- the command or entry point you used;
- your environment when relevant.

Clear, minimal reproductions are especially helpful.

## Good first contributions

Good first contributions include:

- improving docs;
- adding examples;
- adding fixture cases;
- improving error messages;
- adding tests around existing behavior;
- making quickstart instructions easier to follow.
