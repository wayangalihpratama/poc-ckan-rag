---
description: BMAD v6 Code Review & Security Audit — audits PR diffs, checks security vulnerabilities, and evaluates rule compliance
---

# BMAD v6 Code Review & Security Audit (`/bmad-review`) 🔍

## Purpose
Executes a comprehensive, senior-staff code review and security audit on active feature changes, uncommitted diffs, or open Pull Requests using **Rachel (`bmad-reviewer`)**.

---

## Steps

### 1. Scope & Diff Extraction
1. Inspect the active branch against `main` (or active uncommitted changes):
   ```bash
   git diff origin/main...HEAD
   ```
2. Identify all modified files, routes, schemas, and tests.

### 2. Invoke Code Reviewer Subagent (`bmad-reviewer`)
Spawn or simulate **Rachel (`bmad-reviewer`)** to perform line-by-line inspection across the 7 severity categories:
- **`[SEC]` (Critical)**: Injection flaws, unprotected endpoints, hardcoded credentials.
- **`[DATA]` (Critical)**: Unhandled transactions, data corruption risks, concurrency issues.
- **`[ARCH]` (Major)**: SOLID violations, architecture boundary leaks, circular imports.
- **`[PERF]` (Major)**: N+1 database queries, unindexed queries, blocking I/O on async loops.
- **`[TEST]` (Major)**: Missing test cases for critical paths or untested error handling.
- **`[ERR]` (Major)**: Swallowed exceptions, empty try/except blocks.
- **`[PAT]` (Minor)**: Deviations from project standards or framework anti-patterns.
- **`[NIT]` (Optional)**: Styling, naming, or minor doc suggestions.

### 3. Generate Structured Review Report

```markdown
# 🔍 Code Review Report — {Branch / PR Name}
**Reviewer**: Rachel (Senior Staff Code Reviewer) | **Date**: {YYYY-MM-DD}
**Verdict**: [APPROVE / REQUEST CHANGES / COMMENT]

## 📊 Summary Scorecard
- **Files Audited**: N
- **Critical Issues [SEC/DATA]**: N (Blockers)
- **Major Issues [ARCH/TEST/ERR/PERF]**: N
- **Minor / Nits [PAT/NIT]**: N

## 🚨 Critical & Major Findings
- [ ] **[SEC]** `file.py:L45` — Missing authorization check on admin route.
  - *Fix*: Add `@require_admin` dependency.

## 💡 Suggestions & Nits
- [ ] **[NIT]** `service.py:L89` — Rename `data` to `payload_dto` for clarity.

## 🛡️ Rule Compliance
- Verified against `.agent/rules/` (@security-mandate.md, @coding-standards.md)
```

### 4. Single-Pass Review Resolution & Handoff (Akvo Standard)
- **Atomic Pass Resolution**: **Amelia (`bmad-dev`)** resolves ALL numbered findings in a single comprehensive pass, noting the exact resolution under each checklist item.
- **Iteration Limit**: Feedback loops must be completed within **1 to 3 cycles maximum**.
- **Greenlight**: Once all Critical `[SEC]`/`[DATA]` and Major `[ARCH]`/`[TEST]` findings are checked off and tests pass with ≥80% coverage ➔ Greenlight for PR (`👉 Run /6-pr`).

