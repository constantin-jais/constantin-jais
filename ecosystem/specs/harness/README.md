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
→ registry-backed human approval
→ only then implementation work
```

## P0 Doctrine

Bolt P0 is hardened inside `cos-matic`; no separate `bolt-runner` exists until a runtime/service boundary becomes impossible to hold in the current harness.

References:

- [`01-bolt-cosmatic-hardening.md`](01-bolt-cosmatic-hardening.md)
- [`02-bolt-evidence-gated-planning.md`](02-bolt-evidence-gated-planning.md)
- [`03-rumble-delivery-maturity.md`](03-rumble-delivery-maturity.md)
- [`04-stack-validation-tooling.md`](04-stack-validation-tooling.md)
- [`cosmatic-planning.v0.1.schema.json`](cosmatic-planning.v0.1.schema.json)
- [`human-approval.v0.1.schema.json`](human-approval.v0.1.schema.json)
- [`approval-key-registry.v0.1.schema.json`](approval-key-registry.v0.1.schema.json)
- [`rumble-delivery-maturity.v0.1.schema.json`](rumble-delivery-maturity.v0.1.schema.json)

Bolt centralizes the agentic primitives that Rumbles must not reimplement locally:

```text
handoff → validate → planning_run → plan/refusal → gate → evidence_ref → audit
```

P0 remains planning-only. Any implementation execution requires a later explicit human gate.

Rumble delivery maturity is also contract-first: commercializable, multi-platform ambition is represented as verifiable maturity claims, not as business prioritization.

## P0 Work Items

| Priority | Item | Owner layer | Output |
| --- | --- | --- | --- |
| P0 | `ImplementationHandoff v0.1` contract | Shared / Bolt seam | `specs/shared/contracts/implementation-handoff.v0.1.md` |
| P0 | Bolt/cos-matic hardening doctrine | Bolt / `cos-matic` | `specs/harness/01-bolt-cosmatic-hardening.md` |
| P0 | Handoff validator | Bolt / `cos-matic` | CLI validates/refuses payloads |
| P0 | Dry-run planner | Bolt / `cos-matic` | `PlanReport`, no execution |
| P0 | Evidence-gated planning contract | Bolt / `cos-matic` | `cosmatic.planning_bundle.v0.1` schema + fixtures |
| P0 | Minimal fixtures | Shared specs | valid/invalid JSON examples |
| P0 | Refusal model | Bolt / `cos-matic` | structured reason codes, findings, remediation |
| P0 | Gate model | Bolt / `cos-matic` | typed gates for human approval, sovereignty, Wrench reports, artifact integrity |
| P0 | Traceability checker | Wrench Inspect | coverage report |
| P0 | Waiver policy checker | Bolt + Wrench | accepted/refused gates |
| P0 | SpecPackage artifact rules | Gear candidate | hash/provenance/export rules |
| P0 | Rumble delivery maturity claims | Harness / Bolt consumes | `rumble.delivery_maturity.v0.1` schema + valid/invalid fixtures |
| P0 | Stack validation tooling spec | Harness / Bolt + Wrench seam | `project_status`, `stack_detect`, `stack_scorecard`, `dependency_audit`, `local_smoke` contracts |

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
wrench-inspect handoff inspect specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run
cosmatic handoff plan specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run --json
```

Maturity contract smoke fixtures:

```bash
python3 specs/validate_spec_schemas.py
```

Recommended pre-execution evidence flow:

```text
1. cosmatic handoff validate --json   # Bolt boundary refusal/safety gate
2. wrench-inspect handoff inspect --json # Wrench quality/compliance evidence
3. cosmatic handoff plan --dry-run --json # Bolt planning report, no execution
```

## Canonical Vertical P0 Proof Command

From the ecosystem repository root:

```bash
python3 specs/harness/run_vertical_p0.py --output specs/harness/proofs/vertical-p0.proof.json
```

The proof must show:

- `validate.success: true`;
- `inspect.no_critical_finding: true`;
- `plan.dry_run_only: true`;
- `gear_contract_validation.success: true`;
- `human_approval_placeholder.required: true` with no execution performed.

Warning fixtures should exit successfully but emit warnings. Invalid fixtures should fail once the corresponding Bolt P0 refusal code is implemented.

New contract-first fixtures may temporarily expose `cos-matic` gaps; that is intentional evidence for the next hardening implementation slice, not permission to weaken the contract.
