# Cockpit central — product-readiness Libre IA

Date canonique : 2026-07-14

Ce cockpit est la référence transversale pour comparer les produits et l’infrastructure.

- Les dépôts produit gardent leurs capacités détaillées, leurs tests et leurs roadmaps.
- Ce cockpit compare l’état de disponibilité, pas la promesse ni la maturité seule.
- La maturité d’un dépôt n’est pas une preuve de disponibilité produit.
- Le nombre d’issues n’est qu’un signal d’audit, jamais une preuve de readiness.
- Website reste la gateway ; Benchmarks reste un programme de preuve.
- Agent Factory est traité comme infrastructure habilitante, pas comme un huitième produit.

## Sources de vérité / anti-drift

- [`governance/repo-profiles.json`](governance/repo-profiles.json) fixe la maturité officielle.
- Les README, ROADMAP, docs, tests et issues des repos portent les preuves locales.
- Ce cockpit est le seul endroit où la comparaison cross-product est consolidée.
- Aucun claim public-alpha n’est déduit d’un label de dépôt.
- Aucun chemin local, secret, calendrier ou promesse de disponibilité publique n’est publié ici.

## Audit vérifié

| Repo | HEAD | Sources vérifiées | Signal issues |
| --- | --- | --- | --- |
| Feed Radar | `main@9ab78a8` | README, ROADMAP, `docs/launch-target.md` | aucune ouverte détectée via `gh` |
| Notebook | `main@e0f66b4` | README, ROADMAP | aucune ouverte détectée via `gh` |
| AI Practices | `main@41302e7` | README, preuves de tests et `docs/testing-strategy.md` | aucune ouverte détectée via `gh` |
| Sessions | `main@36e7efb` | README, ROADMAP, `docs/evidence/stack-traversal-2026-07-13.md` | `#109` ouverte |
| Boussole Politique | `main@2c58f02` | README, `roadmap.md`, scripts de vérification Rust et M1 | aucune ouverte détectée via `gh` |
| Spec Studio | `main@ba203cf` | README, ROADMAP, `docs/OPERATIONS.md` | aucune ouverte détectée via `gh` |
| Agent Board | `main@36fd7fa` | README, ROADMAP, `scripts/validate_mission_contracts.py` | aucune ouverte détectée via `gh` |
| Agent Factory (infra) | `main@fe0004f` | README, `engine/ROADMAP.md`, `harness/README.md` | aucune ouverte détectée via `gh` |

## Synthèse disponibilité

> Légende : `P0` = noyau local manquant ; `P1` = passage staging / private-alpha ; `P2` = durcissement public-alpha / production.

| Produit | Maturité repo | Étape disponibilité | Local journey | Staging | Public alpha | Production | Prochaine gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Feed Radar | `dojo` | `discovery` | oui — revue read-only | absent | absent | absent | P1 |
| Notebook | `specification` | `discovery` | non | absent | absent | absent | P0 |
| AI Practices | `dojo` | `discovery` | oui — fixture locale | absent | absent | absent | P1 |
| Sessions | `contract-first` | `discovery` | oui — owner + guest | absent | absent | absent | P1 |
| Boussole Politique | `contract-first` | `discovery` | partiel — dry-run méthodologique, aucun shell | absent | absent | absent | P0 |
| Spec Studio | `contract-first` | `discovery` | oui — CLI locale | absent | absent | absent | P1 |
| Agent Board | `contract-first` | `discovery` | partiel — cycle de contrat, aucun board | absent | absent | absent | P0 |

## Fonctionnalités prouvées / partielles / bloquées

| Produit | Fonctionnalités prouvées | Partiel | Bloqué / à faire | Preuve |
| --- | --- | --- | --- | --- |
| Feed Radar | OPML → règle visible → sélection explicable ; import HTTPS borné et allowlisté ; replay hash-only ; export client-safe ; revue Dioxus read-only ; cadence worker bornée | import interactif, stockage durable, scheduler seulement local, sandbox réseau hébergée | URL canonique, preuve publique revue, workflow hébergé | [`main@9ab78a8`](https://github.com/libre-ai/feed-radar/commit/9ab78a8) · [README](https://github.com/libre-ai/feed-radar/blob/main/README.md) · [ROADMAP](https://github.com/libre-ai/feed-radar/blob/main/ROADMAP.md) · [launch target](https://github.com/libre-ai/feed-radar/blob/main/docs/launch-target.md) |
| Notebook | frontière produit, roadmap et politique de sécurité | aucun modèle de bloc ni fixture d’export exécutable | runtime capture/édition/sync/export et futur contrat `NoteContextExport` | [`main@e0f66b4`](https://github.com/libre-ai/notebook/commit/e0f66b4) · [README](https://github.com/libre-ai/notebook/blob/main/README.md) · [ROADMAP](https://github.com/libre-ai/notebook/blob/main/ROADMAP.md) |
| AI Practices | corpus validation/audit ; sessions fixture ; API/PWA locale ; 78 tests avec PostgreSQL jetable | activités draft, feedback non punitif, résultat local | contenu `approved`, runtime partagé de session, ops de prod | [`main@41302e7`](https://github.com/libre-ai/ai-practices/commit/41302e7) · [README](https://github.com/libre-ai/ai-practices/blob/main/README.md) · [testing strategy](https://github.com/libre-ai/ai-practices/blob/main/docs/testing-strategy.md) |
| Sessions | owner + guest Dioxus/WASM ; create/join/answer/reveal/leaderboard/late join/reconnect ; OIDC in-process ; corpus borné ; retrieve → generate → verify → approve avec citations ; PWA shell-only et bundles reproductibles ; 283 tests Rust + 41 tests navigateur | état owner/corpus/membership process-local ; mono-instance ; token participant en query WebSocket | staging #109 : Keycloak réel, Clever HTTPS/WSS, politique de logs proxy et téléphone physique ; persistance/multi-instance ensuite | [`main@36e7efb`](https://github.com/libre-ai/sessions/commit/36e7efb) · [README](https://github.com/libre-ai/sessions/blob/main/README.md) · [ROADMAP](https://github.com/libre-ai/sessions/blob/main/ROADMAP.md) · [stack traversal](https://github.com/libre-ai/sessions/blob/main/docs/evidence/stack-traversal-2026-07-13.md) · [#109](https://github.com/libre-ai/sessions/issues/109) |
| Boussole Politique | dry-run reproductible ; formule canonique ; contrats Rust purs ; assets déterministes ; sensibilité M1 scriptée | spec v1, architecture et identité visuelle proposées ; gate M1 conditionnelle | symétrie/couverture, revue indépendante, shell public, revue juridique | [`main@2c58f02`](https://github.com/libre-ai/boussole-politique/commit/2c58f02) · [README](https://github.com/libre-ai/boussole-politique/blob/main/README.md) · [roadmap](https://github.com/libre-ai/boussole-politique/blob/main/roadmap.md) |
| Spec Studio | workspace/package/handoff/plan CLI ; SpecPackage immuable ; semantics planning-only | identité multi-acteur et provenance durables, meilleurs messages d’erreur, exemples de sortie | UI collaborative durable, workflow multi-utilisateur, provenance de release | [`main@ba203cf`](https://github.com/libre-ai/spec-studio/commit/ba203cf) · [README](https://github.com/libre-ai/spec-studio/blob/main/README.md) · [ROADMAP](https://github.com/libre-ai/spec-studio/blob/main/ROADMAP.md) · [OPERATIONS](https://github.com/libre-ai/spec-studio/blob/main/docs/OPERATIONS.md) |
| Agent Board | `MissionRecord v1`, fixtures positives/négatives, moteur local de transitions immuables, verdict humain | vocabulaire de blocage/reprise dans le contrat ; aucune projection | board local read-only, persistance, exécution d’agent, collaboration hébergée | [`main@36fd7fa`](https://github.com/libre-ai/agent-board/commit/36fd7fa) · [README](https://github.com/libre-ai/agent-board/blob/main/README.md) · [ROADMAP](https://github.com/libre-ai/agent-board/blob/main/ROADMAP.md) |

## Infrastructure habilitante

| Composant | Maturité repo | Étape disponibilité | Local journey | Staging | Public alpha | Production | Prochaine gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Agent Factory | `consolidated` | `private-alpha` | oui | pas de preuve live sandbox | `engine-v0.1.0-alpha.6` installable, mais les dernières fonctionnalités n’y figurent pas encore | absent | P1 |

## Lecture synthétique

- Aucun des sept produits publics n’atteint ici `public-alpha`.
- Aucun des produits audités n’est en production.
- Sessions a un seul signal d’écart ouvert (`#109`) et reste sans staging.
- Feed Radar a un parcours local prouvé, mais toujours aucun workflow hébergé.
- Agent Factory a une release installable, mais pas de preuve live sandbox ni de couverture complète des dernières fonctionnalités.
