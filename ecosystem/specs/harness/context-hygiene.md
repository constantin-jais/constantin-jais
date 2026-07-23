# Context hygiene — méthode de cloisonnement des dépôts publics

Méthode appliquée aux dépôts publics de la constellation (y compris celui-ci) pour garantir deux invariants de publication :

1. **Aucun identifiant privé** (identifiants d'un contexte de travail distinct, adresses associées) dans les fichiers trackés.
2. **Aucun chemin machine-local** (`/Users/<user>/...`) dans les fichiers trackés — formes `~`, repo-relatives ou `<workspace>/...` à la place — hors registres scellés exemptés fichier par fichier (voir plus bas).

## Principe : le détecteur ne publie jamais ce qu'il bannit

Les motifs de déni sont stockés **encodés en base64** dans le workflow : le fichier ne porte le littéral ni pour `git grep` ni pour un lecteur humain. C'est de l'obfuscation, pas du chiffrement — l'objectif est zéro mention lisible, pas le secret cryptographique (un motif de CI doit rester greppable une fois décodé à l'exécution). Le motif décodé garde en outre une classe de caractères sur sa première lettre (`[x]yz` pour bannir `xyz`), si bien que même les messages d'erreur peuvent l'afficher sans reproduire le littéral. Les audits se rédigent avec la même discipline (référence indirecte, jamais le littéral).

Version antérieure de la méthode : classe de caractères seule — suffisante contre `git grep`, mais un lecteur humain décodait l'identifiant à vue dans un workflow public. La revue adversariale a requalifié ce point ; le base64 corrige.

## Structure du garde-fou

Un workflow CI `context-hygiene.yml` par dépôt (répliqué, jamais partagé en dépendance), trois steps bloquants :

- **Identifiants privés** : `git grep` insensible à la casse sur le motif décodé.
- **Identifiants et chemins machine-locaux** : motif générique `/Users/<nom>` (aucune identité dans le motif lui-même) + motif username encodé (couvre les formes hors `/Users/`, ex. chemins de répertoires temporaires). Deux exemptions :
  - lignes portant le marqueur `allow-local-path` (fixtures, exemples d'anti-pattern documentés, lignes de définition de motif) ;
  - **fichiers de preuve scellés, exclus fichier par fichier** (jamais des répertoires entiers) : un rapport dont l'empreinte SHA est vérifiée par un autre gate est immuable — on ne le retouche pas, on l'exempte.
- **Cibles de symlinks** : `git grep -I` ne lit pas les cibles de liens symboliques (contournement démontré empiriquement) — step dédié qui les inspecte.

Limites connues, documentées dans le workflow : fichiers texte uniquement (`-I` — un identifiant embarqué dans un binaire échappe au grep) ; sur les dépôts portant leur propre garde de chemins, la ligne de motif et le step symlink portent le marqueur d'exemption.

## Séquencement d'adoption sur un dépôt existant

1. Poser le workflow avec le tier chemins en **warning** si des occurrences existent déjà (l'inventaire est affiché à chaque run).
2. Nettoyer les occurrences (remplacements `~` / repo-relatifs / `<workspace>`), en restaurant verbatim tout fichier scellé touché par erreur.
3. Promouvoir le tier en **échec bloquant** dans le même changement que le nettoyage — jamais de fenêtre où le compteur peut remonter.
4. Ajouter le check aux **required status checks** de la branche par défaut quand le dépôt a une protection de branche — sans cela le rouge est visible mais non bloquant au merge.

Sur un dépôt propre, les trois steps sont bloquants d'emblée. Preuve reproductible du rouge : ajouter un fichier fixture contenant un motif (ex. `/Users/jane/leak`), le stager, exécuter le grep du step — détection attendue ; retirer la fixture.

## Famille de gates

Ce garde-fou complète, sans les recouvrir, les gates de même famille déjà en place : interdiction des marques retirées dans les documents vivants (control-plane et monorepo, exclusions de registres historiques fichier par fichier), scan de secrets, conformité REUSE. La règle commune : **une interdiction éditoriale n'est réelle que portée par un job CI bloquant** — une convention seule ne tient pas.

## État de déploiement (2026-07-23, v2)

Déployé sur le monorepo (check **requis** au merge), les dépôts satellites actifs de l'org et ce dépôt. Passe de nettoyage préalable sur le monorepo : 25 occurrences de chemins machine-locaux **traitées — 22 réécrites, 3 exemptées** (preuves scellées, fichier par fichier) — puis 4 formes résiduelles hors motif initial éliminées lors de la revue adversariale. Sur les satellites sans protection de branche, le check est visible mais non requis (décision de protection = arbitrage owner, cf. `docs/branch-protection.md`).
