# Secret scanning baseline

Current baseline: lightweight regex smoke in each `security.yml` plus GitHub-native secret scanning when enabled on the repository.

## What the smoke catches

The local workflow grep blocks common high-risk patterns:

- AWS access key IDs (`AKIA...`);
- GitHub classic tokens (`ghp_...`);
- GitHub fine-grained tokens (`github_pat_...`);
- private key PEM headers.

It intentionally excludes lockfiles to avoid noisy dependency metadata.

## What remains to enable in GitHub

- GitHub secret scanning / push protection where available.
- Optional full-history scan with an open-source scanner such as Gitleaks before public release.
- Manual review of screenshots, logs, examples, and generated reports.

## Measuring success

```bash
git grep -nEI '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----)' -- ':!package-lock.json' ':!Cargo.lock'
```

Success: no output.

## Best practice

- Keep CI runnable without secrets by default.
- Prefer OIDC short-lived credentials over long-lived tokens.
- Never add real tokens to fixtures, docs, screenshots, issue bodies, or golden files.
- If a secret is committed, rotate it first, then clean history if needed.
