# Ecosystem logicielle — convention CI/CD

Objectif : construire un écosystème souveraine, auditable et reproductible sans publication automatique dangereuse.

## Plan de contrôle de ce dépôt

Les workflows réellement actifs ici vivent tous sous `.github/workflows/` — GitHub
ne lit aucun autre emplacement. Trois d'entre eux portent un check **requis** sur
`main` ; le quatrième est filtré par `paths:` et ne l'est donc pas, à raison.

| Workflow                                  | Job (nom du check)                              | Requis |
| ----------------------------------------- | ----------------------------------------------- | ------ |
| `.github/workflows/context-hygiene.yml`   | `No private identifiers or machine-local paths` | oui    |
| `.github/workflows/stack-conventions.yml` | `Stack workflow conventions`                    | oui    |
| `.github/workflows/spec-contracts.yml`    | `json-schema-fixtures`                          | oui    |
| `.github/workflows/readme-guardrail.yml`  | `README guardrail`                              | non    |

Un contrôle qui n'est pas dans un de ces trois jobs requis produit un check
non requis, donc mergeable en rouge : décoratif. Tout nouveau garde-fou se câble
dans le job requis dont il partage le sujet, il ne fonde pas un workflow de plus.

## Convention de nommage pour les dépôts produits

Nomenclature attendue sous `.github/workflows/` dans les dépôts produits de
l'écosystème (ces noms décrivent d'autres dépôts, pas celui-ci) :

- `ci.yml` : qualité code, compilation, tests, documentation/build.
- `security.yml` : dépendances, advisories, licences, sources, audit de secrets simples.
- `contracts.yml` : preuves métier par couche, fixtures, snapshots, golden files, schémas.
- `release.yml` : artefacts distribuables uniquement, déclenchés par tag `v*.*.*` ou `workflow_dispatch`.

## Règles communes

- `SECURITY.md` et `.github/CODEOWNERS` présents sur les repos publics, avec revue humaine sur workflows, releases et dépendances.
- Branch protection appliquée selon `docs/branch-protection.md`; agent merge encadré par `docs/agent-merge-policy.md`.
- Secret scanning baseline documentée dans `docs/secret-scanning.md` ; le grep CI est un smoke, pas un audit complet d'historique.
- Vérification release selon `docs/release-verification.md` avant toute promotion de maturité release.
- Permissions GitHub Actions minimales : `contents: read` par défaut.
- CI de base sans secret.
- Release uniquement manuelle ou tag-based.
- Artefacts release : checksums SHA256, SBOM quand pertinent, et attestations de provenance avec `id-token: write` limité au job d'attestation.
- Pas de publication automatique crates/npm/container sans étape explicite et revue.
- Rust : `RUSTFLAGS: "-D warnings"`, `cargo fmt --all --check`, `cargo check --workspace --all-targets --all-features`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`, `cargo doc --workspace --all-features --no-deps`.
- Supply-chain Rust : `cargo deny check` si `deny.toml`, plus `cargo audit` avec waivers documentés.
- Node : `npm ci`, typecheck/lint/build, audit dépendances, politique licence progressive.
- Actions : pinner les actions GitHub à un SHA de commit ; garder le tag d'origine en commentaire pour la maintenance humaine.

## Adaptation par couche

### Rumble — produits

- Build produit.
- Tests unitaires/intégration.
- Smoke e2e si web.
- Accessibilité progressivement.
- Pas de déploiement automatique par défaut.

### Bolt — orchestration

- Dry-run déterministe.
- Refusal tests.
- Safe-write boundaries.
- Drift detection.
- Tout chemin live doit être manuel, fenced, et sandbox-only par défaut.

### Wrench — inspection / validation

- Fixtures hostiles.
- Snapshots ou golden reports.
- Fail-closed behavior.
- Rapports inspectables, sans fuite de secret.

### Gear — infrastructure / supply-chain

- Manifests.
- Checksums.
- SBOM.
- Provenance.
- Release plans reproductibles.
- Politiques artefact explicites.

## Branch protection recommandée

Sur `main`, exiger :

- PR obligatoire.
- `ci` vert.
- `security` vert pour les repos avec dépendances.
- `contracts` vert quand présent.
- Pas de bypass administrateur sauf urgence documentée.
- Suppression de branche après merge.
- Auto-merge autorisé uniquement après checks/reviews requis ; pas de bypass agent.
- Revue obligatoire avant tout changement de `release.yml`, dépendances critiques, ou permissions Actions.

## Progression

1. Phase 1 : CI standard + badges utiles.
2. Phase 2 : `security.yml` séparé sur repos sensibles.
3. Phase 3 : `contracts.yml` avec preuves par couche.
4. Phase 4 : `release.yml` pour outils distribuables, avec checksums/SBOM/provenance.
5. Phase 5 : `ecosystem-health.yml` global dans `constantin-jais` ; inventaire public remote en hard-fail après adoption multi-repos.
