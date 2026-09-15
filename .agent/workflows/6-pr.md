---
description: Create a high-quality Pull Request following Akvo Developer Guidelines & HackerOne best practices
---

# Phase 6: Pull Request (Akvo Standard) 🚀

## Purpose
Create a clear, informative, and professional Pull Request (PR) description following **Akvo Developer Guidelines** (`@akvo-developer-guidelines.md`).

## Prerequisites
- **Phase 5 (Commit)** completed and branch pushed using Akvo branch naming: `feature/<issue_number>-<issue_description>`.
- Code formatted with Akvo standards (Prettier for JS/TS, Black/Flake8 for Python).
- **All CI tests passing with minimum 80% code coverage**.

---

## Steps

### 1. Gather Context & Verification
Collect the following information:
- **What**: Functional changes (brief summary).
- **Why**: Motivation and issue/task links (`[#issue_number]`).
- **How**: Implementation strategy (architecture, patterns, libraries).
- **Testing**: Test results summary, minimum 80% test coverage verification.
- **Screenshots**: Visual evidence (if UI changes).

### 2. Generate PR Description
Draft the description using the `bmad-team/templates/PULL_REQUEST.md` template.

#### Akvo Requester Checklist:
- [ ] Linked GitHub issue in PR title (`[#issue] <type>(<scope>): <description>`).
- [ ] Task linked in sprint board (Asana / GitHub Projects).
- [ ] Minimum 80% test coverage verified (Coveralls / test report).
- [ ] Assigned reviewer (Lead Developer / peer).
- [ ] Target branch verified to be `main`.
- [ ] Limited feedback iterations planned (target 1–3 review cycles).

### 3. Create PR
Execute the git command or provide the content for the PR.

```bash
# Example using GH CLI
gh pr create --base main --title "[#issue_number] <type>(<scope>): <description>" --body-file docs/PULL_REQUEST.md
```

## Completion Criteria
- [ ] PR description follows What/Why/How/Testing structure.
- [ ] Issue and task links included.
- [ ] 80% test coverage gate confirmed.
- [ ] PR created or ready for review.

