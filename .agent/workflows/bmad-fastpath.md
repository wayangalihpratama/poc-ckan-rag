---
description: BMAD v6 Scale-Adaptive Fastpath — 2-step Quick-Spec + Ship flow for small features, bugfixes, and refactors
---

# BMAD v6 Fastpath (Quick-Spec + Ship) ⚡

## Purpose
For minor tickets, bugfixes (`hotfix/*`, `bugfix/*`), or small refactors, bypass the full 9-phase lifecycle. BMAD v6 introduces the **Scale-Adaptive Quick-Spec + Ship** flow.

---

## 2-Step Execution Flow

### Step 1: Quick-Spec (Technical Design & Task Checklist)
- **Agents Involved**: `bmad-architect` (Winston) + `bmad-sm` (Bob) [Model: `flash`]
1. **Analyze Issue**: Identify root cause or requirement.
2. **Determine Footprint**: List exact files to modify and test files to create.
3. **Generate Checklist**: Write a compact, actionable checklist directly into `task.md` with explicit criteria.
- **Gate**: User approves the Quick-Spec.

---

### Step 2: Build, Verify & Ship
- **Agents Involved**: `bmad-dev` (Amelia) + `bmad-tester` (Murat) + `bmad-writer` (Paige)
1. **TDD Implementation**: Spawn `bmad-dev` (Amelia) to implement fix with a failing test first.
2. **Verification (TEA)**: Spawn `bmad-tester` (Murat) to run automated test commands and confirm zero regressions.
3. **Doc Sync & Commit**: Spawn `bmad-writer` (Paige) to update README/docs if needed, followed by user confirmation for `git commit`.
- **Gate**: All automated tests green, user approves commit.
