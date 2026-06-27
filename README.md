Hey 👋 I'm Constantin

I build **resilient Rust systems for trustworthy AI, sovereign tooling, and auditable automation**.

My work sits at the intersection of:

- **Rust backend & CLI tooling**
- **agentic systems and AI orchestration**
- **deterministic, auditable infrastructure**
- **sovereign / self-hostable software**
- **security, supply-chain, and regulated environments**

I come from **critical embedded systems** — C, VHDL, real-time constraints, zero-error tolerance — and I now apply the same discipline to AI-era software: no silent failures, no hidden state, no unnecessary lock-in.

## Ecosystem doctrine

My forge is organized as four isolated but composable layers:

- **Rumble — Products:** what users see and use.
- **Bolt — Orchestration:** how intent becomes safe execution.
- **Wrench — Tooling:** deterministic transformation, inspection, and validation capabilities.
- **Gear — Infrastructure:** sovereign memory, distribution, integrity, and release substrate.

Rule of thumb:

> A layer may consume capabilities from lower layers, but must not absorb their responsibility.

That means a product can call an extractor without becoming one; an orchestrator can coordinate memory without owning storage; infrastructure can provide primitives without embedding business logic.

## Projects

The portfolio is split by responsibility, not by technology. Each family has a clear job in the chain: **Rumble creates learning pressure through real product-shaped experiences, Bolt coordinates decisions, Wrench provides callable capabilities and critique, and Gear supplies the sovereign substrate.**

Current ecosystem status is tracked in [`ecosystem/status.md`](ecosystem/status.md); the target self-improving loop is described in [`ecosystem/loop.md`](ecosystem/loop.md).

### Rumble — product experiences

**Rumble projects are what people touch.** They turn the lower layers into useful products: product-conception workspaces, learning sessions, notes, agent boards, and public knowledge surfaces.

They own UX, workflows, and product framing. They should not own raw ingestion, orchestration internals, artifact distribution, or infrastructure truth. Product needs should instead create reusable Bolt, Wrench, and Gear capabilities that feed the whole ecosystem.

| Project                                                           | Role | Product boundary |
| ----------------------------------------------------------------- | ---- | ---------------- |
| [rumble-canvas](https://github.com/constantin-jais/Rumble-Canvas) | Product conception | Turn conversations into specs, screens, and implementation-ready deliverables; not just a design canvas. |
| [rumble-cos](https://github.com/constantin-jais/rumble-cos)       | Education blog | Personal education and sharing surface for essays, courses, resources, and ecosystem explanations; not a monolithic CMS. |
| [rumble-feed-mind](https://github.com/constantin-jais/rumble-feed-mind) | Intelligent watch pipeline | Curates high-volume feeds into explainable, reusable knowledge for the harness; not the generic ingestion engine, memory substrate, or AI provider. |
| [rumble-crew](https://github.com/constantin-jais/Rumble-Crew)     | Agentic teamwork | Humans and agents side by side with tasks, status, blockers, skills, and evidence; not the orchestration brain. |
| [rumble-lm](https://github.com/constantin-jais/Rumble-LM)         | Learning facilitation | Grounded learning sessions, live activities, and audience engagement; not a generic chat app. |
| [rumble-note](https://github.com/constantin-jais/Rumble-Note)     | Personal knowledge | Local-first block notes that feed the agentic harness; not the ingestion engine or orchestrator. |

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
| `wrench-inspect`                                                     | Inspection | General structural/design/policy validation; planned companion, no public repo yet; not DB-specific security ownership. |
| [wrench-db-inspect](https://github.com/constantin-jais/wrench-db-inspect) | DB audit | SQL/Postgres/RLS/grants/migration inspection; not a vault application. |

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
        RFM["rumble-feed-mind<br/>Watch Pipeline"]
        RCanvas["rumble-canvas<br/>Product Conception"]
        RCrew["rumble-crew<br/>Agentic Teamwork"]
        RNote["rumble-note<br/>Knowledge Capture"]
    end

    subgraph Bolt_Layer ["🧠 Bolt (Orchestration)"]
        CM["cos-matic<br/>Planner / Gates / Execution"]
    end

    subgraph Wrench_Layer ["🛠️ Wrench (Tooling)"]
        WL["wrench-loader<br/>Ingestion"]
        WI["wrench-inspect<br/>General Inspection"]
        VI["wrench-db-inspect<br/>DB Security Evidence"]
    end

    subgraph Gear_Layer ["⚙️ Gear (Infrastructure)"]
        GM["gear-memory<br/>Context Substrate"]
        GD["gear-depot<br/>Artifact Policy"]
        GC["gear-cable<br/>Release Wiring"]
    end

    RCanvas --> CM
    RCrew --> CM
    RL --> CM
    RFM --> CM
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
    GD --> RFM
    GD --> RCanvas
    GD --> RCrew
    GD --> RNote
```

## Reach me

- **LinkedIn** — [linkedin.com/in/constj](https://www.linkedin.com/in/constj/)
- Open to talking about sovereign/self-hosted AI, agent tooling, and getting rigorous systems
  adopted in regulated spaces.

---

_Building in the open. MIT · Rust · ADR-driven · deterministic. No silent failures._
