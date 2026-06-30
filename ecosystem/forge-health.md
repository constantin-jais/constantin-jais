# Forge health

Source de vérité légère pour suivre la maturité CI/CD de la stack.

| Repo | Couche | CI | Security | Contracts | Release | Notes |
|---|---|---:|---:|---:|---:|---|
| `constantin-jais` | Ecosystem | partiel | — | specs | — | cockpit et contrats globaux |
| `cos-matic` | Bolt | oui | oui | oui | non | handoff smoke et dogfood drift gate |
| `wrench-db-inspect` | Wrench | oui | oui | à créer | tag/manual | CLI distribuable avec checksums/SBOM/provenance-lite |
| `wrench-loader` | Wrench | oui | oui | oui | non | fixtures hostiles en gate dédiée |
| `gear-memory` | Gear | oui | oui | oui | non | contrats mémoire/provenance en gate dédiée |
| `gear-depot` | Gear | oui | oui | oui | non | contrats artefacts en gate dédiée |
| `gear-cable` | Gear | oui | oui | oui | tag/manual | release CLI avec checksums/SBOM/provenance-lite |
| `rumble-feed-mind` | Rumble | oui | oui | à créer | tag/manual | release CLI avec checksums/SBOM/provenance-lite |
| `rumble-lm` | Rumble | oui | oui | à créer | non | intégration Postgres/Redis existante |
| `rumble-cos` | Rumble | oui | oui | oui | non | Astro + Playwright en contracts |

## Légende

- `oui` : workflow dédié ou gate explicite présent.
- `partiel` : couverture utile mais non alignée complètement sur la convention.
- `à créer` : attendu par la forge cible, non bloquant phase 1.
- `tag/manual` : release déclenchée uniquement par tag ou dispatch manuel.

## Prochaine évolution

- Ajouter un `forge-health.yml` qui vérifie automatiquement la présence des workflows, licences, badges et fichiers de politique.
- Ajouter des `contracts.yml` par couche, sans dupliquer inutilement les tests unitaires.
- Introduire SBOM/provenance seulement sur les repos qui produisent des artefacts distribuables.
