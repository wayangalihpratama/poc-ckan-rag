---
description: Align the copied .agent config to the destination project's real stack, conventions, and feature doc standard.
---

# Align Project Stack

> **Context**: Run from within the **destination project directory** (where BMAD assets were copied via `setup.sh`), NOT from `my-antigravity-pilot`.

## Purpose

After `setup.sh` copies BMAD assets into a project, the `.agent/` config may not match the project's real setup — especially when initiated by another toolchain (Claude, Cursor, Windsurf). This workflow makes BMAD respect what the existing team already decided.

---

## Steps

### 1. Scan for External AI Convention Files (Highest Priority)

Check for existing convention files from other AI toolchains — these **win over BMAD defaults**:

| File | Toolchain |
|------|-----------|
| `CLAUDE.md`, `CLAUDE.local.md` | Claude (Anthropic) |
| `AGENTS.md` | Generic multi-agent |
| `.cursorrules` | Cursor AI |
| `WINDSURF.md` | Windsurf |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.aider.conf.yml` | Aider |

For each file found, extract: tech stack, coding conventions, architecture decisions, run/test/lint commands, and any "do not do X" rules.

**Report** all files found and their key rules. If none found: "No external AI convention files found — BMAD defaults are authoritative."

### 2. Scan Project Structure

Read to identify the real stack:
- **Dependency manifests**: `package.json`, `composer.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `Cargo.toml`, `go.mod`
- **Runners**: `Makefile`, `docker-compose.yml`, `dc.sh`, `justfile`, `.env.example`
- **README**: `README.md` or `README.rst`
- **Existing agent config**: `.agent/rules/`, `.agent/workflows/`

Extract: language/framework, test runner, package manager, how the app runs, env vars, linter/formatter.

### 3. Identify Conflicts and Gaps

Compare Steps 1–2 findings against `.agent/` files. Flag:
- **Conflicts**: external convention says X but BMAD config says Y
- **Gaps**: project reality not mentioned in `.agent/` at all

### 4. Ask for Clarification (If Needed)

For direct conflicts, present them and ask. **Default rule**: external convention files win. Only ask when the conflict is genuinely ambiguous.

### 5. Create / Update `project-context.md`

Create or update `.agent/rules/project-context.md` using the template at `bmad-team/templates/PROJECT_CONTEXT.md`.

> **Re-run Safety**: If the file already exists, **merge** new findings into it — do not overwrite. Append `<!-- last-aligned: YYYY-MM-DD -->`.

### 6. Adopt Target Project's Plan Doc Template & Folder Structure

When running `/align-stack` in a target project, our plan document template MUST respect and adopt the target project's existing plan documentation format and directory location:

1. **Scan for Target Project Plan / Spec Documentation**:
   - Inspect the target project for existing planning documents, implementation plans, RFCs, design docs, or feature specifications (e.g., in `docs/`, `docs/plans/`, `docs/features/`, `docs/specs/`, `plans/`, `.github/`, `wiki/`, `.docs/`).
   - Check if the target project already has an established plan doc template (e.g., `docs/templates/plan.md`, `docs/specs/template.md`, `.github/PULL_REQUEST_TEMPLATE/`, or representative existing plan files).

2. **Adopt the Target Project's Plan Template into `.agent/templates/FEATURE_SPEC.md`**:
   - **If the target project HAS existing plan documentation / templates**:
     - Update `.agent/templates/FEATURE_SPEC.md` to replicate the target project's exact plan doc template and structure.
     - **Add Missing Parts**: Add sections that the target project expects and uses (e.g., Acceptance Criteria, Security/Privacy Review, Rollout/Rollback Plan, User Stories, Impact Analysis, Custom Checklist).
     - **Remove Unused Parts**: Strip out default BMAD sections that the target project does NOT use (e.g., remove the ballpark hourly estimation table if the team does not estimate in hours, remove LLD cross-links if they don't use LLDs, remove UI wireframes if it's an API-only service).
   - **If the target project does NOT have existing plan documentation**:
     - Keep the default BMAD template in `.agent/templates/FEATURE_SPEC.md`, but adjust paths and components to match the target project's directories (e.g. `/app/...` vs `/backend/...`).

3. **Respect the Target Project's Plan Folder Location**:
   - Detect the exact folder where the target project stores plan docs (e.g., `docs/plans/`, `docs/specs/`, `docs/features/`, or custom path).
   - Record this location in `.agent/rules/project-context.md` and `.agent/rules/documentation-hierarchy.md` so that all subsequent planning workflows (e.g. `/0-planning`) save new plan documents directly to the target project's native folder.

4. **Strict Project-Root-Relative Paths Only (#6)**:
   - **MANDATORY**: NEVER include local machine paths or usernames (e.g. `/Users/username/...`, `C:\Users\username\...`, `/home/username/...`, `/mycomputer/project/...`).
   - ALWAYS use **project-root-relative paths** (e.g., `/backend/models/...`, `/app/routers/...`, `docs/plans/...`).
   - Ensure all links in docs use workspace-relative anchors or paths.

5. **Report to User**:
   - Summarize the discovered plan template, sections added/removed, and the configured target plan folder.

### 7. Update `.agent/` Configs for Conflicts Only

Update only files that conflict with project standards:
- `4-verify.md` — actual test/lint commands
- `2-implement.md` — correct directory paths
- `5-commit.md` — commit conventions
- `coding-standards.md` — project addendums (do not replace BMAD defaults)
- `bmad-dev/SKILL.md` — real stack and commands

> Only modify files that *conflict*. Leave BMAD defaults that aren't contradicted.

### 8. Configure & Filter Unneeded Agent Skills (Token Optimization)

Strip out unnecessary domain skills (science/medical DBs, mobile frameworks, heavy cloud/BigQuery pipelines) to minimize token consumption per turn:

1. **Check / Create `.agent/config.yaml` (or `.agents/config.yaml`)** from `bmad-team/templates/CONFIG.yaml`.
2. **Align `skills.allowlist`** to match what the detected stack actually needs:
   - Web/Fullstack/Python: `modern-web-guidance`, `managing-python-dependencies`, `uv`, `debugging-protocol`, `add-stack`, `troubleshooting`, `debug-optimize-lcp`, `chrome-devtools`, `a11y-debugging`, `memory-leak-debugging`
   - Mobile: `flutter-*`, `dart-*`, `xcode-*`, `android-*` (only if mobile project)
   - Data Engineering: `gcp-*`, `bigquery-*`, `dataform-*`, `dbt-*` (only if dedicated data pipeline)
3. **Set `skills.blocklist`** to filter out domain categories irrelevant to the stack:
   ```yaml
   skills:
     allowlist:
       - modern-web-guidance
       - managing-python-dependencies
       - uv
       - debugging-protocol
       - add-stack
       - troubleshooting
       - debug-optimize-lcp
       - chrome-devtools
       - a11y-debugging
       - memory-leak-debugging
     blocklist:
       - "flutter-*"
       - "dart-*"
       - "xcode-*"
       - "android-*"
       - "*-database"
       - "alphafold-*"
       - "alphagenome-*"
       - "protein-*"
       - "literature-search-*"
       - "science-skills-*"
       - "scienceskillscommon"
       - "pymol"
       - "gcp-*"
       - "bigquery-*"
       - "dataform-*"
       - "dbt-*"
       - "firebase-*"
   ```
4. **Automatically Reload Cache & Verify**:
   - The agent executing `/align-stack` **MUST automatically run**:
     ```bash
     antigravity reload --clear-cache
     ```
     *(or `agy reload --clear-cache` depending on CLI alias)* to apply the pruned skill set immediately.
   - Run `antigravity status --skills` to verify that blocked skills are eliminated from active context.

### 9. Validate & Report

Sanity check: confirm runtime accessible, test discovery works, dir layout matches `.agent/rules/`, and skills configuration is trimmed and reloaded.

**Summarize**: convention files found, plan doc template adopted from target project (with added/removed sections and target folder location configured), `project-context.md` updated, `.agent/config.yaml` skill filters configured, cache cleared/reloaded, workflows aligned, any open decisions for the user.

---

## Completion Criteria

- [ ] External AI convention files scanned; key rules extracted
- [ ] `project-context.md` created/updated in `.agent/rules/`
- [ ] Target project scanned for existing plan docs/templates; `.agent/templates/FEATURE_SPEC.md` updated to adopt the project's exact plan doc template (added missing parts, removed unused parts)
- [ ] Target project's plan doc folder location respected and recorded in `project-context.md` and `documentation-hierarchy.md`
- [ ] All document links and file paths verified to be strictly project-root-relative with no local computer or user references (#6)
- [ ] `.agent/config.yaml` created/updated with optimized `skills.allowlist` and `skills.blocklist`
- [ ] `antigravity reload --clear-cache` executed to apply skill filtering immediately
- [ ] `.agent/workflows/` updated to project's actual commands
- [ ] No BMAD rule silently overrides project's external conventions
- [ ] Alignment confirmed with the user




