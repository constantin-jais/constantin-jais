# Forge logicielle — convention CI/CD

Objectif : construire une forge souveraine, auditable et reproductible sans publication automatique dangereuse.

## Workflows standards

- `.github/workflows/ci.yml` : qualité code, compilation, tests, documentation/build.
- `.github/workflows/security.yml` : dépendances, advisories, licences, sources, audit de secrets simples.
- `.github/workflows/contracts.yml` : preuves métier par couche, fixtures, snapshots, golden files, schémas.
- `.github/workflows/release.yml` : artefacts distribuables uniquement, déclenchés par tag `v*.*.*` ou `workflow_dispatch`.
- `.github/workflows/forge-health.yml` : cockpit global dans `constantin-jais`.

## Règles communes

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
- Revue obligatoire avant tout changement de `release.yml`, dépendances critiques, ou permissions Actions.

## Progression

1. Phase 1 : CI standard + badges utiles.
2. Phase 2 : `security.yml` séparé sur repos sensibles.
3. Phase 3 : `contracts.yml` avec preuves par couche.
4. Phase 4 : `release.yml` pour outils distribuables, avec checksums/SBOM/provenance.
5. Phase 5 : `forge-health.yml` global dans `constantin-jais` ; warnings remote tant que les repos ne sont pas mergés, hard-fail local sur les conventions du cockpit.
