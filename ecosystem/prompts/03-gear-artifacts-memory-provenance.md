# Prompt — Session Gear Artifact / Memory / Provenance

## Mission

Tu es chargé de définir puis amorcer les briques Gear nécessaires pour soutenir les Rumble sans absorber leur logique produit.

Objectif central :

> Gear doit fournir les primitives de source, artifact, provenance, memory/index et distribution nécessaires au harness, sans contenir de workflows métier Rumble.

---

## À lire avant modification

```text
constantin-jais/ecosystem/overview.md
constantin-jais/ecosystem/specs/shared/shared-capabilities.md
constantin-jais/ecosystem/specs/shared/contracts/implementation-handoff.v0.1.md
constantin-jais/ecosystem/specs/rumble-canvas/06-data-model.md
constantin-jais/ecosystem/specs/rumble-note/13-gear-memory-boundary.md
constantin-jais/ecosystem/specs/rumble-feed-mind/05-domain-model.md
constantin-jais/ecosystem/specs/rumble-lm/06-data-model.md
gear-memory/README.md
gear-depot/README.md
gear-cable/README.md
```

Lire aussi les `Cargo.toml` des Gear si modification code.

---

## Doctrine Gear

Gear = infrastructure / physics layer.

Gear peut posséder :

- storage primitives ;
- memory/index/search substrate ;
- artifact integrity ;
- provenance ;
- release/distribution wiring ;
- offline/local-first substrate ;
- sync primitives.

Gear ne doit pas posséder :

- product UX ;
- business workflows ;
- agent decisions ;
- ingestion rules métier ;
- learning/session/note/canvas semantics.

---

## Objectifs P0

Définir les contrats minimaux pour :

```text
SourceRef
ArtifactRef
ProvenanceRecord
MemoryEntry
EventLogEntry
PackageManifest
```

Et décider leur placement :

- `gear-memory`
- `gear-depot`
- `gear-cable`

---

## Questions structurantes à trancher

### 1. Source vs Artifact

Challenge : un feed item, une note exportée, un PDF, un SpecPackage, un résumé LM — source ou artifact ?

Proposition à challenger :

- `Source` = entrée référencée ou matière première.
- `Artifact` = sortie produite, packagée, versionnée ou distribuable.
- Un objet peut devenir les deux selon lifecycle : feed item source → curated export artifact.

### 2. Gear Memory vs Rumble Note

Règle :

- `rumble-note` possède block UX et graph personnel.
- `gear-memory` possède index/retrieval/context substrate.

À définir :

- `MemoryEntry` ;
- index metadata ;
- source reference ;
- deletion/anonymization propagation ;
- local-first constraints.

### 3. Gear Depot vs SpecPackage/ExportPackage

Règle :

- Rumble produit le package.
- Gear Depot enregistre hash/provenance/distribution/ref.

À définir :

- `ArtifactManifest` ;
- checksums ;
- signature future ;
- package type ;
- retention/revocation metadata.

### 4. Gear Cable

Rôle probable : release/distribution de binaires/outils, pas stockage de specs.

À clarifier :

- quand un Rumble ou Wrench produit un outil à distribuer ;
- comment gear-cable alimente gear-depot ;
- install floors et provenance de build.

---

## Contrats minimaux proposés

### SourceRef

```json
{
  "source_id": "string",
  "source_type": "file | url | feed_item | note_block | transcript | document",
  "origin_product": "rumble-feed-mind | rumble-note | gear-loader | portal-forge | ...",
  "uri": "optional",
  "content_hash": "sha256:...",
  "provenance_id": "string",
  "created_at": "timestamp"
}
```

### ArtifactRef

```json
{
  "artifact_id": "string",
  "artifact_type": "spec_package | handoff_payload | curated_export | learning_export | release_asset",
  "producer": "rumble-canvas | rumble-lm | rumble-feed-mind | gear-cable",
  "version": "string",
  "hash": "sha256:...",
  "manifest_ref": "string",
  "created_at": "timestamp"
}
```

### ProvenanceRecord

```json
{
  "provenance_id": "string",
  "actor_ref": "string",
  "operation": "created | imported | transformed | exported | signed | distributed",
  "inputs": [],
  "outputs": [],
  "tool_ref": "optional",
  "timestamp": "timestamp"
}
```

### MemoryEntry

```json
{
  "memory_entry_id": "string",
  "source_ref": "string",
  "content_hash": "sha256:...",
  "index_state": "pending | indexed | stale | deleted",
  "metadata": {},
  "created_at": "timestamp"
}
```

---

## Work items possibles

### Option A — specs only

Créer :

```text
constantin-jais/ecosystem/specs/gear/
  00-gear-boundaries.md
  01-source-artifact-provenance.md
  02-memory-entry-contract.md
  03-depot-artifact-manifest.md
```

### Option B — code minimal gear-memory

Dans `gear-memory` :

- créer Rust structs `SourceRef`, `MemoryEntry`, `ProvenanceRecord` ;
- tests de sérialisation ;
- pas de DB encore.

### Option C — code minimal gear-depot

Dans `gear-depot` :

- créer `ArtifactManifest` ;
- hashing ;
- tests ;
- pas de registry complète.

Recommandation : commencer specs + structs minimales, pas infra lourde.

---

## Challenges obligatoires

1. Est-ce que la brique contient de la logique produit ? Si oui, remonter vers Rumble.
2. Est-ce que la brique décide quoi faire ? Si oui, Bolt.
3. Est-ce que la brique transforme/inspecte ? Si oui, Wrench.
4. Est-ce que la brique stocke/indexe/vérifie/distribue ? Gear.
5. Est-ce que le contrat gère suppression/RGPD ?
6. Est-ce que les hashes sont stables ?
7. Est-ce que l'artifact est reproductible ?
8. Est-ce que les secrets sont exclus ?

---

## Tests attendus si code

- serde roundtrip ;
- hash stable ;
- missing required field rejected ;
- no secret in debug/log output ;
- deletion/stale state modeled.

---

## Critères d'acceptation

- frontières Gear clarifiées ;
- SourceRef vs ArtifactRef tranché ;
- contracts JSON/Rust proposés ;
- shared-capabilities mis à jour ;
- aucun workflow métier introduit dans Gear ;
- tests passent si code modifié.

---

## Sortie attendue

Produire :

- décisions ;
- fichiers modifiés ;
- tests ;
- risques ;
- prochaines extractions ;
- impact sur Canvas/Note/LM/FeedMind/Crew.
