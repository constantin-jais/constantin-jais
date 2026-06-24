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
- **Isolated responsibility.** Each repository owns one layer and one job; composition beats scope creep.

## Ecosystem doctrine

The projects are organized as four isolated but composable layers:

- **Rumble — Products:** what users see and use.
- **Bolt — Orchestration:** how intent becomes safe execution.
- **Wrench — Tooling:** deterministic transformation, inspection, and validation capabilities.
- **Gear — Infrastructure:** sovereign memory, distribution, integrity, and release substrate.

Rule of thumb:

> A layer may consume capabilities from lower layers, but must not absorb their responsibility.

That means a product can call an extractor without becoming one; an orchestrator can coordinate memory without owning storage; infrastructure can provide primitives without embedding business logic.

## Projects

The portfolio is split by responsibility, not by technology. Each family has a clear job in the chain: **Rumble creates the user experience, Bolt coordinates decisions, Wrench provides callable capabilities, and Gear supplies the sovereign substrate.**

### Rumble — product experiences

**Rumble projects are what people touch.** They turn the lower layers into useful products: learning sessions, notes, prototypes, collaboration boards, and public knowledge surfaces.

They own UX, workflows, and product framing. They should not own raw ingestion, orchestration internals, artifact distribution, or infrastructure truth.

| Project                                                           | Role | Product boundary |
| ----------------------------------------------------------------- | ---- | ---------------- |
| [rumble-lm](https://github.com/constantin-jais/Rumble-LM)         | Learning | Sovereign collaborative learning sessions; not a generic chat app. |
| [rumble-cos](https://github.com/constantin-jais/rumble-cos)       | Showroom | Public knowledge and project distribution; not a monolithic CMS. |
| [rumble-canvas](https://github.com/constantin-jais/Rumble-Canvas) | Prototyping | Natural-language UI prototyping connected to code; not a full design suite. |
| [rumble-paint](https://github.com/constantin-jais/Rumble-Paint)   | Visual design | Visual/spatial UI refinement; not conversational orchestration. |
| [rumble-crew](https://github.com/constantin-jais/Rumble-Crew)     | Collaboration | Human/agent task visibility; not the orchestration brain. |
| [rumble-note](https://github.com/constantin-jais/Rumble-Note)     | Knowledge capture | Local-first block notes and capture; not the secure vault or ingestion engine. |
| [rumble-vault](https://github.com/constantin-jais/Rumble-Vault)   | Secure knowledge | Secure local-first personal knowledge vault; not a duplicate notes app. |

### Bolt — orchestration and decisions

**Bolt is the coordination layer.** It turns intent into safe, inspectable execution: plans, gates, delegation, safe writes, and operational evidence.

It decides how work should happen, but it should not become the product UI, the extractor, the database, or the package registry.

| Project                                                   | Role | Product boundary |
| --------------------------------------------------------- | ---- | ---------------- |
| [cos-matic](https://github.com/constantin-jais/cos-matic) | Orchestration | Deterministic config compiler and autonomous code-ops harness; not a product UI. |

### Wrench — tools and inspection

**Wrench projects are specialized capabilities.** They extract, transform, inspect, validate, and produce evidence that products and orchestrators can trust.

They do the technical dirty work, but they should not own product strategy, long-term truth, or autonomous decisions.

| Project                                                               | Role | Product boundary |
| --------------------------------------------------------------------- | ---- | ---------------- |
| [wrench-loader](https://github.com/constantin-jais/wrench-loader)     | Ingestion | Sovereign rich-document extraction to canonical text/metadata; not knowledge management. |
| [wrench-inspect](https://github.com/constantin-jais/wrench-inspect)   | Inspection | General structural/design/policy validation; not DB-specific security ownership. |
| [vault-inspector](https://github.com/constantin-jais/vault-inspector) | DB audit | SQL/Postgres/RLS/grants/migration inspection; not a vault application. |

### Gear — sovereign infrastructure

**Gear projects are the system physics.** They provide memory, distribution, policy, provenance, and release wiring so the rest of the ecosystem can stay local-first, reproducible, and sovereign.

They supply primitives. They should not contain product workflows, business logic, or agent decision-making.

| Project                                                       | Role | Product boundary |
| ------------------------------------------------------------- | ---- | ---------------- |
| [gear-memory](https://github.com/constantin-jais/gear-memory) | Memory | Local agentic context and retrieval substrate; not an agent brain. |
| [gear-depot](https://github.com/constantin-jais/gear-depot)   | Supply chain | Registry proxy/cache, provenance, and policy; not a generic file store. |
| [gear-cable](https://github.com/constantin-jais/gear-cable)   | Distribution | Rust-first release and artifact wiring; not application runtime logic. |

_More tools ship from the same discipline — MIT, Rust, ADR-driven, deterministic._

## How it fits together

```mermaid
graph TD
    subgraph Rumble_Layer ["🎯 Rumble (Products)"]
        RL["rumble-lm<br/>Learning Platform"]
        RC["rumble-cos<br/>Showroom"]
        RCanvas["rumble-canvas<br/>UI Prototyping"]
        RCrew["rumble-crew<br/>Agent Board"]
        RNote["rumble-note<br/>Knowledge Capture"]
        RVault["rumble-vault<br/>Secure Vault"]
        RPaint["rumble-paint<br/>Visual Design"]
    end

    subgraph Bolt_Layer ["🧠 Bolt (Orchestration)"]
        CM["cos-matic<br/>Planner / Gates / Execution"]
    end

    subgraph Wrench_Layer ["🛠️ Wrench (Tooling)"]
        WL["wrench-loader<br/>Ingestion"]
        WI["wrench-inspect<br/>General Inspection"]
        VI["vault-inspector<br/>DB Security Evidence"]
    end

    subgraph Gear_Layer ["⚙️ Gear (Infrastructure)"]
        GM["gear-memory<br/>Context Substrate"]
        GD["gear-depot<br/>Artifact Policy"]
        GC["gear-cable<br/>Release Wiring"]
    end

    RCanvas --> CM
    RCrew --> CM
    RL --> CM
    CM --> WL
    CM --> WI
    CM --> VI
    WL --> GM
    WI --> GM
    VI --> GM
    GM --> GD
    GC --> GD
    GD --> RL
    GD --> RC
    GD --> RCanvas
    GD --> RCrew
    GD --> RNote
    GD --> RVault
    GD --> RPaint
```

## Reach me

- **LinkedIn** — [linkedin.com/in/constj](https://www.linkedin.com/in/constj/)
- Open to talking about sovereign/self-hosted AI, agent tooling, and getting rigorous systems
  adopted in regulated spaces.

---

_Building in the open. MIT · Rust · ADR-driven · deterministic. No silent failures._
