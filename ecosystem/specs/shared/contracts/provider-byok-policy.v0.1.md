# Policy Contract — Provider/BYOK v0.1

Status: Accepted by ADR 0043; product instantiation remains required.
Schema: future `provider-byok-policy.v0.1.schema.json` if automation needs it.

## Purpose

Provider/BYOK policy defines how Libre AI products may use user-provided model/provider credentials and external AI providers without leaking secrets, violating sovereignty constraints, or creating hidden product dependencies.

## Applies To

- Feed Radar natural-language rules and explanations;
- Sessions source-grounded generation;
- Spec Studio AI-assisted spec drafting;
- any Bolt-mediated provider call using product context.

## Required Defaults

| Area | Rule |
| --- | --- |
| Sovereign default | Prefer local/self-hosted or Clever AI; no direct-provider or implicit fallback. |
| BYOK | User/provider keys are encrypted at rest, never exported, never logged, never embedded in artifacts or handoffs. |
| Delegation | Provider use across service boundaries requires attenuated delegated authorization; Biscuit is the canonical shared format. |
| Logging | Logs may contain provider class, model ref, token counts, safe request id, and hashes; never prompt body if private, never raw credentials. |
| Retention | Provider request/response retention must be explicit per product and purpose. |
| Deletion | User can delete provider credentials and derived cached provider metadata. |
| Export | Exports include provider policy refs and output provenance, not keys or raw provider credentials. |
| Fallback | If no allowed provider is configured, the feature fails closed or uses deterministic/non-AI path. |

## Provider Classification

| Class | Examples | Default verdict | Conditions |
| --- | --- | --- | --- |
| `local` | local model/runtime | Preferred | Must not silently exfiltrate prompts or telemetry. |
| `eu_open_or_sovereign` | Clever AI, self-hosted OSS, EU-hosted open stack | Preferred | DPA/data residency documented for hosted providers. |
| `direct_model_provider` | Mistral API, OpenAI, Anthropic, Google, AWS Bedrock, Azure OpenAI | Blocked | No default, direct call or implicit fallback; a future exception requires a separate ADR. |
| `payment_provider` | Stripe | Not an AI provider; isolate | Must not be required for local/self-hosted core use. |

## BYOK Storage Requirements

- Encrypt with an application-held master key or local OS secret store.
- Store key version and provider id separately from ciphertext.
- Support rotation by key version.
- Do not store plaintext after validation.
- Never include secrets in `Debug`, JSON reports, fixtures, logs, traces, Wrench reports, Gear metadata, or handoff payloads.
- Treat provider account identifiers as personal/commercial metadata and minimize logs.

## Product Gates

A product is not `READY_FOR_HARNESS_PACKAGE` for model-backed features until it documents:

1. provider allowlist and blocked providers;
2. BYOK encryption and rotation;
3. prompt/context PII classification;
4. log redaction policy;
5. retention/deletion behavior;
6. export/handoff exclusions;
7. Wrench inspection profile for secrets/PII;
8. Bolt delegation boundary if a provider call crosses services.

## Feed Radar-specific Application

Feed Radar remains blocked until this policy is instantiated with:

- provider allowlist for rule explanation;
- key storage and deletion workflow;
- no raw feed private content in provider logs;
- no BYOK material in `CuratedItemExport`;
- Stripe isolated from core curation/export features.

## Sessions-specific Application

Sessions remains warning until this policy is instantiated with:

- source-grounded prompt minimization;
- citation/provenance requirements;
- facilitator validation gate;
- retention defaults for prompts, responses, raw participant data, and exports.
