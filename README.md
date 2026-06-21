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

| Project                                                               | Lang | Status          | What it is                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------- | ---- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Presto-Matic](https://github.com/constantin-jais/Rumble-LM)          | Rust | `v0.1` · active | Self-hostable collaborative learning platform: AI-generated, source-grounded study content (quiz, flashcards, mind maps) in real-time sessions for 200+ participants. Sovereign/BYO-keys, RGPD-compliant, Clever Cloud default.             |
| [Agent-O-Matic](https://github.com/constantin-jais/Agent-O-Matic)     | Rust | `v0` · WIP      | Deterministic, agent-agnostic **config compiler and harness**: one TOML source → native configs for many AI coding agents, with **safe-write** (never clobber a hand-edit), **drift detection** (CI gate), and incident/gate orchestration. |
| [memory-card](https://github.com/constantin-jais/memory-card)         | Rust | Planned         | Local agentic context layer: code map, repo memory, document/search substrate for coding agents — inspired by basemind, but shaped for the Agent-O-Matic ecosystem.                                                                         |
| [disc-loader](https://github.com/constantin-jais/disc-loader)         | Rust | Planned         | Sovereign rich-document ingestion worker/service: Xberg-backed extraction for PDF, Office, OCR, HTML, and archives into canonical text and metadata.                                                                                        |
| [vault-inspector](https://github.com/constantin-jais/vault-inspector) | Rust | Planned         | SQL and database security inspection: Scythe-backed lint/audit/inspect for Postgres, pgvector, RLS, grants, migrations, and CI evidence.                                                                                                    |
| [supply-depot](https://github.com/constantin-jais/supply-depot)       | Rust | Planned         | Sovereign supply-chain depot: Starmetal-backed registry proxy/cache and policy POC across Cargo, npm, PyPI, and other ecosystems.                                                                                                           |
| [link-cable](https://github.com/constantin-jais/link-cable)           | Rust | `v0` · WIP      | Rust-first distribution substrate for multi-platform developer tools: forward-only releases, artifact plans, checksums/signatures/provenance, and sovereign install floors.                                                                 |

_More tools ship from the same discipline — MIT, Rust, ADR-driven, deterministic._

## How it fits together

```mermaid
graph TB
    subgraph product["🎯 Product"]
        RL["Presto-Matic · rumble-lm<br/>Collaborative Learning App"]
    end
    subgraph agentic["🤖 Agentic Tools"]
        AOM["agent-o-matic<br/>Config Compiler + Orchestrator"]
        DL["disc-loader<br/>Document Ingestion Worker"]
        MC["memory-card<br/>Local Agent Context"]
    end
    subgraph devops["🔧 DevOps Tools"]
        LC["link-cable<br/>Distribution Substrate"]
        SD["supply-depot<br/>Registry Proxy / Cache"]
        VI["vault-inspector<br/>Postgres Security Audit"]
    end
    RL --> DL
    RL --> MC
    RL --> VI
    RL --> SD
    RL --> LC
    AOM --> LC
    DL --> MC
```

## Reach me

- **LinkedIn** — [linkedin.com/in/constj](https://www.linkedin.com/in/constj/)
- Open to talking about sovereign/self-hosted AI, agent tooling, and getting rigorous systems
  adopted in regulated spaces.

---

_Building in the open. MIT · Rust · ADR-driven · deterministic. No silent failures._
