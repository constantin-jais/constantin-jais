# Open Questions — rumble-crew

## Scope

This file centralizes remaining open questions after the MVP spec decisions.

Status values:

- `Open` — unresolved and potentially blocking later design.
- `Proposed` — recommended direction exists, not accepted.
- `Accepted` — decision made; kept here for visibility until implemented.
- `Deferred` — intentionally post-MVP.

---

## High-Impact Open Questions

| Question | Impact | Owner | Status | Current direction |
| --- | --- | --- | --- | --- |
| What exact authentication mechanism secures `cos-matic` inbound events? | High | Security/Bolt | Open | Service auth with rotation, replay protection, source_event_id, timestamp freshness. |
| Should approval decisions be pushed only, or should `cos-matic` also poll? | High | Bolt/API | Proposed | Push idempotent + retry in MVP; polling optional later. |
| Should critical audit append-only be DB-enforced or application-enforced? | High | Architecture/Data | Proposed | DB-enforced for critical events when possible; app-enforced fallback only if documented. |
| What is the default raw runtime log TTL? | High | Security/Product | Proposed | 7 days hosted/multi-user; configurable by owner; no indefinite default. |
| What redaction scanner is sufficient before privileged raw log display? | High | Security | Open | Baseline regex/entropy/key-pattern scanner; improve with Wrench/Gear later. |
| What threshold triggers migration from local evidence to Gear? | High | Architecture/Gear | Open | Volume, retention, multi-product reuse, provenance need, or maturity milestone. |
| Is `rumble-crew` required to support local-first mode? | Medium | Product/Architecture | Proposed | Not full local-first MVP; read-only cached degraded mode only. |

---

## Product Decisions Already Accepted

| Decision | Status | Notes |
| --- | --- | --- |
| MVP may request real execution through `cos-matic` | Accepted | Requires `execution_mode=trusted_execution`; Rumble never executes directly. |
| Default completion is review-first | Accepted | Auto-close is explicit policy exception. |
| Auto-close after run success is allowed only for low-risk auto-closable tasks | Accepted | Requires trusted run, no blockers, no approvals, no stale context. |
| Local evidence storage is fallback only | Accepted | Must be extractable toward Gear. |
| Skill cards may be local or `cos_matic` sourced | Accepted | Need sync/drift fields. |
| Current state mutable + critical activity append-only | Accepted | Event sourcing not required for all state. |
| Approval types limited to start/scope/risk/completion | Accepted | Simple risk rules; no workflow builder MVP. |
| Approval sync is push idempotent + retry + visible `sync_failed` | Accepted | Polling may be added later. |
| Raw logs allowed as privileged sensitive data | Accepted | Disabled by default, audited, TTL-limited, non-indexed. |
| Parallel runs not default MVP | Accepted | Post-MVP policy only. |
| Failed run requires recovery decision | Accepted | No automatic task failure. |

---

## Product / UX Questions

| Question | Impact | Status | Current direction |
| --- | --- | --- | --- |
| Should failed/cancelled tasks show as columns or filters? | Medium | Proposed | Collapsed lane or filter by default. |
| Should Review Queue be separate or board view only? | Medium | Accepted direction | Separate top-level entry for decision focus. |
| Should `Agent Supervisor` and `Reviewer` be separate in small teams? | Medium | Proposed | Same human may hold both roles; policy can require separation for high risk. |
| Should Contributors see all agent/skill metadata? | Medium | Proposed | Visible summary; permission-sensitive runtime details redacted. |
| Should raw logs ever appear inline in timeline? | High | Proposed | No. Timeline only metadata/reference/access event. |
| Should task reopen after done/cancelled be MVP? | Medium | Deferred | Owner-only explicit reopen post-MVP. |

---

## Domain / Data Questions

| Question | Impact | Status | Current direction |
| --- | --- | --- | --- |
| Should `Task` and `AgentTask` be separate? | High | Accepted | One `Task` with assignments/run refs. |
| Should parallel runs be modeled now in schema? | Medium | Proposed | Schema can support prior/multiple runs; policy allows one active run by default. |
| Should `RuntimeLog` raw payload live in DB or object/blob store? | High | Proposed | Prefer object/blob/external/Gear ref; DB metadata only. |
| Should local evidence blobs be encrypted at rest in all deployments? | High | Proposed | Required for hosted/multi-user; strongly recommended for self-hosted. |
| How are task context version hashes computed? | High | Open | Need canonical serialization rules before implementation. |
| Should redaction be reversible for privileged users? | High | Open | Prefer store raw separately with privileged access; redacted view irreversible. |

---

## API / Integration Questions

| Question | Impact | Status | Current direction |
| --- | --- | --- | --- |
| Exact `cos-matic` run request response schema | High | Open | Current spec has v0.1 request; response should be formalized with Bolt. |
| Does `cos-matic` acknowledge approval decisions synchronously? | High | Open | API supports sync failure and retry. |
| Should `cos-matic` send raw logs or only references? | High | Proposed | Prefer references; Rumble stores metadata/ref, not large raw bodies. |
| How does capability sync detect drift? | Medium | Proposed | `capabilities_hash` from source; compare on sync. |
| Should inbound events be signed? | High | Proposed | Yes if feasible; otherwise mTLS/service token + replay protection minimum. |
| How are late events handled after task terminal decision? | High | Proposed | Record in run timeline; do not mutate terminal task state without explicit reopen/superseding decision. |

---

## Security / RGPD Questions

| Question | Impact | Status | Current direction |
| --- | --- | --- | --- |
| Default data residency requirement for hosted deployments | High | Proposed | EU/local-first where possible; self-hostable core truth. |
| Can normal audit export include redacted logs? | Medium | Proposed | Include summaries/metadata only, no raw body. |
| Can a user request erasure of audit actor references? | High | Open | Support redaction/anonymization where compatible with legitimate audit retention. |
| Should raw log access require reason text? | Medium | Proposed | Yes for privileged_raw in hosted/multi-user mode. |
| Should owner be able to view all raw logs? | High | Proposed | Only if raw logs enabled and owner has `logs:raw:read`; permission not implicit in all deployments. |

---

## Post-MVP Deferred Questions

| Question | Reason for deferral |
| --- | --- |
| Workflow builder for approvals | Too broad; risks generic PM/workflow product. |
| Advanced dependency graph | Not needed for first agentic supervision slice. |
| Parallel run policies | Requires conflict/write safety model. |
| Organization-wide policy inheritance | Needs shared identity/org model. |
| Full local-first editing/sync | Complex with trusted execution and runtime events. |
| Marketplace/install flow for agents/tools | Out of MVP; skill cards are metadata/projection. |
| Raw log analytics/search | High security risk; raw logs intentionally non-indexed. |

---

## Questions to Resolve Before Implementation Planning

1. Integration authentication mechanism for `cos-matic` events and callbacks.
2. Canonical task context hashing/versioning algorithm.
3. Raw log storage location and TTL default.
4. DB-level append-only enforcement for critical `activity_events`.
5. Gear evidence extraction target format.
6. Exact `cos-matic` v0.1 response schemas.
7. Redaction scanner baseline.

---

## Questions That Can Wait Until After First MVP Slice

1. Parallel run policy details.
2. Full Gear migration automation.
3. Rich audit export formats beyond JSON/Markdown/bundle.
4. Local-first collaboration mode.
5. Organization policy templates.
6. Advanced capability registry ownership.
