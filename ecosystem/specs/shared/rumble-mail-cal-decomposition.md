# rumble-mail + rumble-cal — Contract-First Product Decomposition

Date: 2026-07-04
Status: **Proposed** product-candidate specification. Paper only; no product repository, service, schema crate, or UI implementation is created by this document.
Source anchor: `odysseus-decomposition.md` E12–E21 plus E22, accepted 2026-07-04. Odysseus remains AGPL inspiration only: this file contains prose, product contracts, and stable concept names; no dependency, no source copy, and no line-by-line translation.
Decision context: odysseus Q2 says `rumble-mail` and `rumble-cal` are serious paper candidates, but repository creation is blocked until both product ratification and M1 closure. M1 has the `workspace-identity.v0.1` contract accepted, but remains incomplete until canvas emits `tenant_id` and re-syncs its local schema.
Scope: personal forge ecosystem only.

## 1. Why this document

The accepted odysseus decomposition identifies two candidate Rumble products:

- `rumble-mail`: not a plain IMAP/SMTP client, but an agent-assisted mail triage surface: summaries, reply drafts in the user's style, phishing/marketing/receipt classification, urgency alerts, and calendar extraction from message bodies.
- `rumble-cal`: not a thin CalDAV client, but a calendar sync product whose differentiator is real conflict resolution over CalDAV write-back, recurrence, deletes, and per-occurrence edits.

This document turns those candidates into contract-first paper specs. It intentionally stops before code or repository creation. The output is meant to answer: what must the contracts be, what must be rebuilt from scratch, what lands on Gear/Portal/Biscuit, and what questions must be resolved before any repository exists.

## 2. Method and non-negotiable constraints

| Constraint | Contract impact |
| --- | --- |
| AGPL source boundary | Rebuild concepts from scratch on the forge stack. No copied code, no derived source text, no dependency, no source fragments in examples. |
| M1 gate | Product repos are forbidden until product ratification plus M1 closure. Contracts and specs may proceed in this control plane. |
| Security > Quality > Performance > Completeness | Mail bodies, calendar descriptions, ICS payloads, and contacts are hostile or PII-bearing until proven otherwise. Unsafe completeness is rejected. |
| Workspace identity | Every product object is scoped by `tenant_id` and `workspace_id`; authorization is derived from `workspace-identity.v0.1` plus Biscuit delegation. |
| RGPD erasure | Mail, calendar, contacts, triage outputs, and parse outputs carry PII. Erasure/anonymization wins over stale active records and index rebuilds. |
| Stack target | Rust core, Dioxus 0.7.9 web/PWA shell, Biscuit delegation, Portal tokens for UI, Gear Memory for provenance/state transitions, Gear Loader only when an external-source extraction flow is explicitly needed. |
| Anti-gold-plating | No SSO/OIDC for forge identity, no local-first sync protocol, no org/billing hierarchy, no product repo, no shared contacts database. Provider OAuth is a mail/calendar integration concern, not workspace SSO. |

## 3. Contract-first spine shared by both products

### 3.1 Identity, tenant, and workspace boundary

All product-local contracts carry the following invariant fields directly or through a parent aggregate:

| Field | Rule |
| --- | --- |
| `tenant_id` | Mandatory; matches `Workspace.tenant_id` and the Biscuit `organization` fact. |
| `workspace_id` | Mandatory for user-facing product state; route/body/database scope must agree. |
| `actor_ref` | Uses `workspace-identity.v0.1` `ActorReference` with `actor_type`; adapter maps to the Biscuit actor kind used by the shared delegation contract. |
| `account_id` | Product-local opaque reference to an external mail, SMTP, CalDAV, or CardDAV account. It is not a credential. |
| `provenance_ref` | Safe reference only; no raw message body, event description, contact note, credential, token, or source excerpt. |
| `deleted_at` / `anonymized_at` | Privacy state transitions beat stale active sync data. |

Product roles are named bundles over the closed primitive vocabulary of `workspace-identity.v0.1`:

| Role bundle | Actor types | Workspace primitives | Product meaning |
| --- | --- | --- | --- |
| `Host` | human only for approval/delegation | `read`, `comment`, `write`, `approve`, `invite`, `administer`, `delegate` | Owns a mail/cal workspace, account bindings, provider credentials by reference, conflict decisions, and product policy. |
| `Participant` | human | `read`, `comment`; `write` only when explicitly granted | Can view delegated mail/cal scopes and propose drafts or event changes, without broad account administration. |
| `AssistantAgent` | agent/service only | bounded `read` or `write` through short-lived delegation; never `approve` or `delegate` | May summarize, classify, draft, extract, or propose changes; cannot send mail, approve calendar conflicts, or manage members without a human decision. |

### 3.2 Biscuit delegation boundary

Both products use the shared Biscuit contract rather than product-specific bearer tokens. Product-local authorizers inject current workspace state; tokens only carry bounded facts and checks.

| Resource family | Resource examples | Product-local action vocabulary | Required safeguards |
| --- | --- | --- | --- |
| Mail account and mailbox | `mail_account`, `mail_folder`, `mail_message`, `mail_draft`, `send_intent`, `triage_run` | `mail:sync`, `mail:read`, `mail:draft`, `mail:send`, `mail:classify`, `mail:extract_calendar` | tenant/workspace equality; short TTL; no raw token logging; send requires human actor or explicit human-approved delegation. |
| Calendar account and event | `calendar_account`, `calendar_collection`, `calendar_event`, `write_intent`, `conflict_case`, `parse_candidate` | `calendar:sync`, `calendar:read`, `calendar:write`, `calendar:delete`, `calendar:resolve_conflict`, `calendar:parse` | conflict resolution requires current permission; high-risk resolutions require human actor; retries are idempotent. |
| Contacts | `contact_store`, `contact_record`, `contact_link` | `contacts:sync`, `contacts:read`, `contacts:write` | product-owned store instance; no shared mutable cross-repo database. |

If the same product-local action becomes reused by multiple Rumbles, it must be proposed as a future shared Biscuit right. Until then, the shared token shape and authorizer rules are reused; only the resource/action names are product-local.

### 3.3 Storage and PII boundary

The primary store belongs to each product. Gear can store safe references, provenance, deletion/anonymization events, and derived memory/index projections only when a product explicitly emits them. Gear is not the mailbox, calendar, or contacts database.

| Data class | Examples | Storage rule | Retention / erasure |
| --- | --- | --- | --- |
| Raw PII content | message body, subject, addresses, event title/description/location, contact notes | Product-owned encrypted/permissioned store; not in Gear audit metadata. | Full erasure or anonymization on user request; indexes and summaries are dropped or rebuilt from anonymized projection only. |
| Derived PII | summaries, reply drafts, classifications, extracted event candidates, NL parse outputs | Product store with source links and confidence; never treated as source truth. | Deleted with the source or when user rejects the derived output. |
| Safe audit refs | opaque ids, hashes, timestamps, policy refs, delegation refs, conflict ids | Product/Gear audit allowed if no raw content or credential appears. | Tombstones keep minimum audit fields only when policy permits. |
| Provider credentials | IMAP/SMTP app password refs, OAuth credential refs, CalDAV/CardDAV credential refs | Secret manager or product credential adapter; spec stores reference only. | Revocation deletes secret material and invalidates sync jobs. |

### 3.4 Hostile content envelope

Mail and calendar are hostile-input products. The E22 untrusted-context pattern applies whenever external text is fed to an LLM or assistant. The contract requires:

| Surface | Required treatment |
| --- | --- |
| Incoming mail body, subject, sender display name, attachments | Mark untrusted; disable remote content by default; sanitize before render; size/time limits for parsers; no regex vulnerable to catastrophic backtracking on untrusted bodies. |
| Calendar ICS, description, location, organizer/attendee names | Mark untrusted; bound recurrence expansion; sanitize before render; do not treat ICS content as instructions. |
| Contacts vCard notes, names, URLs | Parse with an RFC-aware parser; sanitize display; never infer account trust from a contact. |
| LLM prompt assembly | External text is wrapped as data with source labels and escaped delimiters; assistant output is a proposal until product policy accepts it. |

This complements ADR 0015. Loader evidence is still used for attachments or imported external sources; mail/cal protocol sync is product-owned and must emit equivalent hostile-content/security findings in product terms.

## 4. Element map and verdicts

All verdicts are **Proposed 2026-07-04**. Dispositions available in this file are `rebuild`, `knowledge`, `reject`, and `quarantine` only.

| # | Source element | Product capability | Layer | Disposition | Contract shape | Action |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | E12 IMAP polling, pooling, UID addressing | Multi-account inbox sync with stable message identity | `rumble-mail` | **rebuild (product-gated)** | `MailAccount`, `MailboxFolder`, `MessageEnvelope`, `MessageBody`, `SyncCursor`, `SyncJob` | Specify provider-neutral UID identity and sync cursors; defer repo until product ratification + M1 closure. |
| M2 | E13 compose, sanitize, SMTP send, scheduled send | Safe draft/send/outbox workflow | `rumble-mail` | **rebuild (product-gated)** | `MailDraft`, `SendIntent`, `ScheduledSend`, `OutboxReceipt` | Require sanitize-before-render, multipart output, idempotent send intent, and human approval before assistant-generated send. |
| M3 | E14 AI triage | Differentiating product layer: summaries, style-aware replies, classification, urgency, calendar extraction | `rumble-mail` | **rebuild (product-gated)** | `TriageRun`, `MessageSummary`, `ReplyDraft`, `MessageClassification`, `UrgencyAlert`, `CalendarExtraction` | Make triage the core product contract; assistant outputs stay proposals with source refs, confidence, and human acceptance gates. |
| M4 | E15 email data model split | Separate list/index, body cache, summaries, replies, tags, extractions | `rumble-mail` | knowledge + rebuild shape | Product-owned tables/collections by concern; no copied schema | Preserve separation of concerns; improve eviction, migrations, and erasure semantics from scratch. |
| M5 | E21 email tool surface | Agent tool API over mail | cross-layer | knowledge | Future tool facade over `mail_message`/`send_intent` refs | Defer until a real Bolt/Rumble assistant surface exists; design fail-closed so callers cannot invent message UIDs. |
| C1 | E16 CalDAV pull sync | Remote-to-local calendar mirror | `rumble-cal` | **rebuild (product-gated)** | `CalendarAccount`, `CalendarCollection`, `CalendarObject`, `CalendarSyncCursor`, `CalendarSyncReport` | Stable account/calendar identity; safe prune only after complete parse; no delete on partial failure. |
| C2 | E17 CalDAV write-back | Local edits pushed to provider | `rumble-cal` | **rebuild (product-gated)** | `CalendarWriteIntent`, `RemotePrecondition`, `WriteBackReceipt`, `CalendarTombstone`, `ConflictCase` | Keep tombstones; replace best-effort write-back with the conflict design in section 8. |
| C3 | E18 recurrence and compound UIDs | Recurring events, exceptions, per-occurrence edits | `rumble-cal` | **rebuild (product-gated)** | `RecurrenceMaster`, `OccurrenceRef`, `OccurrenceOverride`, `RecurrenceExpansionWindow` | Use bounded expansion windows and explicit occurrence identity; conflicts are per master or occurrence, not global. |
| C4 | E20 natural-language calendar parsing | User-timezone-aware event candidate generation | `rumble-cal` | knowledge + rebuild shape | `CalendarParseRequest`, `ParsedEventCandidate`, `ParseConfidence`, `ParseEvidence` | Product UX note; parse output is a proposal, not an event, until accepted by a human with write permission. |
| S1 | E19 CardDAV contacts sync | Contacts substrate for mail + calendar | `rumble-mail` / `rumble-cal` / Gear library candidate | **rebuild (product-gated)** | `ContactStore`, `ContactRecord`, `ContactSyncCursor`, `ContactLink` | Build as product-owned stores using a shared Rust parsing/normalization library only after both products require it; never a shared DB. |
| S2 | E22 untrusted-context envelope | Safe model-facing external content | cross-layer | knowledge (pattern) | `UntrustedContentRef`, `SecurityFinding`, prompt assembly policy | Document now; extract only on a second real model-facing consumer. |
| S3 | Provider credential handling | IMAP/SMTP/CalDAV/CardDAV secrets, OAuth refs | product + auth adapter | **rebuild (product-gated)** | `CredentialRef`, `ProviderCapability`, `AccountBinding` | O365/Outlook basic auth is not viable; provider OAuth may be needed, but this is not forge SSO/OIDC. Store references only. |

## 5. `rumble-mail` product card

| Field | Spec |
| --- | --- |
| Product promise | Turn hostile, noisy email into an auditable, assistant-assisted action stream without surrendering mailbox custody or inventing unsafe auto-send behavior. |
| Target users | A forge workspace host managing one or more personal/professional mailboxes; delegated participants who may draft or classify within explicit scopes; assistant agents with bounded triage rights. |
| Core differentiator | Agent-assisted triage: summarize, classify, detect phishing/marketing/receipts, propose replies in the user's style, alert urgency, and extract calendar candidates. |
| MVP capabilities | IMAP sync/read; safe render; draft creation; SMTP send via explicit send intent; scheduled send; triage runs; calendar extraction proposals; per-product contacts store read/write as needed. |
| Non-goals | No generic webmail clone, no forge-wide identity SSO, no autonomous send, no local-first multi-device sync, no shared contacts DB, no global email search service. |
| Dependencies | `workspace-identity.v0.1`; Biscuit delegated authorization; Portal tokens; Dioxus shell; Gear Memory safe refs/tombstones; Gear Loader only for attachments/imports that need canonical extraction. |
| Technical cost / risk | Provider quirk breadth; Outlook/O365 OAuth requirement; hostile body parsing; phishing and remote content; PII erasure across source and derived triage outputs. |
| Repo trigger | Product decision ratified; M1 closed; contract package accepted; provider credential policy accepted; first hostile-content/triage fixtures defined. |

### 5.1 Mail domain contracts

| Object | Purpose | Required fields / invariants |
| --- | --- | --- |
| `MailAccount` | External mailbox binding | `tenant_id`, `workspace_id`, `account_id`, provider kind, `credential_ref`, sync policy, disabled/revoked state. No secret material. |
| `MailboxFolder` | Provider folder/label projection | Stable folder id, provider path/label, special-use hint, last sync marker, provider quirks. Gmail labels and IMAP folders are normalized without losing provider identity. |
| `MessageEnvelope` | Fast list/index record | Opaque message id, account/folder refs, provider UID, message-id header hash, from/to/cc/bcc refs, subject classification, timestamps, flags, body availability, security summary. |
| `MessageBody` | Read-on-demand body/cache | Sanitized render projection, raw-body custody policy, attachment refs, content hash, hostile-content findings, erasure state. |
| `MailDraft` | User or assistant-authored draft | Author actor, source message optional, body projection, style profile ref optional, validation status, approval state. |
| `SendIntent` | Idempotent send request | Draft ref, recipient refs, idempotency key, scheduled time optional, human approval ref if assistant-generated, provider preflight result. |
| `TriageRun` | Assistant processing unit | Source message ref, model/provider ref, prompt policy version, security findings, outputs refs, confidence, human decision state. |
| `CalendarExtraction` | Proposed calendar event from email | Source span ref, parsed candidate ref, confidence, timezone assumptions, accepted/rejected state, target calendar optional. |

### 5.2 Mail API contract surface

These are proposed service operations, not implementation routes.

| Operation | Input | Output | Auth |
| --- | --- | --- | --- |
| `mail.account.bind` | workspace, provider kind, `credential_ref`, sync policy | `MailAccount` | `Host` with `administer`; Biscuit resource `mail_account`. |
| `mail.sync.request` | account/folder scope, reason, idempotency key | `SyncJob` | `Host` or bounded service delegation with `mail:sync`. |
| `mail.message.list` | folder/filter/page cursor | `MessageEnvelope` page | `read` permission; tenant/workspace equality. |
| `mail.message.read` | message ref and render mode | sanitized `MessageBody` projection | `read`; hostile-content markers preserved. |
| `mail.draft.create` | source message optional, body, recipients | `MailDraft` | `write`; assistant output creates proposal only. |
| `mail.send.intent.create` | draft ref, schedule optional, idempotency key | `SendIntent` | human `write`; assistant-created draft requires approval ref. |
| `mail.send.execute` | send intent ref | `OutboxReceipt` | human actor or approved short-lived delegation; fails closed on stale draft hash. |
| `mail.triage.run` | message refs, requested outputs | `TriageRun` | bounded `mail:classify` / `mail:extract_calendar`; no raw content in logs. |
| `mail.extraction.accept_calendar` | extraction ref, target calendar ref | `CalendarWriteIntent` or parse candidate handoff | `write` on target calendar; human confirmation. |

### 5.3 Mail events

| Event | Producer | Consumers | Payload rule |
| --- | --- | --- | --- |
| `mail.account_bound` | mail service | audit, sync worker | ids and provider capability summary only. |
| `mail.sync_completed` | sync worker | UI, audit, Gear projection optional | counts, cursor refs, error classes; no subjects/body. |
| `mail.message_indexed` | sync worker | UI/search projection | message ref, hashes, flags, security summary. |
| `mail.triage_completed` | triage worker | UI, audit | triage refs, output refs, confidence; no prompt/body. |
| `mail.send_intent_created` | app service | UI, scheduler | draft ref, schedule, actor, approval ref. |
| `mail.send_succeeded` / `mail.send_failed` | send worker | UI, audit | provider receipt/error class; no SMTP transcript. |
| `mail.calendar_extraction_created` | triage worker | mail + cal handoff | extraction ref, source ref, timezone assumption, confidence. |
| `mail.privacy_erased` | privacy workflow | indexes, Gear projection | object refs and state transition only. |

## 6. `rumble-cal` product card

| Field | Spec |
| --- | --- |
| Product promise | Provide a sovereign calendar surface over standard CalDAV accounts with deterministic, auditable conflict handling instead of silent last-writer wins. |
| Target users | A workspace host with one or more calendars; participants with delegated read/write scopes; assistant agents that may parse or propose changes. |
| Core differentiator | Real conflict resolution for CalDAV write-back, including ETag preconditions, tombstones, recurrence exceptions, and human-visible resolution choices. |
| MVP capabilities | CalDAV sync; event list/read; create/update/delete via write intents; recurrence expansion windows; conflict detection/resolution; natural-language parse proposals; per-product contacts store where attendees require it. |
| Non-goals | No local-first sync protocol, no shared organization calendar service, no billing/org hierarchy, no autonomous invite changes by agents, no copy of provider-specific quirks as source code. |
| Dependencies | Same shared stack as mail; plus product-owned calendar store and conflict ledger. |
| Technical cost / risk | iCalendar/RRULE correctness; timezone and all-day semantics; provider ETag behavior; recurring series conflicts; attendee/organizer side effects. |
| Repo trigger | Product decision ratified; M1 closed; conflict contract accepted with fixtures for at least clean write, remote change, delete conflict, recurrence exception, and tombstone replay. |

### 6.1 Calendar domain contracts

| Object | Purpose | Required fields / invariants |
| --- | --- | --- |
| `CalendarAccount` | CalDAV account binding | `tenant_id`, `workspace_id`, `account_id`, provider endpoint ref, `credential_ref`, sync state, disabled/revoked state. |
| `CalendarCollection` | Remote calendar projection | Stable collection id derived from account and remote URL identity, display metadata, sync token/ctag where available, safe-prune marker. |
| `CalendarObject` | Event/task mirror | Product event id, collection id, remote href, UID, optional recurrence id, remote ETag, local revision, base snapshot hash, privacy state. |
| `CalendarWriteIntent` | Local create/update/delete request | Target object or collection, base remote ETag if known, base snapshot hash, local patch, actor, idempotency key, risk class. |
| `RemotePrecondition` | What must still be true before write | Expected ETag, expected href/UID, expected collection sync marker, expected not-deleted state. |
| `ConflictCase` | Durable unresolved conflict | Base snapshot ref, local proposal ref, remote snapshot ref, changed fields, conflict type, risk class, resolution choices. |
| `ConflictResolution` | Human or policy resolution | Resolver actor, selected strategy, merged projection ref, audit reason, new write intent optional. |
| `CalendarTombstone` | Delete/anonymization marker | Minimal refs, timestamps, actor, remote ids/hashes when policy permits, no event title/description/location. |
| `OccurrenceRef` | Recurrence occurrence identity | Collection/account, UID, recurrence id or date key, expansion window, timezone basis. Remote href is not the sole identity. |
| `ParsedEventCandidate` | NL parse output | Original request ref, timezone used, candidate fields, confidence, missing information, accepted/rejected state. |

### 6.2 Calendar API contract surface

| Operation | Input | Output | Auth |
| --- | --- | --- | --- |
| `calendar.account.bind` | workspace, provider endpoint ref, `credential_ref`, sync policy | `CalendarAccount` | `Host` with `administer`. |
| `calendar.sync.request` | account/collection scope, reason, idempotency key | `CalendarSyncReport` | `Host` or bounded service delegation. |
| `calendar.event.list` | collection/time window/filter | event page with recurrence expansion metadata | `read`; expansion cap reported explicitly. |
| `calendar.event.read` | event or occurrence ref | sanitized event projection | `read`; untrusted fields preserved as data. |
| `calendar.write_intent.create` | create/update/delete patch, base refs, idempotency key | `CalendarWriteIntent` | `write`; assistant proposals need human acceptance before execution. |
| `calendar.writeback.execute` | write intent ref | `WriteBackReceipt` or `ConflictCase` | bounded service delegation; preconditions enforced. |
| `calendar.conflict.resolve` | conflict ref, chosen strategy, merged projection optional | `ConflictResolution` and optional new write intent | human `approve` or explicitly allowed `write` policy; high-risk fields require human. |
| `calendar.parse_nl` | text ref or user-entered text, timezone, defaults | `ParsedEventCandidate` | `write` or bounded `calendar:parse`; output is proposal only. |
| `calendar.tombstone.apply` | event/contact refs, privacy reason | tombstone refs | privacy-authorized actor; raw content removed. |

### 6.3 Calendar events

| Event | Producer | Consumers | Payload rule |
| --- | --- | --- | --- |
| `calendar.sync_completed` | sync worker | UI, audit | counts, cursor refs, parse status; no event descriptions. |
| `calendar.safe_prune_skipped` | sync worker | UI/audit | collection ref, reason class; proves no delete on partial failure. |
| `calendar.write_intent_created` | app service | write-back worker, audit | intent ref, target ref, risk class, actor. |
| `calendar.writeback_succeeded` | write-back worker | UI, audit | receipt ref, new ETag/hash, no raw ICS. |
| `calendar.conflict_detected` | sync/write-back worker | UI, audit | conflict ref, changed field classes, risk. |
| `calendar.conflict_resolved` | app service | write-back worker, audit | resolution ref, strategy, resolver actor, no raw event body. |
| `calendar.tombstone_recorded` | privacy/delete workflow | sync worker, indexes | tombstone ref and target refs only. |
| `calendar.parse_candidate_created` | parser/assistant | UI | candidate ref, confidence, missing fields. |

## 7. Contacts substrate contract

Contacts are shared capability pressure, but bounded-context isolation is stricter than convenience. The product rule is: shared parser/normalizer library may exist later; the mutable contacts store stays per product.

| Contract | Rule |
| --- | --- |
| `ContactStore` | One store instance per product workspace. `rumble-mail` and `rumble-cal` do not read or write each other's DB. |
| `ContactRecord` | Opaque contact id, names/emails/phones/addresses, source account, sync cursor, privacy state, security findings for URLs/notes. |
| `ContactLink` | Product-local relation such as sender, recipient, attendee, organizer, extracted-person. |
| CardDAV sync | Rebuilt with an RFC-aware parser; newline-splitting is explicitly rejected as insufficient. |
| Extraction trigger | A shared Rust contacts library may be extracted only after both products need the same parser/normalizer and the ADR 0022 extraction rule is satisfied. |
| Erasure | Contact PII deletion/anonymization cascades to product indexes and derived assistant outputs. |

## 8. `rumble-cal` conflict-resolution design

This section is the distinctive contract for `rumble-cal`. It designs out the odysseus gap: best-effort write-back with non-atomic ETag checks.

### 8.1 Design goals

| Goal | Rule |
| --- | --- |
| No silent overwrite | A local write never overwrites a remote change unless the contract has classified the change and policy allows it. |
| Atomic local intent | The product stores the write intent, base snapshot hash, and expected remote precondition in one local transaction before any network call. |
| Remote precondition | PUT/DELETE uses provider preconditions where available, especially expected ETag. Missing or weak provider support degrades to conflict detection, not blind overwrite. |
| Human-visible conflicts | Same-field concurrent edits, recurrence-shape edits, attendee/organizer changes, and delete-vs-edit conflicts become `ConflictCase` records. |
| Tombstones win privacy | Local privacy deletion hides/removes content locally immediately and cannot be resurrected by stale sync data. Remote cleanup may remain pending. |
| Idempotent retries | A retry of a write intent is the same payload and precondition. Unknown network outcome is reconciled by fetch-before-retry. |

### 8.2 State model

| State | Meaning | Allowed next states |
| --- | --- | --- |
| `clean` | Local mirror matches the last accepted remote snapshot. | `local_dirty`, `remote_changed`, `delete_pending`, `deleted`. |
| `local_dirty` | User accepted a local change but it has not been written remotely. | `write_pending`, `conflict_open`, `clean`, `write_failed_retryable`. |
| `write_pending` | Worker is executing a write intent. | `clean`, `conflict_open`, `write_failed_retryable`, `unknown_outcome`. |
| `unknown_outcome` | Network failed after a possible provider commit. | `clean` after fetch confirms, `conflict_open` if remote differs, `write_failed_retryable` if not committed. |
| `remote_changed` | Sync saw a remote change while no local dirty state exists. | `clean` after mirror update, `conflict_open` if local policy requires review. |
| `conflict_open` | Base/local/remote snapshots cannot be safely merged automatically. | `resolved_keep_local`, `resolved_keep_remote`, `resolved_merge`, `resolved_duplicate`, `cancelled`. |
| `delete_pending` | Local delete/tombstone is recorded; remote delete not yet confirmed. | `deleted`, `conflict_open`, `write_failed_retryable`. |
| `deleted` | Content payload is removed or tombstoned according to retention policy. | No automatic resurrection; explicit human undelete creates a new write intent. |

### 8.3 Write-back algorithm contract

| Step | Contract requirement |
| --- | --- |
| 1. Create intent | Local service records `CalendarWriteIntent` with base snapshot hash, expected ETag, changed field set, actor, idempotency key, and risk class. |
| 2. Re-check local row | Worker locks the local event row. If the row's last remote ETag or base hash no longer matches the intent, it creates a `ConflictCase` before network I/O. |
| 3. Execute provider write | Worker sends create/update/delete with the strongest provider precondition available. For update/delete this is expected ETag where available. |
| 4. Handle success | Worker fetches or accepts returned ETag, then atomically updates local mirror, write receipt, and sync cursor hints. |
| 5. Handle precondition failure | Worker fetches the remote object, stores remote snapshot, and classifies the conflict using base/local/remote comparison. |
| 6. Handle network ambiguity | Worker fetches by stable UID/href before retry. It never replays a changed payload under the same idempotency key. |
| 7. Emit audit | Events include refs, hashes, action, actor, and decision class only. Raw ICS is never emitted to audit. |

### 8.4 Merge policy

| Conflict class | Automatic result | Human choices |
| --- | --- | --- |
| Disjoint low-risk fields | Merge may proceed if base/local/remote prove non-overlap and fields are display metadata such as color/category or local reminder additions. | Review merged projection if policy marks account high risk. |
| Same scalar field changed both sides | Open conflict. | Keep local, keep remote, edit merged value. |
| Time, timezone, all-day flag, duration | Open conflict unless only one side changed from base. | Keep local, keep remote, edit merged value, duplicate as new event. |
| Organizer, attendee list, RSVP state | Open conflict. These can notify other people or change obligations. | Keep remote, propose local with confirmation, duplicate private copy. |
| Description/location | Merge only when mechanically disjoint and size-bounded; otherwise open conflict. | Keep local, keep remote, edit merged value. |
| Remote delete vs local edit | Open conflict. Local content remains hidden if user requested privacy deletion. | Accept delete, restore as new event, or keep local as duplicate if policy permits. |
| Local delete vs remote edit | Tombstone remains local winner for privacy; remote cleanup attempt becomes conflict if provider refuses due to changed ETag. | Confirm remote delete with latest ETag, cancel local delete, or keep local tombstone only. |
| Recurrence rule changed while occurrence edit pending | Open `series_shape_changed` conflict. | Apply occurrence edit to new series shape, keep remote series, duplicate occurrence, or cancel local edit. |
| Two occurrence edits on different occurrence refs | Independent; no conflict if master RRULE/exdates unchanged. | Not needed unless provider stores them as a single object and precondition fails. |

### 8.5 Recurrence and compound identity

| Topic | Contract rule |
| --- | --- |
| Event identity | Product key is account + collection + UID + optional recurrence id. Remote href is stored but not treated as the only identity. |
| Master vs occurrence | Master RRULE/exdates and per-occurrence overrides are separate conflict domains, joined by UID. |
| Expansion cap | UI/API requests use explicit time windows and a bounded occurrence cap. Hitting the cap is reported, not silently truncated. |
| Exceptions | EXDATE and recurrence-id overrides are first-class. A single occurrence delete creates an occurrence tombstone, not a whole-series delete. |
| Timezones | DTSTART/DTEND/UNTIL normalization preserves timezone semantics. Naive datetimes are interpreted only with an explicit account/user timezone policy. |

### 8.6 Tombstones and RGPD

| Case | Contract behavior |
| --- | --- |
| User deletes event normally | Product records delete intent and tombstone, hides event locally, then attempts remote DELETE with expected ETag. |
| User requests privacy erasure | Raw title, description, location, attendee notes, parse outputs, and indexes are removed/anonymized locally before remote cleanup completes. Minimal audit refs remain only if policy allows. |
| Remote resurrects old data | Sync sees stale remote object after local privacy tombstone and does not restore searchable payload. It records a conflict/remediation task. |
| Provider delete fails | Tombstone remains; UI shows remote cleanup pending or conflict, not restored content. |

## 9. Landing map

| Capability | Landing if product is ratified | Gate / trigger |
| --- | --- | --- |
| Mail sync/read/send | Future `rumble-mail` repo | Product ratification + M1 closure + provider credential contract. |
| Mail triage | Future `rumble-mail` core service | Hostile-content fixtures + assistant-output approval contract. |
| Calendar sync/write-back | Future `rumble-cal` repo | Product ratification + M1 closure + conflict fixtures. |
| Calendar conflict engine | `rumble-cal` domain module, possibly reusable only after a second calendar consumer | Conflict contract accepted; tests for ETag, tombstone, recurrence, unknown outcome. |
| Contacts parser/normalizer | Start product-local; extract shared Rust library only after both products need it | ADR 0022 extraction rule; no shared DB. |
| Provenance / privacy transitions | Gear Memory safe refs and tombstones | Product emits safe projections; raw PII never enters Gear audit metadata. |
| Attachments/imported sources | Gear Loader | Only when an attachment/import flow requires canonical extraction and evidence. |
| UI | Dioxus 0.7.9 + Portal tokens | Contracts frozen first; UI after repo trigger. |
| Delegation | Shared Biscuit contract | Product authorizers map local actions to resources and enforce tenant/workspace equality. |

## 10. Acceptance tests for future implementation

These are paper acceptance criteria for the eventual product repos. They are not implemented by this PR.

| Area | Given / When / Then |
| --- | --- |
| M1 gate | Given M1 is not closed, when this spec lands, then no `rumble-mail` or `rumble-cal` repository exists. |
| License boundary | Given odysseus is AGPL, when a future implementation starts, then cargo/npm dependencies and source files contain no odysseus dependency or copied expression. |
| Tenant isolation | Given a token organization differs from route/body/database tenant, when any mail/cal operation is requested, then authorization fails closed. |
| Agent safety | Given an assistant-generated reply draft, when send is requested without human approval, then send fails. |
| Hostile mail | Given a mail body contains prompt injection or active content, when triage/render runs, then content is treated as untrusted data and findings are attached. |
| ReDoS guard | Given a large untrusted mail body, when extraction/classification runs, then parsers are bounded and no catastrophic regex path exists. |
| O365 provider | Given an Outlook/O365 mailbox, when basic auth credentials are supplied, then provider binding is rejected with a provider-capability error; OAuth credential refs require a product-approved adapter. |
| Privacy erasure | Given a user erases a message/event/contact, when old sync data or index rebuild appears, then deleted/anonymized state wins and raw PII is not restored. |
| Calendar clean write | Given local base ETag matches remote, when write-back succeeds, then new ETag and snapshot hash update atomically. |
| Calendar remote change | Given remote ETag changed since local intent, when write-back executes, then a `ConflictCase` is created before overwrite. |
| Calendar unknown outcome | Given network failure after write attempt, when retry starts, then worker fetches remote state before replaying. |
| Calendar recurrence conflict | Given master RRULE changed remotely while a local occurrence edit is pending, when sync/write-back runs, then a `series_shape_changed` conflict opens. |
| Contacts boundary | Given mail and cal both have contacts, when either product syncs contacts, then it writes only its own product store, never a cross-repo DB. |
| Audit safety | Given any operation logs or emits events, then payloads contain safe refs/hashes/error classes only, no raw token, credential, message body, event description, or contact note. |

## 11. Anti-scope and sceptic checklist

| Check | Verdict |
| --- | --- |
| No repository creation | Pass by design: this file is the only product-candidate artifact in this PR. |
| No SSO/OIDC scope creep | Pass: workspace identity stays on `workspace-identity.v0.1`; provider OAuth is scoped to external mailbox/calendar providers only. |
| No local-first sync protocol | Pass: CalDAV/IMAP sync is provider integration; no cross-device local-first protocol is specified. |
| M1 respected | Pass: repo trigger remains product ratification + M1 closure, not just accepted contract text. |
| Bounded context respected | Pass: contacts are per-product stores; Gear stores safe refs/projections only. |
| Conflict design concrete | Pass: state model, write algorithm, merge policy, recurrence, tombstones, and acceptance tests are specified. |
| AGPL boundary respected | Pass: prose and contract shapes only; no code blocks, dependencies, or source-derived snippets. |
| Facts sourced | Pass: anchored to accepted `odysseus-decomposition.md`, `decision-log.md`, ADR 0015/0022/0028/0032, `workspace-identity.v0.1`, and the Biscuit contract. |

## 12. Open questions

| Question | Impact | Owner | Status |
| --- | --- | --- | --- |
| Should mail and calendar be ratified as two repositories, one combined personal-information product, or one first and the other later? | Determines repo boundaries, shared contacts extraction pressure, and product roadmap. | Constantin / product arbitration | Open |
| Which provider set defines MVP: generic IMAP/SMTP + CalDAV/CardDAV only, or explicit Gmail/Google/Outlook/iCloud adapters? | Provider credential contract, OAuth scope, tests, and support burden. | Future product spec | Open |
| What product store is elected first: SQLite local/PWA-friendly store, Postgres service store, or a hybrid? | Affects sync locking, conflict transactions, RLS, backup, and Dioxus deployment shape. | Future product spec + stack review | Open |
| Which assistant runtime is authorized for triage and NL parsing? | Determines prompt envelope, model/provider policy, provenance, and privacy controls. | Rumble/Bolt arbitration | Open |
| Does calendar invite sending and attendee notification belong in MVP? | High-risk side effects; affects conflict policy and human approval gates. | Future `rumble-cal` spec | Open |
| When do contacts become a shared Rust library? | Extraction too early creates premature capability; too late duplicates parsers. | Gear/Rumble architecture | Open, trigger = both products need same parser/normalizer |

## 13. Sources

- `ecosystem/specs/shared/odysseus-decomposition.md` — E12–E21 product candidates, E22 untrusted-context pattern, product cards, landing map, accepted 2026-07-04.
- `ecosystem/specs/shared/decision-log.md` — 2026-07-04 odysseus Q2 paper candidates, C5 M1 partial closure, C9 RGPD erasure.
- `ecosystem/specs/shared/contracts/workspace-identity.v0.1.md` — tenant/workspace/actor/permission contract, accepted 2026-07-04.
- `ecosystem/specs/shared/contracts/delegated-authorization-biscuit.v0.1.md` — shared Biscuit token facts, authorizer rules, safe audit refs.
- `ecosystem/specs/shared/adrs/0015-wrench-loader-hostile-content-evidence.md` — hostile-content evidence doctrine.
- `ecosystem/specs/shared/adrs/0022-starred-repos-strengthen-existing-repos.md` — no speculative repo/extraction rule.
- `ecosystem/specs/shared/adrs/0028-workspace-identity-ownership.md` — identity/workspace split and closed permission vocabulary.
- `ecosystem/specs/shared/adrs/0032-web-shell-dioxus-ratified.md` — Dioxus 0.7.9 web/PWA shell.
- `ecosystem/specs/shared/adrs/0008-gear-memory-privacy-tombstones.md` — privacy tombstone direction for replay and erasure safety.
