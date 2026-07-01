# Forge health

Source de vérité légère pour suivre la maturité CI/CD de la stack.

| Repo | Couche | CI | Security | Contracts | Release | Policy | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| `constantin-jais` | Ecosystem | partiel | oui | specs | — | oui | cockpit, contrats globaux, forge-health local hard-fail |
| `cos-matic` | Bolt | oui | oui | oui | non | oui | handoff smoke et dogfood drift gate |
| `wrench-db-inspect` | Wrench | oui | oui | à créer | tag/manual | oui | CLI distribuable avec checksums/SBOM/attestation |
| `wrench-loader` | Wrench | oui | oui | oui | non | oui | fixtures hostiles en gate dédiée |
| `gear-memory` | Gear | oui | oui | oui | non | oui | contrats mémoire/provenance en gate dédiée |
| `gear-depot` | Gear | oui | oui | oui | non | oui | contrats artefacts en gate dédiée |
| `gear-cable` | Gear | oui | oui | oui | tag/manual | oui | release CLI avec checksums/SBOM/attestation |
| `rumble-feed-mind` | Rumble | oui | oui | oui | tag/manual | oui | CLI + CuratedItemExport contract avec checksums/SBOM/attestation |
| `rumble-lm` | Rumble | oui | oui | à créer | non | oui | intégration Postgres/Redis existante |
| `rumble-cos` | Rumble | oui | oui | oui | non | oui | Astro + Playwright en contracts |

## Légende

- `oui` : workflow dédié ou gate explicite présent.
- `partiel` : couverture utile mais non alignée complètement sur la convention.
- `à créer` : attendu par la forge cible, non bloquant phase 1.
- `tag/manual` : release déclenchée uniquement par tag ou dispatch manuel.
- `Policy` : `SECURITY.md` + `.github/CODEOWNERS` présents.

## Prochaine évolution

- Après merge multi-repos, passer l'inventaire remote de warning à hard-fail.
- Appliquer `docs/branch-protection.md` dans GitHub repo par repo.
- Vérifier les attestations GitHub selon `docs/release-verification.md` sur une première release tag réelle avant de promouvoir la release maturity.
- Ajouter les `contracts.yml` manquants seulement quand une preuve contractuelle réelle existe.
