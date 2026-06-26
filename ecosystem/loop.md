# Self-Improving Process Loop

This ecosystem is a personal forge for learning, reliable process design, and robust tools. The loop below is the intended center of gravity.

```text
idea → specification → inspection → planning → controlled execution → evidence → memory → improvement
```

## Target loop

```text
An idea appears in rumble-note
→ it becomes a discussion/spec in rumble-canvas
→ wrench-inspect critiques the spec
→ cos-matic produces a gated plan
→ implementation creates artifacts and provenance
→ gear-memory keeps decisions, refs, events, and proofs
→ gear-depot verifies and retains artifacts
→ gear-cable makes release/distribution reproducible when needed
→ rumble-cos explains what was learned
→ the next idea starts from better memory and better contracts
```

## Layer responsibilities in the loop

| Step | Primary owner | Supporting layers | Boundary |
| --- | --- | --- | --- |
| Idea capture | `rumble-note` | Gear Memory later | Notes own private UX; Gear only indexes explicit exports. |
| Spec shaping | `rumble-canvas` | Shared specs, Gear artifacts | Canvas owns product/spec semantics; it does not execute. |
| Inspection | `wrench-inspect`, `wrench-db-inspect`, `wrench-loader` | Gear artifacts/memory | Wrench produces evidence; it does not own durable truth. |
| Planning | `cos-matic` | Wrench evidence, Gear refs | Bolt plans and refuses; Rumble approves; Gear stores refs. |
| Controlled execution | `cos-matic` after gates | Rumble approvals, Wrench checks, Gear storage | Execution must be bounded, auditable, and fail closed. |
| Evidence | Wrench + Bolt | Gear Depot/Memory | Evidence travels as refs/artifacts, not raw secrets or PII. |
| Memory | `gear-memory` | Rumble exports, Wrench outputs | Gear stores/indexes references and provenance, not product meaning. |
| Artifact trust | `gear-depot` | Gear Cable, Rumble exports, Wrench reports | Depot owns manifests, checksums, policy, revocation. |
| Release | `gear-cable` | Gear Depot | Cable owns release plans and install floors, not runtime behavior. |
| Teaching/publication | `rumble-cos` | All layers | COS explains lessons; it is not the workflow backend. |

## Missing chain links

| Link | Current state | Needed next |
| --- | --- | --- |
| `rumble-note` → `rumble-canvas` | Conceptual/spec-only. | Define `NoteContextExport` with privacy filters and no-handoff blocks. |
| `rumble-canvas` → Wrench critique | Minimal readiness/spec checks exist; generic `wrench-inspect` repo not present. | Define shared `EvidenceReport` and spec completeness checks. |
| Wrench critique → `cos-matic` plan | Planning bundle and handoff contracts exist. | Keep dry-run/refusal path green; add real Wrench evidence refs. |
| `cos-matic` plan → controlled execution | P0 is planning-only by design. | Add approval/auth/runtime policy only after gates are trusted. |
| Execution → Gear evidence | Gear contracts exist; integration not yet complete. | Store `ArtifactRef`, `ProvenanceRecord`, and `EventLogEntry` from real runs. |
| Wrench Loader → Gear Memory | Contracts exist separately. | Implement `GearSourceCandidate` to `SourceRef` ingestion path. |
| Gear Depot ↔ Gear Cable | Contracts exist separately. | Connect release plans to `ArtifactManifest` verification. |
| Learnings → `rumble-cos` | Public site usable. | Add lightweight publishing workflow for project lessons and evidence summaries. |

## Quality gates for the loop

A loop increment is acceptable only if it leaves at least one durable proof:

- a contract fixture;
- a green test or validation command;
- a Wrench evidence report;
- a Gear artifact/provenance reference;
- an ADR or decision-log entry;
- a public/private learning note that improves the next iteration.

## Non-goals

- Ranking Rumble projects by commercial potential.
- Treating every idea as a product roadmap commitment.
- Moving all logic into one platform repo.
- Letting Rumble products own generic ingestion, orchestration, memory, or artifact trust.
- Letting Gear become product workflow logic.
- Letting Wrench become durable truth.
- Letting Bolt execute without explicit gates and evidence.
