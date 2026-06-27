# App Store Release Contract v0.1

Status: Draft  
Owner: Gear Cable channel adapter  
Consumers: Rumble products that publish iOS-capable builds through App Store Connect.

## Purpose

Define the stable product-to-Gear Cable boundary for TestFlight/App Store publication without coupling every Rumble repository to upstream App Store Connect CLI flags.

Commercializable multi-platform ambition requires a reproducible release rail. This contract keeps App Store publication as distribution plumbing, not product logic.

## Boundary

Rumble owns:

- product metadata authoring;
- signed IPA production;
- screenshots and review notes;
- product-specific release decision.

Gear Cable owns:

- stable wrapper interface;
- upstream CLI compatibility metadata;
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

A product repository may provide:

```json
{
  "version": "app-store-release.v0.1",
  "app": {
    "name": "Rumble Example",
    "bundle_id": "fr.example.rumble",
    "sku": "rumble-example"
  },
  "release": {
    "ipa_path": "dist/rumble-example.ipa",
    "metadata_path": "appstore/metadata",
    "screenshots_path": "appstore/screenshots"
  },
  "policy": {
    "manual_submit_review": true,
    "append_only": true,
    "requires_human_approval": true
  }
}
```

## Required secret handling

CI may inject App Store Connect credentials as environment variables, but reports, artifacts, logs, and metadata must never contain raw key material.

Required runtime environment for the Gear Cable wrapper:

- `ASC_CLI_BIN` — pinned upstream CLI executable.
- `ASC_KEY_ID` — key identifier.
- `ASC_ISSUER_ID` — issuer identifier.
- `ASC_PRIVATE_KEY` — `.p8` private key content, written only to a temporary `0600` file.
- `ASC_TEAM_ID` — Apple team identifier.

The wrapper must remove temporary key files on exit.

## Required actions

The stable wrapper action names are:

- `validate`
- `upload-build --ipa <path>`
- `upload-metadata`
- `submit-review`
- `status`
- `compat`

The wrapper maps these actions to pinned upstream CLI templates through `ASC_CMD_*` variables.

## Forbidden shortcuts

- Rumble CI must not call the upstream App Store Connect CLI directly.
- Product code must not embed App Store credentials.
- Gear Cable must not become iOS build/signing logic.
- Release jobs must not auto-upgrade the upstream CLI.
- App Store submission must not be treated as rollbackable; compensation must be forward-only.

## Evidence expectations

A release job should preserve:

- wrapper version/ref;
- pinned upstream CLI version;
- product config hash;
- IPA artifact ref/checksum when available;
- command action performed;
- human approval reference for submit-review;
- non-secret logs.

Future Gear Depot integration should turn the IPA and metadata package into `ArtifactRef`/`ArtifactManifest` entries.
