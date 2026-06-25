# Open Questions — rumble-lm

Status: Draft — MVP product defaults accepted unless marked Open/Discuss.

P0 source-grounded product slice: [`14-source-grounded-product-slice.md`](./14-source-grounded-product-slice.md).  
Initial contract shapes: [`15-contracts-v0.1.md`](./15-contracts-v0.1.md).  
Owner review pack: [`16-contract-review-pack.md`](./16-contract-review-pack.md).  
Stub-first implementation plan: [`17-p0-stub-implementation-plan.md`](./17-p0-stub-implementation-plan.md).

## Product Decisions

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Is MVP synchronous only or hybrid async? | High | Synchronous live, with post-session read-only recap. | Accepted for MVP |
| Are activities first-class objects? | High | Yes: lifecycle, citations, responses, analytics. | Accepted for MVP |
| Is `Learner` an ACL role? | Medium | No, persona only for MVP. | Accepted for MVP |
| Is scoring central? | Medium | No; aggregate learning signals first, optional quiz correctness. | Accepted for MVP |
| Can sessions be reopened after close? | Medium | No normal reopen; create follow-up or audited revision. | Accepted for MVP |
| Are sources mandatory? | High | Mandatory for source-grounded generation; manual facilitator-authored activities allowed. | Accepted for MVP |
| Are citations mandatory? | High | Mandatory for generated source-grounded claims; unsupported claims must be explicit. | Accepted for MVP |
| Can facilitator edit during live? | Medium | Upcoming unpublished activities only; current running activity is locked. | Accepted for MVP |

## Participation and Identity

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Do participants need accounts? | High | Support authenticated/invited and guest join per workspace policy. | Accepted for MVP |
| What anonymity modes are MVP? | High | Named, anonymous-to-participants, aggregate-only. | Accepted for MVP |
| Is anonymous-to-facilitator required? | High | Post-MVP unless strong guarantee is required. | Open |
| Can participants edit responses? | Medium | Before activity close only, if activity setting allows. | Accepted for MVP |
| Can participants request deletion/anonymization? | High | Yes, via privacy workflow according to policy. | Accepted for MVP |

## Source Grounding

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Who owns source storage/indexing? | High | Gear Memory candidate; Rumble stores refs/snapshots. | Accepted for MVP |
| Who owns extraction? | High | Wrench Loader candidate. | Accepted for MVP |
| Who validates citation support? | Medium | Facilitator final validation; Wrench validator advisory. | Accepted for MVP |
| What is minimum provenance? | High | type, title, source ref, revision/hash if available, chunk location. | Accepted for MVP |
| Can generated content use uncited model knowledge? | High | Not when marked source-grounded; must be unsupported/facilitator-authored otherwise. | Accepted for MVP |
| Should Rumble LM own durable ingestion/search/memory? | High | No. Rumble stores source-set refs/snapshots only; Wrench owns extraction and Gear Memory owns source refs/chunks/provenance/retrieval handles. | Accepted for MVP |
| Should citation support validation be fully automated? | Medium | No. Wrench provides advisory support evidence; facilitator validation remains the publication/export gate in P0. | Accepted for MVP |

## Live Session

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| What is MVP live scale? | Medium | 5–100 participants. | Accepted for MVP |
| Can multiple activities run at once? | Medium | No, one open activity run per session in MVP. | Accepted for MVP |
| Is live transport shared Rumble or product-specific? | Medium | Product-specific first, shared candidate later. | Open |
| What happens on facilitator disconnect? | Medium | Session remains server-stateful; facilitator can reconnect or close from recovery UI. | Accepted for MVP |

## Exports and Retention

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Which export formats are MVP? | Medium | Markdown, HTML/PDF, JSON bundle. | Accepted for MVP |
| Are participant exports allowed by default? | High | Only participant-facing summary/aggregate data unless configured otherwise. | Accepted for MVP |
| Who stores export artifacts? | Medium | Gear artifact candidate; Rumble stores metadata/ref. | Accepted for MVP |
| What are retention defaults? | High | Workspace-configurable; no final default yet. | Open |
| Can exports be revoked? | Medium | Metadata/access revocation where supported; downloaded files cannot be recalled. | Accepted for MVP |

## Analytics

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Are individual learner analytics stored? | High | No hidden individual profiling in MVP; no cross-session learner profile or hidden score graph. | Accepted for MVP |
| Are quiz scores persistent? | Medium | Only if quiz correctness enabled, explicitly disclosed, and policy allows retention. | Accepted for MVP |
| Are analytics exportable? | Medium | Aggregate analytics only by default. | Accepted for MVP |

## Architecture and Shared Capabilities

| Question | Impact | Decision / Default | Status |
| --- | --- | --- | --- |
| Workspace primitive owner? | High | Shared Rumble/auth adapter discussion. | Open |
| Event/audit log owner? | High | Gear candidate; Rumble DB acceptable for first MVP if explicit. | Open |
| Should waiver/gate be shared with Canvas? | Medium | Yes as candidate for generated-content validation exceptions. | Discuss |
| Should summaries/exports be Gear artifacts? | Medium | Yes candidate, with Rumble UX ownership. | Accepted for MVP |
| Should Rumble LM define its own delegated token format? | High | No. Delegated rights use the shared Biscuit authorization contract with attenuated, time-bounded tokens. | Accepted for MVP |
| Which generation backend is allowed? | High | Deployment policy decides; no hard-coded provider; provider policy must prevent silent third-party transmission. | Open |
| What exact contracts are still needed before implementation? | High | Initial v0.1 shapes exist in `15-contracts-v0.1.md`; owner review questions are prepared in `16-contract-review-pack.md`. | Discuss |
| Can implementation start before real lower-layer integrations? | High | Yes only as contract-preserving stubs following `17-p0-stub-implementation-plan.md`; real integration still requires owner review. | Discuss |

## Next Spec Work

1. Decide retention defaults.
2. Review `SourceGroundedGenerationRequest` schema with Bolt using `16-contract-review-pack.md`.
3. Review citation support validation result shape with Wrench using `16-contract-review-pack.md`.
4. Review export artifact manifest shape with Gear using `16-contract-review-pack.md`.
5. Review LM-specific Biscuit caveats/facts and authorizer tests using `16-contract-review-pack.md`.
6. If reviews are not complete, implement only the stub-first slice in `17-p0-stub-implementation-plan.md`.
7. Decide live transport ownership after first implementation slice.
8. Review security/RGPD with actual deployment context.
9. Promote architecture-wide ownership decisions to `specs/shared/decision-log.md` when accepted.
