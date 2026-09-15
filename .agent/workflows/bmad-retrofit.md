---
description: BMAD v6 Spike-to-Production Retrofit — reverse engineers experimental spike prototypes into enterprise-grade PRDs, LLDs, and test stubs with 0 LLM tokens.
---

# BMAD v6 Spike-to-Production Retrofit (`/bmad-retrofit`) ⚡

## Purpose
Convert rapid experimental prototypes built on `spike/*` branches into structured, production-ready specifications (Product Brief, PRD, LLD, and Test Skeletons) before merging to `main`.

---

## Steps

### 1. Execute Zero-Token AST Retrofit Script
Run the local AST parser script:
```bash
python3 .agent/scripts/retrofit_spike.py .
```

This immediately generates:
1. `docs/briefs/retrofit_spike_brief.md` — Functional summary
2. `docs/prd/retrofit_spike_prd.md` — Formal Functional Requirements (`FR-xxx`)
3. `docs/lld/retrofit_spike_lld.md` — Mermaid class diagrams & API contracts
4. `tests/test_retrofit_spike.py` — Test skeletons for QA

### 2. Rename Spike Branch to Akvo Feature Branch
Convert branch from `spike/<name>` to Akvo-compliant branch name:
```bash
git checkout -b feature/<issue_number>-<feature_description>
```

### 3. QA & Security Verification
1. **Murat (`bmad-tester`)** fills out the test skeletons and executes test verification (enforcing ≥80% coverage).
2. **Rachel (`bmad-reviewer`)** audits the code diff for security and code standards.

### 4. Release Council Sign-off (`/bmad-release`)
Convene the Release Council and ship the PR!
