---
description: Gather project requirements or transform an existing System Design Document (SDD) to generate a high-level Project PRD under `docs/prd/project_prd.md`.
---

# 📋 Generate Project-Level PRD

Use this workflow to establish the high-level goals, requirements, success metrics, and scope boundaries for a project under `docs/prd/project_prd.md` using the template `bmad-team/templates/PRD.md`.

## Steps

### 1. Information Gathering
- **Discovery**: Analyze the user's brief, user requests, or existing System Design Document (SDD).
- **5W1H Analysis**: Gather details on **Who** (actors/personas), **What** (features/capabilities), **Where** (frontend/backend integration), **When** (triggers/timeline), **Why** (business value/pain points), and **How** (high-level system interaction).

### 2. Connect Goals to Metrics
- Define concrete success metrics rather than just listing features.
- Identify baseline metrics (where we are today) and target metrics (where we want to be).
- Define anti-goals (explicitly what we will NOT build or optimize for).

### 3. Requirements Outline
- Group requirements into prioritized lists (Must-Have, Nice-to-Have, Out of Scope).
- Formulate high-level Functional Requirements (FRs) and Non-Functional Requirements (Performance, Security, WCAG Accessibility).

### 4. Create the PRD Document
Draft `docs/prd/project_prd.md` using the template `bmad-team/templates/PRD.md`:
- Include Overview, Job-to-be-Done for Personas, User Stories, and a Happy Path flow diagram (using Mermaid).
- If bootstrapping from an existing SDD, ensure all system components map cleanly to the PRD requirements.

### 5. Finalize
- Present the generated PRD to the user for lead sign-off.
- Once signed off, proceed to generating the project-level LLD using the `generate-lld` workflow.
