# Hey 👋 I'm Constantin

[![Spec contracts](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/spec-contracts.yml)
[![Forge health](https://github.com/constantin-jais/constantin-jais/actions/workflows/forge-health.yml/badge.svg?branch=main)](https://github.com/constantin-jais/constantin-jais/actions/workflows/forge-health.yml)

I build **open-source, product-shaped tools for learning, knowledge work, agentic teamwork, and trustworthy automation**.

The visible layer is **Rumble**: products people can use. Underneath, **Bolt**, **Wrench**, and **Gear** form a deterministic, sovereign forge for orchestration, inspection, memory, release, and provenance.

## Start here

| If you want to... | Start with | Status |
| --- | --- | --- |
| see the public product surface | [rumble-cos](https://github.com/constantin-jais/rumble-cos) | `usable` |
| try the feed-to-knowledge pipeline | [rumble-feed-mind](https://github.com/constantin-jais/rumble-feed-mind) | `dojo` |
| inspect the orchestration core | [cos-matic](https://github.com/constantin-jais/cos-matic) | `usable` |
| explore DB/security evidence | [wrench-db-inspect](https://github.com/constantin-jais/wrench-db-inspect) | `dojo` |
| understand the whole stack | [`ecosystem/status.md`](ecosystem/status.md) | live cockpit |

## Rumble products

Rumble projects are the product layer: the things people can read, run, touch, or eventually use directly.

| Product | Purpose | Maturity | Scale-ready? |
| --- | --- | --- | --- |
| [rumble-cos](https://github.com/constantin-jais/rumble-cos) | education blog and public knowledge surface | `usable` | partially |
| [rumble-feed-mind](https://github.com/constantin-jais/rumble-feed-mind) | intelligent feed/watch pipeline | `dojo` | no |
| [rumble-lm](https://github.com/constantin-jais/Rumble-LM) | grounded learning sessions and facilitation | `contract-first` | no |
| [rumble-canvas](https://github.com/constantin-jais/Rumble-Canvas) | product-conception workspace | `contract-first` | no |
| [rumble-crew](https://github.com/constantin-jais/Rumble-Crew) | agentic teamwork board | `contract-first` | no |
| [rumble-note](https://github.com/constantin-jais/Rumble-Note) | local-first personal knowledge | `contract-first` | no |

`scale-ready` is not a maturity status. It means deployment, observability, security boundaries, and operational constraints are explicit enough for broader use.

## Forge underneath

The forge layers exist to make Rumble products reliable without turning every product into a monolith.

| Layer | Role | Main repos |
| --- | --- | --- |
| **Bolt** | safe orchestration, plans, gates, evidence | [cos-matic](https://github.com/constantin-jais/cos-matic) |
| **Wrench** | inspection, validation, extraction, reports | [wrench-loader](https://github.com/constantin-jais/wrench-loader), [wrench-db-inspect](https://github.com/constantin-jais/wrench-db-inspect) |
| **Gear** | memory, artifacts, release, provenance, supply-chain | [gear-memory](https://github.com/constantin-jais/gear-memory), [gear-depot](https://github.com/constantin-jais/gear-depot), [gear-cable](https://github.com/constantin-jais/gear-cable) |

Detailed status, maturity vocabulary, caveats, and verification commands live in [`ecosystem/status.md`](ecosystem/status.md). The target self-improving loop is described in [`ecosystem/loop.md`](ecosystem/loop.md).

## Principles

- **Products first.** Rumble is what people touch; the forge exists to make it reliable.
- **Determinism over magic.** Reproducible outputs, no silent overwrites, no hidden state.
- **No silent failures.** Failure modes should be explicit, inspectable, and testable.
- **Sovereign by default.** Self-hostable, permissive OSS, no unnecessary vendor lock-in.
- **Evidence over claims.** Maturity, releases, and decisions should point to tests, fixtures, CI, ADRs, or demos.

## Open-source evidence

This ecosystem dogfoods its own forge discipline:

- spec-contract workflows validate ecosystem schemas and fixtures;
- forge-health checks track repository workflow conventions;
- maturity and known limits are tracked in [`ecosystem/status.md`](ecosystem/status.md);
- contribution paths are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`ROADMAP.md`](ROADMAP.md).

Contributions are most useful when they improve docs, examples, fixtures, tests, error messages, or small well-scoped behavior. Larger architecture or product-scope changes should start as design discussions.

## Reach me

- **LinkedIn** — [linkedin.com/in/constj](https://www.linkedin.com/in/constj/)
- Open to discussing sovereign/self-hosted AI, Rust tooling, agentic systems, and reliable software for regulated environments.

---

_Building in the open. MIT · Rust · ADR-driven · deterministic. No silent failures._
