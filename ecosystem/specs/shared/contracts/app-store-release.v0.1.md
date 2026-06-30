# App Store Release Contract v0.1

Status: Accepted
Owner: Gear Cable channel adapter  
Consumers: Rumble products that publish iOS-capable builds through App Store Connect.
External tool: `rorkai/App-Store-Connect-CLI` (`asc`) pinned to `2.5.0` until a Gear Cable compatibility PR updates it.

## Purpose

Define the stable product-to-Gear Cable boundary for TestFlight/App Store publication without coupling every Rumble repository to upstream App Store Connect CLI flags.

```text
rumble-* release job
  -> gear-cable/templates/gitlab/ios-appstore-connect.yml
  -> gear-cable/channels/appstore-connect/appstore-release.sh
  -> pinned asc 2.5.0
  -> Apple App Store Connect / TestFlight
```

## Boundary

Rumble owns:

- product metadata authoring;
- signed IPA production;
- screenshots and review notes;
- product-specific release decision.

Gear Cable owns:

- stable wrapper interface;
- upstream CLI install/pin/compatibility metadata;
- CI template shape;
- append-only release channel semantics;
- checksum/provenance handoff to Gear Depot when available.

Gear Cable does **not** own:

- Apple developer account administration;
- signing identities or certificates;
- iOS build logic;
- product copywriting or screenshots;
- App Review business decisions.

## Product config shape

Each iOS-capable product provides `appstore/release.config.json` matching [`app-store-release.v0.1.schema.json`](./app-store-release.v0.1.schema.json).

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
  },
  "policy": {
    "manual_submit_review": true,
    "append_only": true,
    "requires_human_approval": true
  },
  "upstream": {
    "cli_version": "2.5.0",
    "compatibility_profile": "asc-2.5.0"
  }
}
```

If `release.version` is omitted in CI, the wrapper may infer it from tags shaped `ios-vX.Y.Z`.

## Stable wrapper actions

| Action | Meaning | Default `asc 2.5.0` mapping |
| --- | --- | --- |
| `validate` | Check config, secrets, binary, metadata dirs, and key temp-file handling. | no publication |
| `auth` | Login using config-backed auth with bypassed keychain. | `asc auth login --bypass-keychain ...` |
| `upload-build [--ipa <path>]` | Upload a signed IPA and wait for processing when supported. | `asc builds upload --app {APP_ID} --ipa {IPA} --wait --output json` |
| `upload-metadata` | Apply metadata directory for the target version. | `asc metadata apply --app {APP_ID} --version {VERSION} --dir {METADATA}` |
| `upload-screenshots` | Apply reviewed screenshot artifacts for the target version. | `asc screenshots apply --app {APP_ID} --version {VERSION} --review-output-dir {SCREENSHOTS} --confirm` |
| `submit-review [--ipa <path>]` | Canonical App Store publish/submission path. | `asc publish appstore --app {APP_ID} --ipa {IPA} --version {VERSION} --submit --confirm` |
| `status` | Report App Store status as JSON. | `asc status --app {APP_ID} --output json` |
| `compat` | Scheduled compatibility smoke check. | `asc version` + `asc --help` |

The wrapper supports `ASC_CMD_*` mapping overrides, but product pipelines should not need them. Overrides are for Gear Cable compatibility PRs, not per-product drift.

## Required secret handling

Required GitLab protected/masked variables:

- `ASC_KEY_ID`
- `ASC_ISSUER_ID`
- `ASC_PRIVATE_KEY`
- `ASC_TEAM_ID`

The wrapper:

- writes `ASC_PRIVATE_KEY` only to a temporary `0600` file;
- deletes the file on exit;
- sets `ASC_TELEMETRY_DISABLED=1` by default in CI;
- never emits raw key material.

## CI consumption model

Recommended product consumption:

1. Product CI checks out a pinned Gear Cable tag/SHA or consumes a published Gear Cable artifact.
2. Product includes/uses `gear-cable/templates/gitlab/ios-appstore-connect.yml`.
3. Product sets `GEAR_CABLE_REPOSITORY` and pinned `GEAR_CABLE_REF` when Gear Cable is not already present.
4. Product release jobs call only the Gear Cable wrapper.

No `ci/` or `tools/` root-level orphan directory is part of the stack contract.

## Upstream synchronization

- Current upstream version: `asc 2.5.0`.
- Pin metadata: `gear-cable/channels/appstore-connect/compatibility.yml`.
- Installer: `gear-cable/channels/appstore-connect/install-asc.sh`.
- Compatibility job: `appstore-cli:compatibility-check`.

Update process:

1. Change the pin in Gear Cable only.
2. Run installer checksum verification and wrapper `compat`.
3. Update wrapper default mappings only if upstream syntax changed.
4. Merge through a small Gear Cable compatibility PR.
5. Update product `GEAR_CABLE_REF` after the Gear Cable tag/artifact is published.

## Compliance note

Apple App Store Connect is a proprietary US dependency accepted only for iOS distribution. Release automation must not upload business data, learner data, feed content, notes, internal agent traces, or other product/user data beyond app release artifacts and App Store metadata.

## Acceptance criteria

A product is compliant when:

- CI calls the Gear Cable wrapper, never upstream `asc` directly;
- `validate` succeeds before any publication action;
- release jobs are protected and manual for App Store submission;
- `asc` version is pinned and checksum-verified at install;
- `appstore-cli:compatibility-check` exists or is inherited from Gear Cable;
- no App Store Connect secret is committed, logged, or stored as an artifact.
