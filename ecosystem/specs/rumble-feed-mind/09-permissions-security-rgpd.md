# Permissions, Security and RGPD — rumble-feed-mind

Status: Draft / blocker-instantiating spec.

## Security decision summary

| Topic | Decision |
| --- | --- |
| Product session auth | JWT may remain temporary/local session auth only, with ADR/waiver required before production. |
| Delegated/harness auth | Biscuit/shared delegated authorization direction; no product-specific delegation token. |
| BYOK | Encrypted, write-only after submission, never logged/exported/handoffed. |
| Provider default | Local/EU/sovereign first. US proprietary providers blocked by default. |
| Stripe | Optional payment adapter only; not required for local/self-hosted core use. |
| Logs | Safe refs/hashes/statuses only; no PII/secrets/raw private content by default. |

## Roles and permissions

| Action | Owner | Curator | Reviewer | Viewer | Agent | System |
| --- | --- | --- | --- | --- | --- | --- |
| Manage feeds | Yes | Yes | No | No | Suggest | Poll only |
| Manage rules | Yes | Yes | Review | No | Suggest | Evaluate |
| Manage BYOK keys | Yes | No | No | No | No | No |
| Accept provider-backed rule | Yes | Yes | Review | No | No | No |
| Export curated item | Yes | Yes | Review | No | No | Build only after approval |
| Submit planning handoff | Yes | No | Review | No | No | No |
| View audit refs | Yes | Limited | Yes | No | No | Append safe events |

## Privacy classifications

| Class | Export behavior |
| --- | --- |
| `public` | May be exported with normal validation. |
| `normal` | May be exported with hashes/refs and minimized excerpt. |
| `private` | Excluded by default; explicit inclusion reason required. |
| `sensitive` | Excluded unless explicit inclusion reason + human approval. |
| `no_handoff` | Always blocks export. |

## Provider/BYOK policy instantiation

FeedMind instantiates `specs/shared/contracts/provider-byok-policy.v0.1.md` as follows:

- provider classes allowed by default: `local`, `eu_open_or_sovereign`;
- `eu_commercial` requires documented DPA/retention policy;
- `us_proprietary` is blocked by default and requires explicit waiver/user notice;
- BYOK keys are stored as encrypted ciphertext with key version;
- key refs may appear in internal product store, but not exports/handoffs;
- provider prompts use minimized item excerpts and policy refs;
- no raw provider response is retained unless explicitly classified.

## CuratedItemExport security instantiation

FeedMind instantiates `specs/shared/contracts/curated-item-export.v0.1.md`:

- `contains_secrets = false`;
- `contains_byok_material = false`;
- `allow_downstream_execution = false`;
- `content_hash` and `source_url_hash` required;
- `privacy_classification != no_handoff`;
- `sensitive` requires `explicit_inclusion_reason` and `approval_ref`;
- Stripe/payment IDs are excluded;
- JWT/session tokens are excluded.

## RGPD data inventory

| Data | Personal data risk | Retention/delete |
| --- | --- | --- |
| Feed URLs | May reveal interests/work context. | Delete/anonymize on workspace purge. |
| Feed item content | May include personal data from sources. | Retain per workspace policy; minimize exports. |
| Tags/curation reason | May reveal user interests/opinions. | Export only with user action; delete on request. |
| Rule intent text | May include private criteria. | Treat as private by default. |
| Provider key refs/ciphertext | Secret/commercial sensitive. | Delete/rotate immediately on request. |
| Usage counts | Low/medium personal metadata. | Aggregate where possible. |
| Stripe customer/payment ids | Payment/personal/commercial metadata. | Isolate in billing adapter; never export to harness. |

## Logging policy

Allowed:

- request id;
- actor ref;
- workspace id if pseudonymous;
- item/export/rule ids;
- hashes;
- counts;
- safe status codes.

Forbidden:

- BYOK plaintext/ciphertext;
- JWT/session tokens;
- Stripe secrets/payment details;
- email addresses in general logs;
- raw private feed content;
- provider prompts/responses unless explicit debug mode with redaction and TTL.

## Threats and mitigations

| Threat | Risk | Mitigation |
| --- | --- | --- |
| BYOK key leak | Critical | Write-only UI, encryption, redaction, tests, no export. |
| Provider exfiltration | High | Provider allowlist, context minimization, user policy. |
| Stripe dependency becomes core | High | Feature/config gate, optional adapter, self-hosted core path. |
| JWT reused for delegation | High | JWT limited to local session; Biscuit for delegated/harness flows. |
| Private item exported accidentally | High | Classification gates, preview, Wrench inspection. |
| Rule hides bias/errors | Medium | Explanation/evidence, sample evaluation, human acceptance. |

## Required acceptance before product UI expansion

- Wrench PII/secrets inspection profile exists.
- BYOK lifecycle tests exist in product repo.
- Stripe optionality is enforced or documented by ADR/waiver.
- JWT/Biscuit boundary is documented.
- `CuratedItemExport` fixture passes validation.
- `cargo deny check advisories` is green or explicitly waived with expiry.
