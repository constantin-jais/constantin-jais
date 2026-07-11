# ADR 0042 — Clean-room adoption from private studies

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Related: ADR 0038, ADR 0040

## Context

Private technical studies may identify useful behavior in systems whose source, prompts, schemas, fixtures and content must not enter Libre IA repositories. A behavioral catalogue is not permission to transliterate implementation details.

## Decision

Adoption from a private study is clean-room:

1. implementation consumes only an autonomous behavior/invariant specification;
2. contracts and names are designed for the destination domain;
3. fixtures are entirely synthetic;
4. source code, prompts, schemas, migrations, UI components and textual corpus from the studied system are not copied or transliterated;
5. provenance records the autonomous specification and destination decisions, not private source excerpts;
6. reviewers check suspicious similarity before merge;
7. private study directories and hashes are never published as product runtime inputs.

## Acceptance criteria

Every adoption PR identifies its new contract, synthetic fixtures, license/SBOM evidence and rollback. A reviewer can understand and test the behavior without access to the private study.
