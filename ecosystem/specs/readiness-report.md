# Rumble Spec Readiness Report

Status date: 2026-06-30  
Scope: readiness for harness packaging and implementation planning.  
Rule: no product may be `READY_*` without evidence for specs, acceptance tests, security/RGPD, handoff/export path, and Bolt/Wrench/Gear boundaries.

## Status vocabulary

- `BLOCKED` — critical spec/contract/boundary gaps; do not feed harness.
- `WARNING` — substantial specs exist, but critical open questions or contracts remain.
- `READY_FOR_HARNESS_PACKAGE` — enough evidence to produce/validate a planning-only package; implementation still gated.
- `READY_FOR_IMPLEMENTATION_PLANNING` — package can enter Bolt planning after human approval and Wrench/Gear evidence.

## Product readiness matrix

| Product | Status | Evidence files | Blockers | Next action |
| --- | --- | --- | --- | --- |
| `rumble-canvas` | `READY_FOR_HARNESS_PACKAGE` | `specs/rumble-canvas/00-product-charter.md`; `01-personas-and-roles.md`; `02-user-journeys.md`; `04-screens-and-actions.md`; `05-domain-model.md`; `06-data-model.md`; `07-services-and-apis.md`; `08-events-and-workflows.md`; `09-permissions-security-rgpd.md`; `11-acceptance-tests.md`; `specs/shared/contracts/implementation-handoff.v0.1.md`; `specs/harness/fixtures/handoffs/canvas-minimal.valid.json`; `specs/harness/proofs/vertical-p0.proof.json` | Remaining open questions: first canonical deliverable name/scope, solo vs team emphasis, AI assistance boundary, exact Wrench completeness checks. | Use Canvas as the next authorized product to feed the harness; produce a full `SpecPackage` from the existing fixture path, still planning-only. |
| `rumble-note` | `WARNING` | `specs/rumble-note/00-product-charter.md` through `13-gear-memory-boundary.md`; acceptance tests in `11-acceptance-tests.md`; security/RGPD in `09-permissions-security-rgpd.md`; handoff concepts in `05-domain-model.md`, `08-events-and-workflows.md`, `13-gear-memory-boundary.md` | Minimal block model, local-first sync, and concrete `NoteContextExport` contract remain open. | Define `NoteContextExport` and privacy-filtered handoff package before harness readiness. |
| `rumble-lm` | `WARNING` | `specs/rumble-lm/00-product-charter.md` through `15-contracts-v0.1.md`; acceptance tests in `11-acceptance-tests.md`; security/RGPD in `09-permissions-security-rgpd.md`; source-grounded slice in `14-source-grounded-product-slice.md` | Retention defaults, provider policy, citation validation evidence format, and live presence/shared infrastructure remain open. | Define `CitationValidation` + provider/BYOK policy before `READY_FOR_HARNESS_PACKAGE`. |
| `rumble-crew` | `WARNING` | `specs/rumble-crew/00-product-charter.md` through `13-implementation-plan.md`; acceptance tests in `11-acceptance-tests.md`; security/RGPD in `09-permissions-security-rgpd.md` | Agent task lifecycle, runtime identity model, explicit human approval policy, and `AgentTaskRequest` contract remain open. | Contract Bolt-owned task/run request lifecycle before any implementation planning. |
| `rumble-libre-ia` | `BLOCKED` | `specs/rumble-libre-ia/00-product-charter.md` only | Specs are effectively not started: missing roles, journeys, screens/actions, domain/data model, APIs, events, security/RGPD, acceptance tests, and handoff/export path. | Complete the product spec template before any harness package. |
| `rumble-feed-mind` | `READY_FOR_IMPLEMENTATION_PLANNING` | Ecosystem specs: `specs/rumble-feed-mind/00-product-charter.md` through `12-open-questions.md`; contracts: `specs/shared/contracts/curated-item-export.v0.1.md`, `provider-byok-policy.v0.1.md`; export smoke: `specs/rumble-feed-mind/verify_curated_item_export.py`; planning proof: `specs/rumble-feed-mind/verify_handoff_planning.py`; handoff fixture: `specs/harness/fixtures/handoffs/feedmind-curated-export.valid.json`; active repo evidence: `docs/adr/0002-rust-first-product-stack.md`, `0003-stripe-optional-payment-adapter.md`, `0004-auth-boundary-jwt-session-biscuit-delegation.md`, `0005-dependency-advisory-waivers.md`, `docs/readiness-audit.md`, `deny.toml`; tests: Stripe optionality, JWT/Biscuit boundary, BYOK Debug redaction. | Advisory waivers expire 2026-09-30; UI authorized only for MVP Rust-first surfaces and must not expand Stripe/provider-backed AI beyond tested gates. | Start implementation planning for the scoped FeedMind package only; UI product allowed for MVP screens after planning tasks are accepted. |

## Criteria coverage by product

| Criterion | canvas | note | lm | crew | cos | feed-mind |
| --- | --- | --- | --- | --- | --- | --- |
| Mission clear | Pass | Pass | Pass | Pass | Partial | Pass |
| Non-goals | Pass | Pass | Pass | Pass | Missing | Pass |
| MVP slice | Pass | Pass | Pass | Pass | Missing | Pass with warnings |
| Roles | Pass | Pass | Pass | Pass | Missing | Pass |
| Journeys | Pass | Pass | Pass | Pass | Missing | Pass |
| Screens/actions | Pass | Pass | Pass | Pass | Missing | Pass with freeze warning |
| Domain model | Pass | Pass | Pass | Pass | Missing | Pass |
| Data model | Pass | Pass | Pass | Pass | Missing | Pass draft |
| Services/API | Pass | Pass | Pass | Pass | Missing | Pass draft |
| Events/workflows | Pass | Pass | Pass | Pass | Missing | Pass draft |
| Security/RGPD | Pass | Pass | Pass | Pass | Missing | Pass with expiring advisory waivers |
| Acceptance tests | Pass | Pass | Pass | Pass | Missing | Pass draft + smoke |
| Open questions | Pass with non-blocking gaps | Open critical | Open critical | Open critical | Open critical | Non-blocking; waiver expiry remains |
| Handoff/export path | Pass for planning-only Canvas fixture | Conceptual only | Conceptual/contracts emerging | Conceptual only | Missing | Planning-only handoff proof passes |
| Bolt/Wrench/Gear boundaries | Pass | Pass | Pass | Pass | Missing | Export + handoff smoke covers Wrench-like/Gear-like checks |

## Critical open questions by owner layer

| Product | Question | Owner layer | Blocking? |
| --- | --- | --- | --- |
| `rumble-canvas` | Which Wrench completeness checks are mandatory before full package approval? | Wrench | No for minimal harness; yes before implementation planning. |
| `rumble-canvas` | What is the full `SpecPackage` schema beyond the minimal fixture? | Rumble Canvas / Gear Depot seam | Yes before broad package reuse. |
| `rumble-note` | What is `NoteContextExport` and how are private/no_handoff/sensitive blocks excluded? | Rumble Note / Gear Memory | Yes before harness package. |
| `rumble-lm` | What provider/BYOK policy is allowed for source-grounded generation? | Shared Security / Bolt | Yes before package. |
| `rumble-lm` | What is the Wrench `CitationValidation` evidence format? | Wrench Inspect | Yes before implementation planning. |
| `rumble-crew` | What is the Bolt-owned `AgentTaskRequest` lifecycle and execution policy? | Bolt / `cos-matic` | Yes before harness package. |
| `rumble-libre-ia` | What is the product unit and MVP slice? | Product | Yes. |
| `rumble-feed-mind` | How are temporary advisory waivers removed before 2026-09-30? | Product / Security | No for current planning; yes before waiver expiry/release. |

## Products authorized to feed the harness

`rumble-canvas` remains the canonical first harness package path, validated by:

```bash
python3 specs/harness/run_vertical_p0.py --output specs/harness/proofs/vertical-p0.proof.json
```

`rumble-feed-mind` is authorized for planning-only implementation planning for the scoped `CuratedItemExport` / Provider-BYOK hardening package, validated by:

```bash
python3 specs/rumble-feed-mind/verify_curated_item_export.py --output specs/rumble-feed-mind/proofs/curated-item-export.proof.json
python3 specs/rumble-feed-mind/verify_handoff_planning.py --output specs/rumble-feed-mind/proofs/handoff-planning.proof.json
```

Neither product is authorized to execute implementation work from Rumble. Human planning approval remains required before coding tasks are started.
