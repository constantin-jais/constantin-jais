# Security Policy

## Supported status

This repository is pre-`trusted` unless its README or ecosystem cockpit states otherwise. Treat security reports as valid even when the project is experimental.

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub Security Advisories for this repository when available. If private advisories are unavailable, open a minimal issue that does not disclose exploit details and request a private follow-up channel.

Do not include secrets, personal data, tokens, exploit payloads, or production credentials in public issues, logs, screenshots, or attachments.

## Expected handling

- Acknowledge the report before discussing remediation publicly.
- Reproduce with the smallest safe fixture possible.
- Prefer fail-closed fixes and regression tests.
- Document any temporary waiver with scope, owner, expiry, and removal plan.
- Do not publish a release automatically as part of triage.

## Supply-chain baseline

- GitHub Actions must be pinned to commit SHAs.
- CI must run without secrets by default.
- Release workflows must remain tag/manual only.
- Published artifacts should include checksums, SBOM/provenance where applicable, and minimal permissions.
