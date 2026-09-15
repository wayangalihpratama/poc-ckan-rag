---
description: TDD implementation workflow
---

# Phase 2: Implement (Generic)

Write production code following strict **TDD** principles and project-specific design patterns.

## Prerequisites
- **Phase 1 (Research)** completed with a confirmed Specification.
- **Feature Spec** (path per @documentation-hierarchy.md or `project-context.md`) approved and available — sole implementation source.
- **Collaboration**: Invoke **Amelia (Developer)** for core logic, **Sally (UX)** for frontend styling.

## Steps

**Set Mode:** Use `task_boundary` to set mode to **EXECUTION**.

### 1. Workspace Setup
Before coding, ensure the environment is ready:
- Review the requirements for responsive design or backend constraints.
- Identify the correct test runner and command wrapper (e.g., `./dc.sh`, `npm`, `pytest`).

### 2. TDD Cycle: RED (Failing Test)
Create the test files first:
- Locate the project's test directory (e.g., `tests/`, `backend/tests/`, `src/__tests__`).
- Write a test that fails because the feature does not exist yet.

### 3. TDD Cycle: GREEN (Minimal Code)
Write **only** the code necessary to make the tests pass:
- Follow the project's coding standards (e.g., Pydantic v2, React 19, Laravel Eloquent).
- Verify that the tests now pass.

### 4. TDD Cycle: REFACTOR (Blue)
Improve the code while keeping the tests green:
- **Quality**: Ensure type hinting, logging, and proper documentation.
- **Story Alignment**: Verify work against the specific Acceptance Criteria (UAC/TAC).

### 5. Repeat
Continue the Red-Green-Refactor cycle for each story requirement until the task is complete.

## Development Commands

> [!NOTE]
> These are placeholder commands. Run `/align-stack` to update them for your project.

```bash
# Backend Tests
./dc.sh exec backend pytest

# Frontend Tests
./dc.sh exec frontend npm test
```

## Completion Criteria
- [ ] Unit tests passing (TDD cycle strictly followed)
- [ ] **Standards**: DRY, KISS, YAGNI, SOC, SOLID, Security — see @coding-standards.md
- [ ] **Security**: User inputs sanitized and validated
- [ ] Implementation aligns with UAC/TAC in the Feature Spec (`docs/features/{NNN}_{feature_name}_spec.md`)
- [ ] Document Sync: Update `task.md` (mark tasks `[x]`, note actual time)

## Next Phase
Ready for integration? Use the `/3-integrate` workflow or invoke **Amelia (Developer)** and **Murat (Tester)**.
