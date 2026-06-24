# Events and Workflows — rumble-canvas

Status: Draft / MVP package+handoff slice.

## Event Rules

- Events are append-only audit facts.
- Events reference actor, target, timestamp, and payload hash/reference when relevant.
- Events must not include secrets or unnecessary PII.
- System-derived reports should be recomputable from canonical state and events.

## Core Events

| Event | Producer | Consumers | Audit relevance |
| --- | --- | --- | --- |
| `spec_workspace_created` | WorkspaceService | UI, activity log | Yes |
| `spec_section_revision_created` | SpecSectionService | Review, package readiness | Yes |
| `spec_section_marked_ready_for_review` | ReviewService | Review queue | Yes |
| `section_approved` | ReviewService | Package readiness | Yes |
| `waiver_accepted` | WaiverService | Package readiness, handoff validation | Yes |
| `traceability_link_created` | TraceabilityService | Wrench inspection, readiness | Yes |
| `spec_package_created` | PackageService | Export/handoff | Yes |
| `spec_package_approved` | PackageService | HandoffService | Yes |
| `implementation_handoff_created` | HandoffService | Bolt adapter | Yes |
| `implementation_handoff_validated` | HandoffService / cos-matic | UI, audit | Yes |
| `bolt_handoff_submitted` | HandoffService | Bolt | Yes |
| `bolt_handoff_failed` | HandoffService | UI, audit | Yes |

## Workflow: Package Approval

1. Owner opens package readiness.
2. System computes readiness:
   - required sections approved;
   - traceability present;
   - no blocking questions without waiver;
   - no high/critical risks without waiver;
   - high/critical waivers have distinct Owner + Reviewer approval.
3. Owner resolves or waives blockers.
4. System creates `PackageReadinessSnapshot`.
5. Owner approves package.
6. System computes `package_hash`.
7. Package becomes immutable.

Failure:

- blocker present → package approval refused;
- hash computation fails → package remains draft;
- section changes after package approval → package unchanged, new draft revision created.

## Workflow: Implementation Handoff

1. Owner/delegated Editor selects approved package.
2. HandoffService prepares canonical payload `canvas.bolt_handoff.v0.1`.
3. Payload includes package, traceability, waivers, risks, open questions, capability candidates, constraints.
4. Execution policy is forced planning-only.
5. Payload hash is computed.
6. `cosmatic handoff validate` validates locally.
7. If clean, user may submit to Bolt planning.
8. `cosmatic handoff plan --dry-run` produces planning report.
9. No execution happens.

## Workflow: Wrench Inspection

Target future command:

```bash
wrench-inspect handoff inspect handoff.json
```

Checks:

- traceability coverage;
- waiver validity;
- PII classification presence;
- shared capability owner assignment;
- package/handoff consistency.

Temporary location: `cos-matic handoff validate` until `wrench-inspect` is active.

## Workflow: Shared Capability Extraction

1. Canvas detects repeated or cross-layer need.
2. Editor creates `CapabilityCandidate`.
3. Reviewer challenges owner layer.
4. Candidate enters package/handoff.
5. Bolt dry-run plan includes `shared_capability_extraction_review`.
6. Human decides whether to keep local, extract to shared Rumble, Bolt, Wrench, or Gear.

## Retry / Idempotency

- Handoff identity: `handoff_id + payload_hash`.
- Retrying same handoff must not create duplicate Bolt planning requests.
- Changing package content requires new package hash and handoff hash.
