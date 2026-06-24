# Harness Readiness Plan

Status: P0 before Rumble product development.

## Goal

Before building the Rumble products, the harness must prove it can receive structured product intent, validate it, refuse unsafe inputs, and produce a planning-only implementation plan.

## Target Flow

```text
Rumble spec package
→ ImplementationHandoff v0.1
→ cos-matic validate
→ cos-matic dry-run plan
→ Wrench inspection reports
→ Gear artifact/provenance references
→ human approval
→ only then implementation work
```

## P0 Work Items

| Priority | Item | Owner layer | Output |
| --- | --- | --- | --- |
| P0 | `ImplementationHandoff v0.1` contract | Shared / Bolt seam | `specs/shared/contracts/implementation-handoff.v0.1.md` |
| P0 | Handoff validator | Bolt / `cos-matic` | CLI validates/refuses payloads |
| P0 | Dry-run planner | Bolt / `cos-matic` | Planning report, no execution |
| P0 | Minimal fixtures | Shared specs | valid/invalid JSON examples |
| P0 | Traceability checker | Wrench Inspect | coverage report |
| P0 | Waiver policy checker | Bolt + Wrench | accepted/refused gates |
| P0 | SpecPackage artifact rules | Gear candidate | hash/provenance/export rules |

## Definition of Ready for Rumble Development

A Rumble product can enter implementation only when:

- its MVP slice is specified;
- its package/handoff/export path is defined;
- its PII/RGPD classification is explicit;
- its events are named;
- its acceptance tests exist;
- shared capability candidates are logged;
- `cos-matic` can validate or refuse its handoff/export input;
- no infrastructure need is hidden inside the product.

## Suggested Build Order

1. Implement `cos-matic handoff validate` as a no-op validator.
2. Add fixtures for valid, warning, and invalid handoffs.
3. Implement dry-run planning output, including machine-readable JSON.
4. Add Wrench inspection for traceability and waiver coverage.
5. Add Gear artifact/provenance references after package format stabilizes.
6. Only then start UI/product implementation.

## Current CLI Smoke Targets

```bash
cosmatic handoff validate specs/harness/fixtures/handoffs/canvas-minimal.valid.json
cosmatic handoff validate specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run --json
```

Warning fixtures should exit successfully but emit warnings. Invalid fixtures should fail.
