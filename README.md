# Hey 👋 I'm Constantin

I build **resilient systems where machines decide better — without failing silently.**

## One question, one obsession

From genetic algorithms and Monte-Carlo to today's models, I've worked on the same problem:
**how does a system decide, and how do you trust the decision?** GenAI changed the _cost_ of a
machine decision, not its _nature_. The hard part was never the model — it's distribution,
adoption, and trust: teams, ops, and regulators only secure what they understand.

That conviction has a root. I came up in **critical embedded systems** — real-time, close to
the hardware (C, VHDL), zero-error tolerance, where a single undetected fault is not an option.
The principle I took from it: **a system is robust only with multiple supply lines — never a
single dependency.** At company scale that's resilience; at country scale, sovereignty.

## How that shows up in the code

- **Determinism over magic.** Reproducible outputs, no silent overwrites, no hidden state.
- **Multiple supply lines.** MIT, self-hostable, no vendor lock-in. Solution A, backup B,
  challenger C.
- **Decisions are written down.** Every non-obvious choice gets an ADR, so the _why_ is
  auditable — not just the _what_.

## Projects

| Project                                                           | Lang | Status     | What it is                                                                                                                                                                                                                                                              |
| ----------------------------------------------------------------- | ---- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Agent-O-Matic](https://github.com/constantin-jais/Agent-O-Matic) | Rust | `v0` · WIP | Deterministic, agent-agnostic **config compiler**: one TOML source → native configs for many AI coding agents, with **safe-write** (never clobber a hand-edit) and **drift detection** (CI gate). A clean-room study of the two subsystems mature tools leave implicit. |

_More tools ship from the same discipline — MIT, Rust, ADR-driven, deterministic._

## Reach me

- **LinkedIn** — [linkedin.com/in/constj](https://www.linkedin.com/in/constj/)
- Open to talking about sovereign/self-hosted AI, agent tooling, and getting rigorous systems
  adopted in regulated spaces.

---

_Building in the open. MIT · Rust · ADR-driven · deterministic. No silent failures._
