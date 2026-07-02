# Gear Onboarding

Status: P0 onboarding guide.

Audience: humans and agents discovering the Gear layer before implementation.

## 1. Gear in 5 Minutes

Gear is the infrastructure layer for verifiable local-first truth.

It provides stable, auditable, exportable references for sources, artifacts, memory, code maps, events, hashes, lifecycle state, and provenance.

Short definition:

> Gear turns content, artifacts, and events into stable references that can be verified, indexed, synchronized, revoked, deleted, anonymized, and replayed offline.

Gear does not decide what should happen next. It makes reliable references available so Rumble products, Wrench tools, and Bolt orchestration can act safely in their own layers.

## 2. What Gear Centralizes

Gear exists to prevent every Rumble from rebuilding dangerous infrastructure locally.

| Repeated need | Gear primitive | Why centralize it |
| --- | --- | --- |
| cite or reuse a source | `SourceRef` | one source identity/hash/provenance model across products |
| package produced output | `ArtifactRef` / `ArtifactManifest` | immutable output references, revocation, verification |
| search/index context | `MemoryEntry` | deletion/anonymization/stale behavior is security-sensitive |
| link source/code/document graph | graph edges / `CodeMap` | avoids incompatible code graphs in Bolt/Crew/Canvas |
| prove who produced what | `ProvenanceRecord` | evidence over claims, reproducible chains |
| audit substrate transitions | `EventLogEntry` | safe reference-only event history |
| delete/anonymize/revoke | lifecycle states + tombstones | RGPD and offline sync must not diverge by product |

## 3. What Gear Solves

### 3.1 Reliable references

A product can pass a reference instead of copying raw content:

- LM cites `SourceRef` IDs instead of raw documents;
- Crew stores evidence refs instead of raw logs;
- Canvas hands Bolt package refs instead of private context dumps;
- Note exports selected blocks instead of granting unrestricted note access.

### 3.2 Provenance and auditability

Gear records:

- actor reference;
- operation;
- input refs;
- output refs;
- tool/build refs;
- timestamp;
- safe metadata.

This lets agents and humans ask: “where did this come from and can I trust it?”

### 3.3 Local-first/offline-first operation

Core truth must work without hosted services:

- local structured store;
- deterministic hashes;
- replayable event/provenance streams;
- exportable JSON/NDJSON;
- offline fixture validation.

Network sync may improve collaboration, but it must not be required for core truth.

### 3.4 RGPD lifecycle enforcement

Gear standardizes lifecycle transitions:

```text
active → stale
active → deleted
active → anonymized
active → revoked
```

Deletion/anonymization must remove searchable payloads from full-text/vector/graph/code indexes while retaining only legal/audit-safe references when policy allows.

### 3.5 Agent-readable context without magic

Gear returns references, states, hashes, excerpts only when allowed, and provenance. It does not return an instruction like “do this next”.

Compact prompt projections are allowed only when generated from canonical records and round-trip tested.

## 4. What Gear Does Not Do

| If the feature primarily... | It belongs in... | Example |
| --- | --- | --- |
| decides, sequences, gates, refuses, retries | Bolt | `cos-matic` planning/refusal/gates |
| parses, extracts, inspects, validates | Wrench | HTML/PDF/feed ingestion, policy inspection |
| defines screens, workflows, product meaning | Rumble | note UX, LM activities, Crew board |
| owns delegated authorization semantics | Biscuit/shared auth | attenuated rights, caveats, revocation refs |
| distributes packages/releases | Gear Depot/Cable subdomains | manifests, releases, install floors |

Hard non-goals:

- no agent brain;
- no product UI;
- no hidden ranking of importance;
- no crawler/feed product;
- no parser implementation inside Gear Memory;
- no opaque hosted storage;
- no raw PII/secrets in logs or debug metadata.

## 5. Gear Subdomains

| Subdomain | Mission | P0 files |
| --- | --- | --- |
| `gear-memory` | local-first memory/source/code graph/index/provenance substrate | `04-gear-memory-substrate.md`, `05-gear-memory-consumer-alignment.md`, `gear-memory.v0.1.schema.json` |
| `gear-depot` | artifact/package manifests, verification, retention, revocation, artifact trust state | `03-depot-artifact-manifest.md` |
| `gear-cable` | release/distribution planning inputs, install floors, target matrices, checksums/signature planning | boundary documented in decision log; detailed spec later |

## 6. Key Object Vocabulary

### SourceRef

Referenced input or grounding material: file, URL, feed item, note block export, transcript, document, dataset, or prior artifact reused as source.

Think: “something we can cite or ground against.”

### ArtifactRef

Produced, versioned, packageable output: spec package, handoff payload, curated export, inspection report, learning export, release asset.

Think: “something produced and verifiable.”

### MemoryEntry

Indexed snapshot rooted in a `SourceRef`.

Think: “searchable/indexable view of a source at a point in time.”

### CodeMap

Reproducible source/code symbol and edge map over `SourceRef` values. Wrench parses; Gear stores/indexes.

Think: “code graph reference map, not code truth.”

### ProvenanceRecord

Reference-only chain of actor, operation, input refs, output refs, tool refs, timestamp, safe metadata.

Think: “who/what/when/how, without raw secrets.”

### EventLogEntry

Append-only safe event for substrate transitions.

Think: “state changed, here is the safe reference trail.”

### ArtifactManifest

Depot-owned manifest for artifact integrity, hash, included files, retention, revocation, distribution metadata.

Think: “artifact verification envelope.”

## 7. Source vs Artifact Rule

Source and Artifact are lifecycle roles, not mutually exclusive identities.

Example:

```text
feed item observed by FeedMind
→ SourceRef
curated feed bundle exported
→ ArtifactRef
that curated bundle reused by LM as grounding input
→ SourceRef of type artifact pointing at ArtifactRef
```

Gear records the lifecycle explicitly. It does not infer product meaning.

## 8. Typical Flows

### 8.1 Gear Loader → Gear Memory → Rumble LM citation

```text
URL/PDF/Feed item
→ Gear Loader extracts CanonicalSourceDocument + LoaderEvidenceReport
→ Gear receives GearSourceCandidate
→ Gear creates SourceRef + MemoryEntry + ProvenanceRecord
→ LM source set references SourceRef
→ citation resolves to source ref, hash, state, provenance
```

Solved: LM does not implement its own ingestion, source database, or provenance store.

### 8.2 Rumble Note export → Gear Memory → Canvas context

```text
User selects note blocks
→ NoteContextExport excludes private/no_handoff/sensitive blocks by default
→ Gear creates SourceRef per exported block/projection
→ MemoryEntry indexes allowed context
→ Canvas/Bolt receive refs, not unrestricted note access
```

Solved: Note remains product UX; Gear handles indexing and stale/delete propagation.

### 8.3 FeedMind item → curated artifact → LM source

```text
FeedMind requests feed parsing
→ Gear Loader normalizes feed item
→ Gear Memory stores feed item as SourceRef
→ FeedMind curates bundle
→ Gear Depot stores curated export as ArtifactRef
→ LM reuses artifact as source via SourceRef(type=artifact)
```

Solved: feed provenance survives reuse across products.

### 8.4 Canvas package → Depot artifact → Bolt plan

```text
Canvas approves SpecPackage
→ Gear Depot records ArtifactRef/ArtifactManifest
→ Bolt planning request cites artifact refs and hashes
→ Bolt validates/gates/plans without storing package body
```

Solved: Bolt does not become artifact store or product spec database.

### 8.5 Crew evidence → Gear refs → Bolt gate

```text
Crew task gathers evidence
→ evidence stored as artifact/source refs
→ runtime logs remain privileged/non-indexed with safe metadata only
→ Bolt consumes EvidenceRef + Gear refs
→ stale/quarantined/missing refs block planning/execution gates
```

Solved: Crew does not invent an unsafe evidence store.

## 9. “Does This Belong in Gear?” Checklist

Answer “yes” to Gear if the feature primarily:

- stores a reference;
- indexes source/materialized content;
- records provenance;
- verifies hashes/manifests;
- tracks lifecycle state;
- syncs/replays local-first substrate state;
- connects artifacts/sources through references.

Answer “no” and route elsewhere if it primarily:

- decides what should happen next → Bolt;
- extracts/parses/validates content → Wrench;
- defines user-facing workflow/meaning → Rumble;
- grants/verifies delegated rights → Biscuit/shared auth;
- runs arbitrary commands → Bolt/runtime future;
- ranks what matters to a user → Rumble/Bolt policy, not Gear.

## 10. Read Path

For a new contributor:

1. Read this file.
2. Read `README.md` for file map.
3. Read `00-gear-boundaries.md` for layer boundaries.
4. Read `04-gear-memory-substrate.md` for Gear Memory P0.
5. Read `05-gear-memory-consumer-alignment.md` for Rumble/Bolt/Wrench seams.
6. Inspect `gear-memory.v0.1.schema.json` and `fixtures/memory/`.
7. Run `sh ../ci-validate-contracts.sh` from repository root as `sh ecosystem/specs/ci-validate-contracts.sh`.

## 11. Mental Model

Gear is not where intelligence lives. Gear is where references become trustworthy.

If a future feature makes agents more capable by giving them reliable, current, provenance-backed references, it probably belongs near Gear.

If it makes a choice, applies product meaning, or tells the user what matters, it does not.
