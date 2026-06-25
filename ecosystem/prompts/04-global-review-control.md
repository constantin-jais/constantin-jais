# Prompt — Session Review et Contrôle Global Rumble / Harness

## Mission

Tu es chargé de réaliser une review globale de cohérence produit, architecture, specs, stacks, sécurité, souveraineté et harness readiness.

Objectif central :

> Vérifier que les Rumble alimentent bien le harness, que Bolt/Wrench/Gear restent dans leurs responsabilités, et qu'aucun développement produit ne démarre avant que les contrats critiques soient prêts.

---

## À lire

```text
constantin-jais/ecosystem/overview.md
constantin-jais/ecosystem/specs/README.md
constantin-jais/ecosystem/specs/shared/**
constantin-jais/ecosystem/specs/harness/**
constantin-jais/ecosystem/specs/rumble-*/*.md
cos-matic/README.md
cos-matic/crates/aom/src/handoff.rs
cos-matic/.github/workflows/ci.yml
rumble-feed-mind/README.md
rumble-feed-mind/Cargo.toml
rumble-feed-mind/docs/adr/*.md
gear-memory/README.md
gear-depot/README.md
gear-cable/README.md
wrench-loader/README.md
```

---

## Axes de review

### 1. Produit

Pour chaque Rumble :

- mission claire ?
- non-objectifs clairs ?
- MVP slice défini ?
- rôles définis ?
- écrans/actions définis ?
- modèle métier suffisant ?
- risques produit identifiés ?
- différenciation claire avec les autres Rumble ?

Rumbles à couvrir :

```text
rumble-canvas
rumble-note
rumble-lm
rumble-crew
rumble-cos
rumble-feed-mind
```

### 2. Architecture Layering

Vérifier :

- Rumble ne fait pas Bolt ;
- Rumble ne fait pas Wrench ;
- Rumble ne fait pas Gear ;
- Bolt ne fait pas UI ;
- Wrench ne stocke pas la vérité long terme ;
- Gear ne contient pas de workflow métier.

Signaler tout leak.

### 3. Harness flow

Vérifier que le flow est câblé :

```text
SpecPackage / ExportPackage
→ ImplementationHandoff / ContextExport
→ cosmatic validate
→ cosmatic plan --dry-run
→ Wrench inspect
→ Gear artifact/provenance
→ human approval
→ execution later only
```

Questions :

- Quel produit peut déjà produire un input harness ?
- Quels contrats manquent ?
- Quels tests prouvent le flow ?
- Quel est le prochain flow vertical à implémenter ?

### 4. Shared capabilities

Revoir :

```text
constantin-jais/ecosystem/specs/shared/shared-capabilities.md
```

Classer les capacités :

- P0 : nécessaires maintenant ;
- P1 : bientôt ;
- P2 : garder candidates ;
- Reject : trop prématuré.

Capacités critiques :

- ImplementationHandoff
- SpecPackage
- TraceabilityLink
- Waiver
- ActorReference
- SourceRef
- ArtifactRef
- ProvenanceRecord
- NoteContextExport
- CuratedItemExport
- AgentTaskRequest
- CitationValidation
- Provider/BYOK policy

### 5. Stack coherence

Vérifier :

- Rumble interactifs convergent Rust/Dioxus ;
- `rumble-cos` Astro reste exception justifiée ;
- legacy TS/Expo/Next sont clairement migration refs, pas cible ;
- Bolt/Wrench/Gear restent Rust-first ;
- toute exception a ADR.

### 6. Sécurité / RGPD / souveraineté

Pour chaque produit et contrat :

- PII identifiée ?
- secrets exclus des logs ?
- BYOK policy claire ?
- rétention/suppression définie ?
- audit actor/timestamp présent ?
- no US hyperscaler as core truth ?
- licence compatible ?
- export/handoff minimise les données ?

### 7. Qualité specs

Vérifier :

- dual-format respecté ;
- acceptance criteria testables ;
- events nommés ;
- data model avec invariants ;
- services/API avec idempotency/failure modes ;
- open questions à jour ;
- décisions acceptées dans decision log.

---

## Livrable attendu

Produire un rapport structuré :

```md
# Global Review Report — Rumble Harness

## Executive Summary

## Critical Blockers

## Warnings

## Suggestions

## Product-by-Product Status

### rumble-canvas
- Status
- Strengths
- Missing
- Next action

...

## Shared Capability Prioritization

| Capability | Priority | Owner | Reason | Next action |

## Harness Readiness

## Stack Coherence

## Security / RGPD / Sovereignty

## Decisions To Make

## Recommended Next Sessions
```

---

## Review severity

### Critical

Blocks development or risks breaking the doctrine.

Examples:

- Rumble executes directly ;
- secret may be logged ;
- no handoff validation ;
- product duplicates Gear memory ;
- licence incompatible non décidée.

### Warning

Should fix before implementation.

Examples:

- missing retention policy ;
- unclear owner layer ;
- weak traceability ;
- no acceptance tests.

### Suggestion

Useful improvement but not blocking.

---

## Commands recommandées

```bash
# docs/specs
python3 - <<'PY'
from pathlib import Path
import json
for p in Path('constantin-jais/ecosystem').rglob('*.md'):
    assert p.read_text().startswith('# '), p
for p in Path('constantin-jais/ecosystem').rglob('*.json'):
    json.loads(p.read_text())
print('ecosystem docs OK')
PY

# cos-matic handoff
cd cos-matic
cargo test --workspace --all-features
cargo run -q -p cos-matic-cli -- handoff validate ../constantin-jais/ecosystem/specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
cargo run -q -p cos-matic-cli -- handoff plan ../constantin-jais/ecosystem/specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run --json

# FeedMind
cd ../rumble-feed-mind
cargo test --workspace --no-run
```

---

## Contraintes

- Ne pas inventer de produits inexistants.
- Ne pas mentionner les inspirations externes dans les docs publiques.
- Ne pas pousser de secrets.
- Ne pas modifier du code pendant une review sauf demande explicite.
- Signaler les changements préexistants avant commit/push.

---

## Prompt court de synthèse

Si la session doit être courte :

```text
Lis constantin-jais/ecosystem/overview.md et specs/**.
Fais une review globale Rumble/Bolt/Wrench/Gear selon sécurité, qualité, performance, complétude, souveraineté/RGPD.
Priorise les blockers avant dev produit.
Donne un plan d'action P0/P1/P2 et les prochaines sessions recommandées.
```
