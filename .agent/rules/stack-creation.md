---
trigger: model_decision
description: When creating a new stack directory or adding rules/skills/workflows to an existing stack
---

## Stack Creation Guide

### Adding a New Stack

1. Create a directory with the stack name (kebab-case): `laravel/`, `django-react/`, etc.
2. Create the `.agent/` structure inside:
   ```
   <stack-name>/.agent/
   ├── rules/
   ├── skills/
   └── workflows/
   ```

### Dockerization Strategy

Every stack created from zero MUST adhere to the standard Dockerization strategy:
1. **Docker Wrapper Script (`dc.sh`)**: Every stack must include a `./dc.sh` bash script in its root as a standardized wrapper for `docker compose` commands (e.g., `./dc.sh up -d`, `./dc.sh exec [service] [command]`). All commands referenced in `.agent` workflows and rules must use this wrapper.
2. **Compose Configurations (`compose.yml`)**:
   - The stack must utilize `compose.yml` (the modern standard replacing `docker-compose.yml`) for local development orchestration.
   - Separate configurations or overrides (e.g., `compose.prod.yml` or production-optimized Dockerfiles) should be defined for production parity.

### Required Rules (Minimum)

Every stack MUST include at minimum:

| Rule | Trigger | Purpose |
|------|---------|---------|
| `professional-team-sop.md` | `always_on` | Core TDD/DRY/LLD professional standards |
| `rule-priority.md` | — | Conflict resolution hierarchy |
| `security-mandate.md` | `always_on` | Security principles adapted for the stack |
| `docker-commands.md` | `always_on` | Docker/container execution commands |
| `error-handling.md` | `model_decision` | Error handling patterns for the stack |
| `testing-strategy.md` | `model_decision` | Test pyramid and conventions |
| `git-workflow.md` | `model_decision` | Commit and branch conventions |

### Required Skills (Minimum)

Every stack SHOULD include at minimum:

| Skill | Purpose |
|-------|---------|
| `debugging-protocol` | Structured debugging methodology |
| `guardrails` | Pre-flight and post-implementation checklists |

### Recommended Skills

| Skill | Purpose |
|-------|---------|
| `code-review` | Structured code review with severity tags |
| Stack-specific CRUD skill | Step-by-step resource creation guide |
| Stack-specific patterns skill | Framework best practices and patterns |

### Quality Checklist for New Stacks

- [ ] All SKILL.md files have `name` and `description` frontmatter
- [ ] All rules with triggers use valid `always_on` or `model_decision` values
- [ ] All commands reference the stack's Docker wrapper (not bare commands)
- [ ] Cross-references between rules, skills, and workflows are consistent
- [ ] README section updated in root `README.md`
