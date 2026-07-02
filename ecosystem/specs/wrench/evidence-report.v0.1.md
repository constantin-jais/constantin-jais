# Wrench EvidenceReport v0.1

Status: Draft / fixture-backed contract  
Format: `wrench.evidence_report.v0.1`  
Schema: [`evidence-report.v0.1.schema.json`](evidence-report.v0.1.schema.json)

## Purpose

`EvidenceReport` is the common Wrench envelope consumed by Bolt/Gear/Rumble references. It lets domain inspectors keep rich local reports while exposing a safe, hash-backed, agent-readable summary.

## Ownership

- Wrench produces inspection reports and evidence envelopes.
- Bolt consumes evidence refs and statuses for gates; it does not store report bodies.
- Gear may store or transport evidence artifacts when a durable artifact path is needed.
- Portal still owns token generation and contrast report production.

## Shape

A report contains:

- `format`: `wrench.evidence_report.v0.1`;
- `report_id`: deterministic report identifier derived from the source report hash;
- `producer`: emitting tool name/version;
- `subject`: inspected target, such as `portal_ui`;
- `status`: `passed`, `warning`, or `failed`;
- `summary` and safe `findings`;
- `checks`: normalized gate-friendly check outcomes;
- `evidence_refs`: hash-backed file/report references;
- `source_report`: typed inspector-specific report body plus SHA-256 hash;
- `next_actions`: deterministic remediation hints.

## Current proof

The first fixture is produced by:

```bash
cd wrench-inspect
cargo run -- portal inspect tests/fixtures/portal/rumble-lm-ui.valid --evidence
```

This proves the Rumble LM UI Portal fixture can be represented as a Wrench evidence envelope without moving Portal generation or Bolt gate ownership into Wrench.
