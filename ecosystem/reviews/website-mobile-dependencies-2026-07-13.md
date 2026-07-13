# Website — revue des dépendances Dioxus mobile

Date : 2026-07-13  
Périmètre : `libre-ai/website`, Dioxus 0.7.9, feature Cargo `mobile`.

## Verdict

La configuration Cargo du Website suit la recommandation Dioxus 0.7 : features séparées `web = ["dioxus/web"]`, `desktop = ["dioxus/desktop"]` et `mobile = ["dioxus/mobile"]`. La documentation consultée est `/llmstxt/dioxuslabs_learn_0_7_llms-full_txt` via Context7.

Activer `dioxus/mobile` dépend intentionnellement de `dioxus-desktop` dans Dioxus 0.7.9. Les WebView et dépendances natives observées ne proviennent donc pas d’une erreur de feature locale que Website pourrait supprimer sans remplacer ou patcher Dioxus.

Une commande hôte telle que :

```bash
cargo check --no-default-features --features mobile --bin libre-ai-website
```

prouve uniquement que le chemin de code activé compile sur l’hôte. Elle ne prouve ni build Android, ni build iOS, ni installation, cycle de vie, permissions, accessibilité, signature, mise à jour ou rollback.

## Preuves reproduites

```bash
cargo tree --no-default-features --features mobile -e features -i dioxus-desktop
cargo tree --no-default-features --features mobile -i block
cargo report future-incompatibilities --id 1
cargo audit --json
```

Résultats :

- `dioxus/mobile` active `dioxus-desktop 0.7.9` ;
- `block 0.1.6` arrive par `cocoa → dioxus-desktop` et déclenche un avertissement de future incompatibilité Rust ;
- aucune vulnérabilité RustSec bloquante n’est déclarée dans le lockfile ;
- `cargo audit` recense 14 avertissements : 12 crates non maintenues et 2 avis d’unsoundness (`glib 0.18.5`, `rand 0.7.3`) ;
- l’audit du lockfile couvre toutes les cibles et ne signifie pas que chacune de ces crates est liée dans l’artefact web statique.

## Décision

1. **Ne pas patcher localement Dioxus ou ses WebView aujourd’hui.** Un fork de framework augmente fortement le risque de maintenance et ne crée aucune preuve produit mobile.
2. **Conserver mobile en statut expérimental.** La compilation hôte reste un signal de non-régression, pas une claim de support.
3. **Isoler les gates par artefact.** Le web statique garde ses gates actuels ; Android et iOS suivent la matrice `specs/shared/dioxus-target-evidence.md`.
4. **Suivre une mise à jour Dioxus qui renouvelle la chaîne native.** Toute promotion doit comparer le graphe, les avis RustSec et les preuves appareil avant/après.
5. **N’envisager un patch que si un avis devient exploitable sur une cible distribuée ou bloque une version Rust requise.** Le patch doit alors être minimal, upstream-first, borné par un ADR et des tests Android/iOS réels.

## Gate de sortie mobile

Avant toute annonce Android ou iOS :

- compilation de la cible réelle et non de l’hôte seulement ;
- installation sur simulateur puis appareil ;
- navigation, liens profonds, hors ligne et reprise après suspension ;
- lecteur d’écran, clavier externe, tailles de texte et contrastes ;
- permissions minimales et absence de données sensibles dans les logs ;
- signature, provenance, mise à jour de version distincte et rollback ;
- taille et mémoire mesurées ;
- audit RustSec du graphe réellement distribué ;
- limites publiées et procédure de retrait.

Le Website peut continuer à partager son domaine et ses composants avec une future application mobile, mais aucun travail produit ne doit être planifié à partir de la seule réussite du `cargo check` hôte.
