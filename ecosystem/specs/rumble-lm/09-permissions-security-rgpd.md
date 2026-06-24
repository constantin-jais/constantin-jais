# Permissions, Security, and RGPD — rumble-lm

Status: Draft.

## Security Goals

- Prevent unauthorized access to sessions, sources, responses, summaries, and exports.
- Preserve participant privacy and configured anonymity.
- Keep generated content auditable and source-grounded.
- Avoid leaking personal data through logs, analytics, exports, or summaries.
- Remain self-hostable and compatible with sovereign infrastructure.

## Roles

- `Admin`: workspace governance and policy.
- `Facilitator`: session owner/operator.
- `Participant`: session contributor.
- `Learner`: persona only, not an MVP ACL role.

## Permission Matrix

| Action | Admin | Facilitator | Participant |
| --- | --- | --- | --- |
| Create workspace session | Optional policy | Yes | No |
| View session metadata | Yes | Own/assigned | Joined/current only |
| View session content | Policy-based | Own/assigned | Published participant view only |
| Import sources | Policy-based | Yes | No |
| Generate activities | No by default | Yes | No |
| Validate citations | No by default | Yes | No |
| Start/end live session | No by default | Yes | No |
| Join live session | No | Optional as participant | Yes if invited/allowed |
| Submit response | No | Only if also participant | Yes |
| View individual responses | Policy-based | According to visibility settings | Own response only unless shared |
| View aggregates | Policy-based | Yes | If facilitator publishes |
| Generate summary | No by default | Yes | No |
| Publish participant summary | No by default | Yes | No |
| Export session | Policy-based | Yes if allowed | Download/view only if shared |
| Archive/delete session | Yes | Own session if policy allows | No |
| Manage retention policy | Yes | No | No |

## Authorization Rules

- Every request is scoped by `workspaceId` and role assignment.
- Session ownership and assignment are checked for facilitator actions.
- Participant access is scoped to the specific session and current published state.
- Admin content access must be explicit; admin metadata access does not imply automatic content access.
- Generated content publication requires facilitator validation, not just service success.

## Sensitive Data

### Personal Data

- participant display names;
- actor references;
- free-text responses;
- attendance/presence timestamps;
- quiz scores if enabled;
- summaries that quote or paraphrase participants;
- source excerpts containing personal data.

### Potentially Sensitive Organizational Data

- imported sources;
- session objectives and decisions;
- internal discussions;
- exported summaries and audit bundles.

## Privacy Rules

- Show response visibility/anonymity rules before response submission.
- Snapshot visibility at submission time.
- Do not retroactively deanonymize responses.
- Individual analytics are off by default in MVP.
- Participant-facing summaries must not reveal private responses beyond policy.
- Free-text response content must not be logged in audit metadata.

## Anonymity Modes

| Mode | Meaning | MVP Notes |
| --- | --- | --- |
| Named | Facilitator can see participant identity | Default for controlled training if configured |
| Anonymous to participants | Facilitator sees identity, peers see aggregate/anonymous | Common MVP default |
| Anonymous to facilitator | Facilitator sees aggregate/anonymous only | Harder; requires stronger guarantees |
| Aggregate only | No individual response display after collection | Strong privacy option |

MVP recommendation: support `Named`, `Anonymous to participants`, and `Aggregate only`. Treat `Anonymous to facilitator` as post-MVP unless architecture can guarantee it.

## RGPD Lawful Basis Candidates

Depends on deployment context:

- training/workshop within organization: legitimate interest or contract;
- education context: public interest/contract/consent depending controller;
- open/public session: consent may be required.

The product must allow the deploying organization to configure notices, retention, and export rules. Specs should not assume one universal lawful basis.

## Data Subject Rights

Support workflows for:

- access to own participant data;
- correction of display name/profile where applicable;
- deletion/anonymization request for participant identity and responses;
- export of own data where appropriate;
- retention expiry.

## Retention

- Workspace-level default retention.
- Session-level override only if policy allows.
- Separate retention for raw responses, summaries, exports, and audit events.
- Expired exports should be revoked or removed according to policy.

## Export Security

- Exports must declare audience and included data classes.
- Export preview must show privacy blockers.
- Export artifacts should include checksum/provenance where available.
- Participant exports should exclude facilitator-only notes and private responses.
- Admin audit exports are high-sensitivity artifacts.

## Audit Requirements

Audit events required for:

- role/permission changes;
- session lifecycle transitions;
- source import/remove;
- generated content requests;
- citation validation/rejection;
- live start/close;
- summary validation/publication;
- exports and revocations;
- deletion/anonymization actions.

Audit logs must not contain secrets, raw source content, or raw response content unless explicitly designed as secure audit artifacts.

## Threat Model Notes

| Threat | Risk | Mitigation |
| --- | --- | --- |
| Participant accesses unpublished activities | Medium | State and role checks on participant endpoints |
| Facilitator accidentally leaks private responses in summary | High | Privacy scanner/gate before publish/export |
| Generated unsupported claim appears authoritative | High | Citation-required gating and unsupported markers |
| Admin overreach into sensitive content | Medium | Separate metadata/content access policies |
| Response content leaked via logs | High | Structured logs without content payloads |
| Join link shared publicly | Medium | Expiry, access mode, optional invite/auth requirements |
| Source contains personal/confidential data | High | Provenance, policy, retention, export controls |
| Live transport spoofing | Medium | Authenticated participant session tokens and server-side activity state |

## Security Controls

- CSRF protection for browser-authenticated writes.
- Session-scoped participant tokens for guest flows.
- Rate limiting on join, submit response, imports, generation, exports.
- Server-side validation of activity response schemas.
- Access checks on every object by workspace and session.
- No client-side trust for live state or visibility rules.
- Sanitization/escaping for rich text, source excerpts, participant responses, and summaries.

## Sovereignty and Data Residency

- Core data must be self-hostable.
- Avoid mandatory US hyperscaler dependencies.
- Imported sources, responses, summaries, and exports should remain in configured data region.
- Generation providers must be policy-controlled; no silent third-party transmission.
- Dependency choices should prefer open-source licenses compatible with the ecosystem policy.

## Compliance Open Points

- Final shared identity/auth model.
- Whether anonymous-to-facilitator is required in MVP.
- Exact retention defaults.
- Whether educational deployments require additional learner-record protections.
- Whether audit log is implemented in Rumble DB first or Gear event log from day one.
