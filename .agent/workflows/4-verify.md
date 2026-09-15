---
description: Verify phase - run full validation suite
---

# Phase 4: Verify (Generic)

## Purpose
Run all linters, type checkers, and test suites to ensure the implementation meets the technical and quality standards.

## Prerequisites
- **Phase 3 (Integrate)** completed with all integration tests passing.
- All unit tests passing.

## If This Phase Fails
1. **Do not proceed** to Phase 5 (Ship).
2. Address the failure in the relevant component.
3. Re-run the full verification suite until 100% success is achieved.

## Steps

**Set Mode:** Use `task_boundary` to set mode to **VERIFICATION**.

### 1. Code Quality Validation
Run the project's quality suite:
- **Linting**: Check for style violations.
- **Formatting**: Ensure consistent code style.
- **Type Checking**: Verify type safety.

### 2. Full Test Suite
Run the complete test suite (Unit + Integration + E2E).

### 3. Build Check
Ensure the code can be built for production without errors.

### 4. Coverage Audit
Verify that domain logic meets the project's coverage mandates (default target: >85%).

## Development Commands

> [!NOTE]
> These are placeholder commands. Run `/align-stack` to update them for your project.

```bash
# Linting
./dc.sh exec backend flake8
./dc.sh exec frontend npm run lint

# Build
./dc.sh exec frontend npm run build
```

## Completion Criteria
- [ ] All linting and formatting checks pass.
- [ ] Production build succeeds.
- [ ] Overall coverage meets the project target.
- [ ] Accessibility (WCAG) and Performance targets verified.

## Next Phase
Proceed to **Phase 5: Ship** (`/5-commit`)
