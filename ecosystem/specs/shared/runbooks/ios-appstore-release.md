# Runbook — iOS App Store release for Rumble products

## Preconditions

- A signed `.ipa` is produced by the product build job.
- Gear Cable is available in CI via a pinned `GEAR_CABLE_REF` checkout, vendored tree, or published artifact.
- `gear-cable/channels/appstore-connect/appstore-release.sh` is executable.
- `appstore/release.config.json` follows `app-store-release.v0.1`.
- GitLab protected/masked variables are configured:
  - `ASC_KEY_ID`
  - `ASC_ISSUER_ID`
  - `ASC_PRIVATE_KEY`
  - `ASC_TEAM_ID`
- Optional but recommended CI variables:
  - `GEAR_CABLE_REPOSITORY`
  - `GEAR_CABLE_REF` pinned to a Gear Cable tag/SHA
  - `ASC_VERSION=2.5.0`

## Product config

Minimal `appstore/release.config.json`:

```json
{
  "version": "app-store-release.v0.1",
  "app": {
    "name": "rumble-example",
    "bundle_id": "fr.example.rumble",
    "app_store_id": "1234567890",
    "primary_locale": "fr-FR"
  },
  "release": {
    "version": "1.2.3",
    "ipa_path": "dist/rumble-example.ipa",
    "metadata_path": "appstore/metadata",
    "screenshots_path": "appstore/screenshots"
  }
}
```

## Release flow

1. Create a protected tag:

   ```bash
   git tag ios-vX.Y.Z
   git push origin ios-vX.Y.Z
   ```

2. Run `release:ios:testflight` manually.
3. Verify TestFlight processing in App Store Connect.
4. Run `release:ios:submit` manually only when metadata/build are approved.

## Upstream CLI update flow

1. Update the pinned version in `gear-cable/channels/appstore-connect/compatibility.yml` and CI `ASC_VERSION` defaults.
2. Run `appstore-cli:compatibility-check`.
3. If upstream flags changed, update Gear Cable wrapper defaults or mappings.
4. Merge as `chore(update-app-store-connect-cli): <version>` in Gear Cable.
5. Move product `GEAR_CABLE_REF` to the new Gear Cable tag/SHA.

## Incident recovery

App Store publication is append-only. Do not describe recovery as rollback.

- Revert the CLI/Gear Cable pin for future releases if needed.
- Use App Store Connect cancellation/removal/metadata correction flows for submitted versions.
- Do not rotate Apple credentials unless leakage is suspected.
- If a `.p8` key was exposed in logs/artifacts, revoke it immediately in App Store Connect and rotate GitLab variables.

## Compliance note

Apple App Store Connect is a proprietary US dependency accepted only for iOS distribution. Release automation must not upload business data, learner data, feed content, notes, internal agent traces, or other product/user data beyond app release artifacts and App Store metadata.
