# rumble-lm Pilot — Open Findings

No real product run yet. The repository currently contains only specs and sanitized example schemas.

## Input blockers

| ID | Status | Owner | Description | Next action |
| --- | --- | --- | --- | --- |
| LM-PILOT-INPUT-001 | open | product/DB owner | Sanitized PostgreSQL schema dump is not present. | Provide `inputs/schema.sql` or run `SCHEMA_DUMP=/path/to/schema.sql ./run-pilot.sh`. |
| LM-PILOT-INPUT-002 | open | product/DB owner | Product DB security manifest is not present. | Provide `inputs/security-manifest.json`, seeded from `../../examples/security-manifest.rumble-lm.example.json`. |
| LM-PILOT-INPUT-003 | open | product/DB owner | Actual app/readonly/migration role names are not confirmed. | Confirm in manifest before release-profile audit. |
| LM-PILOT-INPUT-004 | open | product/security owner | Embedding/vector tables for MVP are not confirmed. | Mark absent, tenant-scoped, or justified public in manifest. |
| LM-PILOT-INPUT-005 | open | product/DB owner | Multi-hop tenant derivations may exist in source/activity option paths. Inspector now supports conservative FK-chain + policy-chain proofs. | Run real schema; add fixture if the product uses a safe SQL form not yet recognized. |

## After first run

For every finding, add:

- report path and timestamp;
- `rule_id`;
- subject type/name only — no raw SQL, no row data;
- gate profile and decision;
- triage: true positive / false positive / product decision / parser limitation;
- owner and target date;
- remediation or bounded waiver reference.
