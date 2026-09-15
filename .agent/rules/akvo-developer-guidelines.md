---
trigger: model_decision
description: Official Akvo Developer Guidelines & Tech Team Operations standard. Mandatory for all BMAD personas, code formatting, git branch naming, test coverage, and PR reviews.
---

# Akvo Developer Guidelines 📘

> **Reference**: [Akvo Wiki — Tech Team Operations: Developer Guidelines](https://wiki.cloud.akvo.org/books/tech-team-operations/page/developer-guidelines)

---

## 1. Version Control & Git Workflow

### Branch Naming Convention
Every feature branch MUST be linked to an issue number:
- **Format**: `feature/<issue_number>-<issue_description>`
- **Example**: `feature/13-backend-test-setup`, `feature/363-precommit-config`
- **Rule**: Never create feature branches without an issue number.

### Git Sync Mandate (`git pull --rebase`)
- **Always** use `git pull --rebase` instead of `git merge` or merge commits to keep the git history clean, linear, and readable.
- Never use raw merge commits when updating your local branch with `origin/main`.

### Pre-Commit Hooks
- Use local pre-commit checks (Flake8, Black, Prettier, linters) to catch syntax errors, typing issues, and formatting before pushing.

---

## 2. Pull Request (PR) & Code Review Protocol

### As a Requester (Author)
1. **Link to Sprint Task**: Link GitHub PR to the sprint board task (e.g. Asana/GitHub Project).
2. **Assign Reviewers**: Assign the project Lead Developer or designated peer reviewer.
3. **CI Status**: Ensure 100% passing status on CI (Semaphore CI / GitHub Actions) before marking Ready for Review.
4. **Mandatory Tests**: Every PR must include unit tests or API integration tests.
5. **Follow-Up**: If unreviewed after 2 days, follow up in project Slack channels (`#team-tech-general` or `#proj-<name>-tech`).

### As a Reviewer
1. **Verify CI Status First**: If CI is red/failing, reject immediately and move the task back to *In Progress*.
2. **Review Context**: Inspect the Technical Acceptance Criteria (Tech AC) and Low-Level Design (LLD).
3. **Consolidated Numbered Findings**: Output all findings in a single numbered checklist (`[SEC]`, `[DATA]`, `[ARCH]`, `[PERF]`, `[TEST]`, `[PAT]`, `[NIT]`) so the author can resolve everything in one atomic pass.
4. **Run Code Locally**: For complex or architectural changes, run and verify the code locally.
5. **Time-box**: Keep PR reviews focused (target ≤ 1 hour).
6. **Target Branch**: Verify PR is targeting `main`.
7. **Limit Iteration Cycles**: Keep review iterations between **1 and 3 cycles** maximum (enforce single-pass fix batches).


---

## 3. Code Quality & Core Engineering Principles

All code must strictly adhere to:
1. **SOLID Principles**:
   - **S**: Single Responsibility Principle (one class/function, one reason to change).
   - **O**: Open-Closed Principle (open for extension, closed for modification).
   - **L**: Liskov Substitution Principle (subtypes must be substitutable for base types).
   - **I**: Interface Segregation Principle (clients should not depend on unused interfaces).
   - **D**: Dependency Inversion Principle (depend on abstractions, not concretions).
2. **DRY (Don't Repeat Yourself)**: Modularize and reuse logic.
3. **KISS (Keep It Simple, Stupid)**: Favor simple, readable solutions over convoluted code.
4. **YAGNI (You Aren't Gonna Need It)**: Do not add speculative features or unused abstractions.
5. **Clean Code**: Descriptive naming, explicit exception raising (never return error strings or swallow exceptions), and avoid shadowing built-ins.

---

## 4. Code Formatting Standards

### JavaScript & TypeScript (Prettier)
- `tabWidth`: 2 spaces (no tabs)
- `semi`: true (always terminate statements with semicolons)
- `singleQuote`: true
- `printWidth`: 80
- `trailingComma`: "es5"
- `singleAttributePerLine`: true
- `camelCase` for variables and functions, `===` / `!==` for strict equality.

### Python (Black & Flake8)
- `line-length`: 79 characters (or Black standard)
- Indentation: 4 spaces (no tabs)
- Naming: `lowercase_with_underscores` for variables/functions, `Capitalized` for classes.
- Imports: One module per line, grouped (standard, third-party, local), relative imports for intra-package.
- Blank Lines: 2 blank lines between top-level classes/functions; 1 blank line between methods.

---

## 5. Testing & Code Coverage Gate

### Test-Driven Development (TDD)
- Write a failing test first, write minimal code to make it pass, then refactor.
- Tests act as living documentation and a safety net against regressions.

### Test Pyramid
- **Unit Tests**: Test smallest isolated functions.
- **Integration Tests**: Verify API endpoints, database interactions, and service layers.
- **Functional & Security Tests**: Verify authentication, authorization, and error boundaries.

### Minimum Code Coverage Gate (80%)
- **Mandatory 80% Minimum Coverage**: In accordance with Akvo Tech KPI, all repositories must maintain **at least 80% test coverage** (tracked via Coveralls / pytest-cov / c8).

---

## 6. Living Documentation

1. **API Documentation**: Document inputs, outputs, error payloads, and status codes.
2. **Keep it Up to Date**: Update documentation alongside code; zero documentation drift.
3. **Root-Relative Paths**: Always use project-root-relative links (`/backend/...`).
