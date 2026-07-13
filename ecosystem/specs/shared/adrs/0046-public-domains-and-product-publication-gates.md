# ADR 0046 — Domaines publics et gates de publication par produit

- Statut : accepté
- Date : 2026-07-12
- Portée : Website, sept produits et programme de preuve
- Supersède : la partie « domaine canonique » de la décision Brand v2 du 2026-07-10

## Contexte

La marque reste « Libre IA », mais la décision précédente faisait de `libre-ia.fr` le domaine canonique et de `libre-ai.fr` un domaine défensif. La topologie produit a depuis été clarifiée : Website doit permettre de comprendre, chaque application d’agir indépendamment, et le programme de preuve de vérifier.

Une gate unique exigeant les sept parcours avant toute publication de Website crée un couplage artificiel. Elle empêche de publier un état honnête du portefeuille et transforme le produit le moins mûr en verrou global. À l’inverse, publier des sous-domaines vides ou des CTA vers GitHub ferait passer une intention pour une disponibilité.

## Décision

### Domaine canonique

`https://libre-ai.fr` devient l’origine publique canonique. La marque affichée reste « Libre IA ».

- `www.libre-ai.fr` redirigera en 301 vers `libre-ai.fr` ;
- `libre-ia.fr`, `libreia.fr` et `libreai.fr` restent défensifs et redirigeront en 301 vers l’origine canonique ;
- une seule origine produit des URLs canoniques, sitemap, OpenGraph et indexation ;
- aucune modification DNS n’est incluse dans cette décision documentaire : l’activation reste une opération humaine séparée.

### Séparation comprendre, agir, vérifier

```text
libre-ai.fr/produits/<slug>       comprendre l’intention et l’état
<produit>.libre-ai.fr             utiliser l’application
preuves.libre-ai.fr/<slug>        vérifier les preuves publiées
```

Noms réservés dans la topologie :

| Produit technique | Nom public | Hôte réservé |
| --- | --- | --- |
| Feed Radar | Radar | `radar.libre-ai.fr` |
| Notebook | Carnet | `carnet.libre-ai.fr` |
| AI Practices | Pratiques IA | `pratiques.libre-ai.fr` |
| Sessions | Sessions | `sessions.libre-ai.fr` |
| Boussole Politique | Boussole Politique | `boussole.libre-ai.fr` |
| Spec Studio | Studio de spécification | `specs.libre-ai.fr` |
| Agent Board | Missions | `missions.libre-ai.fr` |
| Benchmarks | Preuves | `preuves.libre-ai.fr` |

La réservation est un contrat de nommage, pas une déclaration DNS. Un hôte produit reste sans URL applicative tant que sa gate d’alpha publique n’est pas satisfaite.

### Trois parcours publics

Les sept produits ne sont pas présentés comme sept logos équivalents. Website oriente d’abord par intention :

1. **Comprendre et surveiller** — Radar, Carnet, Boussole Politique ;
2. **Apprendre et pratiquer** — Pratiques IA, Sessions ;
3. **Concevoir et piloter** — Carnet, Studio de spécification, Missions.

Un produit peut appartenir à plusieurs parcours. Cette relation n’impose aucune dépendance runtime.

### États publics

| État | Signification |
| --- | --- |
| `discovery` | vision, contrat ou prototype ; aucune disponibilité |
| `private-alpha` | parcours réservé à un groupe borné ; aucune URL publique |
| `public-alpha` | parcours cœur publiquement utilisable avec preuve datée |
| `stable` | exploitation, restauration, retrait et incidents éprouvés |

`public-alpha` et `stable` exigent simultanément :

- `app_url=https://<hôte-réservé>` ;
- `evidence_url=https://preuves.libre-ai.fr/<slug>` ;
- attestation de publication propre au produit ;
- parcours, erreurs, export, données, accessibilité, licences et retrait vérifiés.

Website peut être publié avec des produits `discovery`, à condition d’afficher cet état et de ne produire aucun CTA de lancement. Sa propre publication conserve une approbation humaine distincte.

### Isolation technique

- chaque produit est un déploiement autonome sur Clever Cloud en région européenne ;
- chaque produit possède ses données et son cycle de restauration ;
- les API publiques restent sous le même origin que l’application, par exemple `/api/v1` ;
- aucun `api.libre-ai.fr` global, aucune base globale et aucun bus central ne sont créés par défaut ;
- les intégrations commencent par des exports versionnés et des liens profonds ;
- les assets Client Kit sont embarqués dans chaque build, sans CDN runtime.

### Sécurité des sous-domaines

- entrées DNS explicites, jamais de wildcard catch-all ;
- cookies host-only avec préfixe `__Host-`, jamais `Domain=.libre-ai.fr` ;
- audiences Biscuit distinctes ;
- redirect URI, CORS et CSP explicitement bornés par produit ;
- `id.libre-ai.fr` reste réservé mais absent tant qu’une identité partagée n’est pas prouvée ;
- `status.libre-ai.fr` reste réservé mais absent tant qu’au moins deux applications publiques ne justifient une page d’état commune open source ;
- les interfaces d’infrastructure ne reçoivent pas de sous-domaines publics de marque.

## Conséquences

- Website décrit désormais l’état réel plutôt qu’un état final fictivement disponible.
- La variable globale `LIBRE_AI_PRODUCTS_VERIFIED` disparaît au profit d’une approbation Website et de gates par produit.
- Le catalogue public devient un contrat versionné incluant nom public, état, hôte réservé, URLs, action, non-objectifs et critères d’alpha.
- Passer un produit en alpha publique est une décision locale et réversible ; cela ne promeut pas les autres produits.
- Le changement de domaine canonique nécessite ultérieurement une opération DNS/301 contrôlée, une vérification TLS et une preuve post-déploiement.

## Alternatives rejetées

- **Tout publier sous `libre-ai.fr/apps/*`** : couple déploiements, auth et cycles de panne.
- **Un seul `app.libre-ai.fr`** : reconstitue le super-produit refusé par la doctrine.
- **Un domaine par produit** : fragmente la confiance, la marque et les opérations.
- **Wildcard DNS et cookie partagé** : augmente le rayon d’impact et les risques CSRF/session.
- **Attendre sept produits avant Website** : confond publication honnête du portefeuille et affirmation de disponibilité.
- **Garder `libre-ia.fr` canonique** : possible techniquement, mais contraire à la nouvelle topologie explicitement retenue sous `*.libre-ai.fr` ; le domaine reste défensif et redirigé.
