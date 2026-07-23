# Context hygiene — méthode de cloisonnement des dépôts publics

Méthode appliquée à l'ensemble des dépôts publics de la constellation pour garantir deux invariants de publication :

1. **Aucun identifiant privé** (identifiants d'un contexte de travail distinct, adresses associées) dans les fichiers trackés.
2. **Aucun chemin machine-local** (`/Users/<user>/...`) dans les fichiers trackés — formes `~`, repo-relatives ou `<workspace>/...` à la place.

## Principe : le détecteur ne contient jamais ce qu'il bannit

Les motifs sont écrits avec une classe de caractères sur leur première lettre (ex. `[x]yz` pour bannir `xyz`) : le fichier de workflow matche la cible sans jamais porter le littéral. Le dépôt reste conforme à sa propre règle, et les audits se rédigent de la même façon (référence indirecte, jamais le littéral).

## Structure du garde-fou

Un workflow CI `context-hygiene.yml` par dépôt (répliqué, jamais partagé en dépendance) :

- **Tier identifiants privés** : `git grep` insensible à la casse sur le motif classe-encodé → échec bloquant à la première occurrence.
- **Tier chemins machine-locaux** : même mécanique, avec deux exemptions :
  - lignes portant le marqueur `allow-local-path` (fixtures, exemples d'anti-pattern documentés) ;
  - **fichiers de preuve scellés, exclus fichier par fichier** (jamais des répertoires entiers) : un rapport dont l'empreinte SHA est vérifiée par un autre gate est immuable — on ne le retouche pas, on l'exempte.

## Séquencement d'adoption sur un dépôt existant

1. Poser le workflow avec le tier chemins en **warning** si des occurrences existent déjà (l'inventaire est affiché à chaque run).
2. Nettoyer les occurrences (remplacements `~` / repo-relatifs / `<workspace>`), en restaurant verbatim tout fichier scellé touché par erreur.
3. Promouvoir le tier en **échec bloquant** dans le même changement que le nettoyage — jamais de fenêtre où le compteur peut remonter.

Sur un dépôt propre, les deux tiers sont bloquants d'emblée.

## Famille de gates

Ce garde-fou complète, sans les recouvrir, les gates de même famille déjà en place : interdiction des marques retirées dans les documents vivants (control-plane et monorepo, exclusions de registres historiques fichier par fichier), scan de secrets, conformité REUSE. La règle commune : **une interdiction éditoriale n'est réelle que portée par un job CI bloquant** — une convention seule ne tient pas.

## État de déploiement (2026-07-23)

Déployé et vérifié (rouge prouvé sur fixture seedée, vert sur l'arbre réel) sur le monorepo et les dépôts satellites actifs de l'org, via une passe de nettoyage préalable sur le monorepo (25 occurrences de chemins machine-locaux éliminées, 3 preuves scellées exemptées fichier par fichier).
