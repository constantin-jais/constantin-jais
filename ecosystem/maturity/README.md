# Rumble Delivery Maturity Claims

This directory contains real, current maturity claims for Rumble projects.

Fixtures under `ecosystem/specs/harness/fixtures/maturity/` test the contract. Files here are the operational claims consumed by:

```bash
cosmatic maturity report ecosystem/maturity
```

Rules:

- Claims are read-only evidence, not automatic promotion.
- `current_level` must be honest and dated.
- `target_level` may express long-term product ambition.
- `blocked_by` is useful: it defines the next quality increment.
- Commercializable maturity means external-user quality, not monetization or startup prioritization.
