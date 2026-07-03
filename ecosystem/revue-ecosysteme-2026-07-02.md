# Revue d'écosystème par comité — Rumble / Bolt / Wrench / Gear

**Date** : 2026-07-02 · **Périmètre** : stack perso GitHub `constantin-jais` (~/Documents, 17 cibles)
**Méthode** : cartographie factuelle (17 agents de reconnaissance, 1 par repo, lecture seule) → validation utilisateur → comité de 6 lentilles (CPO, CTO, architecte, UX, sécurité/RGPD, support/ops) → vérification adversariale de chaque finding non trivial par un sceptique indépendant.
**Volume vérifié** : 71 findings → **11 CONFIRMED**, 52 PLAUSIBLE (souvent reformulés par les vérificateurs), **8 REFUTED (éliminés)**. Ce rapport reflète les versions **corrigées** post-vérification, pas les affirmations brutes des experts. Chaque constat porte une preuve (chemin + citation).

---

## 1. Synthèse (10 lignes)

1. La doctrine est d'une rigueur rare (couches, boundary tests, 65 décisions, 22 ADRs, vocabulaire de maturité, forge-health) — mais **la gouvernance de la vérité est en retard sur elle** : 3/14 repos ont un `maturity/*.json`, le cockpit affiche des états déjà faux, et deux `overview.md` coexistent malgré une décision déjà actée.
2. La valeur réelle démontrée est **le processus, pas les produits** : `bolt-cos-matic` (usable, 35 ADRs) et la chaîne contrats/fixtures/CI sont le vrai actif ; 4 des 7 Rumbles sont des squelettes — ce qui est **conforme au cadrage « dojo »**, pas une faute.
3. Le risque n°1 est **l'autorisation de l'orchestration** : cos-matic pousse des branches, merge et déploie sans vérifier aucun token Biscuit, alors que Biscuit est décidé « standard » — l'écart entre décision et enforcement est au point le plus dangereux du système.
4. Le risque n°2 est **la preuve décorative** : les 6 gates du dry-run plan sont hardcodées `status=pass` — « evidence-gated planning » ne consomme aujourd'hui aucune evidence, ce qui contredit la devise « evidence over claims ».
5. Le risque n°3 est **opérationnel** : zéro backup/restore/DR (Postgres de lm, journal `~/.cosmatic`), `wrench-inspect` non versionné (1080 LOC perdables par un `rm -rf`), pas de runbook incident.
6. **RGPD** : les états `deleted/anonymized` existent dans les schémas mais aucune opération ne les applique ; la rétention de lm est ouverte ; le droit à l'effacement est déclaratif — problématique pour le seul produit manipulant des PII réelles en contexte pédagogique.
7. **Souveraineté** : la doctrine anti-hyperscaler US coexiste avec GitHub (Microsoft) comme substrat unique de la CI, la gouvernance, l'orchestration et les releases — accepté par ADR (0012/0027) mais sans exit path ni snapshot hors GitHub.
8. La **sécurité agentique** n'a pas de threat model écrit alors que le pipeline est agent-first (source non fiable → loader → handoff → orchestrateur qui agit sur GitHub) ; la détection d'injection est par mots-clés.
9. Les vérificateurs adversariaux ont **réfuté 8 accusations** : la plupart des « écarts » dénoncés (extraction db-inspect, registre partagé prudent, cockpit Markdown, offline non syncé) sont en réalité des choix documentés — l'écosystème s'auto-décrit honnêtement, ses vrais défauts sont l'enforcement et l'ops, pas la lucidité.
10. Verdict : **architecture cohérente, gouvernance sincère mais semi-appliquée, exécution jeune** — consolider la boucle de confiance (auth réelle, gates réelles, claims synchronisées, sauvegardes) avant d'étendre le portefeuille ou les UI.

---

## 2. Cartographie des produits et briques

### Vision (validée)

Forge personnelle de processus — « the process is the product », explicitement pas un portefeuille startup. Rumble = dojos générant des contraintes réelles ; Bolt/Wrench/Gear = cœur réutilisable. Boucle : idée → spec → inspection → plan → exécution contrôlée → preuve → mémoire → amélioration. Doctrine : souveraineté, déterminisme, agent-readability, spec-first, convergence Rust+Dioxus (exception Astro documentée pour cos).

### Couches

```
┌─ PLAN DE CONTRÔLE  constantin-jais/ecosystem/ (canonique) ── overview · status cockpit · 65 décisions
│                    · 22 ADRs · 4 contrats shared v0.1 · maturity R0-R10 · forge-health (14 repos)
│                    ⚠ double : ~/Documents/overview.md divergent (décision #63 actée, non appliquée)
│                    ⚠ héberge aussi prototypes/wrench-db-inspect (~2000 LOC de code hors doctrine)
├─ RUMBLE (produits/dojos)
│    rumble-canvas      contract-first ✓   13 specs, ~1300 LOC CLI, contrat canvas.bolt_handoff.v0.1
│    rumble-cos         usable R5          Astro SSG, 221 contenus, e2e Playwright — spec 1/13 (BLOCKED)
│    rumble-crew        contract-first ✓   0 code, matrice 8 rôles × 9 permissions, 7 décisions M0 ouvertes
│    rumble-feed-mind   dojo R1 ✓          11 crates Rust + legacy Next.js + skeleton Leptos (≠ ADR Dioxus)
│    rumble-lm          contract-first R1  ⚠ runtime beta réel (10 130 LOC, Postgres/Redis/Biscuit/WS/Dioxus)
│    rumble-note        contract-first     ⚠ constaté speculative : 0 code, 0 fixture, 5 décisions ouvertes
│    rumble-ai-practices (hors cockpit)    ADR locale acceptée, sans remote, docs fr, recouvrement lm admis
├─ BOLT (orchestration)
│    bolt-cos-matic     usable ✓           3 500+ LOC, 208 commits, planning-only enforced, kill-switches
│                                          ⚠ gates dry-run hardcodées · ⚠ Biscuit non vérifié au runtime
│    bolt-harness       contract-first     banc d'essai, moteur épinglé v0.1.0-alpha.4, absent d'overview §3.2
├─ WRENCH (outillage / evidence)
│    wrench-loader      dojo ✓             contrats v0.1, extraction+feeds réels, PDF/Office fail-closed
│    wrench-inspect     dojo de facto      ⚠ NON VERSIONNÉ (pas de .git) — 1080 LOC, 14 tests, 8 checks
│    wrench-db-inspect  coquille (47 LOC)  implémentation réelle (~2000 LOC) dans ecosystem/prototypes/
└─ GEAR (substrat)
     gear-memory        contract-first ✓   5 contrats validés, anti-secrets — zéro persistance/index/effacement
     gear-depot         contract-first ✓   ArtifactRef/Manifest — zéro proxy/cache réel
     gear-cable         contract-first ✓   plans de release, sovereign floor testé, CI SBOM/SLSA réelle
                                           ⚠ ne produit pas les ArtifactRef que la spec lui assigne
```

### Données et intégrations

- **PII réelles** : rumble-lm (noms, présence, réponses, scores — 4 modes d'anonymat spécifiés, rétention ouverte), feed-mind (emails, hash argon2, clés BYOK aes-gcm, IDs Stripe), cos (emails newsletter → Brevo EU). Doctrine zéro PII/secret en logs, `SafeMetadata` anti-secrets dans Gear.
- **Intégrations** : GitHub (Actions + API octocrab — cœur opérationnel), Clever Cloud (EU), Brevo (EU), Stripe (optionnel par ADR), rorkai/App-Store-Connect-CLI (asc 2.5.0 pinned + checksum), Postgres+pgvector, Redis, Biscuit (contrat Draft).
- **Rôles** : matrices riches en spec (crew 8×9, lm 3×15, note 5 rôles) ; enforcement runtime : rumble-lm uniquement (capabilities Host/Participant).

---

## 3. Tableau : brique / rôle / criticité / risques / recommandations

Criticité = exigence de solidité **dès maintenant** compte tenu du rôle dans la boucle (pas de l'ambition future).

| Brique                        | Rôle                                          | Criticité               | Risques principaux (verdict)                                                                                                                                            | Recommandations                                                                                                                |
| ----------------------------- | --------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **bolt-cos-matic**            | Moteur d'orchestration — agit sur GitHub réel | **CRITIQUE**            | Gates hardcodées `status=pass` (CONFIRMED) ; Biscuit non vérifié (CONFIRMED) ; pas de retry/backoff octocrab ni runbook automerge (PLAUSIBLE)                           | Gates dérivées du handoff ou renommage honnête ; trancher le modèle d'auth ; alerting automerge + runbook                      |
| **constantin-jais/ecosystem** | Plan de contrôle, source de vérité            | **CRITIQUE**            | Cockpit désynchronisé (CONFIRMED) ; 3/14 maturity.json (CONFIRMED) ; prototypes/ héberge du code produit ; hub dans le repo profil (PLAUSIBLE)                          | Automatiser status.md depuis maturity/*.json ; gate forge-health « maturity.json requis » ; trancher le placement du hub       |
| **rumble-lm**                 | Dojo principal, seules PII réelles            | **HAUTE**               | Effacement/rétention non implémentés (PLAUSIBLE haute) ; axes maturity mesurent le stub, pas le runtime (CONFIRMED, corrigé) ; CitationValidation non gated live        | API mark_deleted/anonymize + TTL + ADR rétention ; clarifier la sémantique des axes ; gater la citation avant publication      |
| **wrench-inspect**            | Producteur d'evidence de la boucle            | **HAUTE**               | Non versionné — perte totale possible (PLAUSIBLE critique en ops) ; statut « No local repo yet » périmé                                                                 | `git init` + remote + tag immédiats ; mettre à jour status.md                                                                  |
| **rumble-canvas**             | Contrat P0 du harness                         | **HAUTE**               | Spec promet UI/multi-user que le CLI ne portera pas sans refonte (PLAUSIBLE) ; LICENSE absent                                                                           | Découper spec en P0 CLI / P1 UI ; LICENSE ; rester contract-first sans honte                                                   |
| **wrench-loader**             | Ingestion canonique                           | **HAUTE**               | 3-4 divergences code↔fixtures vérifiées (`reference` vs `ref`, block_id…) ; URL fetch « in scope P0 » absent                                                            | Aligner code et fixtures (décider l'owner du schéma) ; c'est LE point d'entrée de l'injection : gates structurelles            |
| **bolt-harness**              | Banc de preuve public                         | MOYENNE                 | Absent d'overview §3.2 ; claims contradictoires (« usable » vs « contract-first ») ; politique de transition alpha absente (PLAUSIBLE corrigé : ROADMAP moteur périmée) | Ajouter à la carte ; unifier la claim ; documenter la politique de dé-pinning                                                  |
| **rumble-cos**                | Vitrine publique, seul usable                 | MOYENNE                 | Exception de méthode (code-first) non documentée contrairement à l'exception de stack (CONFIRMED corrigé) ; inspection R4 sans note                                     | Documenter l'exception code-first pour sites de contenu OU rétro-spécifier ; risque produit faible                             |
| **rumble-feed-mind**          | Dojo importé, le plus complet                 | MOYENNE                 | Leptos contredit l'ADR Dioxus sans override documenté (CONFIRMED corrigé) ; 5 waivers RustSec expirent 2026-09-30 (PLAUSIBLE haute) ; LICENSE absent ; double UI legacy | Trancher Leptos vs Dioxus par ADR ; plan de purge des waivers (contrainte externe réelle) ; LICENSE                            |
| **wrench-db-inspect**         | Inspection sécurité DB                        | MOYENNE                 | Extraction en attente : ADR-0004 **Proposed**, pas de timeline (PLAUSIBLE corrigé : intentionnel mais non piloté)                                                       | Accepter ADR-0004 et exécuter la migration, ou canoniser prototypes/ explicitement dans le README                              |
| **gear-memory**               | Contrats mémoire/provenance                   | MOYENNE (haute à terme) | Stage 0/1 spécifiés non implémentés ; états deleted/anonymized sans opérations (support du droit à l'effacement)                                                        | Stage 0 (store+lookup) en premier — c'est le maillon « memory » de la boucle ET le socle RGPD                                  |
| **gear-cable**                | Release/distribution                          | MOYENNE                 | Ne produit pas les ArtifactRef assignés (PLAUSIBLE) ; zéro consommateur réel (corrigé : pré-consommation délibérée) ; ASC_PRIVATE_KEY en env vars shell (PLAUSIBLE)     | Désigner un premier client E2E ; ArtifactRef ou redéfinir le rôle ; confinement des secrets                                    |
| **gear-depot**                | Supply-chain souveraine                       | SIMPLE OK               | Ambition (proxy/cache/policy) >> code (contrats) — écart documenté                                                                                                      | Peut rester contract-first ; ne pas implémenter le proxy sans demandeur réel                                                   |
| **rumble-crew**               | Workspace agentique                           | SIMPLE OK               | 7 décisions Milestone 0 toutes ouvertes ; 45 acceptance tests non exécutables ; LICENSE/maturity absents                                                                | Squelette assumé ; convertir 5-10 tests en fixtures JSON exécutables quand M0 tranché                                          |
| **rumble-note**               | Base de connaissance locale                   | SIMPLE OK               | Déclaré contract-first, constaté speculative (0 fixture, NoteContextExport non exécutable)                                                                              | Rétrograder la claim ou produire les fixtures promises ; 5 décisions techniques à trancher avant tout code                     |
| **rumble-ai-practices**       | Formation pratiques IA                        | À TRANCHER              | Hors cockpit, sans remote, recouvrement lm admis (corrigé : ADR locale acceptée, jour 1 — résidu administratif réel)                                                    | Décision : produit officiel (remote + cockpit + maturity.json + frontière lm par ADR) ou pack de contenu lm ou sandbox déclaré |
| **specs/ + overview racine**  | Vestiges                                      | —                       | Double source de vérité malgré décision #63 (CONFIRMED)                                                                                                                 | Supprimer/rediriger la racine ; gate anti-duplication                                                                          |

---

## 4. Incohérences détectées (dédupliquées, post-vérification)

**Confirmées :**

1. **Claims de maturité désynchronisées, dans les deux sens** — lm : `maturity.json` dit « no persistence / no UX » alors que Postgres store, Redis fanout, Biscuit minting, WebSocket et UI Dioxus existent et sont testés (les axes mesurent le stub P0, pas le runtime — non dit) ; cos : R5 usable avec spec 1/13 « Not started » ; bolt-harness : « usable proof bench » (ROADMAP) vs « contract-first » (status.md). → La base de confiance du cockpit est fragile (doc-01 CONFIRMED).
2. **« Evidence-gated planning » sans evidence** — les 6 gates du dry-run sont hardcodées `status=pass` (handoff.rs:102-133), ne consomment ni le handoff ni Wrench/Gear/Biscuit, et ne correspondent pas aux gate_type du schéma (cpo-12/cpo-13 CONFIRMED).
3. **Biscuit : décidé partout, appliqué dans un seul repo** — cos-matic ignore `biscuit_authorization_references` ; le contrôle réel est kill-switches env + scope du token GitHub (CONFIRMED).
4. **Convergence Rust+Dioxus non appliquée** — feed-mind implémente Leptos sans ADR d'override (l'ADR 0002 mandate Dioxus) ; aucune UI Dioxus fonctionnelle n'a jamais été rendue dans l'écosystème ; criticité corrigée à moyenne (cos est une exception documentée, canvas CLI est conforme).
5. **Deux overview.md** — la décision #63 désigne ecosystem/ comme canonique, mais la racine survit sans redirect ni gate (CONFIRMED, corrigé : problème d'enforcement, pas de décision).
6. **Exception de méthode non documentée pour cos** — l'exception de _stack_ (Astro) est actée ; l'exception de _méthode_ (code-first sans spec amont) ne l'est pas (CONFIRMED corrigé).
7. **wrench-inspect** — status.md dit « No local repo yet », or 1080 LOC + 14 tests + ADR accepté existent, non versionnés (le fond « intentionnel » est plaidable, le risque de perte est réel).
8. **Contrats vs code** — wrench-loader diverge de ses propres fixtures de spec sur 3-4 points vérifiés ; gear-cable ne produit pas les ArtifactRef assignés par `01-source-artifact-provenance.md`.
9. **Souveraineté** — doctrine « independent from US hyperscalers » vs GitHub comme substrat opérationnel unique ; accepté par ADR-0012/0027 mais sans posture écrite distinguant « core truth » de « substrat opérationnel », ni snapshot hors GitHub (CONFIRMED).
10. **ai-practices** — revendique la couche Rumble (ADR locale acceptée) mais absent d'overview/status/maturity, sans remote, docs 100 % fr (CONFIRMED en ops ; criticité corrigée : administrative, produit jour-1).

**Accusations réfutées (à ne PAS corriger — l'écosystème avait raison) :**

- « Sous-déclaration délibérée de lm » — non : système de gates documenté, README honnête ; le vrai défaut est la sémantique des axes (stub vs runtime), pas la sincérité.
- « Extraction db-inspect cassée » — non : pattern d'extraction progressive documenté (ADR-0004) ; le défaut résiduel est l'absence de timeline et le statut Proposed.
- « Registre partagé paralysé » — non : « product demand drives platform work » est une règle explicite ; le défaut résiduel est l'absence de critères d'Accepted pour les capacités ayant déjà ≥ 2 demandeurs.
- « Offline-first sans sync = bug » — non : note est local-only par décision de spec, lm est online-first MVP ; la question ouverte légitime est l'ownership du futur sync (Gear vs produit).
- « Cockpit non navigable » — non : cockpit Markdown est une décision d'architecture assumée (§2.3).
- « Boucle 8/10 manquante » — citation inexacte : les chaînons manquants sont documentés comme travail futur dans loop.md.

---

## 5. Briques manquantes

1. **Threat model agentique** (sécurité) — le pipeline source non fiable → wrench-loader → handoff → cos-matic (qui agit sur GitHub) n'a aucun threat model écrit ; la détection d'injection est keyword-based. Adversaire, assets, surfaces, mitigations, validation structurelle des handoffs.
2. **Opérations d'effacement/anonymisation** (RGPD) — `mark_deleted()/mark_anonymized()` dans gear-memory + workflow d'effacement lm + TTL réels (crew spec : 7 j, jamais implémenté). Les états existent, les opérations non.
3. **Backup/Restore/DR + snapshots d'état** (ops) — pg_dump lm, rollup du journal `~/.cosmatic`, export périodique de status/maturity/decision-log hors GitHub. Exigé par la méthode §4.10, implémenté nulle part.
4. **Vérification Biscuit au runtime** (auth) — dans cos-matic, ou une rétrogradation documentée du standard.
5. **Gates de planning dynamiques** (Bolt) — dérivées du handoff et des rapports Wrench/Gear ; sinon renommer.
6. **Observabilité/alerting de l'orchestration + runbook incident** — détection d'un automerge silencieusement défaillant, retry/backoff octocrab, runbook humain.
7. **Preuve E2E Dioxus** — une démo navigateur réelle (3 écrans lm + assertions Playwright) avant d'étendre la doctrine à note/crew/feed-mind.
8. **maturity/\*.json pour les 11 repos manquants** + gate forge-health, ou règle d'exemption explicite ; génération automatisée du cockpit.
9. **LICENSE files** (canvas, feed-mind, + décision pour crew/note spec-only) + extension du gate hygiene (LICENSE, maturity.json).
10. **Fixtures exécutables** pour une sélection d'acceptance tests (crew/note) — 5-10 scénarios critiques en JSON + validation CI.
11. **Premier consommateur E2E de gear-cable** — un produit désigné dont le binaire passe par plan → release → checksum → install.
12. _(conditionnel à la décision souveraineté)_ **Exit path forge** — miroir Gitea/Forgejo + inventaire de ce qui survit à un outage GitHub.

---

## 6. Décisions structurantes à prendre

| #   | Décision                                    | Options (trade-offs sur les axes)                                                                                                                                                                                                         |
| --- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | **Sémantique et couverture de la maturité** | (a) maturity.json obligatoire × 14 + axes documentés « stub vs runtime » + cockpit généré ; (b) status.md prose reste la SSOT et maturity.json devient optionnel documenté. Ne pas garder les deux divergents.                            |
| D2  | **Posture souveraineté**                    | (a) GitHub assumé comme substrat opérationnel (documenter core truth vs substrate + snapshots hors GitHub) ; (b) exigence dure → exit path planifié (trait Forge existe déjà comme abstraction, ADR-0027).                                |
| D3  | **Modèle d'auth de l'orchestration**        | (a) Biscuit enforced dans cos-matic (contrat Draft→Accepted, vérification des references) ; (b) rétrogradé « cible future », kill-switches documentés comme modèle réel. L'état actuel — obligatoire non appliqué — est le pire des deux. |
| D4  | **Gates de planning**                       | (a) implémenter la dérivation depuis le handoff/evidence ; (b) renommer « planning skeleton » et dater la vraie feature.                                                                                                                  |
| D5  | **rumble-ai-practices**                     | (a) produit officiel : remote + cockpit + maturity.json + frontière lm par ADR ; (b) pack de contenu lm ; (c) sandbox déclaré hors gouvernance.                                                                                           |
| D6  | **Méthode pour les sites de contenu**       | Documenter l'exception code-first (cos) ou rétro-spécifier ; sinon la doctrine spec-first n'est plus falsifiable.                                                                                                                         |
| D7  | **Stack UI**                                | (a) preuve Dioxus E2E puis convergence forcée (feed-mind migre) ; (b) pluralisme documenté (ADR override Leptos, doctrine assouplie). Pas de demi-mesure.                                                                                 |
| D8  | **Feed parsing**                            | (a) wrench-loader owner effectif — feed-mind consomme CanonicalSourceDocument ; (b) duplication assumée et documentée (offline-first standalone). ~2200 LOC dupliquées en jeu.                                                            |
| D9  | **wrench-db-inspect**                       | Accepter ADR-0004 et exécuter la migration prototypes/ → repo, ou canoniser prototypes/ dans le README. Statut transitoire non piloté aujourd'hui.                                                                                        |
| D10 | **Placement du plan de contrôle**           | Rester dans le repo profil (assumé, double rôle documenté) ou repo gouvernance dédié. Impacte l'autorité et la portabilité.                                                                                                               |
| D11 | **Critères Draft→Accepted**                 | Pour contrats shared et capacités partagées : p.ex. ≥ 2 implémentations + 1 test cross-repo + ADR d'adoption. Appliquer d'abord aux capacités ayant ≥ 2 demandeurs actifs (Workspace, Source, Identity).                                  |
| D12 | **RGPD art. 17**                            | Formaliser l'exemption 17(3) revendiquée (contexte pédagogique/scientifique, à documenter) ou implémenter le droit à l'effacement complet. Change le design de gear-memory et lm.                                                         |
| D13 | **RTO/RPO**                                 | Définir la perte acceptable (sessions lm, journal cosmatic) — sans ce chiffre, aucune stratégie de backup n'est dimensionnable.                                                                                                           |

---

## 7. Recommandations

Séquencées par dépendances (pas de planning calendaire). La seule échéance externe réelle : les 5 waivers RustSec de feed-mind expirent le **2026-09-30**.

### Court terme — protéger l'existant et rétablir la vérité (aucune dépendance, coût faible)

1. `git init` + remote + tag pour **wrench-inspect** ; remote pour **ai-practices**. C'est la seule perte irréversible possible aujourd'hui.
2. Appliquer la décision #63 : supprimer/rediriger `~/Documents/overview.md` (+ gate anti-duplication).
3. LICENSE (MIT) dans canvas et feed-mind (+ trancher pour crew/note spec-only) ; étendre hygiene.yml à LICENSE.
4. Resynchroniser les claims : documenter dans `maturity/rumble-lm.json` que les axes mesurent le stub P0 (le runtime beta existe en parallèle) ; unifier la claim bolt-harness ; noter l'exception de méthode cos.
5. Trancher D3 (auth) et D4 (gates) **sur le papier** — deux ADRs. L'implémentation suit, mais l'honnêteté du cockpit ne doit pas attendre le code.
6. Écrire la posture souveraineté (core truth vs substrat opérationnel) + premier snapshot d'état hors GitHub (export status/maturity/decision-log/journal).
7. Lancer le plan de purge des waivers RustSec (contrainte 2026-09-30).

### Moyen terme — fermer la boucle de confiance (dépend des ADRs ci-dessus)

8. Implémenter la décision D3 : vérification Biscuit dans cos-matic (ou documentation du modèle kill-switches si rétrogradé).
9. Implémenter la décision D4 : gates dérivées du handoff + consommation des rapports Wrench (wrench-inspect est prêt : 8 checks, 14 tests).
10. RGPD : `mark_deleted/anonymize` dans gear-memory (Stage 0 store+lookup d'abord — c'est aussi le chaînon « memory » de la boucle), workflow d'effacement lm, TTL, ADR rétention (D12).
11. Threat model agentique + validation structurelle des handoffs (grammar/schema, provenance) — wrench-loader est le point d'entrée, cos-matic le point d'impact.
12. Ops : backup automatisé (pg_dump lm, rollup journal), alerting automerge, runbook incident, retry/backoff octocrab.
13. Exécuter D9 (migration db-inspect) et D8 (feed parsing) ; aligner wrench-loader sur ses fixtures.
14. maturity.json × 14 + génération automatisée du cockpit + gate forge-health (D1).
15. Preuve Dioxus E2E (D7) avant toute nouvelle spec d'écran ; convertir 5-10 acceptance tests crew/note en fixtures exécutables.

### Long terme — n'ouvrir qu'avec des demandeurs réels

16. Capacités partagées : appliquer les critères D11 aux ~5 candidates à ≥ 2 demandeurs (Workspace, Source, Artifact, Identity, Agent-task) ; les autres restent Candidate sans honte.
17. Premier canal réel gear-cable + premier consommateur E2E ; ArtifactRef (ou redéfinition du rôle).
18. Multi-user/collaboration (canvas UI, crew runtime) **après** validation des personas par au moins un utilisateur externe réel.
19. Exit path forge (miroir Gitea/Forgejo) si D2 = exigence dure ; sandbox d'exécution (gVisor/Firecracker, déjà identifié par cos-matic readiness) avant toute expansion de l'autonomie d'exécution.
20. Cockpit web : seulement si la charge de navigation du cockpit Markdown devient un point de douleur mesuré — la décision actuelle (Markdown) est saine.

---

## 8. Questions à poser avant de valider l'architecture cible

1. **Souveraineté** : GitHub est-il une dépendance opérationnelle assumée (et alors documentée comme telle), ou l'exit path est-il une exigence ? Ta doctrine actuelle dit les deux.
2. **Auth** : Biscuit doit-il être vérifié par cos-matic avant toute action GitHub, et si oui, qui mint les tokens dans le flux canvas → handoff → plan ?
3. **RGPD** : revendiques-tu l'exemption art. 17(3) pour lm (contexte pédagogique) ou le droit à l'effacement complet ? Des mineurs sont-ils envisagés parmi les participants ?
4. **Portefeuille** : ai-practices — produit, pack de contenu lm, ou sandbox ? Et plus largement : quel Rumble doit rencontrer un utilisateur externe en premier, et qu'est-ce que ça change à son niveau d'exigence ?
5. **Vérité** : quelle est LA source de vérité de la maturité (maturity/*.json ou status.md), et acceptes-tu qu'un gate CI la fasse respecter contre toi-même ?
6. **UI** : quelle preuve suffirait à valider (ou invalider) la doctrine Dioxus — et si Leptos gagne dans feed-mind, la doctrine tombe-t-elle ?
7. **Perte acceptable** : quel RTO/RPO pour les sessions lm et le journal d'audit ? (« Aucune perte » = un vrai coût d'infra ; « tout est reconstructible » = à prouver.)
8. **Granularité** : 15 repos / 4 couches pour un solo — assumes-tu le coût de gouvernance par repo (hygiene, maturity, security × 15), ou faut-il fusionner (p.ex. les 3 gear en un workspace) tant qu'aucun n'a de consommateur externe ?
9. **Séquencement** : canvas reste-t-il « harness-critical first » (et alors lm/cos attendent le handoff) ou officialises-tu l'avancement parallèle ?
10. **Le processus est le produit** : quel est le critère de succès de la forge elle-même — et à quel moment un dojo qui ne génère plus de contraintes pour Bolt/Wrench/Gear est-il retiré (`retired`) ?

---

## Addendum — arbitrages de Constantin (2026-07-02)

**Actés** :

- **D1 → (a)** : maturity.json obligatoire ×14, axes documentés (stub vs runtime), cockpit généré, gate forge-health.
- **D2 → (a)** : GitHub assumé comme substrat opérationnel — documenter la posture (core truth vs substrat) + snapshots hors GitHub.
- **D4 → (a)** : gates de planning dérivées du handoff/evidence (pas de renommage cosmétique).
- **D5 → (a)** : rumble-ai-practices devient produit officiel — remote + cockpit + maturity.json + frontière lm par ADR.
- **D9** : migration explicite — ADR-0004 passé à Accepted, code `ecosystem/prototypes/wrench-db-inspect` migré vers le repo GitHub, prototype archivé.
- **D11, D12, D13** : acceptés tels que formulés (critères Draft→Accepted ; RGPD effacement + ADR rétention ; RTO/RPO à chiffrer).

**Actés au second tour (2026-07-02)** :

- **D3** : validé — contrat unique à double profil (délégation produit A→B ≤ 3 niveaux tout-ou-partie ; délégation pipeline vérifiée par cos-matic) ; implémentation demand-driven : profondeur 1, one-shot d'abord ; « N fois » différé (exige un état serveur — à mutualiser avec le registre de révocation le jour venu).
- **D8** : reco suivie — ADR wrench-loader owner de bytes→CanonicalSourceDocument (point de passage unique du scan sécurité) ; feed-mind garde polling/règles/curation ; duplication gelée puis parsing rebâti selon les préférences maison à la bascule (gates R2 feed-mind).
- **D10** : reco suivie — repo de gouvernance dédié, exécuté après D9 (le repo profil viole « one repo, one responsibility » : profil + gouvernance + specs + prototypes, 196 MB).

- **D6 (acté au 3ᵉ tour)** : remise à plat de rumble-cos assumée — le site entre dans le process standard (spec-first 00-12 puis rebuild sur la stack cible : shell web élu + tokens portal-forge), car il évoluera au-delà du simple contenu. L'exception Astro disparaît ; le débat Zola-vs-Astro est superseded. Contraintes posées par le comité : (1) le site actuel (seul produit usable R5, vitrine publique) reste en ligne jusqu'aux gates vertes du remplaçant ; (2) les 221 contenus et la chaîne de redirects (SEO) sont des actifs à migrer, pas à recréer ; (3) le charter doit définir ce que « plus que du contenu » signifie AVANT le rebuild ; (4) le rendu contenu reste statique par défaut (axe sécurité), l'interactif s'ajoute en îlots spécifiés ; (5) séquencement : après l'élection du shell web (spike lm).

**Précisions de vision (3ᵉ tour, 2026-07-02)** — sémantique des couches clarifiée par Constantin :

1. **rumble-\*** = produits livrables en natif sur 6 cibles (Web, iOS, Android, macOS, Linux, Windows).
2. **bolt-\*** = l'usine : toute la logique de gestion des agents, aussi autonomes que possible pour produire les rumble-\*. Doctrine : Rust at core, compile once, run everywhere.
3. **gear-\* / wrench-\*** = capacités pour les agents (double client à formaliser : l'usine ET les runtimes produit consomment les mêmes contrats — sinon D8 casse).
4. **rumble-canvas** = inspiré de Claude Design/Peinture : produit collaboratif multi-utilisateurs de prototypage + écriture de specs, agent-in-the-loop, itérations branchées avec sync/merge, preview live, double vue Prototype/Specs. Frontière à tenir : l'agent s'exécute dans Bolt, canvas est la fenêtre. Règle structurante posée : **on itère en web, on release en natif** (la preview live par itération n'est réaliste qu'en web).
5. **portal-\*** (D14 affiné) : niveau confirmé — substrat design partagé sous les produits, MAIS double nature actée : c'est aussi la capacité de production d'UI des agents (le garde-fou qui rend l'UI générée cohérente/accessible). Règle à outiller : les agents n'écrivent jamais de styles en dur, uniquement des tokens portal (check wrench-inspect à ajouter).

**Précisions de vision (4ᵉ tour, 2026-07-02)** :

- **rumble-canvas affiné** : produit DS-agnostique — ingère n'importe quel design system (repo, site de référence, documentation, screenshot, draft) avec synchro possible sur l'existant. **MVP = production de spec collaborative** (pas de preview ni d'ingestion DS au départ) ; dogfooding rapide ensuite (les specs rumble-* dedans). C'est un produit destiné à être lancé publiquement, utilisé aussi pour ses propres besoins. Conséquences actées en session : portal-* n'est pour canvas qu'un DS parmi d'autres (jamais hard-codé) ; l'ingestion de références externes est un vecteur d'injection majeur → passe par le loader unique + threat model ; multi-tenant/PII dès la spec.
- **D15 (proposé) — re-découpage wrench/gear par CLIENT et non par verbe** : wrench-\* = outils de l'usine uniquement (ne shippent jamais dans un produit) ; gear-\* = substrat runtime linkable dans les produits ET utilisé par les agents. Test de classement : « ce code peut-il être linké dans un binaire produit ? oui → gear, non → wrench ». Conséquence : **wrench-loader → gear-loader** (consommé au runtime par feed-mind (D8) et demain par canvas) — seul repo mal rangé ; inspect/db-inspect restent wrench ; memory/depot/cable restent gear ; portal-\* = famille conservée, définie « substrat design (gear spécialisé) + portal-forge côté usine ».

**En cours d'arbitrage** :

- **D7 — architecture de stack cible (élection du shell web restante)** : intention posée par Constantin : « Rust at core, compile once, run everywhere with native language of platforms », pivot bienvenu tant qu'aucun utilisateur. Proposition en session : architecture à 3 étages — (1) cœur produit Rust (domain + view-models MVU, cible ~80 % du code d'un écran), (2) substrat design compile-once (portal-forge tokens + portal-core i18n/a11y via UniFFI), (3) shells de rendu minces par cible : web = UN framework Rust wasm élu par spike E2E (Dioxus dans lm vs Leptos dans feed-mind, le perdant est supprimé), desktop = shell web empaqueté Tauri 2, mobile natif SwiftUI/Compose = voie premium différée par produit (demande réelle + vérifiabilité locale). rumble-cos reste hors système (site de contenu) mais consomme les tokens CSS de portal-forge ; ADR Zola vs Astro assumé à trancher, non urgent.
- **D14 — famille `portal-*`** (née hors gouvernance : core/apple/android sans remote ; 5ᵉ préfixe hors doctrine) : challenge livré — verdict recommandé : portal-forge conservé (1ᵉʳ consommateur immédiat : cos), portal-core conservé et à épaissir (66 LOC de Rust vs ~4 200 LOC de shells : ratio inverse de la promesse « compile once »), portal-apple gelé au tag « pont UniFFI prouvé » (learning yield documenté), portal-android gelé/archivé (1 commit, 0 test, invérifiable localement — pas de SDK/NDK). Tous à intégrer à la gouvernance (remote + cockpit + maturity.json).

---

## Annexe — méthodologie et traçabilité

- **Phase A** : 17 agents de reconnaissance (1 par repo, périmètre borné, lecture seule, aucun build) → fiches structurées avec preuves ; cartographie validée par Constantin avant toute critique.
- **Phase B** : 6 experts (CPO, CTO, architecte, UX, sécurité/RGPD, ops) sur la cartographie validée ; chaque finding de criticité ≥ moyenne contre-vérifié par un sceptique indépendant chargé de le réfuter preuve en main.
- **Verdicts** : 71 findings → 11 CONFIRMED · 52 PLAUSIBLE (dont beaucoup reformulés/atténués) · 8 REFUTED éliminés. Les criticités de ce rapport sont celles **corrigées** par la vérification.
- Fiches détaillées, findings bruts et verdicts complets conservés dans le scratchpad de session (`fiches.json`, `comite.json`).
