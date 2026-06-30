# rumble-lm pilot inputs

Place only sanitized, non-secret inputs here when running the product-dependent pilot locally.

Expected files:

- `schema.sql` — sanitized PostgreSQL schema dump, no row data, no comments containing secrets/PII.
- `security-manifest.json` — DB security manifest using `{ data, meta }` and `wrench.db_inspect.manifest.v0.1`.
- optional `migrations/` — sanitized migration SQL excerpts.

Do not commit real DB dumps, DSNs, tokens, row data, prompts, source excerpts, embeddings, or personal data.
