# Rumble Product Specifications

This directory contains the product specifications for the active Rumble products.

The goal is not to write static documentation. The goal is to create implementation-ready product contracts that connect:

- product intent;
- roles and permissions;
- screens and actions;
- domain logic;
- data models;
- services and APIs;
- security/RGPD constraints;
- shared Bolt/Wrench/Gear capabilities.

## Active Products

| Product | Spec status | Purpose |
| --- | --- | --- |
| `rumble-canvas` | Drafting / harness producer | Product-conception workspace: conversations → decisions → specs → packages → handoffs. |
| `rumble-cos` | Not started | Education and sharing blog. |
| `rumble-crew` | Drafting | Human/agent teamwork workspace. |
| `rumble-feed-mind` | Drafting / needs license-stack decision | Intelligent feed/watch pipeline producing curated knowledge for the harness. |
| `rumble-lm` | Drafting | Source-grounded learning and facilitation platform. |
| `rumble-note` | Drafting | Local-first block-based personal knowledge system. |

## Spec Rule

Every product spec must identify when a need is product-specific and when it should become a shared capability.

Shared capabilities are logged in:

- `shared/shared-capabilities.md`

Decisions and unresolved questions are logged in:

- `shared/decision-log.md`
- `shared/open-questions.md`

## Product Spec Structure

Each product should eventually contain:

```text
00-product-charter.md
01-personas-and-roles.md
02-user-journeys.md
03-information-architecture.md
04-screens-and-actions.md
05-domain-model.md
06-data-model.md
07-services-and-apis.md
08-events-and-workflows.md
09-permissions-security-rgpd.md
10-non-functional-requirements.md
11-acceptance-tests.md
12-open-questions.md
```

Use `shared/spec-template.md` as the canonical template.
