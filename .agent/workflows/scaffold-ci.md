---
description: Scaffold production-grade CI/CD pipelines (Semaphore CI & GitHub Actions) compliant with Akvo Developer Guidelines.
---

# Akvo CI/CD Pipeline Scaffolder (`/scaffold-ci`) ⚙️

## Purpose
Automatically generate and install `.semaphore/semaphore.yml` and `.github/workflows/ci.yml` configured with Akvo linting standards (Black 79-char, Prettier) and mandatory **80% minimum test coverage gates**.

---

## Steps

### 1. Scaffold CI Files
Run the copy commands or let the agent install them into the project workspace:

```bash
# 1. Semaphore CI (Default for Akvo Tech Projects)
mkdir -p .semaphore
cp .agent/templates/ci/semaphore.yml .semaphore/semaphore.yml

# 2. GitHub Actions (Simple & Integrated CI)
mkdir -p .github/workflows
cp .agent/templates/ci/github-ci.yml .github/workflows/ci.yml
```

### 2. Verify Local Pipeline Simulation
Run local lint and test commands to ensure the build passes locally before pushing:
```bash
# Python check
flake8 . --max-line-length=79
pytest --cov=. --cov-fail-under=80

# JS/TS check
npx prettier --check "**/*.{ts,js,tsx,jsx,json}"
npm test
```

### 3. Commit CI Configuration
Commit under the conventional format:
```bash
git add .semaphore .github
git commit -m "[#issue_number] chore(ci): scaffold Semaphore CI and GitHub Actions pipelines with 80% coverage gate"
```
