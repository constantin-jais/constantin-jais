# Open Questions — rumble-feed-mind

| Question | Impact | Owner | Status |
| --- | --- | --- | --- |
| Is `rumble-feed-mind` an active Rumble product or primarily a source pipeline feeding other Rumbles? | High | Product/Architecture | Open |
| Should feed parsing and content extraction remain product-local or become Wrench capability? | High | Wrench/Product | Open |
| Should saved feed items become Gear `Source`, Gear `Artifact`, or both depending on lifecycle? | High | Gear/Product | Open |
| Is AGPL acceptable, or must the project relicense / receive a documented waiver? | High | Product/Legal | Accepted: MIT workspace license. |
| Is the current Rust backend + Expo client target still desired, or should it converge with interactive Rumble stack decisions? | High | Architecture | Accepted: Rust/Dioxus convergence; legacy client is migration reference. |
| What model/provider policy is allowed for natural-language rules and explanations? | High | Security/Sovereignty | Open |
| How are BYOK secrets stored, rotated, exported, and deleted? | Critical | Security | Open |
| What is the minimum export/handoff format from curated item to `rumble-note`, `rumble-lm`, `rumble-cos`, and Gear Memory? | High | Architecture | Open |
