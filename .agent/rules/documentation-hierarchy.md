---
trigger: model_decision
description: BMAD Documentation Hierarchy (Brief -> PRD -> LLD -> Feature Spec). Load when initiating new initiatives, planning features, or structuring product specs.
---


## Documentation Hierarchy: Brief → PRD → LLD → Feature Spec

Advisory for BMAD-owned projects. **If the project has its own doc structure (e.g., Claude-initiated), respect that instead.** See `.agent/rules/project-context.md` for project-native paths.

> [!IMPORTANT]
> **Feature Spec is the only mandatory gate before implementation.** PRD and LLD are optional upstream context — read them if they exist, do NOT auto-create them.

---

### Stage 1: Product Brief
**Template**: `bmad-team/templates/PRODUCT_BRIEF.md` | **Location**: `docs/briefs/{NNN}_{product}_brief.md`
One brief per product or major release cycle. Executive-facing north star. **Per-feature briefs are forbidden.**
Required content: Problem Statement, Target Audience, Strategic Alignment, Success KPIs, Assumptions.

> If `docs/product_brief.md` exists directly under `docs/`, treat it as the primary brief.

---

### Stage 2: Project PRD
**Template**: `bmad-team/templates/PRD.md` | **Location**: `docs/prd/project_prd.md`
One per project or major initiative. Contains: Goals & Metrics, Scope (Must/Nice/Out), Assumptions.

---

### Stage 3: Project LLD
**Template**: `bmad-team/templates/LLD.md` | **Location**: `docs/lld/project_lld.md` (components under `docs/lld/components/`)
One project-wide system design. Contains: Core Architecture & Data Flow, Modular Layout.

---

### Stage 4: Feature Specification *(Mandatory gate)*
**Template**: `bmad-team/templates/FEATURE_SPEC.md` | **Location**: `docs/features/{NNN}_{feature_name}_spec.md`
Created per feature branch. Moved to `docs/features/implemented/` or marked `[STATUS: IMPLEMENTED]` after completion.
Contains: Architecture + Mermaid diagram, DB schema & migrations, API payloads, Frontend & UI wireframes, Test commands, Task estimates (≤16h each).

> **PRD/LLD vs Feature Spec**: High-level constraints and global layouts → PRD/LLD. Specific implementation steps, routes, schema files, UI components → Feature Spec. No per-feature PRD or LLD files.

---

### Deterministic Branch Routing
- `spike/*` or `experiment/*` → **Spike Mode** (bypass Stages 1–3)
- `hotfix/*` or `bugfix/*` → **Fastpath** (`/bmad-fastpath`)
- All other branches → **Standard Lifecycle**

---

### Spike Mode
- Bypass Stages 1–3 for velocity. Maintain a `spike_notes.md` (gitignored) with a `## Micro-Retrofit Log` — log structural/schema/API changes incrementally after each subtask.
- **Hard Gate**: Never merge spike branches to `main` without a retrospective doc cycle (retrofit Brief, PRD, LLD from the log before opening a PR).

---

### In-Flight Design Amendment Protocol
If a blocker requires a design change mid-sprint:
1. Draft the amendment in chat → get approval from Architect/PM → proceed immediately.
2. Tag the relevant LLD: `<!-- DIRTY_AMENDMENT: [details, approved date] -->` at the top.
3. Tech Writer (Phase 8) harvests tags, updates PRD/LLD/System Map, clears tags, and runs `git diff origin/main --name-only` as a safety net for untagged changes.

---

### Enforcement
- Detect mode at Pre-Flight via git branch check.
- **Feature Spec mandatory**: Missing spec → run `/0-planning` before any code.
- **PRD/LLD optional**: If they exist, read and respect them. If missing, continue without — do NOT block or auto-generate.
- If project uses a different doc system (from `/align-stack`), follow that instead.
