# DEPRECATED — migrated to the wrench-db-inspect repository

This prototype was migrated into the standalone repository
`constantin-jais/wrench-db-inspect` on 2026-07-02 (decision D9, ADR-0004 in
that repo), and is no longer the source of truth.

- **Canonical implementation:** `constantin-jais/wrench-db-inspect` (SQL fact
  extraction, rules engine, redaction, reports, gate profiles, CLI — ~2442 LOC,
  24 integration tests, CI green).
- **This directory:** kept for historical reference only. Do not extend it.
  Any change to the SQL security inspector goes to the repository above.

The canonical fixtures now live in `wrench-db-inspect/tests/fixtures`
(vendored so the test suite is self-contained; the ecosystem spec fixtures
remain the contract reference under `ecosystem/specs/wrench-db-inspect`).
