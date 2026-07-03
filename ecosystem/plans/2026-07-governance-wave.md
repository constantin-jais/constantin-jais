# Plan — governance-wave-and-root-hygiene (2026-07 wave)

```yaml
# forge.plan.v0.1 — bolt-handoff-compatible header (maps onto canvas.bolt_handoff.v0.1)
format: forge.plan.v0.1
kind: planning_request
source:
  product: constantin-jais
  plan_id: plan-2026-07-governance-wave-r2
  created_at: "2026-07-03"
  revision: "2 (blocking points corrected; améliorations intégrées)"
execution_policy:
  planning_only: true
  allow_execution: false
  requires_human_approval_for_execution: true
traceability:
  - "target-version 1.0.0 (ADR 0032, ADR 0033, ADR 0028, ADR 0029)"
  - "target-version.md §1: deployment_class is a CI-gated claim in maturity/stack/*.json, not a naming convention"
  - "architecture-alignment-2026-07.md — DA-1..DA-12 arbitration"
  - "DA-6 governance onboarding (branch-policy extension)"
  - "M7 maturity/stack coverage with deployment_class (ADR 0033)"
  - "DA-10 root hygiene (tombstone cleanup + archive)"
depends_on: []
blocks:
  - "per-repo agent sessions executing versioned governance plans (DA-12 wave framing)"
  - "Phase B ratification PR (M5, DA-1/DA-3/DA-11)"
open_questions: []
risks:
  - id: R1
    severity: medium
    description: "Repos I4/I5/I6 (wrench-db-inspect, rumble-crew, rumble-note) are remote standalone repos, not locally checked out; I4/I5/I6 require repo owner execution or gh CLI remote commits"
    mitigation: "I4/I5/I6 are marked as 'repo owner responsibility' with bootstrap instructions; agent executing this plan forks/clones or uses gh CLI for remote edits; unclear ownership defaults to control plane (constantin-jais) owner for review"
  - id: R2
    severity: low
    description: "deployment_class field in stack/*.json must be one of product-linkable | factory-only | build-time (per ADR 0033); existing bolt-cos-matic.json has maturity_mode field instead; migration required"
    mitigation: "I2 includes migration of existing bolt-cos-matic.json to add deployment_class; verify existing maturity_mode field is preserved or replaced per repo's classification"
  - id: R3
    severity: low
    description: "wrench-dioxus-lab rename (GitHub rename dioxus-lab → wrench-dioxus-lab): timing hazard if branch-policy.json updated before GitHub rename completes"
    mitigation: "I1 defers wrench-dioxus-lab key to post-rename; keep dioxus-lab in branch-policy.json until GitHub rename is confirmed by repo owner, then single follow-up commit renames key"
evidence_expectations: "each increment CI-gated: branch-policy.json validates against governance schema; maturity/stack/*.json validate against stack.project_maturity.v0.1 schema; root hygiene commits pass git status check (no orphaned files); wrench-db-inspect and rumble-* repos validate with their own CI gates post-commit"
```

## Context

This governance wave operationalizes three foundational decisions from the architecture alignment (architecture-alignment-2026-07.md):

1. **DA-6: Governance onboarding** — The forge contains ~20 repos across six layers (Rumble, Portal, Bolt, Wrench, Gear, control plane). Currently only 4 are under branch-policy governance (constantin-jais, gear-memory, Rumble-Note, dioxus-lab). No scalable workflow extension mechanism exists; policies are ad-hoc.

2. **M7: Maturity/stack coverage** — ADR 0033 (accepted 2026-07-03) introduces `deployment_class` (product-linkable | factory-only | build-time) as a **CI-gated claim in `ecosystem/maturity/stack/*.json`** (per target-version.md §1). Currently only bolt-cos-matic.json exists in stack/ (with `maturity_mode` field, not `deployment_class`). The remaining ~19 repos lack stack claims, blocking cockpit generation and CI enforcement of the layer model.

3. **DA-10: Root hygiene** — The ~/Documents root contains tombstone directories and files (decided #63, 2026-07-02), merged patches, and items awaiting archival. No anti-duplication gate prevents reintroduction. Cleanup is a prerequisite for crisp governance tooling onboarding.

**Evidence:**
- target-version.md §1: "deployment class is a CI-gated claim in maturity/stack/*.json, never a naming convention"; layer model defined with permitted deployment_classes per layer.
- architecture-alignment-2026-07.md §3.2: root hygiene table; §6 open decisions DA-6/DA-10; addendum arbitration (DA-6 ratified, DA-10 ratified as proposed).
- branch-policy.json: currently 4 repos (constantin-jais/constantin-jais, gear-memory, Rumble-Note, dioxus-lab).
- ecosystem/maturity/stack/: only bolt-cos-matic.json present (has `maturity_mode`, not `deployment_class`).
- ~/Documents: dioxus-template/, specs/, overview.md, .patch, Codex/, github-date-normalization/ present.

## Target state

1. **Governance onboarded:** All ~20 repos listed in ecosystem/governance/branch-policy.json with CI-checkable required_checks reflecting each repo's stack layer. Case corrections applied (Rumble-Note GitHub name verified and matched in branch-policy.json). wrench-dioxus-lab rename (GitHub step executed by repo owner) followed by branch-policy.json key update in single commit.

2. **Maturity/stack complete:** ecosystem/maturity/stack/*.json exists for all ~20 repos with `deployment_class` field conforming to ADR 0033 (product-linkable | factory-only | build-time). Schema stack.project_maturity.v0.1.schema.json created (new; captures repo-level deployment_class claim, distinct from layer model's permitted classes). Existing bolt-cos-matic.json migrated to include deployment_class. Cockpit generation unblocked.

3. **Root clean:** Tombstone directories/files deleted. Patches deleted. Items archived. Anti-duplication guard in place (CI check or pre-push hook). References to ~/Documents directories in scattered places cleaned up.

4. **Micro-fixes merged:** wrench-db-inspect stack maturity claim added (or README refreshed if repo-owner-driven); rumble-crew CONTRIBUTING path corrected or documented; rumble-note hygiene verified.

## Repos and inventory

**Local control plane (in-repo, can execute immediately):**
- `constantin-jais/constantin-jais` (root)

**Factory/Wrench (in-repo or prototype):**
- `ecosystem/prototypes/wrench-db-inspect` (local; deprecated; actual repo is remote)
- `wrench-inspect` (remote)
- `wrench-dioxus-lab` (remote; currently named dioxus-lab; awaiting GitHub rename DA-5)

**Rumble (~11 repos, remote):**
- `rumble-ai-practices`, `rumble-canvas`, `rumble-cos`, `rumble-crew`, `rumble-feed-mind`, `rumble-lm`, `rumble-note`

**Portal (~5 repos, remote):**
- `portal-android`, `portal-apple`, `portal-core`, `portal-forge`

**Bolt (~2 repos, remote):**
- `bolt-cos-matic`, `bolt-harness`

**Gear (~4 repos, remote):**
- `gear-cable`, `gear-depot`, `gear-loader`, `gear-memory`

**Note:** This list is derived from target-version.md layer definitions and ecosystem/specs references. For a complete and up-to-date repo enumeration, consult the GitHub org `constantin-jais` and cross-reference with the Forge Compass (when available).

---

## Increments

### I1 — DA-6 branch-policy.json governance extension (PR independent, control-plane-only)

**Prerequisites:**
- gh CLI authenticated with fine-grained PAT (Administration: read/write on target repos in org)
- Access to ecosystem/governance/branch-policy.json

**Files:**
- `ecosystem/governance/branch-policy.json` (modified, extended)
- Reference: `ecosystem/governance/forge_policy.py` (consulted, not modified)

**Work:**

1. **Verify repo names and casing against GitHub org:**
   - Manually spot-check 3–5 repos via `gh repo list constantin-jais --limit 25` to confirm exact GitHub casing.
   - Verify "Rumble-Note": check if GitHub URL is `github.com/constantin-jais/rumble-note` or `github.com/constantin-jais/Rumble-Note`. Use exact match in branch-policy.json.
   - Verify "dioxus-lab" is current; DA-5 rename to "wrench-dioxus-lab" pending (do not add wrench-dioxus-lab key yet; see mitigation R3).

2. **Add missing repos to branch-policy.json:**
   - Extend `repos` object with all ~20 repos (or ~19 if wrench-dioxus-lab rename is pending).
   - Do NOT attempt to pull live GitHub ruleset config with `forge_policy.py dump`; instead, populate required_checks based on repo's layer and ADR 0033 classification:
     - **Rumble** (rumble-*): `["Rust quality gates", "e2e tests", "Dioxus patterns", "wrench-db-inspect gate"]` (if Postgres-backed).
     - **Portal** (portal-*): `["Rust quality gates", "UniFFI bindings CI", "token gates"]` (if applicable).
     - **Bolt** (bolt-*): `["Rust quality gates", "planning-only enforcement"]`.
     - **Wrench** (wrench-*): `["Rust quality gates", "supply-chain gates", "shared fixture validation"]`.
     - **Gear** (gear-*): `["Rust quality gates", "contract tests", "provenance gates"]`.
   - Each entry: `"required_checks": [...], "strict_up_to_date": true`.
   - Preserve existing 4 repos (no overwrite; review casing for "Rumble-Note").

3. **Defer DA-5 wrench-dioxus-lab rename:**
   - Add a comment in branch-policy.json:
     ```json
     "dioxus-lab": {
       "__comment__": "DA-5 rename to wrench-dioxus-lab pending GitHub rename by repo owner; single follow-up commit will rename key post-completion",
       "required_checks": [...],
       "strict_up_to_date": true
     }
     ```
   - OR defer adding the comment and keep dioxus-lab key; plan a small I1b PR post-rename.

4. **Ratify with control plane conventions:**
   - Ensure no machine-local paths (e.g., ~/Documents) leak into branch-policy.json.
   - JSON format valid; no trailing commas.

**Exit gates:**
```bash
# JSON valid
python3 -c "import json; json.load(open('ecosystem/governance/branch-policy.json')); print('✓ JSON valid')"

# All expected repos present (verify count and key format)
EXPECTED_REPOS='constantin-jais|gear-memory|rumble-|portal-|bolt-|wrench-|Rumble-Note|dioxus-lab'
grep -oE '"constantin-jais/[^"]*"' ecosystem/governance/branch-policy.json | wc -l | awk '{print ($1 >= 19 ? "✓ " $1 " repos >= 19" : "⚠ " $1 " < 19")}'

# No machine-local paths
! grep -qE 'Documents|home|/tmp|/var' ecosystem/governance/branch-policy.json && echo "✓ No local paths"

# Rumble-Note casing checked against GitHub (manual verification, not automated)
echo "⚠ Verify Rumble-Note casing manually via: gh repo view constantin-jais/rumble-note (or Rumble-Note)"
```

---

### I2 — M7 maturity/stack/*.json generation with deployment_class (PR independent, control-plane-only)

**Prerequisites:**
- target-version.v1.json ratified (2026-07-03, present in repo)
- ADR 0033 accepted (deployment_class nomenclature defined; target-version.md confirms location in maturity/stack/*.json)
- Schema stack.project_maturity.v0.1.schema.json will be created as part of this increment

**Files:**
- `ecosystem/maturity/stack/*.json` — extend existing (bolt-cos-matic.json) and create for remaining ~19 repos
- `ecosystem/specs/harness/stack-project-maturity.v0.1.schema.json` — create (NEW)

**Work:**

1. **Create schema stack-project-maturity.v0.1.schema.json:**
   - New file in `ecosystem/specs/harness/`.
   - JSON Schema draft-2020-12.
   - Required properties:
     - `format`: const "stack.project_maturity.v0.1"
     - `project.name`: string (repo name)
     - `project.layer`: enum ["rumble", "portal", "bolt", "wrench", "gear"]
     - `project.role`: string (one-line role from README or ADR)
     - `project.deployment_class`: enum ["product-linkable", "factory-only", "build-time"]
     - `claimed_at`: ISO 8601 timestamp
     - `current_increment`: string (P0, P1, etc. or descriptive state)
     - `scale_ready`: boolean or string ("no", "yes", "conditional")
     - `status_summary`: string
     - `next_quality_step`: string (optional)
     - `boundaries`, `evidence[]`, `verification_commands[]`: reference or consistent with bolt-cos-matic.json structure
     - `open_questions[]`: array of strings (optional)
     - `risk_notes[]`: array of strings (optional)
   - Example fixture (copy + adapt from bolt-cos-matic.json):
     ```json
     {
       "format": "stack.project_maturity.v0.1",
       "project": {
         "name": "rumble-lm",
         "layer": "rumble",
         "role": "LM-backed product workflows, session orchestration, cost optimization.",
         "deployment_class": "product-linkable"
       },
       "claimed_at": "2026-07-03T00:00:00Z",
       "current_increment": "P1 production ready (session ownership per ADR 0029)",
       "scale_ready": "yes",
       "status_summary": "...",
       "boundaries": { ... },
       "evidence": [ ... ],
       "verification_commands": [ ... ]
     }
     ```

2. **Migrate existing bolt-cos-matic.json:**
   - Read current bolt-cos-matic.json (has `maturity_mode: "usable"`).
   - Add `project.deployment_class: "factory-only"` (Bolt layer allows only factory-only per target-version.v1.json).
   - Keep all other fields intact.
   - Verify against new schema.

3. **Generate stack maturity for remaining ~19 repos:**
   - For each repo not yet in ecosystem/maturity/stack/:
     - Determine layer (prefix match rumble-*, portal-*, etc.).
     - Infer or read deployment_class from layer model (target-version.v1.json):
       - Rumble: product-linkable (always, per layer definition).
       - Portal: product-linkable or build-time (depends on repo; e.g., portal-core is factory, portal-apple/android are product-linkable).
       - Bolt: factory-only (always).
       - Wrench: factory-only or build-time (depends; db-inspect is factory-only).
       - Gear: product-linkable, factory-only, or build-time (depends on service).
     - Use role from target-version.md layer table or repo README.
     - Create JSON with current status from existing ecosystem/maturity/REPO.json (if present) or leave as "under assessment".
     - Set `claimed_at` to 2026-07-03 for all new claims.

4. **Validate all stack/*.json files:**
   - Run schema validation: `python3 -c "import json, jsonschema; schema = json.load(open('ecosystem/specs/harness/stack-project-maturity.v0.1.schema.json')); [jsonschema.validate(json.load(open(f)), schema) for f in glob.glob('ecosystem/maturity/stack/*.json')]"`.
   - Ensure no schema violations.

5. **Coordinate with spec-contracts CI:**
   - After merge, spec-contracts CI (`ecosystem/specs/validate_spec_schemas.py`) will validate stack/*.json against stack-project-maturity.v0.1.schema.json automatically.

**Exit gates:**
```bash
# Schema file exists and is valid JSON
python3 -c "import json; json.load(open('ecosystem/specs/harness/stack-project-maturity.v0.1.schema.json')); print('✓ Schema valid')"

# All ~20 repos have stack claims
EXPECTED=20
ACTUAL=$(find ecosystem/maturity/stack -name "*.json" -type f | wc -l)
[ "$ACTUAL" -ge "$EXPECTED" ] && echo "✓ $ACTUAL repos have stack claims (expected ≥$EXPECTED)"

# deployment_class field present in all stack/*.json
COUNT=$(grep -l '"deployment_class"' ecosystem/maturity/stack/*.json | wc -l)
[ "$COUNT" -ge "$EXPECTED" ] && echo "✓ All $COUNT repos have deployment_class"

# Validate all stack/*.json against schema (requires Python + jsonschema)
python3 << 'EOF'
import json, glob, sys
try:
    schema = json.load(open('ecosystem/specs/harness/stack-project-maturity.v0.1.schema.json'))
    errors = []
    for f in glob.glob('ecosystem/maturity/stack/*.json'):
        try:
            import jsonschema
            jsonschema.validate(json.load(open(f)), schema)
        except Exception as e:
            errors.append(f"{f}: {e}")
    if errors:
        print("✗ Schema validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"✓ All stack/*.json valid against schema")
except Exception as e:
    print(f"✗ Schema validation setup failed: {e}")
    sys.exit(1)
EOF

# Spec-contracts gate can now consume maturity/stack/ (post-merge CI will validate)
echo "✓ Spec-contracts CI will validate on next push"
```

---

### I3 — DA-10 root hygiene cleanup (PR independent, control-plane-only)

**Prerequisites:**
- Full backup of ~/Documents exists (backups/ directory contains snapshot)
- No in-flight work depends on the files to be deleted/archived
- Review of decision #63 (tombstone list confirmed)

**Files:**
- Deletions at ~/Documents root level (outside repo, via shell commands)
- Archive operations (move to ecosystem/archived/ or mark in-repo reference)

**Work:**

1. **Delete tombstones (decision #63, verified):**
   ```bash
   # Verify before deletion (dry run)
   [ -d ~/Documents/dioxus-template ] && echo "Will delete: ~/Documents/dioxus-template"
   [ -d ~/Documents/specs ] && echo "Will delete: ~/Documents/specs"
   [ -f ~/Documents/overview.md ] && echo "Will delete: ~/Documents/overview.md"
   [ -d ~/Documents/Codex ] && echo "Will delete: ~/Documents/Codex"
   
   # Execute deletion (only after confirmation)
   rm -rf ~/Documents/dioxus-template
   rm -rf ~/Documents/specs
   rm -f ~/Documents/overview.md
   rm -rf ~/Documents/Codex
   ```
   Evidence: decision #63 lists these as tombstones; `ecosystem/specs/` and `ecosystem/overview.md` are the canonical in-repo versions.

2. **Delete merged patch:**
   ```bash
   rm -f ~/Documents/bolt-cos-matic-wip-*.patch
   ```
   Evidence: Content merged as commit 4d6f496; patch file is now superfluous.

3. **Archive github-date-normalization/ (ad-hoc utility, no load-bearing use):**
   ```bash
   mkdir -p ecosystem/archived
   mv ~/Documents/github-date-normalization ecosystem/archived/
   
   # Create a reference note in-repo
   cat > ecosystem/archived/github-date-normalization.reference.md <<'EOF'
   # Archived: github-date-normalization
   
   **Archive date:** 2026-07-03 (DA-10 wave)
   **Reason:** Ad-hoc utility, no load-bearing integration into forge workflows
   **Original location:** ~/Documents/github-date-normalization/ (pre-archive)
   
   If revived, restore from git history or ~/backups/ snapshot.
   EOF
   ```

4. **Create anti-duplication guard (in-repo documentation + optional CI hook):**
   - Create `ecosystem/root-disposition.md`:
     ```markdown
     # Root-level Directory Disposition (DA-10 wave, 2026-07-03)
     
     ## Deleted (Tombstones, decision #63)
     - `dioxus-template/` — superseded by dioxus-app-template; canonical in ecosystem/
     - `specs/` — tombstone; canonical versions in ecosystem/specs/
     - `overview.md` — retired; canonical: ecosystem/overview.md
     - `bolt-cos-matic-wip-*.patch` — merged as commit 4d6f496
     - `Codex/` — empty, no load-bearing purpose
     
     ## Archived (ecosystem/archived/)
     - `github-date-normalization/` — ad-hoc utility (2026-07-03)
     
     ## Retained with Notes
     - `dioxus/` — active fork; upstream for PRs #5662/#5663; reference for wrench-dioxus-lab evidence
     - `dioxus-v0.7.9/` — pinned GO baseline (wrench-dioxus-lab ADR 0001 evidence); tied to web-shell specification
     - `dioxus-app-template/` — canonical template; synced from wrench-dioxus-lab via M12 protocol (future)
     - `backups/` — automated snapshots (M11 weekly, future)
     
     **Anti-duplication rule:** Do not re-introduce dioxus-template/, specs/, overview.md, or patch files to ~/Documents without explicit decision review. See decision #63.
     ```
   - Optional: Add a `.github/workflows/anti-duplication-check.yml` or pre-push hook:
     ```bash
     # .git/hooks/pre-push (example; requires manual installation)
     if git diff origin/main..HEAD --name-only | grep -qE '(dioxus-template|^specs|overview.md|\.patch$)'; then
       echo "⚠ ERROR: Detected attempt to re-introduce tombstone files (decision #63)."
       echo "See ecosystem/root-disposition.md for details."
       exit 1
     fi
     ```

5. **Update CONTRIBUTING.md (if present):**
   - Reference the root disposition document:
     ```markdown
     ## Root-level file organization
     
     Several root-level directories have been retired or archived as part of the 2026-07 governance wave (DA-10). Refer to [`ecosystem/root-disposition.md`](ecosystem/root-disposition.md) for context and anti-duplication rules before adding files to ~/Documents.
     ```

**Exit gates:**
```bash
# All tombstones deleted
[ ! -d ~/Documents/dioxus-template ] && \
[ ! -d ~/Documents/specs ] && \
[ ! -f ~/Documents/overview.md ] && \
[ ! -d ~/Documents/Codex ] && \
echo "✓ All tombstones deleted" || echo "✗ Some tombstones still present"

# Archive directory exists in-repo
[ -d ecosystem/archived ] && echo "✓ Archive directory present" || echo "✗ Archive directory missing"

# Reference files committed
[ -f ecosystem/root-disposition.md ] && echo "✓ Disposition reference present" || echo "✗ Disposition reference missing"

# No tombstone files in current git status (verification post-commit)
git status --short | grep -qE '(dioxus-template|specs|overview.md|Codex)' && \
  echo "✗ Tombstone files detected in git status" || \
  echo "✓ No tombstone files in git status"
```

---

### I4 — wrench-db-inspect maturity stack claim (repo owner or agent-executed PR, wrench-db-inspect repo)

**Prerequisites:**
- wrench-db-inspect repository accessible (remote; requires clone or gh CLI remote edit)
- Verify: repository exists and matches `constantin-jais/wrench-db-inspect` on GitHub
- Optional: Cargo + clippy available if running local verify; otherwise defer to repo owner CI

**Files:**
- `ecosystem/maturity/stack/wrench-db-inspect.json` — create (in remote repo or control plane)
- `wrench-db-inspect/README.md` — optional refresh (if repo owner executes)

**Work:**

**Option A (repo owner executes):**
- Repo owner clones wrench-db-inspect locally.
- Verifies clippy debt resolved: `cd wrench-db-inspect && cargo clippy --all-targets -- -D warnings`.
- Creates `ecosystem/maturity/stack/wrench-db-inspect.json` (or ecosystem/maturity/wrench-db-inspect.json if no stack subdir):
  ```json
  {
    "format": "stack.project_maturity.v0.1",
    "project": {
      "name": "wrench-db-inspect",
      "layer": "wrench",
      "role": "PostgreSQL/database security inspector: RLS, grants, migrations, pgvector, tenant isolation.",
      "deployment_class": "factory-only"
    },
    "claimed_at": "2026-07-03T00:00:00Z",
    "current_increment": "P1 CLI proof with 20+ fixtures; prototype proven",
    "scale_ready": "no",
    "status_summary": "Fixtures, RLS/grants/migration/pgvector inspection proven; clippy debt resolved 2026-07; ready for cos-matic CI gate integration.",
    "next_quality_step": "Integrate as cos-matic CI gate; publish example inspection reports.",
    "boundaries": {
      "owns": ["PostgreSQL DDL/DCL fact extraction", "tenant isolation validation", "RLS/grant inspection"],
      "does_not_own": ["live DB mutation", "application authorization", "row-level data", "credentials/PII"]
    },
    "evidence": [
      { "kind": "doc", "ref": "wrench-db-inspect/README.md", "status": "present" },
      { "kind": "fixture", "ref": "wrench-db-inspect/fixtures/", "status": "20+ fixtures passing" },
      { "kind": "command", "ref": "cd wrench-db-inspect && cargo clippy --all-targets -- -D warnings", "status": "passing 2026-07-03" }
    ],
    "verification_commands": [
      "cd wrench-db-inspect && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test --all-targets"
    ]
  }
  ```
- Repo owner commits and pushes to wrench-db-inspect main branch.

**Option B (control plane agent executes remotely):**
- Agent uses `gh CLI` to create a PR in wrench-db-inspect repo:
  ```bash
  cd /tmp
  gh repo clone constantin-jais/wrench-db-inspect
  cd wrench-db-inspect
  mkdir -p ecosystem/maturity/stack
  # Create wrench-db-inspect.json (JSON as above)
  git add ecosystem/maturity/stack/wrench-db-inspect.json
  git commit -m "M7: Add stack maturity claim (deployment_class: factory-only)"
  git push origin feature/m7-maturity-claim
  gh pr create --title "M7: Stack maturity claim" --body "..."
  ```
- Or: Use gh CLI to create the file remotely without clone:
  ```bash
  gh api repos/constantin-jais/wrench-db-inspect/contents/ecosystem/maturity/stack/wrench-db-inspect.json \
    --input=wrench-db-inspect.json
  ```

**Exit gates (repo owner or control plane CI to verify):**
```bash
# File exists
[ -f ecosystem/maturity/stack/wrench-db-inspect.json ] && echo "✓ Stack claim exists"

# Validates against schema (if available in wrench-db-inspect repo; else, control plane CI validates on import)
python3 -c "import json; json.load(open('ecosystem/maturity/stack/wrench-db-inspect.json'))"

# Optional: Clippy passes (repo owner's CI)
# cd wrench-db-inspect && cargo clippy --all-targets -- -D warnings
```

**Note on responsibility:** I4 is marked "repo owner responsibility" because wrench-db-inspect is a remote repository. Control plane agent can assist with PR creation via gh CLI, but code ownership and CI validation remain with the repo owner. If timing is blocked, defer I4 to a follow-up wave and mark as "pending repo owner execution."

---

### I5 — rumble-crew CONTRIBUTING path correction (repo owner or agent-executed PR, rumble-crew repo)

**Prerequisites:**
- rumble-crew repository accessible (remote; requires clone or gh CLI remote edit)
- Verify: CONTRIBUTING.md line 58–64 references stale ecosystem path

**Files:**
- `rumble-crew/CONTRIBUTING.md` — update lines 58–64

**Work:**

1. **Identify the issue:**
   - Current CONTRIBUTING.md may reference: `sh ecosystem/specs/ci-validate-contracts.sh` or similar.
   - This path does NOT exist in rumble-crew repo; it exists only in control plane (constantin-jais/ecosystem/).
   - Rumble-crew is a standalone repo; spec-contracts validation is centralized.

2. **Correct CONTRIBUTING.md:**
   - Replace stale path with reference to control plane (if rumble-crew integrates with control plane specs).
   - Example correction (replace lines 58–64 in CONTRIBUTING.md):
     ```markdown
     ## Specification and contract validation
     
     Rumble-crew is part of the Constantin-Jais ecosystem. Its specification contracts are validated centrally in the control plane.
     
     For local development, refer to:
     - **Control plane repo:** https://github.com/constantin-jais/constantin-jais
     - **Spec validation:** `cd ecosystem && python3 specs/validate_spec_schemas.py`
     - **Contracts:** `ecosystem/specs/` (schema definitions and fixtures)
     
     Before pushing to rumble-crew, ensure:
     - Rust quality gates pass: `cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test`
     - Any database-backed features validate against wrench-db-inspect spec
     - Any UI patterns conform to portal design system
     ```

3. **Verify no other broken paths:**
   - Grep CONTRIBUTING.md for `ecosystem/`, `~/`, or machine-local paths.
   - Remove or correct any stale references.

**Exit gates:**
```bash
# Stale path removed
! grep -q "sh ecosystem/specs/ci-validate-contracts.sh" rumble-crew/CONTRIBUTING.md && echo "✓ Stale path removed"

# Control plane reference present (or documentation updated)
grep -q "constantin-jais/constantin-jais\|ecosystem/specs/validate_spec_schemas.py\|control plane" rumble-crew/CONTRIBUTING.md && \
  echo "✓ Control plane reference present"

# No other machine-local paths leak
! grep -qE 'home|Documents|/tmp|/var' rumble-crew/CONTRIBUTING.md && echo "✓ No local paths"
```

**Repo owner responsibility:** As I4, this is marked for repo owner execution. Control plane can assist via PR template or gh CLI.

---

### I6 — rumble-note hygiene verification (repo owner or control plane, rumble-note repo)

**Prerequisites:**
- rumble-note repository accessible (remote)
- architecture-alignment-2026-07.md confirms no blocking issues beyond case mismatch (already addressed in I1 branch-policy.json)

**Files:**
- `rumble-note/CONTRIBUTING.md` — if correction needed (same as I5)
- Reference: Hygiene notes in control plane `ecosystem/hygiene-notes.md` — update or create

**Work:**

1. **Verify no blocking issues in rumble-note:**
   - Check CONTRIBUTING.md for stale ecosystem paths (same pattern as rumble-crew).
   - Check README.md for stale claims.
   - Check .github/CODEOWNERS for valid file references.
   - Based on architecture-alignment B8, rumble-note has case mismatch (addressed in I1); no other blocking issues expected.

2. **Apply I5 fix if needed:**
   - If CONTRIBUTING.md has stale ecosystem path, apply same correction as I5.

3. **Document resolution:**
   - Create/update `ecosystem/hygiene-notes.md`:
     ```markdown
     # Hygiene Resolution — DA-10 Wave (2026-07-03)
     
     ## rumble-note
     - **Case mismatch:** GitHub repo name verified and matched in branch-policy.json (I1).
     - **CONTRIBUTING.md paths:** Corrected to reference control plane (if present; same as rumble-crew I5).
     - **Status:** No blocking issues observed.
     
     ## rumble-crew
     - **CONTRIBUTING.md paths:** Corrected in I5.
     
     ## wrench-db-inspect
     - **Stack maturity claim:** Added in I4.
     ```

**Exit gates:**
```bash
# No blocking issues remain
echo "✓ rumble-note verified (case mismatch handled in I1, paths corrected if present)"

# Hygiene notes updated
[ -f ecosystem/hygiene-notes.md ] && echo "✓ Hygiene notes present" || echo "⚠ Create hygiene-notes.md"
```

**Repo owner responsibility:** Verification and PR creation; control plane can assist.

---

## Out of scope

1. **D10 (dedicated governance repo extraction):** Deferred as a cold operation, not part of this wave. The current control plane (constantin-jais/ecosystem) will hold governance until D10 is executed in a future wave.

2. **wrench-dioxus-lab GitHub rename (DA-5):** Execution deferred to repo owner. Control plane will update branch-policy.json key in follow-up commit post-rename. See R3 mitigation in I1.

3. **Template sync protocol (M12):** Documented separately; not part of this governance wave. I1/I2 enable governance; M12 is a process/tooling increment.

4. **Backup automation (M11):** Separate operational increment; out of scope here.

5. **Dioxus/upstream PR governance:** dioxus/ fork and dioxus-v0.7.9/ remain reference artifacts. Root disposition documented in I3; no policy changes.

6. **Portal-core cargo-deny gate (DA-9):** Separate security increment; noted in target-version.md but execution outside this wave.

7. **ADR renumbering (DA-3):** Covered by M5 ratification vehicle; not a governance operation.

## Verification

**End-to-end governance wave validation (post-merge):**

1. **Governance applied (I1):**
   ```bash
   # All ~20 repos in branch-policy.json
   grep -oE '"constantin-jais/[^"]*"' ecosystem/governance/branch-policy.json | wc -l
   # Expected: ≥ 19 (or ≥ 20 if wrench-dioxus-lab already renamed)
   ```

2. **Maturity/stack complete (I2):**
   ```bash
   # Schema exists and is valid
   python3 -c "import json; json.load(open('ecosystem/specs/harness/stack-project-maturity.v0.1.schema.json'))"
   
   # All ~20 repos have stack claims
   find ecosystem/maturity/stack -name "*.json" | wc -l
   # Expected: ≥ 20
   
   # All have deployment_class
   grep -h "deployment_class" ecosystem/maturity/stack/*.json | wc -l
   # Expected: ≥ 20
   ```

3. **Root clean (I3):**
   ```bash
   # Tombstones deleted
   [ ! -d ~/Documents/dioxus-template ] && \
   [ ! -d ~/Documents/specs ] && \
   [ ! -f ~/Documents/overview.md ] && \
   [ ! -d ~/Documents/Codex ] && \
   echo "✓ Tombstones cleaned"
   
   # Archive present
   [ -d ecosystem/archived ] && echo "✓ Archive exists"
   ```

4. **Micro-fixes integrated (I4, I5, I6):**
   ```bash
   # wrench-db-inspect stack claim (check control plane or remote)
   [ -f ecosystem/maturity/stack/wrench-db-inspect.json ] && echo "✓ I4 claim exists"
   
   # rumble-crew/rumble-note CONTRIBUTING corrected (check remote, or documented as pending)
   echo "⚠ Verify rumble-crew and rumble-note CONTRIBUTING via gh CLI or repo owner PR"
   ```

5. **Full CI gate (post-merge):**
   ```bash
   # Spec-contracts validation passes
   cd ecosystem && python3 specs/validate_spec_schemas.py 2>&1 | tail -10
   # Expected: all stack.project_maturity.v0.1, stack.target_version.v0.1 fixtures validate
   
   # Branch-policy schema validates
   python3 -c "import json; json.load(open('ecosystem/governance/branch-policy.json'))"
   ```

---

**Ratification anchor:** target-version 1.0.0 (2026-07-03), with flagship slice rumble-lm proving the patterns. This governance wave unblocks per-repo agent plans (DA-12, C4) and operationalizes ADR 0033 (deployment_class CI-gated claims).

---

SendUserFile
