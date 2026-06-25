# Acceptance Tests — rumble-feed-mind

Status: Draft / pre-product-development gates.

## Feed ingestion and triage

### Scenario: Add valid feed

Given an Owner submits a valid feed URL  
When the system validates the feed  
Then a `FeedSource` is created  
And the stored/exportable evidence uses a URL hash by default  
And `feed_source.created` is recorded without secrets.

### Scenario: Poll feed and discover items

Given a feed source exists  
When the worker polls the feed  
Then new `FeedItem` records are created with `content_hash` and `source_url_hash`  
And `feed_item.discovered` events contain safe refs only.

### Scenario: Override classification

Given an item was classified by a rule  
When a Curator overrides the decision  
Then the previous and new decisions are audited  
And the override does not mutate the original rule evidence.

## Rules and explanations

### Scenario: Deterministic rule evaluation

Given a deterministic rule and a feed item  
When the rule is evaluated  
Then a `RuleEvaluation` is produced with decision, explanation, evidence hash, and timestamp.

### Scenario: Provider-backed rule is blocked without policy

Given no accepted Provider/BYOK policy exists  
When a user requests provider-backed rule evaluation  
Then the request is refused fail-closed  
And no provider call is made.

### Scenario: Provider-backed rule minimizes context

Given an accepted Provider/BYOK policy and a normal item  
When provider-backed evaluation runs  
Then the provider receives only minimized context  
And logs include provider class/model ref/counts but no prompt body or key material.

## BYOK and provider policy

### Scenario: Store BYOK key write-only

Given an Owner submits a provider key  
When the key is stored  
Then it is encrypted with a key version  
And the response contains only `key_ref`  
And logs do not contain plaintext or ciphertext.

### Scenario: Delete BYOK key

Given a stored key ref exists  
When the Owner deletes it  
Then it is deactivated/deleted  
And future provider calls using the key fail closed  
And `byok_key.deleted` is recorded safely.

### Scenario: US proprietary provider is blocked by default

Given a provider class `us_proprietary`  
When no waiver/user notice is accepted  
Then provider routing is refused.

## CuratedItemExport

### Scenario: Preview export for normal curated item

Given a curated item with privacy `normal`  
When the Curator previews export to `rumble-note`  
Then the preview conforms to `CuratedItemExport v0.1`  
And includes content hash, source URL hash, curation reason, rule evidence, source ref, artifact/provenance refs or pending refs.

### Scenario: no_handoff item blocks export

Given a curated item with privacy `no_handoff`  
When the user attempts export  
Then the export is refused  
And no artifact/handoff is created.

### Scenario: sensitive item requires approval

Given a curated item with privacy `sensitive`  
When the user attempts export without explicit inclusion reason and approval ref  
Then the export is refused.

### Scenario: export excludes secrets and payment data

Given a workspace has BYOK keys and optional Stripe billing  
When a curated item export is created  
Then the export contains no BYOK material, no JWT/session token, and no Stripe/payment identifiers.

## Harness boundary

### Scenario: FeedMind export cannot execute

Given a valid `CuratedItemExport`  
When it is used as context for a future harness package  
Then downstream execution remains forbidden  
And only planning-only handoff is allowed after human approval.

### Scenario: Wrench critical finding blocks export submission

Given Wrench reports a critical PII/secrets finding  
When export submission is requested  
Then submission is blocked until the finding is resolved or explicitly waived by policy.

## Sovereignty and dependency gates

### Scenario: self-hosted core works without Stripe

Given Stripe is not configured  
When feeds, rules, triage, and exports are used locally/self-hosted  
Then core features remain available  
And billing features are disabled only as optional adapter behavior.

### Scenario: dependency advisories block READY status

Given `cargo deny check advisories` is red  
When readiness is evaluated  
Then product status cannot become `READY_FOR_HARNESS_PACKAGE` or `READY_FOR_IMPLEMENTATION_PLANNING` without accepted waivers and expiry.

## Minimum command gates

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace
cargo test --workspace --no-run
cargo deny check licenses
cargo deny check advisories
```

Expected current state:

- fmt/clippy/test/no-run/licenses pass;
- advisories remain blocking until fixed or formally waived.
