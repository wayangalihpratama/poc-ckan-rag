---
trigger: always_on
description: Mandatory rules for minimizing token usage during planning, research, implementation, and verification phases.
---

## Token Conservation Rules

All agents under the `bmad-team` or `.agent` folder MUST strictly adhere to these token-minimization protocols to optimize cost, speed, and efficiency:

### 1. Scale-Adaptive Routing (Prefer Fastpath)
- For minor tasks, bugs, or refactors, bypass the full 8-agent orchestrator. Switch immediately to `/bmad-fastpath.md`.
- Do not invoke phases (PM, Analyst, UX) that do not directly contribute to solving a minor ticket.

### 2. Targeted File Reading
- **NEVER** read an entire code or documentation file if you only need a specific portion.
- Always use `grep_search` to locate target areas first.
- When calling `view_file`, specify the `StartLine` and `EndLine` to read only the relevant context window (e.g., 50–100 lines).

### 3. Localized Code Edits
- Do **NOT** rewrite or overwrite entire files to make small changes.
- Always use `replace_file_content` or `multi_replace_file_content` for precise, drop-in replacement chunks.

### 4. Concise Communication & Output
- Eliminate conversational fluff, repetitive greetings, and redundant summaries of work done.
- Do not repeat or re-summarize content that is already written to artifacts (such as plans or feature specs) in the chat response. Keep chat messages to actionable next steps.
- Write compact, structured research logs and notes.

### 5. Efficient Scanning
- Avoid recursive directory listing (`list_dir` or similar) on large project roots.
- Target search queries precisely using specific paths or includes.

### 6. Skill Context Pruning & Filtering
- All projects must configure `.agent/config.yaml` (or `.agents/config.yaml`) with tailored `skills.allowlist` and `skills.blocklist`.
- Block unneeded heavy domain skills (e.g., `*-database`, `flutter-*`, `dart-*`, `gcp-*`, `alphafold-*`) to prevent hundreds of lines of unused tool descriptions from polluting every turn's system prompt context.

### 7. Subagent Handoff Output Budget (Max 15 Lines)
- Subagents returning execution results to the parent orchestrator MUST limit their chat response to a **strict ≤15-line Executive Summary** (Status, Touchpoint Files, Test/Coverage Metrics, Blocking Issues).
- **NEVER** dump full code blocks or entire file contents into the parent chat thread. Provide file paths and allow the parent or user to view targeted line ranges on demand.


