# Forge health

Source de vérité légère pour suivre la maturité CI/CD de la stack.

| Repo | Couche | CI | Security | Contracts | Release | Policy | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| `constantin-jais` | Ecosystem | partiel | oui | specs | — | oui | cockpit, contrats globaux, forge-health remote hard-fail |
| `bolt-harness` | Bolt | hygiene | n/a | n/a | non | oui | dépôt public de harness, gate `Harness hygiene` |
| `bolt-cos-matic` | Bolt | oui | oui | oui | non | oui | ancien `cos-matic`; handoff smoke et dogfood drift gate |
| `wrench-db-inspect` | Wrench | oui | oui | à créer | tag/manual | oui | CLI distribuable avec checksums/SBOM/attestation |
| `wrench-loader` | Wrench | oui | oui | oui | non | oui | fixtures hostiles en gate dédiée |
| `gear-memory` | Gear | oui | oui | oui | non | oui | contrats mémoire/provenance en gate dédiée |
| `gear-depot` | Gear | oui | oui | oui | non | oui | contrats artefacts en gate dédiée |
| `gear-cable` | Gear | oui | oui | oui | tag/manual | oui | release CLI avec checksums/SBOM/attestation |
| `rumble-canvas` | Rumble | oui | hygiene | à créer | non | oui | repo public avec Rust quality gates + hygiene |
| `rumble-crew` | Rumble | hygiene | n/a | à créer | non | oui | repo public placeholder gouverné |
| `rumble-feed-mind` | Rumble | oui | oui | oui | tag/manual | oui | CLI + CuratedItemExport contract avec checksums/SBOM/attestation |
| `rumble-lm` | Rumble | oui | oui | à créer | non | oui | intégration Postgres/Redis existante |
| `rumble-note` | Rumble | hygiene | n/a | à créer | non | oui | repo public placeholder gouverné |
| `rumble-cos` | Rumble | oui | oui | oui | non | oui | Astro + Playwright en contracts; repo public protégé |

## Légende

- `oui` : workflow dédié ou gate explicite présent.
- `partiel` : couverture utile mais non alignée complètement sur la convention.
- `à créer` : attendu par la forge cible, non bloquant phase 1.
- `tag/manual` : release déclenchée uniquement par tag ou dispatch manuel.
- `Policy` : `SECURITY.md` + `.github/CODEOWNERS` présents.

## Prochaine évolution

- Maintenir `forge-health.yml` en hard-fail sur l'inventaire public lisible par `GITHUB_TOKEN` : policy files, workflows attendus et visibilité publique.
- Pour auditer les settings admin (`allow_auto_merge`, suppression de branche, secret scanning, push protection) et branch protection dans GitHub Actions, configurer un secret admin dédié `FORGE_HEALTH_ADMIN_TOKEN`; sans ce secret, ces audits restent vérifiés localement par admin et signalés en warning dans le workflow.
- Vérifier les attestations GitHub selon `docs/release-verification.md` sur une première release tag réelle avant de promouvoir la release maturity.
- Ajouter les `contracts.yml` manquants seulement quand une preuve contractuelle réelle existe.
- Piloter toute autonomie agent via `docs/agent-merge-policy.md`, pas par bypass global de `main`.
