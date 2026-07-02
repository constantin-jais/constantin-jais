# Prompt — Session rumble-canvas MVP Handoff Producer

## Mission

Tu es chargé de transformer `rumble-canvas` en premier producteur réel de packages/handoffs exploitables par le harness.

Objectif central :

> `rumble-canvas` doit pouvoir produire un `SpecPackage`, générer un `ImplementationHandoff v0.1`, appeler `cosmatic handoff validate --json`, afficher les findings, et ne jamais déclencher d'exécution.

Cette session ne doit pas construire tout le produit. Elle doit livrer une tranche verticale minimale, testable, qui prouve le flow produit → harness.

---

## À lire avant toute modification

Lire intégralement :

```text
constantin-jais/ecosystem/overview.md
constantin-jais/ecosystem/specs/README.md
constantin-jais/ecosystem/specs/shared/contracts/implementation-handoff.v0.1.md
constantin-jais/ecosystem/specs/shared/contracts/implementation-handoff.v0.1.schema.json
constantin-jais/ecosystem/specs/harness/README.md
constantin-jais/ecosystem/specs/rumble-canvas/*.md
cos-matic/README.md
cos-matic/crates/aom/src/handoff.rs
cos-matic/crates/cli/src/main.rs
```

Si `rumble-canvas` repo existe et contient du code, lire aussi :

```text
rumble-canvas/README.md
rumble-canvas/Cargo.toml
rumble-canvas/package.json
rumble-canvas/docs/**
```

---

## Doctrine à respecter

- Interactive Rumble = Rust-first product core + Portal client platform. Dioxus/PWA est la voie rapide par défaut ; SwiftUI/Compose sont first-class si besoin produit + vérification locale.
- Markdown est projection/export ; la vérité machine est structurée.
- Canvas ne possède pas l'exécution.
- Canvas ne contourne jamais Bolt.
- Canvas peut préparer et valider un handoff, mais pas exécuter.
- Toute action agentique doit rester planning-only tant que Bolt n'a pas validé et qu'un humain n'a pas approuvé.
- Ne pas mentionner les inspirations externes dans les docs publiques.

---

## Objectifs fonctionnels MVP

Livrer une tranche qui permet :

1. Créer ou charger un `SpecWorkspace` minimal.
2. Définir une `ProductCharter` minimale.
3. Définir au moins :
   - un rôle ;
   - un journey ;
   - un screen ;
   - une action ;
   - une acceptance criterion ;
   - un traceability link.
4. Créer un `SpecPackage` immutable logique.
5. Générer un `ImplementationHandoff v0.1` conforme.
6. Appeler :
   ```bash
   cosmatic handoff validate <handoff.json> --json
   ```
7. Afficher ou stocker les findings.
8. Appeler :
   ```bash
   cosmatic handoff plan <handoff.json> --dry-run --json
   ```
9. Afficher ou stocker le dry-run plan.
10. Garantir qu'aucune exécution n'est possible depuis Canvas.

---

## Objectifs techniques

### Architecture cible

Préférer une structure de type :

```text
rumble-canvas/
  crates/
    domain/       # objets métier purs
    package/      # SpecPackage, hashing, export
    handoff/      # génération ImplementationHandoff
    cli/          # outil local MVP
    ui/           # Dioxus plus tard si nécessaire
```

Si le repo est vide, commencer par crates Rust minimales plutôt que par UI.

### Premier livrable recommandé

Construire d'abord une CLI :

```bash
rumble-canvas package sample --out target/sample-package.json
rumble-canvas handoff sample --out target/sample-handoff.json
rumble-canvas handoff validate target/sample-handoff.json
```

La UI Dioxus vient après le contrat.

---

## Modèle minimal attendu

Implémenter ou documenter clairement :

```text
SpecWorkspace
SpecSection
SpecSectionRevision
TraceabilityLink
Waiver
SpecPackage
SpecPackageItem
PackageReadinessSnapshot
ImplementationHandoff
ActorReference
```

Champs obligatoires minimum :

- IDs stables ;
- timestamps ;
- actor attribution ;
- structured content ;
- content/package hash ;
- status ;
- traceability links ;
- execution_policy planning-only.

---

## Tests attendus

Créer tests unitaires/CLI couvrant :

1. Génération d'un handoff valide.
2. Refus si `allow_execution = true`.
3. Refus si traceability absente.
4. Refus si blocking question sans waiver.
5. Refus si high risk sans waiver.
6. Refus si waiver expiré.
7. Warning si capability candidate sans owner.
8. Hash stable pour package identique.
9. Package immutable après approval logique.

Réutiliser les fixtures :

```text
constantin-jais/ecosystem/specs/harness/fixtures/handoffs/*.json
```

---

## Intégration avec cos-matic

Ne pas réimplémenter la validation si `cosmatic` est disponible.

Canvas peut :

- générer le payload ;
- appeler `cosmatic`; 
- parser le JSON de findings ;
- afficher le résultat.

Canvas ne doit pas :

- décider seul que c'est exécutable ;
- créer une branche ;
- lancer un agent ;
- écrire dans un repo cible.

---

## Briques communes à identifier

Pendant l'implémentation, remplir ou mettre à jour :

```text
constantin-jais/ecosystem/specs/shared/shared-capabilities.md
```

Pour chaque brique :

- nom ;
- besoin produit ;
- produits concernés ;
- owner proposé : Rumble shared / Bolt / Wrench / Gear ;
- décision : candidate / discuss / accepted / rejected.

Briques probables :

- `SpecPackage`
- `ImplementationHandoff`
- `TraceabilityLink`
- `Waiver`
- `PackageReadinessSnapshot`
- `ActorReference`
- `ArtifactReference`

---

## Challenges obligatoires

Avant de coder, répondre :

1. Le besoin appartient-il vraiment à Canvas ou à Bolt/Wrench/Gear ?
2. Est-ce que la donnée est vérité produit, artifact, source ou mémoire ?
3. Est-ce que le modèle permet audit et replay ?
4. Est-ce que le flow fonctionne offline/local ?
5. Est-ce que le handoff contient trop de PII ?
6. Est-ce que l'agent peut modifier la vérité sans humain ? Si oui, corriger.
7. Est-ce que tout output est déterministe/testable ?

---

## Non-objectifs

- Pas d'exécution agentique.
- Pas de génération de code applicatif cible.
- Pas de backend multi-tenant complet.
- Pas de realtime collaboration.
- Pas de design UI complet.
- Pas de dépendance obligatoire à un provider IA.

---

## Critères d'acceptation

La session est réussie si :

- un handoff valide est généré ou au moins fixture-compatible ;
- `cosmatic handoff validate --json` passe sur le handoff valide ;
- `cosmatic handoff plan --dry-run --json` produit un plan ;
- les fixtures invalides sont refusées ;
- les tests passent ;
- les docs/specs sont mises à jour ;
- aucun secret/PII inutile n'est loggé ;
- les branches sont propres ou l'état Git est explicitement rapporté.

---

## Commandes de vérification minimales

```bash
cargo fmt
cargo test --workspace
cosmatic handoff validate constantin-jais/ecosystem/specs/harness/fixtures/handoffs/canvas-minimal.valid.json --json
cosmatic handoff plan constantin-jais/ecosystem/specs/harness/fixtures/handoffs/canvas-minimal.valid.json --dry-run --json
```

Adapter les chemins selon le repo courant.

---

## Sortie attendue de l'assistant

En fin de session, produire :

```text
[DELTA]
Fait    ... avec preuves
Reste   ...
Bloqué  ... si applicable
```

Inclure :

- fichiers modifiés ;
- commandes exécutées ;
- résultats ;
- décisions prises ;
- risques restants ;
- prochaines briques à extraire.
