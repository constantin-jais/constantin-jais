# Contract — SpecPackage v0.1

Status: Draft / P0 harness dependency.  
Schema: `spec-package.v0.1.schema.json`.

## Purpose

`SpecPackage` is the immutable product-approved bundle that a Rumble product exports before an `ImplementationHandoff`.

It proves that product intent is explicit, traceable, reviewed, and safe to submit to Bolt for planning-only validation. It does **not** authorize implementation execution.

## Boundary

| Concern | Owner |
| --- | --- |
| Product semantics and approval UX | Rumble product |
| Package hash, manifest, artifact identity | Gear Depot |
| Source/provenance references | Gear Memory |
| Validation and planning request | Bolt / `cos-matic` |
| Inspection reports | Wrench Inspect |

## Non-Negotiable Rules

1. A package is immutable once approved/exported.
2. A package contains references and safe summaries, not secrets or raw private data.
3. Package approval is distinct from execution approval.
4. A package may feed only planning-only `ImplementationHandoff` until Bolt execution gates are separately approved.
5. Gear owns artifact/provenance substrate; Rumble owns product meaning.

## Required Shape

```json
{
  "format": "rumble.spec_package.v0.1",
  "package_id": "package-demo",
  "origin_product": "rumble-canvas",
  "workspace_id": "workspace-demo",
  "version": "0.1.0",
  "created_by": "actor-ref",
  "created_at": "2026-06-30T00:00:00Z",
  "approved_by": ["actor-ref"],
  "approval_status": "approved",
  "items": [],
  "traceability_snapshot": {},
  "readiness_snapshot": {},
  "constraints": {},
  "artifact_ref": {},
  "provenance_ref": {},
  "wrench_report_refs": []
}
```

## Required Gates

A package is not handoff-ready if:

1. `approval_status` is not `approved`.
2. `items` is empty.
3. Any item lacks `section_id`, `revision_id`, `content_hash`, `privacy_classification`, or `approval_status`.
4. Any item has `privacy_classification = no_handoff`.
5. Any `sensitive` item lacks explicit inclusion reason and approval.
6. Traceability coverage is missing for MVP-required journeys/screens/actions/acceptance tests.
7. Blocking questions or high/critical risks are present without accepted waiver references.
8. Gear `ArtifactRef` / `ProvenanceRecord` references are missing or malformed.
9. Wrench reports contain critical findings.
10. Any field contains secret-like keys or raw secret values.

## Relationship to ImplementationHandoff

`ImplementationHandoff.package` is a projection of `SpecPackage` identity:

- `package_id` = `SpecPackage.package_id`;
- `version` = `SpecPackage.version`;
- `package_hash` = stable hash of canonical `SpecPackage` JSON;
- `artifact_reference_id` = Gear Depot artifact id when available;
- `items` = package item revision references.

The handoff may include summarized context, but the package remains the approved product artifact.

## Audit Requirements

Persist or emit safe refs for:

- actor refs for creation/approval;
- timestamps;
- package hash;
- item revision hashes;
- traceability/readiness snapshot hashes;
- Wrench report refs;
- Gear artifact/provenance refs;
- approval status and waiver refs.

## CLI / Smoke Target

P0 may validate `SpecPackage` indirectly through `ImplementationHandoff`. A later CLI should expose:

```bash
cosmatic package validate <spec-package.json> --json
wrench-inspect package inspect <spec-package.json> --json
```

No package command may execute implementation work.
