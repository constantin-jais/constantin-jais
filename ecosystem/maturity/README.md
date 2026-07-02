# Maturity Claims

This directory contains real, current maturity claims.

- Rumble delivery claims use `rumble.delivery_maturity.v0.1` and live at the top level.
- Portal/Bolt/Wrench/Gear stack claims use `stack.project_maturity.v0.1` and live in `stack/`.

Fixtures under `ecosystem/specs/harness/fixtures/maturity/` and `ecosystem/specs/harness/fixtures/stack-maturity/` test the contracts. Files here are operational claims validated by:

```bash
bash ecosystem/specs/ci-validate-contracts.sh
```

The older `cosmatic maturity report ecosystem/maturity` command is only valid when the installed Cosmatic binary supports that subcommand.

Rules:

- Claims are read-only evidence, not automatic promotion.
- `current_level` must be honest and dated.
- `target_level` may express long-term product ambition.
- `blocked_by` is useful: it defines the next quality increment.
- Commercializable maturity means external-user quality, not monetization or startup prioritization.
