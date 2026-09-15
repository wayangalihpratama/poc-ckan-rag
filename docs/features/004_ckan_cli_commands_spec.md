# Feature Spec 004: CKAN Click CLI Commands

## Overview
Provides administrative CLI commands integrated directly into the CKAN CLI entrypoint (`ckan akvorag ...`) to automate host application registration, check Akvo RAG connection health, and bulk-sync existing PDF files across all datasets.

---

## 1. Technical Deliverables

### 1.1 CLI Module
**File**: `/ckanext/akvorag/cli.py`
- Implements Click command group `akvorag`:
  - `ckan akvorag register --admin-token <TOKEN> [--app-name <NAME>] [--domain <DOMAIN>]`:
    - Calls `AkvoRAGClient.register_app()` using the superuser admin token.
    - Saves the generated `access_token` and `knowledge_base_id` into CKAN configuration or `.env`.
  - `ckan akvorag status`:
    - Validates connectivity to Akvo RAG via `GET /api/v1/apps/me`.
    - Displays app status, tenant ID, and registered Knowledge Bases.
  - `ckan akvorag sync-all [--force]`:
    - Iterates over all datasets in CKAN (`toolkit.get_action('package_list')`).
    - Scans for PDF resources and submits upload jobs for any unsynced documents.
  - `ckan akvorag query "<PROMPT>"`:
    - Interactive CLI query tool to test RAG answers and source citations directly from the terminal.

### 1.2 Setup Entrypoint
**File**: `/setup.py`
```python
entry_points='''
    [ckan.cli]
    akvorag=ckanext.akvorag.cli:akvorag
'''
```

---

## 2. Verification & Testing

### 2.1 Automated Unit Tests
**File**: `/tests/test_cli.py`
- Uses `click.testing.CliRunner`.
- Test cases:
  - `test_cli_register_success()`
  - `test_cli_status_success()`
  - `test_cli_sync_all()`
  - `test_cli_query()`

### 2.2 Test Command
```bash
pytest tests/test_cli.py -v --cov=ckanext.akvorag.cli
```

---

## 3. Vibe Coding Estimation ⏱️

| Subtask | Dev | Testing | QA & Review | Total |
| :--- | :---: | :---: | :---: | :---: |
| Click CLI Commands Implementation (`register`, `status`, `sync-all`, `query`) | 15m | 10m | 5m | **30m** |
| CLI Config Persistence & Output Formatting | 10m | 5m | 5m | **20m** |
| Unit Test Suite (Click CliRunner) | - | 5m | 5m | **10m** |
| **TOTAL** | **25m** | **20m** | **15m** | **60m (1.0h)** |
