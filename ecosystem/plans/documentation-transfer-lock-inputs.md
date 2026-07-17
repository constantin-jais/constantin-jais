# Documentation de transfert — manifeste d’entrée du futur package canonique

- **Statut** : need-capture méta proposé ; aucune autorité produit
- **Date** : 2026-07-17
- **Frontière** : control-plane ADR 0047
- **Cible d’exécution** : monorepo `libre-ai/libre-ai`, jamais les dépôts historiques archivés

## Pourquoi ce manifeste existe

La reprise de l’actif exige davantage qu’un README ou une présentation produit. Un acteur indépendant doit pouvoir comprendre les responsabilités, vérifier les parcours, diagnostiquer les refus, reconstruire les artefacts et, lorsque la capacité est autorisée, exécuter sauvegarde, restauration, incident, mise à jour et rollback.

Les dépôts historiques ne sont plus les unités d’ownership. Le périmètre ne doit donc pas reproduire quinze fiches de repositories archivés. Il doit couvrir les unités canoniques du monorepo : applications, capacités partagées, opérations globales et distribution.

Ce fichier prépare les entrées de documentation pour les packages G3, G4 et G5. Il ne modifie aucun Specification Lock, n’autorise aucune implémentation hors package et ne transforme aucune procédure cible en preuve.

## Autorités à relire au déclenchement

- monorepo `GOALS.md` et `STATUS.md` ;
- monorepo `docs/decisions/DECISION-REGISTER.md` ;
- monorepo `docs/transformation/G1-WORK-PACKAGES.md` et `work-packages.v1.json` ;
- monorepo `docs/transformation/REPOSITORY-MAP.md` ;
- monorepo `docs/architecture/TARGET.md` et `DATA-OWNERSHIP.md` ;
- monorepo `docs/specifications/DATA-LIFECYCLE.md` ;
- monorepo `docs/reviews/AGENT-REVIEW-PROTOCOL.md` ;
- control-plane ADR 0047.

## Cartographie canonique à documenter

### Applications G3

Les neuf packages applicatifs possèdent leur documentation locale sous leur `writePaths` `apps/<nom>/**` :

1. Website ;
2. Practices ;
3. Radar ;
4. Notebook ;
5. Sessions ;
6. Model Policy ;
7. Boussole ;
8. Specifications ;
9. Missions.

Chaque application doit laisser, dans son propre périmètre, un point d’entrée de reprise qui décrit l’état réellement implémenté. Les anciennes fiches `website`, `ai-practices`, `feed-radar`, `notebook`, `sessions`, `policy`, `boussole-politique`, `spec-studio` et `agent-board` ne sont que des sources historiques référencées par SHA.

### Capacités partagées

L’index transverse G5 doit couvrir au minimum :

- contrats et SDK générés ;
- web runtime, UI, auth web, données et cache ;
- moteurs Rust spécialisés effectivement autorisés ;
- Proof et Artifact ;
- template Bun qualifié ;
- toolchain et quality gates ;
- projections et packages de distribution.

`agent-factory`, `context-kit` et `dioxus-app-template` restent des archives tant qu’un package canonique ne recrée pas explicitement leur capacité. Une fiche ne doit jamais les faire apparaître comme runtime vivant.

## Contrat documentaire proposé

### Produit ou capacité

- public ou consommateurs ;
- cas d’usage et parcours de bout en bout ;
- limites, refus et non-objectifs ;
- roadmap exprimée en gates, sans date-promesse ;
- critères d’acceptation identifiés, statut, commande ou preuve, commit et date de dernière vérification.

### Architecture

- **C4 L1** : personnes, système, systèmes externes et frontière de confiance ;
- **C4 L2** : processus, applications, workers, stores et services réellement déployables ;
- **C4 L3 facultatif** : packages, crates et composants structurants ;
- flux de données, classification, rétention et frontières de sécurité ;
- dépendances externes, nécessité, licence, résidence, mode dégradé et stratégie de sortie.

Une crate ou un package n’est pas un conteneur C4 L2. Une vue cible porte explicitement `cible` et ne sert pas de preuve d’implémentation.

### Exploitation

- installation et configuration sans valeur secrète ;
- inventaire des stores et classes de données ;
- sauvegarde/restauration avec RPO/RTO et drill daté lorsque des données durables existent ;
- santé, SLI/SLO, journaux redacted, alertes et capacité ;
- incident : détection, confinement, rôles, récupération, communication et retour d’expérience ;
- mise à jour, migrations, compatibilité, release, rollback ou compensation.

Les runbooks globaux appartiennent à `WP-G4-H01`/`WP-G4-C01`. Avant G4, `non autorisé` ou `non implémenté` est la seule formulation acceptable pour l’infrastructure, les secrets, DNS et production.

### Développement et décisions

- environnement reproductible et première contribution bornée ;
- architecture du code et emplacement de chaque invariant ;
- tests par couche et commandes réellement rejouées ;
- conventions sécurité, données, licences et dépendances ;
- release et contribution ;
- ADR, alternatives rejetées, contraintes, conséquences et supersession.

### Inventaire d’actifs et d’accès

L’inventaire est fondé sur des rôles, jamais sur des données personnelles publiques. Il référence sans les contenir :

- ownership produit, technique, sécurité, données et opérations ;
- repositories/projections, domaines, DNS, registres, artefacts et clés de signature ;
- noms des secrets, source d’autorité, rotation et procédure de révocation — jamais leur valeur ;
- fournisseurs, région/résidence, contrats/DPA, licences et chemin de remplacement ;
- données, sauvegardes, rétention, obligations légales et support/EOL.

## Répartition par phase

| Phase/package | Livrable documentaire | Gate |
| --- | --- | --- |
| G3 — chaque `WP-G3-*` | reprise locale de l’application, C4 courant, parcours et commandes prouvées | reste dans `apps/<nom>/**` ; aucune exploitation G4 anticipée |
| `WP-G3-X01..X03` | preuves transverses de contrats, sécurité, accessibilité, offline et mode dégradé | les claims renvoient à des artefacts immuables |
| `WP-G4-H01` | runbooks testés de backup/restore, supervision, incident, migration et rollback | candidat déployé, drills datés, aucune résurrection de données |
| `WP-G4-C01` | manuel opérateur du cutover global et inventaire d’actifs vivant | contrôle humain de cutover |
| `WP-G5-D01` | index de transfert, paquets documentaires, contexte et reproduction indépendante | environnement propre et approbation distribution/licences |

Si une gate documentaire nécessite d’écrire hors des `writePaths` verrouillés, l’auteur doit proposer un amendement par ADR et obtenir l’approbation humaine avant édition. Il ne contourne pas le plan par un workflow ad hoc.

## Gate documentaire proposée

Le futur package G5 doit fournir un vérificateur hors réseau qui refuse :

- unité canonique sans point d’entrée ;
- rubrique requise absente ;
- lien relatif cassé ;
- C4 L2 composé uniquement de crates/packages ;
- claim opérationnel sans preuve immuable ;
- date sans commit vérifié ;
- secret, PII ou chemin machine ;
- référence mutable à un dépôt historique comme autorité ;
- dépendance externe sans licence/résidence/mode dégradé/sortie.

Les snippets critiques d’installation, build, restore et rollback sont exécutés par leur package propriétaire. Un simple parse Markdown ne prouve pas leur validité.

## Parcours d’autonomie et mesure

- **Jour 1** : mission, vocabulaire, statut, ownership et limites ;
- **Semaine 1** : clean checkout, chemin local, flux de données, premier changement sous tests ;
- **Semaines 2–3** : diagnostic d’un refus, traçabilité vers l’ADR et exercice non productif de restore/incident lorsque G4 l’autorise ;
- **Sortie** : l’acteur distingue preuve, cible et blocage, puis reproduit un artefact publié sans connaissance tacite.

Avant acceptation G5, une personne qui n’a pas participé à l’implémentation effectue le parcours dans un environnement propre. Le dossier conserve durée, frictions, commandes, écarts et corrections. Une auto-évaluation par l’auteur ne satisfait pas cette gate humaine.

## Critères d’acceptation du futur incrément

1. Toutes les unités canoniques vivantes sont couvertes ; aucune archive n’est présentée comme autorité modifiable.
2. Les C4 L1/L2 correspondent à l’architecture déployée ; les composants internes sont séparés en L3.
3. Chaque critère d’acceptation renvoie à une preuve et à un commit immuable.
4. Les runbooks G4 ont été exécutés sur le candidat global lorsque la capacité s’applique.
5. L’inventaire d’actifs permet rotation, remplacement et révocation sans publier de secret ou PII.
6. Le vérificateur documentaire passe en clean checkout et échoue sur fixtures négatives.
7. L’onboarding à froid est mesuré et ses blocages majeurs sont fermés.
8. Les licences, provenances et dépendances souveraines sont approuvées avant distribution.

## Trigger

Ne pas exécuter ce chantier pendant le milestone Notebook Core Gate B. Consommer ce manifeste :

- lors de l’ouverture des packages G3 pour les fiches locales ;
- lors de `WP-G4-H01`/`WP-G4-C01` pour les procédures opérationnelles ;
- lors de `WP-G5-D01` pour l’index, le gate et la reproduction indépendante.

Toute exécution anticipée exige un nouvel ADR monorepo, un amendement de work-package et une instruction humaine qui remplace explicitement le milestone courant.
