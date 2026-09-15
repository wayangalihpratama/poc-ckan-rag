---
description: Zero-Token Living Architecture Map AST Generator — scans code AST to generate or update docs/architecture_map.md with Mermaid diagrams and API catalogs
---

# Generate Architecture Map (`/generate-arch-map`) 🗺️

## Purpose
Runs a deterministic, zero-token AST analysis of your project's models, database schemas, and API routes. Generates or updates `docs/architecture_map.md` with an accurate **Mermaid ER Diagram** and **API Catalog** without consuming LLM tokens.

---

## Steps

### 1. Run AST Generator Script
Execute the zero-token scanner:
```bash
python3 .agent/scripts/generate_architecture_map.py . docs/architecture_map.md
```
*(or `python3 bmad-team/scripts/generate_architecture_map.py . docs/architecture_map.md` depending on workspace path)*

### 2. Verify Output
Inspect `docs/architecture_map.md`:
- Verify all discovered models are rendered in the Mermaid `erDiagram`.
- Verify API routes and HTTP endpoints are listed in the catalog.
- Verify existing manual sections (Granular LLD Registry and Spike Log) are preserved.

### 3. Report Results
Provide a brief summary of discovered models, routes, and components to the user.
