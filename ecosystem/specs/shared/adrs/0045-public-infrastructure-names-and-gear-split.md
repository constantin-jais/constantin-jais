# ADR 0045 — Public infrastructure names and Gear split

Status: Accepted
Date: 2026-07-11
Decision owner: Constantin Jais
Supersedes in naming only: ADR 0033 family labels
Related: ADR 0028, ADR 0031, ADR 0033, ADR 0038, ADR 0043

## Context

The consolidated repositories proved the technical boundaries of Portal, Bolt, Wrench and Gear, but their short internal family names do not explain those boundaries on a public forge. Gear also contains two intentionally isolated Cargo workspaces with different credentials, consumers and release lifecycles. Keeping the public topology aligned with ownership now matters more than preserving temporary consolidation names.

Boussole Politique has also joined the public portfolio. Its civic methodology, local political preferences and source datasets must not become infrastructure-owned state merely because it consumes shared technical capabilities.

## Decision

### Public repositories

The following target names are ratified:

| Current repository | Target repository | Bounded meaning |
| --- | --- | --- |
| `libre-ai/portal` | `libre-ai/client-kit` | Client primitives, adaptive Dioxus UI, accessibility, tokens, bindings, adapters and canonical app templates. |
| `libre-ai/bolt` | `libre-ai/agent-factory` | Bounded planning and orchestration with explicit handoffs, approvals, refusals and evidence. It is not a general autonomous-agent platform. |
| `libre-ai/wrench` | `libre-ai/proof-kit` | Reproducible inspection evidence for structure, databases, accessibility and target experiments. “Proof” does not mean formal verification. |
| `libre-ai/gear` | `libre-ai/context-kit` plus `libre-ai/artifact-supply` | Context owns ingestion, source references and memory; Artifact Supply owns manifests, packaging, provenance and distribution. |

Simple renames use GitHub repository redirects. Gear is not renamed into one half: both workspaces are extracted with path history, while `libre-ai/gear` remains archived as the compatibility and full-history repository until every consumer and published URL has moved.

Existing crate names, binary names, schema identifiers, release archive names and contract discriminants remain compatibility interfaces. They change only through separately versioned migrations; a repository rename alone never changes them.

### Boussole Politique

`libre-ai/boussole-politique` is an autonomous, local-first civic product. It owns political methodology, scoring semantics, source selection and private citizen positions. It may consume renderer-independent client primitives and explicit context/artifact contracts, but it does not share a product database, identity store or political domain model with infrastructure repositories. `mes-elus` remains a historical identifier only.

### Control plane

The target control-plane location is `libre-ai/ecosystem`. Transfer remains blocked until GitHub Support confirms hidden-ref/cache cleanup and a fresh privacy scan, bundle and ref manifest pass. No rename or transfer bypasses that gate.

## Migration protocol

1. Freeze concurrent repository mutation for the repository being moved.
2. Record all refs, rulesets, releases, Pages, environments, packages, topics and consumers; create and hash a full bundle.
3. For a simple rename, rename one repository, update the local directory and remotes, then update policy, profiles, metadata and consumers before starting the next rename.
4. For Gear, create path-history repositories for `context/` and `supply/`, verify their independent builds and supply-chain gates, migrate consumers and releases, then archive the full-history compatibility repository.
5. Keep `main` green between every operation. Required checks and rulesets must refer to contexts that actually run on pull requests.
6. Preserve old public identifiers only in an explicit compatibility/historical allowlist. New documentation uses target names.
7. Prefer archive to deletion. Deletion requires a privacy/security reason plus verified recovery bundles and a zero-release/zero-consumer record.

## Acceptance criteria

- repository profiles, branch policy and public metadata match the live topology;
- old simple-rename URLs redirect and release assets remain downloadable;
- Gear consumers use one or both extracted repositories without cross-workspace path dependencies;
- Pages, release workflows, SBOMs and attestations remain attributable after migration;
- a public-tree scan finds no unprofiled `libre-ai/*` repository URL;
- all primary local clones are clean, on their canonical branches and under `Documents/<owner>/<repository>`;
- no support claim for Dioxus desktop/mobile is promoted by a rename.

## Consequences

The architecture boundaries remain those proved by the consolidated repositories; only their public expression changes. Documentation and migration fixtures may retain Portal/Bolt/Wrench/Gear as historical terms, but active public surfaces move to Client Kit, Agent Factory, Proof Kit, Context Kit and Artifact Supply. The split increases release and policy count, but removes a credential and lifecycle ambiguity that a single Gear repository could only mitigate, not eliminate.
