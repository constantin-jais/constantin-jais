# Wrench DB Inspect — Gate Profiles

Status: Draft contract; implemented in the prototype through `--gate-profile-config <path>`.

## Purpose

Gate profiles define when a finding blocks CI/Bolt. They keep `wrench-db-inspect` focused on producing evidence while allowing Bolt/CI to choose strictness by context.

Without explicit profiles, the tool would either be too strict for local/PR work or too lax for protected branches/releases. Profiles also prevent each Rumble from inventing local blocking logic.

## Default Profiles

| Profile | Intended use | Default behavior |
| --- | --- | --- |
| `local` | Developer local loop | Block unwaived `critical`; warn on `high/medium/low`. |
| `pull_request` | Review before merge | Block unwaived `critical/high`; warn on `medium/low`. |
| `protected_branch` | Main branch gate | Block unwaived `critical/high`; block P0 `inspection_integrity`; warn on `medium/low`. |
| `release` | Release/promote gate | Protected-branch behavior plus no expired waiver, no unknown table classification, no unsupported P0 analysis state. |

Prototype behavior:

- without `--gate-profile-config`, it uses built-in versions of these profiles;
- with `--gate-profile-config <path>`, it loads the JSON envelope described below;
- `gate.blocks`, `gate.action`, `gate.profile`, and `gate.reason` are written per finding.

## Profile Config Shape

Configurable profiles use JSON envelope `{ data, meta }`.

```json
{
  "data": {
    "format": "wrench.db_inspect.gate_profiles.v0.1",
    "profiles": {
      "protected_branch": {
        "default_actions": {
          "critical": "block",
          "high": "block",
          "medium": "warn",
          "low": "warn",
          "info": "ignore"
        },
        "category_overrides": {
          "inspection_integrity": "block"
        },
        "rule_overrides": {
          "TABLE_CLASSIFICATION_REQUIRED": "block"
        },
        "waivers": {
          "allow_active": true,
          "block_expired": true,
          "require_owner": true,
          "require_reviewer": true,
          "require_expiry": true
        }
      }
    }
  },
  "meta": {
    "schema_version": "0.1",
    "generated_at": "2026-06-30T00:00:00Z"
  }
}
```

## Action Semantics

| Action | Meaning |
| --- | --- |
| `block` | Finding contributes to `data.summary.gate_blocked=true` and exit code `1`. |
| `warn` | Finding appears in reports but does not block. |
| `ignore` | Finding may be omitted from gate decision; use sparingly and never silently for P0. |

A finding should include the resolved gate decision:

```json
{
  "gate": {
    "blocks": true,
    "profile": "protected_branch",
    "action": "block",
    "reason": "severity high blocks in protected_branch"
  }
}
```

## Rules

- P0 `critical/high` must block in `protected_branch` and `release` unless an explicit valid waiver applies.
- `medium` P1 findings should start as warnings to measure false positives before promotion.
- Unknown P0 analysis state must not pass silently.
- Waiver acceptance is part of the profile, not hidden rule code.
- Bolt may select a profile and consume `summary.gate_blocked`; Bolt must not reinterpret raw SQL.
- Reports must remain safe: no secrets, PII, raw embeddings, row data, prompts, or DSNs.
- In `release`, `meta.redaction.applied=true` must block or require review because it means unsafe evidence reached final rendering.

## Acceptance Tests To Add

- Given `local`, a `high` finding warns but does not block.
- Given `protected_branch`, the same `high` finding blocks.
- Given a profile override promotes a P1 rule to `block`, a `medium` finding blocks.
- Given an expired waiver in `release`, the gate blocks with reason `waiver expired` and emits `WAIVER_INVALID`.
- Given an incomplete waiver in `release`, the gate blocks with reason such as `waiver missing reviewer` and emits `WAIVER_INVALID`.
- Given `meta.redaction.applied=true` in `release`, the gate blocks with reason `redaction applied in release requires review`.
- Given invalid profile config, CLI exits `2` and emits no misleading pass report.
