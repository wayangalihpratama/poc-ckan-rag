---
description: Analyze the codebase/PRD and generate or update the project-level Low-Level Design (LLD) document under `docs/lld/project_lld.md`.
---

# 🏗️ Generate Project-Level LLD

Use this workflow to generate or update the project-level LLD under `docs/lld/project_lld.md` based on the requirements defined in the high-level Project PRD (`docs/prd/project_prd.md`).

## Steps

### 1. Requirements & PRD Context
- Review the high-level Project PRD (`docs/prd/project_prd.md`) or transform an existing System Design Document (SDD) into the PRD format.
- Load the `bmad-architect` skill.
- Perform a **Docs-First** research to identify target architecture patterns for the current stack.
- Check `.agent/rules/` and existing `docs/` for stack-specific rules.

### 2. Analyze Core Components
- Identify main application entry points and service structure.
- Map out the directory structure and module boundaries.
- Extract data schemas (database tables, models, API contracts) to support the PRD goals.

### 3. Draft & Index the LLD
Create or update `docs/lld/project_lld.md` using the template `bmad-team/templates/LLD.md`. The LLD structure covers:
- **System Summary**: High-level technical stack and core modules.
- **Module Decomposition**: Folder structures, packages, and their responsibilities.
- **Data Architecture**: Schema definitions, indexes, relations, and entity relationship diagrams.
- **Integration Points**: Core APIs, third-party services, webhooks, or background queue architecture.
- **Security & Safety**: Authentication, authorization, cryptography, and PII protection rules.
- **Component LLD Indexing**: If component LLDs are split under `docs/lld/components/`, the main `docs/lld/project_lld.md` MUST contain a `# Component Directory` index. The agent automatically synchronizes this index by scanning `docs/lld/components/*.md`, resolving their paths, and parsing their main headings as link titles.

### 4. Review for Safety
- Verify that the LLD contains NO credentials, active tokens, API keys, or PII.
- Follow the `docs-standard.md` no-credentials policy.

### 5. Finalize
- Present the generated LLD to the user for approval. Once approved, you can create detailed `FEATURE_SPEC.md` specs for individual feature implementation.
