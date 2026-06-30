# rumble-lm Sanitized Schema Export

Use this guide to produce the product-dependent input required by `run-pilot.sh`.

## Hard safety rules

- Export schema only, never data.
- Do not include DSNs, passwords, tokens, comments containing secrets, row values, prompts, source text, response content, or raw embeddings.
- Prefer running from a trusted developer machine or CI job with read-only schema access.
- Store outputs in `pilots/rumble-lm/inputs/` only for local runs; do not commit unless reviewed and sanitized.

## Recommended command

```bash
pg_dump \
  --schema-only \
  --no-owner \
  --no-privileges \
  --no-comments \
  --schema=public \
  "$DATABASE_URL" \
  > /tmp/rumble-lm.schema.raw.sql
```

Then sanitize and review:

```bash
# Remove accidental connection strings or secret-like fragments if tooling appended any.
perl -pe 's#postgres(ql)?://[^[:space:]]+#postgres://[REDACTED]#g; s#(password|secret|token|api_key)=\S+#$1=[REDACTED]#ig' \
  /tmp/rumble-lm.schema.raw.sql \
  > /tmp/rumble-lm.schema.sql

# Must return no matches before sharing/committing.
grep -E 'postgres://|postgresql://|password=|secret=|token=|api_key=|sk_test_|sk_live_|Bearer |Basic ' \
  /tmp/rumble-lm.schema.sql && exit 1 || true
```

Copy locally for the pilot:

```bash
cp /tmp/rumble-lm.schema.sql ecosystem/specs/wrench-db-inspect/pilots/rumble-lm/inputs/schema.sql
cp ecosystem/specs/wrench-db-inspect/examples/security-manifest.rumble-lm.example.json \
  ecosystem/specs/wrench-db-inspect/pilots/rumble-lm/inputs/security-manifest.json
```

Edit `inputs/security-manifest.json` to match actual tables, roles, and embedding status.

## Run

```bash
cd ecosystem/specs/wrench-db-inspect/pilots/rumble-lm
PROFILE=release ./run-pilot.sh
```

## Expected current behavior

- One-hop and supported multi-hop tenant derivations can pass when FK-chain and policy-chain evidence are present.
- If the real schema uses safe SQL forms not recognized by the current AST proof, triage the finding and add a minimal sanitized fixture before changing the rule.

## Review before sharing report

```bash
python3 - <<'PY'
import json
p='ecosystem/specs/wrench-db-inspect/pilots/rumble-lm/reports/rumble-lm.release.json'
j=json.load(open(p))
assert j['meta']['redaction']['secrets_or_pii_included'] is False
print(j['data']['status'], j['data']['summary'])
for f in j['data']['findings']:
    print(f['rule_id'], f['severity'], f['subject'])
PY
```

Do not attach reports to CI/Bolt evidence until `open-findings.md` and `false-positive-notes.md` are updated.
