---
description: BMAD v6 Interactive Guidance — inspects active sprint state, branch mode, and recommends next workflows/subagents.
---

# BMAD v6 Interactive Help (`/bmad-help`) 💡

## Purpose
Provides instant, context-aware assistance on your project's active development state, documentation status, and recommended next action without reading bulky documentation.

---

## Steps

### 1. Inspect Project State
1. **Branch Mode Detection**: Check current branch (`git branch --show-current`).
   - `spike/*` → Spike Mode active (Retrofit docs needed before merge)
   - `hotfix/*` / `bugfix/*` → Fastpath Mode active
   - `feature/*` / `main` → Standard BMAD Lifecycle
2. **Sprint & Task Status**: Check if `task.md` exists at the workspace root. Count completed `[x]` vs pending `[ ]` tasks.
3. **Doc Hierarchy Status**:
   - Check `docs/briefs/`, `docs/prd/`, `docs/lld/`, and `docs/features/`.
   - Check if project is aligned (`.agent/rules/project-context.md` present).

### 2. Present State Summary

Display a clean summary table to the user:

```text
╔═════════════════════════════════════════════════════════════════╗
║                   🤖 BMAD v6 Project Status                     ║
╠═════════════════════════════════════════════════════════════════╣
║ Stack:         [e.g., FastAPI + Next.js]                        ║
║ Active Branch: [e.g., feature/auth-v2] (Standard Lifecycle)     ║
║ Sprint Tasks:  [e.g., 3/5 Completed (60%)]                      ║
║ Feature Spec:  [e.g., docs/features/002_auth_spec.md (Approved)] ║
║ Subagent Pool: [bmad-pm, bmad-architect, bmad-dev, bmad-tester] ║
╚═════════════════════════════════════════════════════════════════╝
```

### 3. Recommend Next Workflow / Subagent

Based on the inspection, recommend the precise next command:
- If no spec exists: `👉 Run /0-planning to create the Feature Specification.`
- If spec exists but not debated: `👉 Run /bmad-party for Multi-Agent Deliberation.`
- If spec is ready for code: `👉 Run /2-implement or invoke bmad-dev subagent.`
- If code is written: `👉 Run /4-verify to execute TEA test suites.`
- If tests pass: `👉 Run /5-commit to prepare atomic conventional commits.`
- If minor fix: `👉 Run /bmad-fastpath for 2-step Quick-Spec + Ship flow.`
