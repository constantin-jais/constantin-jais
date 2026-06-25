# Prompt — Session wrench-inspect Handoff Inspector

## Mission

Tu es chargé de créer ou spécifier le premier inspecteur Wrench dédié aux handoffs Rumble → Bolt.

Objectif central :

> `wrench-inspect` doit produire des rapports déterministes sur la qualité, la sécurité, la traçabilité et la gouvernance d'un `ImplementationHandoff v0.1`.

Wrench ne décide pas quoi exécuter. Wrench inspecte, valide, signale, et produit de l'évidence.

---

## À lire avant modification

```text
constantin-jais/ecosystem/overview.md
constantin-jais/ecosystem/specs/shared/contracts/implementation-handoff.v0.1.md
constantin-jais/ecosystem/specs/shared/contracts/implementation-handoff.v0.1.schema.json
constantin-jais/ecosystem/specs/harness/README.md
constantin-jais/ecosystem/specs/shared/shared-capabilities.md
constantin-jais/ecosystem/specs/rumble-canvas/*.md
cos-matic/crates/aom/src/handoff.rs
wrench-loader/README.md
```

Si un repo `wrench-inspect` existe, lire :

```text
wrench-inspect/README.md
wrench-inspect/Cargo.toml
wrench-inspect/docs/**
```

Sinon créer un squelette minimal Rust si demandé explicitement.

---

## Doctrine

Wrench = capability layer.

Il peut :

- inspecter ;
- valider ;
- auditer ;
- produire des findings ;
- produire des rapports machine-readable ;
- être appelé par Rumble ou Bolt.

Il ne doit pas :

- décider de l'exécution ;
- posséder le package ;
- modifier le produit ;
- stocker la vérité long terme ;
- devenir une UI.

---

## Objectif MVP

Créer un inspecteur :

```bash
wrench-inspect handoff inspect <handoff.json>
wrench-inspect handoff inspect <handoff.json> --json
```

Si `wrench-inspect` n'est pas encore prêt, ajouter temporairement une spec et une ADR d'extraction depuis `cos-matic`.

---

## Checks obligatoires

### 1. Contract shape

- format connu ;
- kind `planning_request` ;
- JSON Schema valide ;
- package hash présent ;
- items non vides.

### 2. Execution safety

- `planning_only = true` ;
- `allow_execution = false` ;
- `requires_human_approval_for_execution = true`.

### 3. Traceability coverage

Vérifier :

- au moins un lien de traceability ;
- les actions importantes ont un lien amont ;
- les acceptance criteria ont un lien à une action ou journey ;
- les capability candidates ont une origine.

Rapport attendu :

```json
{
  "coverage": {
    "journey_to_screen": 0.8,
    "screen_to_action": 0.9,
    "action_to_acceptance": 0.7
  }
}
```

### 4. Waiver policy

- waiver expiré = error ;
- waiver sans rationale = error ;
- high/critical waiver sans séparation Owner/Reviewer = error ;
- waiver sans target = warning/error selon sévérité.

### 5. Risk and blocker policy

- blocking question sans waiver = error ;
- high/critical risk sans mitigation/waiver = error ;
- open medium risk = warning ;
- risk sans catégorie = warning.

### 6. Shared capability extraction

- candidate sans owner = warning ;
- candidate owner inconnu = warning ;
- candidate critique sans décision = warning ;
- candidate déjà connue dans registry = info.

### 7. PII / RGPD heuristics

Ne pas faire de classification parfaite, mais signaler :

- champs `participant`, `email`, `name`, `display_name`, `response`, `free_text` ;
- absence de `pii_classification` si données sensibles détectées ;
- présence possible de secrets/API keys ;
- payload trop large contenant raw content inutile.

### 8. Sovereignty policy

- provider externe mentionné sans policy = warning ;
- US hyperscaler comme core truth = error/warning selon policy ;
- licence non permissive dans metadata = warning/error selon contexte.

---

## Format de rapport cible

```json
{
  "valid": false,
  "summary": {
    "errors": 1,
    "warnings": 2,
    "infos": 3
  },
  "findings": [
    {
      "severity": "error",
      "code": "missing_traceability",
      "path": "traceability_links",
      "message": "At least one traceability link is required",
      "recommendation": "Link journey/screen/action before handoff"
    }
  ],
  "coverage": {},
  "next_actions": []
}
```

---

## Tests attendus

Utiliser les fixtures :

```text
constantin-jais/ecosystem/specs/harness/fixtures/handoffs/*.json
```

Tests minimum :

- valid fixture passes ;
- execution fixture fails ;
- missing trace fails ;
- blocking question fails ;
- high risk fails ;
- expired waiver fails ;
- capability missing owner returns warning but not hard failure.

---

## Relation avec cos-matic

`cos-matic` valide déjà une partie des règles.

Challenge attendu :

- Qu'est-ce qui reste dans `cos-matic` ?
- Qu'est-ce qui doit migrer vers `wrench-inspect` ?

Recommandation probable :

- `cos-matic`: validation minimale bloquante avant planning ;
- `wrench-inspect`: rapport détaillé de qualité, conformité, coverage, policy.

---

## Non-objectifs

- Pas d'exécution.
- Pas d'appel LLM obligatoire.
- Pas d'UI.
- Pas de stockage long terme.
- Pas de mutation des handoffs.

---

## Critères d'acceptation

Session réussie si :

- commande/spec d'inspection définie ;
- format de rapport défini ;
- checks P0 couverts ;
- tests/fixtures listés ou implémentés ;
- séparation `cos-matic` vs `wrench-inspect` clarifiée ;
- shared capability registry mis à jour ;
- aucun secret/PII n'est loggé.

---

## Commandes de vérification suggérées

```bash
cargo fmt
cargo test --workspace
wrench-inspect handoff inspect constantin-jais/ecosystem/specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
```

Si le binaire n'existe pas encore, documenter le blocage et proposer le squelette.

---

## Sortie attendue

Rapporter :

- fichiers changés ;
- tests exécutés ;
- findings de design ;
- ce qui reste dans `cos-matic` ;
- ce qui part dans `wrench-inspect` ;
- prochaines décisions.
