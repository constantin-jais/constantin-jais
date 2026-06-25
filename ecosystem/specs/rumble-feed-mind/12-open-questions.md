# Open Questions — rumble-feed-mind

| Question | Impact | Owner | Status |
| --- | --- | --- | --- |
| Is `rumble-feed-mind` an active Rumble product or primarily a source pipeline feeding other Rumbles? | High | Product/Architecture | Partially answered: active Rumble product, but product UI expansion remains blocked until security/dependency gates clear. |
| Should feed parsing and content extraction remain product-local or become Wrench capability? | High | Wrench/Product | Partially answered: product-local for MVP; extract to Wrench when reused by Note/LM/COS. |
| Should saved feed items become Gear `Source`, Gear `Artifact`, or both depending on lifecycle? | High | Gear/Product | Accepted: both depending on lifecycle; source/artifact are roles, not exclusive identities. |
| Is AGPL acceptable, or must the project relicense / receive a documented waiver? | High | Product/Legal | Accepted: MIT workspace license. |
| Is the current Rust backend + Expo client target still desired, or should it converge with interactive Rumble stack decisions? | High | Architecture | Accepted: Rust/Dioxus convergence; legacy client is migration reference. |
| What model/provider policy is allowed for natural-language rules and explanations? | High | Security/Sovereignty | Drafted: instantiate `shared/contracts/provider-byok-policy.v0.1.md`; provider-backed features blocked until accepted. |
| How are BYOK secrets stored, rotated, exported, and deleted? | Critical | Security | Drafted in `09-permissions-security-rgpd.md`; product tests/implementation still required. |
| What is the minimum export/handoff format from curated item to `rumble-note`, `rumble-lm`, `rumble-cos`, and Gear Memory? | High | Architecture | Drafted: `shared/contracts/curated-item-export.v0.1.md` instantiated in FeedMind specs. |
