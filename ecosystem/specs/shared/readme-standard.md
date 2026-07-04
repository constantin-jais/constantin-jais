# README standard guardrail

Status: Active guardrail after the 2026-07-04 README rollout
Related: ADR 0033 (layer model and `deployment_class`), ecosystem maturity claims

## Purpose

Every public Rumble/Bolt/Wrench/Gear/Portal repository should make its real state obvious before a reader reaches quickstart commands or badges. The header is a truth surface, not marketing copy: maturity must stay conservative, current, and tied to visible evidence.

The guardrail is intentionally mechanical. It catches missing fields, vocabulary drift, empty sections, and machine-local paths. It does **not** decide whether a maturity claim is true; that remains a human review against tests, fixtures, CI, ADRs, demos, and known limits.

## Canonical header

Place this block immediately after the H1 title:

```markdown
# repo-name

**Couche** : Rumble | Bolt | Wrench | Gear | Portal | Control plane
**Rôle** : one-line role, in current tense
**deployment_class** : product-linkable | factory-only | build-time
**Maturité** : level — concise evidence and explicit caveat
**Place dans la chaîne DoD** : where this repo contributes to proof-gated delivery.
**Doctrine** : the rule this repo must not violate.
**Souveraineté** : licences MIT/Apache/MPL compatibles ; pas d’AGPL/SSPL dans la chaîne versionnée.

## Ce que ça fait

Short current-state explanation, including what is deliberately not done yet.

## Où ça se branche

- Amont : upstream contracts, specs, inputs, or evidence.
- Aval : products, gates, users, or downstream services.
- Contrats/preuves : schemas, fixtures, CI, demos, reports, or ADRs.
```

## Field rules

- `Couche` follows ADR 0033: `Rumble`, `Portal`, `Bolt`, `Wrench`, `Gear`, or the control plane when documenting the ecosystem itself.
- `deployment_class` is one of `product-linkable`, `factory-only`, `build-time`.
- `Maturité` starts with a conservative level and includes a qualifier after an em dash. A bare label is not enough.
- `Place dans la chaîne DoD` must say how the repo participates in proof-gated delivery.
- `Doctrine` states the boundary that prevents misuse or scope inflation.
- `Souveraineté` explicitly mentions permissive-compatible licensing (`MIT/Apache/MPL`) and banned-license exclusion (`AGPL/SSPL`).

## Maturity rubric

Use the lowest honest level that describes the current repository state:

| Level | Use when | Do not imply |
| --- | --- | --- |
| `contract-first` | specs, contracts, fixtures, stubs, or scaffolding are useful, but the product/runtime is not complete | usable product, operational service, scale-readiness |
| `dojo` | a working slice exists and is useful for learning/proof, with known caveats | production readiness or broad external-user quality |
| `usable` | the repo performs its stated role for maintainers/users under documented constraints | scale-readiness, no known limits |
| `frozen` | the repo is intentionally paused or kept for compatibility/evidence | active roadmap or fresh investment |
| `done` | the repo is a finished artifact or benchmark whose value is preservation | evolving runtime component |

`scale-ready` is not a maturity level. It is an operational claim about deployment, observability, security boundaries, and support constraints.

## Validator

Run the dependency-free guardrail from the ecosystem repository:

```bash
python3 ecosystem/tools/readme_guardrail.py ../repo-a ../repo-b/README.md
```

For a fleet check, pass a newline-delimited list of repo directories or README files:

```bash
python3 ecosystem/tools/readme_guardrail.py --from-list readme-paths.txt
```

The validator currently checks:

- the seven canonical fields;
- accepted layer and `deployment_class` vocabulary;
- an explicit maturity qualifier;
- the two required sections;
- sovereign licensing vocabulary;
- absence of machine-local paths.

It deliberately does not rewrite README files or enforce exact prose beyond the contract above.
