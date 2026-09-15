---
description: Migrate a project from any legacy structure to the current single-tier docs/ model.
---

# 📦 Migrate to Current Documentation Structure

Use this workflow when a project was set up with an **older BMAD approach** (either `agent_docs/`-only, or a `docs/` + `agent_docs/` split) and needs to be migrated to the current **single-tier `docs/` model**.

## Current Target Structure

```
docs/
├── architecture_map.md          # Living global system overview & module registry
├── api_contract.md              # API JSON contract (if present)
├── briefs/
│   └── 001_product_brief.md    # NNN_ prefixed, one per product/release
├── prd/
│   └── project_prd.md          # One per project
├── lld/
│   ├── project_lld.md          # One per project (master)
│   └── components/             # Optional sub-components for large systems
└── features/
    ├── 001_feature_spec.md     # Active specs (NNN_ prefixed)
    └── implemented/            # Archived completed specs
task.md                         # Root-level local execution checklist (gitignored)
spike_notes.md                  # Root-level spike log (gitignored, only in Spike Mode)
```

## Pre-Flight

1. Confirm the project path with the user.
2. Detect the legacy structure type:
   - **Type A** — All artifacts in `agent_docs/` only (oldest pattern)
   - **Type B** — `docs/` + `agent_docs/` split (previous pattern)
   - **Type C** — `docs/` with per-feature LLD files but missing `features/` directory
3. Check if `docs/` already exists — if so, read its current state before any action.

## Steps

### Step 1: Bootstrap `docs/` Sub-directories

Create any missing sub-directories under `docs/`:

```bash
mkdir -p docs/briefs docs/prd docs/lld/components docs/features/implemented
```

### Step 2: Migrate Shared Documents

Scan for legacy artifacts and migrate to the correct location using this mapping:

| Legacy Location | New Location | Action |
|---|---|---|
| `agent_docs/product-brief.md` | `docs/briefs/001_product_brief.md` | Move, rename with `NNN_` prefix. Reformat using `PRODUCT_BRIEF.md` template. |
| `agent_docs/prd.md` or similar | `docs/prd/project_prd.md` | Move and rename. Reformat using `PRD.md` template. |
| `agent_docs/architecture.md` or `docs/LLD.md` | `docs/lld/project_lld.md` | Consolidate into single project LLD using `LLD.md` template. |
| `docs/lld/{feature}_lld.md` (per-feature LLDs) | `docs/features/{NNN}_{feature_name}_spec.md` | Convert to Feature Spec format using `FEATURE_SPEC.md` template. |
| Global schema/ADR indexes | `docs/architecture_map.md` | Bootstrap System Architecture Map with global configs and core ERDs. |

> [!IMPORTANT]
> Feature-specific LLDs from the old pattern must be converted to **Feature Specs** (`FEATURE_SPEC.md` template), not kept as LLDs. Only project-wide architecture belongs in `docs/lld/project_lld.md`.

### Step 3: Handle Local Execution Artifacts

The following legacy artifacts are **discarded or converted** — they do NOT migrate to `docs/`:

| Legacy File | Action |
|---|---|
| `agent_docs/sprint-plan.md` | Convert active tasks to `task.md` entries at workspace root |
| `agent_docs/stories/*.md` | Extract UAC/TAC into `task.md` checklist items |
| `agent_docs/research_logs/` | Discard — research findings belong in the PRD |
| `agent_docs/decisions/` | Fold relevant ADRs inline into `docs/lld/project_lld.md` |
| `agent_docs/ux-design-specification*.md` | Fold UX notes into the relevant Feature Spec |
| `agent_docs/test-strategy.md` | Fold test notes into the relevant Feature Spec |
| `agent_docs/spike_notes.md` | Move to root-level `spike_notes.md` (keep gitignored) |

### Step 4: Apply `NNN_` Numbering Convention

Rename all files in `docs/briefs/` and `docs/features/` to use the three-digit sequential prefix:

```bash
# Example renames
mv docs/briefs/product_brief.md docs/briefs/001_product_brief.md
mv docs/features/auth_spec.md   docs/features/001_auth_spec.md
```

### Step 5: Update `.gitignore`

Ensure these entries are in `.gitignore`:

```
.agent/
task.md
spike_notes.md
```

Remove any `agent_docs/` entry — it's no longer needed.

### Step 6: Clean Up Git Tracking

If `agent_docs/` was previously tracked by git:

```bash
git rm -r --cached agent_docs/
git rm -r --cached .agent/
```

This removes them from git tracking without deleting local files.

### Step 7: Safety Audit

1. Scan all files in `docs/` for credentials, API keys, or PII.
2. Replace any found secrets with placeholders (e.g., `YOUR_API_KEY`).
3. Verify compliance with `@docs-standard.md`.

### Step 8: Present to User

Show the user:
- List of files moved to `docs/`
- List of legacy files discarded or folded
- Any credentials found and sanitized
- Suggested commit message: `chore: migrate to single-tier docs/ structure`

## Completion Criteria

- [ ] `docs/` contains `briefs/`, `prd/`, `lld/`, and `features/` subdirectories
- [ ] All briefs in `docs/briefs/` use `NNN_` prefix
- [ ] All feature specs in `docs/features/` use `NNN_` prefix
- [ ] `task.md` exists at workspace root with active tasks (if any)
- [ ] `.gitignore` includes `task.md` and `spike_notes.md`; `agent_docs/` entry removed
- [ ] No credentials in `docs/`
- [ ] User has reviewed and approved the migration
