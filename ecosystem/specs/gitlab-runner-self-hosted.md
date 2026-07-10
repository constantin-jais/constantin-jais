# GitLab Runner self-hosted — Spec Contracts

Status: optional compatibility note, not active CI target.

Active CI for this repository is GitHub Actions: root `.github/workflows/spec-contracts.yml`.

## Local prerequisites verified

On this workstation:

- `gitlab-runner` is installed;
- `uv` is installed (provisions Python per the validation script's PEP 723 header);
- a future optional GitLab CI job could use tag `self-hosted`.

## Register the runner, only if GitLab becomes active later

Do not commit or paste the runner token in files or logs.

Set the URL and token in the shell session only:

```bash
export GITLAB_URL="https://gitlab.example.eu"
export GITLAB_RUNNER_TOKEN="glrt-REPLACE_WITH_RUNNER_TOKEN"
```

Register a shell runner with the required tag:

```bash
gitlab-runner register \
  --non-interactive \
  --url "$GITLAB_URL" \
  --token "$GITLAB_RUNNER_TOKEN" \
  --executor "shell" \
  --description "constantin-jais-spec-contracts" \
  --tag-list "self-hosted" \
  --run-untagged="false" \
  --locked="true"
```

Then unset the token:

```bash
unset GITLAB_RUNNER_TOKEN
```

## Run locally before pushing

```bash
sh ecosystem/specs/ci-validate-contracts.sh
```

Expected result:

```text
OK: 12 positive fixtures and 15 negative fixtures validated.
```

## Start the runner

Foreground, useful for first verification:

```bash
gitlab-runner run
```

As a service on macOS/Homebrew, if desired:

```bash
gitlab-runner install
gitlab-runner start
```

## Security notes

- Use a project-scoped or group-scoped runner token with minimal scope.
- Keep `run_untagged=false`; only jobs tagged `self-hosted` should run here.
- Do not mount secrets into this job; schema validation does not need them.
- Prefer an internal Python package mirror/cache for `jsonschema` dependencies if the CI environment must avoid public package egress.
- Do not publish CI logs containing raw fixture bodies if future fixtures include sensitive examples; current fixtures use fake opaque IDs only.
