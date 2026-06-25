# GitHub Stars Stack Audit Design

Date: 2026-06-30
Status: Draft for review

## Context

The public GitHub starred list for `constantin-jais` contains 80 repositories as
of 2026-06-30. The repositories are heterogeneous: product inspirations,
technical primitives, learning material, agent workflows, security references,
privacy resources, and projects that should not enter the stack directly.

The ecosystem already uses four ownership layers:

- Rumble owns product experience, workflows, screens, and user-facing meaning.
- Bolt owns orchestration, sequencing, execution gates, and run lifecycle.
- Wrench owns extraction, transformation, inspection, validation, and evidence.
- Gear owns storage, indexing, provenance, packaging, distribution, auth
  substrate, and offline/local-first infrastructure.

The audit must extract maximum value from the starred repositories without
turning passive watch material into roadmap debt.

## Goal

Create a reproducible audit method that classifies every starred repository by
actionability, ecosystem layer, technical fit, and risk. The output must support
repo-by-repo discussion and produce concrete follow-up decisions for Rumble,
Bolt, Wrench, and Gear.

## Non-Goals

- Do not copy upstream code or product language.
- Do not add dependencies during the audit.
- Do not treat popularity as a stack-fit criterion.
- Do not classify a repository as `rebuild` unless it maps to an existing
  ecosystem need.
- Do not accept AGPL, SSPL, BSL, proprietary, or unclear-license projects as
  direct dependencies.

## Decision Axes

Every classification is measured in this order:

1. Security: attack surface, prompt-injection risk, PII exposure, secrets, auth.
2. Quality: maintainability, explicit contracts, type discipline, testability.
3. Performance: hot-path impact, local-first viability, unnecessary allocation or
   network dependence.
4. Completeness: whether the repository helps complete an existing ecosystem
   contract, product workflow, or quality gate.

Human effort, calendar planning, and MVP framing are not classification axes.

## Repository Record

Each audited repository gets one record:

```text
name:
url:
description:
language:
license:
topics:
stars:
updated_at:
disposition:
layer:
ecosystem_need:
fit_score:
risk_level:
risk_notes:
recommended_action:
discussion_notes:
```

## Disposition

`adopt`
: The project can be used directly as a dependency or tool after license,
security, and contract checks.

`rebuild`
: The idea maps to an existing ecosystem need, but direct adoption is blocked by
architecture, language, license, sovereignty, or product-boundary issues.

`knowledge`
: The project is useful for learning, benchmark comparison, threat modeling, or
product thinking, but it does not create an implementation obligation.

`reject`
: The project does not fit the stack or fails a hard criterion.

`quarantine`
: The project is useful only as hostile input, red-team material, or a cautionary
case. It must not influence prompts, runtime behavior, dependencies, or product
copy without explicit threat-model handling.

## Layer

`rumble`
: Product UX, workflows, user meaning, screens, collaboration, learning, notes,
feeds, content, or productized agent surfaces.

`bolt`
: Agent orchestration, task lifecycle, planning, execution gates, run state,
agent-team management, or deterministic automation.

`wrench`
: Crawling, parsing, extraction, validation, inspection, evals, reports, and
evidence generation.

`gear`
: Storage, local databases, vector/search indexes, auth primitives, provenance,
artifact packaging, release distribution, sync, or memory substrate.

`cross-layer`
: A project informs more than one layer and must be decomposed into layer-owned
capabilities before adoption or rebuild.

`outside`
: Useful personally or educationally, but not part of the ecosystem stack.

## Risk Rules

- `AGPL-3.0`, `SSPL`, `BSL`, and proprietary licenses are direct-dependency
  blockers.
- `GPL-3.0` is not accepted as a direct dependency without an explicit legal and
  architecture decision.
- `NOASSERTION` requires manual license verification before `adopt`.
- Projects centered on OSINT dossiers, default credentials, jailbreaks, or
  prompt-injection payloads default to `quarantine` unless a narrow defensive
  use is documented.
- SaaS-first products that depend on US hyperscalers, closed cloud services, or
  opaque hosted control planes cannot be `adopt`.
- AI/LLM tooling must document provider policy, data residency, and prompt/data
  exposure before integration.

## Fit Score

Use a 0 to 5 score, but never let the number override the textual verdict.

- 5: Directly advances an accepted ecosystem contract with acceptable risk.
- 4: Strong candidate, but needs focused verification.
- 3: Useful influence; likely `knowledge` or `rebuild`.
- 2: Weak or indirect relevance.
- 1: Mostly outside the stack.
- 0: Reject or quarantine.

## Audit Order

1. Import the public starred repository metadata.
2. Normalize name, URL, language, license, description, topics, stars, and update
   timestamp.
3. Apply hard risk filters: license, sovereignty, PII, prompt injection, hosted
   lock-in.
4. Assign primary disposition.
5. Assign layer.
6. Link to an existing ecosystem need or mark `none`.
7. Write a recommended action.
8. Discuss only the ambiguous or high-value records repo by repo.

## Initial Calibration Examples

`eclipse-biscuit/biscuit`
: `adopt`, `gear`, fit 5. Apache-2.0 delegated authorization aligns with the
existing Biscuit auth direction. Bolt consumes the primitive, but Gear owns the
auth substrate contract.

`Goldziher/ai-rulez`
: `knowledge`, `bolt`, fit 4. Strong comparator for `cos-matic`; not copied or
adopted because the ecosystem already chose a clean-room learning and
determinism path.

`xberg-io/xberg`
: `rebuild`, `wrench`, fit 4. Strong document-intelligence inspiration for
`wrench-loader`; adoption requires license, dependency, and boundary review
before any direct dependency decision.

`siyuan-note/siyuan`
: `knowledge`, `rumble`, fit 3. Relevant to `rumble-note`, but AGPL-3.0 blocks
direct adoption.

`PostHog/posthog`
: `knowledge`, `outside`, fit 2. Product analytics is useful conceptually, but
the surface area and data sensitivity are too high for stack adoption without a
separate analytics/product telemetry spec.

`elder-plinius/L1B3RT4S`
: `quarantine`, `outside`, fit 0. Prompt-injection and jailbreak content is only
valid as hostile test material.

## Output Artifact

The next artifact should be a Markdown or CSV audit table under
`ecosystem/specs/shared/` with one row per starred repository. The table should
be stable enough to review in diffs and sortable enough to support batch
analysis.

Recommended columns:

```text
repo | disposition | layer | fit | risk | license | language | ecosystem_need | recommended_action
```

## Acceptance Criteria

- All 80 public starred repositories are represented exactly once.
- Every `adopt` or `rebuild` row names an ecosystem need.
- Every `reject` or `quarantine` row names the blocking reason.
- Every non-permissive or unclear license is visible in the table.
- No row relies on popularity alone as justification.
- The audit can be repeated from GitHub metadata without changing the taxonomy.
