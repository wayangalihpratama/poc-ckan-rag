---
description: Planning & Estimation — creates a Feature Specification with ballpark estimates. Read-only. No file writes.
---

# Phase 0: Planning & Estimation 📋

> [!IMPORTANT]
> **Read-only phase.** No code, no file writes, no migrations. Halt after Feature Spec is produced and approved. Spike Mode bypasses this phase entirely.
>
> **Pre-Flight**: Read `.agent/rules/project-context.md` if it exists (from `/align-stack`) — use its feature doc path, commands, and conventions instead of BMAD defaults.

---

## Steps

### 1. Requirements Discovery — 5W1H

Analyze the user's request with a 5W1H lens:
- **Who**: Primary actors / personas
- **What**: Feature and key functional requirements
- **Where**: System location (frontend paths, backend modules, DB schemas)
- **When**: Trigger condition or delivery timeline
- **Why**: User pain point addressed
- **How**: High-level logic flow

> Research boundary: read-only on interfaces, models, routes, and component boundaries only. No helper logic, no optimization paths.

### 2. Check Upstream Docs (Do NOT Auto-Create)

Read if they exist; skip if they don't — **do not generate**:
- `docs/prd/project_prd.md` — project goals and constraints
- `docs/lld/project_lld.md` — current architecture
- Any alternative doc locations listed in `project-context.md`

Only create/update PRD or LLD if the user **explicitly requests** it.

### 3. Feature Specification

**Path**: Check `project-context.md` for native feature doc location. Default: `docs/features/{NNN}_{feature_name}_spec.md` (auto-increment from highest existing prefix).

**Template**: Use `.agent/templates/FEATURE_SPEC.md` if it exists, otherwise `bmad-team/templates/FEATURE_SPEC.md`.

The spec MUST cover:
- **Overview**: Feature goal and target outcome
- **Architecture Overview**: Logic flow + Mermaid sequence diagram
- **Backend**: DB model changes (fields, constraints, migrations), API payloads/responses
- **Frontend**: State management, UI components, ASCII wireframes if needed
- **Verification**: Automated test commands + manual steps
- **Vibe Coding Estimation**: Task table with 3-part breakdown: **Vibe Coding (Dev)** + **Automated Testing** + **QA & Review** = **Total Est. Time** (atomic tasks ≤4h each)

---

## Completion Criteria

- [ ] 5W1H requirements analyzed
- [ ] PRD/LLD checked (read if present, skipped if not — not created)
- [ ] Feature Specification created at the project-native path
- [ ] All tasks estimated with 3-part Vibe Coding breakdown (Dev + Testing + QA)
- [ ] User reviewed and approved the Feature Specification


## 🛑 HALT

Present the Feature Specification. Do not proceed to implementation.

**Handoff**: User must invoke `/1-research` or `/2-implement`. Fast-track allowed if spec is complete and has no open questions — ask first.
