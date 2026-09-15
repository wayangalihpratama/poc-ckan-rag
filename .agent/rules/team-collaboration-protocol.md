---
trigger: always_on
description: Operational Collaboration Protocol for BMAD Team — governs contract handoffs (Briefing Packets), shift-left QA, single-pass review resolutions, and 3-tier autonomy levels.
---

# BMAD Team Operational Collaboration Protocol 🤝

## Purpose
This protocol standardizes **the way agents work and collaborate** across the lifecycle to eliminate ambiguity, avoid token waste, reduce review iterations, and establish clear human-in-the-loop boundaries.

---

## 1. Contract-Driven Handoffs (The "Briefing Packet")

Whenever an agent hands off a task to another persona (e.g. Architect ➔ Dev, SM ➔ Dev, Dev ➔ QA), they MUST provide a standardized **5-Point Briefing Packet** instead of expecting the receiver to re-read multiple documents:

```markdown
### 📦 Handoff Briefing Packet
1. **Target Goal**: [Exact feature, user story, or bugfix scope]
2. **Touchpoint Files**:
   - `[CREATE]` `backend/app/routers/v1/auth.py`
   - `[MODIFY]` `backend/app/models/user.py`
   - `[TEST]` `backend/tests/test_auth.py`
3. **Interface Signatures**:
   - `POST /api/v1/auth/login` ➔ Input: `LoginRequestDTO` | Output: `TokenResponseDTO` (200 OK, 401 Unauthorized)
4. **Boundary Constraints & Security**:
   - Enforce rate limiting, password hashing (Argon2/Bcrypt), zero plaintext logging.
5. **Deterministic Verification Command**:
   - `pytest backend/tests/test_auth.py -v` (Must achieve ≥80% coverage)
```

---

## 2. Shift-Left QA Pairing (In-Sprint TDD Synchronization)

To prevent late-stage testing bottlenecks in Phase 7:
1. **Upfront Test Criteria**: When Bob (Scrum Master) defines user stories, **Murat (`bmad-tester`)** outlines the exact test cases, edge cases, and failure scenarios *before* coding begins.
2. **Story-by-Story Verification**: **Amelia (`bmad-dev`)** implements against Murat’s test checklist, executing the TDD cycle (Red ➔ Green ➔ Refactor) per story.
3. **Final Gate**: Phase 7 becomes a fast automated regression verification rather than an exploratory discovery phase.

---

## 3. Single-Pass Review Resolution (Akvo 1-Cycle Protocol)

To adhere strictly to Akvo's **1–3 review iteration limit**:
1. **Consolidated Numbered Checklist**: When **Rachel (`bmad-reviewer`)** audits code diffs, she outputs a single comprehensive numbered checklist of findings categorized by severity (`[SEC]`, `[DATA]`, `[ARCH]`, `[PERF]`, `[TEST]`, `[PAT]`, `[NIT]`).
2. **Atomic 1-Pass Resolution**: **Amelia (`bmad-dev`)** addresses ALL findings in a single, comprehensive pass.
3. **Audit Verification**: Amelia notes the exact resolution and file line under each checkbox item and presents the diff back to Rachel for final sign-off.

---

## 4. Deterministic 3-Tier Autonomy Framework

To eliminate unnecessary conversational interruptions while preserving strict user authority over critical decisions:

### 🟢 Tier 1: Fully Autonomous (No User Pause Required)
- Generating internal boilerplate and schema classes.
- Running test suites, linters, and formatters (`pytest`, `npm test`, `black`, `prettier`).
- Writing unit test mocks and fixtures.
- Updating local `task.md` checklist items.
- Running zero-token AST scripts (`generate_architecture_map.py`).

### 🟡 Tier 2: Checkpoint Summaries (Inform User & Proceed)
- Completing a lifecycle phase (e.g. Phase 2 Analyze completed, moving to Phase 3 Architect).
- Presenting Party Mode synthesis notes.
- Reporting test execution & 80% coverage gate status.

### 🔴 Tier 3: Hard Stop (Mandatory Explicit User Approval)
- Signing off on initial **Product Brief** or **Project PRD**.
- Approving breaking API changes or database migration schema changes.
- Final commit split plan and executing `git commit` / `git push` (per `@git-workflow.md`).
- Overriding an existing external convention file (`CLAUDE.md`, `.cursorrules`).

---

## 5. Vibe Coding Estimation Standard ⏱️

In modern AI-assisted engineering ("vibe coding"), implementation speed is accelerated, while testing and verification become the primary quality safeguards. All task breakdowns and sprint checklists (`task.md`) MUST explicitly separate effort into three distinct phases:

```markdown
| Task ID | Story / Task Description | Vibe Coding (Dev) | Automated Testing | QA & Review | Total Est. | Actual Time |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **TASK-01** | User Auth Endpoint (`POST /api/v1/login`) | 25m | 20m | 15m | **60m (1.0h)** | - |
| **TASK-02** | JWT Token Validation & Middleware | 20m | 15m | 10m | **45m (0.75h)**| - |
```

### Allocation Guidelines:
1. **💻 Vibe Coding (Implementation)**: Core logic, models, controllers, and UI built with AI assistance.
2. **🧪 Automated Testing (TEA)**: Unit tests, mock fixtures, edge cases, and achieving the ≥80% coverage gate.
3. **🔍 QA & Review**: Security audit, manual smoke tests, PR review resolution, and sign-off.
4. **⏱️ Total Time**: The true end-to-end velocity metric for planning and tracking.

---

## 6. Automated Parallel Subagent Execution Protocol ⚡

Antigravity automatically supports launching multiple subagents concurrently in a single `invoke_subagent` tool call:

```json
{
  "Subagents": [
    { "TypeName": "bmad-analyst", "Role": "Mary (Analyst)", "Prompt": "..." },
    { "TypeName": "bmad-ux", "Role": "Sally (UX)", "Prompt": "..." }
  ]
}
```

### Automation Rules:
1. **Phase 2 & 4 (Analyze + UX)**: Always execute `bmad-analyst` and `bmad-ux` concurrently in a single tool call.
2. **Phase 6 (Multi-Dev Slicing)**: Execute `/bmad-parallel-dev` to launch 2+ `bmad-dev` (Amelia) instances on isolated workspace branches (`Workspace: branch`) whenever independent stories exist in `task.md`.
3. **Phase 7 & 8 (Verify + Docs)**: Always execute `bmad-tester` (80% coverage runner) and `bmad-writer` (AST Architecture Map generator) concurrently in a single tool call.
4. **Reactive Wakeup**: Parent orchestrator halts tool calls while background subagents run. Antigravity automatically notifies the parent when subagents report back.


