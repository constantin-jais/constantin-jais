# ADR 0047 — Frontière de gouvernance entre le plan de contrôle et le monorepo

- Statut : accepté
- Date : 2026-07-17 (option A arbitrée par Constantin)
- Portée : tout le plan de contrôle (`constantin-jais/constantin-jais/ecosystem`) et sa relation au monorepo canonique `libre-ai/libre-ai`
- Contexte déclencheur : découverte en session du Big Bang du 2026-07-16 (org libre-ai gelée en monorepo, 18 dépôts archivés) lors de l'atterrissage des increments de la décomposition TencentDB-Agent-Memory

## Contexte

Depuis le 2026-07-16, deux surfaces de gouvernance vivantes coexistent :

- le **plan de contrôle** (`constantin-jais/constantin-jais/ecosystem`) : décompositions de projets externes, stars-audit, decision-log, ADR 0001–0046, specs par produit héritées de la topologie multi-dépôts, doctrine de forge ;
- le **monorepo canonique** (`libre-ai/libre-ai`) : reconstruction Big Bang en sept phases sous Specification Lock, avec ses propres specs applicatives au standard G1, ses 55 autorités de contrats, ses 26 work-packages verrouillés et **sa propre série d'ADR qui recommence à 0001**.

Aucune règle écrite ne définissait qui possède quoi. Les risques constatés : travail poussé vers des dépôts archivés (403 en session), citations d'ADR ambiguës entre les deux séries, backlog du plan de contrôle décrivant un monde gelé, et à terme des specs produits contradictoires entre les deux surfaces.

L'option B (absorber le plan de contrôle dans le monorepo) a été écartée : le méta déborde la portée produit du monorepo (les décompositions et le stars-audit couvrent plus que les produits libre-ai), le Specification Lock n'a jamais prévu cette entrée, et l'absorption gonflerait un dépôt déjà sous discipline stricte.

## Décision

### Rôles des deux surfaces

- Le **plan de contrôle** est le foyer **méta** : décompositions de projets externes (méthode `external-project-inspiration`), stars-audit, decision-log, ADR de doctrine de forge, need-captures et manifests d'entrée pour les futurs locks. Il reste vivant et hors du périmètre du Big Bang.
- Le **monorepo** possède la **vérité produit** : specs applicatives au standard G1, contrats et autorités, work-packages, work d'implémentation. Aucune spec produit nouvelle ou amendée ne naît dans le plan de contrôle.

### Règles de frontière

1. **Aucun travail produit hors work-package.** Toute implémentation, spec applicative ou amendement de contrat passe par le régime du monorepo (work-packages, Specification Lock, protocole de revue role-separated). Le plan de contrôle ne gate que ses propres artefacts méta.
2. **Citations d'ADR préfixées.** Deux séries homonymes existent ; toute citation croisée précise sa série : « control-plane ADR NNNN » (`ecosystem/specs/shared/adrs/`) vs « monorepo ADR NNNN » (`libre-ai/libre-ai/docs/adr/`). À l'intérieur d'une surface, la série locale est implicite.
3. **Les arbres de specs produits du plan de contrôle sont des entrées historiques.** `specs/rumble-*`, `specs/gear*`, `specs/harness`, `specs/wrench-db-inspect` ont nourri les neuf specs applicatives G1 du monorepo et sont désormais **superseded** : gelés en l'état comme trace, plus jamais amendés. Tout besoin nouveau sur un produit se capture en need-capture méta (décomposition, cold-backlog) avec re-routage vers la cible `REPOSITORY-MAP`, ou directement dans le régime du monorepo.
4. **Aucun push vers les dépôts legacy archivés.** Vérifier `archived` avant tout travail sur un clone local de `~/Documents/libre-ai/*` ; le seul dépôt libre-ai vivant est le monorepo.
5. **Les décompositions continuent d'atterrir ici.** Précédent : `tencentdb-agent-memory-decomposition.md` et son design N4 — les besoins restent capturés côté méta avec notes de re-routage, le code reste gaté par les locks du monorepo.

## Conséquences

- Le backlog du plan de contrôle (`remaining-work.md`, `plans/cold-backlog.md`, `status.md`) doit être réconcilié contre les 26 work-packages : chaque item marqué absorbé / survivant méta / caduc (passe dédiée, même décision).
- Les futurs locks du monorepo (notamment le lock composite orchestrateur : plan d'exécution + protocole de contrôle + harness + mémoire) consomment les manifests d'entrée préparés côté méta (`plans/orchestrator-lock-inputs.md`).
- La règle de citation s'applique rétroactivement aux specs méta récentes (déjà fait dans `agent-conversational-memory-design.md`).
