---
trigger: model_decision
description: Documentation standard for docs/ directory, task.md, and spike_notes.md. Load when creating, modifying, reading, or structuring project documentation.
---


## Documentation Standard

Documentation is streamlined to the git-tracked `docs/` directory for shared designs, plus a single local `task.md` for task checklists.

### Local Coordination (Not in Git)
- **`task.md`**: Workspace-root checklist for implementation tracking. Only local execution file needed.
- **`spike_notes.md`** (optional): Root-level gitignored file for Spike Mode logging.

### `docs/` — Shared Project Documentation (IN git)

> [!IMPORTANT]
> **STRICT CONSTRAINTS**:
> 1. **No Untemplated Documents**: Only create files defined by templates in `bmad-team/templates/`.
> 2. **Sequential Sorting**: Files in `docs/briefs/` and `docs/features/` MUST use a 3-digit prefix (`001_`, `002_`).

```
docs/
├── architecture_map.md         # Living global system overview & module registry
├── api_contract.md             # API JSON Contract (if present)
├── briefs/                     # Product Briefs (sequential)
│   └── 001_product_v2_brief.md
├── prd/
│   └── project_prd.md
├── lld/
│   ├── project_lld.md
│   └── components/
│       └── auth_lld.md
└── features/
    ├── 002_billing_spec.md
    └── implemented/
        └── 001_chat_playground_spec.md
```

### System Architecture Map
`docs/architecture_map.md` maps system modules, shared code, DB entities, and API prefixes. Feature LLDs must link to it for shared components to avoid duplicating schemas.

### Doc Hierarchy & Spike Mode
For stage definitions (Brief → PRD → LLD → Feature Spec), Spike Mode rules, and In-Flight Amendment Protocol — see @documentation-hierarchy.md.

### "Dirty LLD" Tagging
Tag dirty LLDs with `<!-- DIRTY_AMENDMENT: [details, approved date] -->` at the top. Tech Writer clears tags at Phase 8. See @documentation-hierarchy.md for full protocol.

### Implementation-Doc Synchronization

> [!IMPORTANT]
> For every completed task, ensure all relevant docs (`docs/lld/`, `docs/prd/`, `docs/architecture_map.md`, `docs/api_contract.md` if present, `README.md`) match the actual implementation.
> 1. **Check**: Look for mismatches in API contracts, data models, or feature behavior.
> 2. **Resolve**: Update docs if impl is correct; fix impl if it deviates from spec.
> 3. **Verify**: Ask the user to confirm alignment before committing.

### No Credentials Policy

> [!CAUTION]
> Files in `docs/` are pushed to the repo. NEVER include API keys, passwords, tokens, credentials, or PII. Use placeholders like `YOUR_API_KEY`.

### Project-Root-Relative Paths Only (#6)

> [!CAUTION]
> NEVER include local machine paths or usernames (e.g. `/Users/username/...`, `C:\Users\username\...`, `/home/username/...`, `/mycomputer/project/...`) in any documentation, link, template, or code comment.
> ALWAYS refer to paths relative to the project workspace root (e.g., `/backend/models/...`, `/app/routers/...`, `docs/lld/project_lld.md`).

