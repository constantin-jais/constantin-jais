# Release verification checklist

Use this before promoting release maturity for any repository that publishes artifacts.

## Required release assets

For each distributed artifact, expect:

- artifact archive or binary;
- `.sha256` checksum;
- SBOM when the stack supports it;
- provenance-lite JSON or GitHub build provenance attestation;
- release notes identifying the tag and scope.

## Local verification

```bash
sha256sum -c *.sha256
```

On macOS:

```bash
shasum -a 256 -c *.sha256
```

## GitHub attestation verification

```bash
gh attestation verify <artifact> --repo constantin-jais/<repo>
```

Success means the artifact is linked to the repository workflow identity. It does not replace code review, dependency review, or runtime security testing.

## Release constraints

- Releases are tag/manual only.
- No automatic crate/npm/container publication without explicit review.
- `contents: write` is limited to the release upload job.
- `id-token: write` and `attestations: write` are limited to the attestation job.
- Failed checksum/SBOM/attestation blocks promotion of release maturity.

## First-release recommendation

Validate the process on the smallest CLI artifact first, then reuse the same checklist for larger products.
