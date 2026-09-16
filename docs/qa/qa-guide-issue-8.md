# QA Guide: CKAN Click CLI Commands (Issue #8)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #8** ([`004_ckan_cli_commands_spec.md`](../features/004_ckan_cli_commands_spec.md)), which implements administrative CLI commands integrated directly into the CKAN CLI entrypoint (`ckan akvorag ...`) in `ckanext/akvorag/cli.py` and registered via `IClick`.

---

## 2. Automated Test Execution & Coverage

### Scenario 1: Automated Click CLI Unit Tests
**Objective**: Verify all Click CLI commands (`register`, `status`, `sync-all`, `query`), argument parsing, formatting, and error handling pass with ≥80% test coverage.

1. Execute test suite inside the container:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/test_cli.py -v --cov=ckanext.akvorag.cli --cov-report=term-missing
   ```

2. **Expected Output**:
   - `9 passed in ~0.5s`
   - Test Coverage: **88%** on `cli.py` (exceeds the 80% coverage mandate).

3. Execute full extension test suite:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/ -v --cov=ckanext.akvorag --cov-report=term-missing
   ```
   - `34 passed in ~1.9s`
   - Overall Coverage: **90%**.

---

## 3. Manual Testing Walkthrough (Step-by-Step) 🧪

### Step 1: Verify CLI Command Registration
Run the top-level CKAN CLI help inside the container:
```bash
docker compose exec -it ckan ckan akvorag --help
```
**Expected Output**:
```
Usage: ckan akvorag [OPTIONS] COMMAND [ARGS]...

  Akvo RAG management and synchronization CLI commands.

Options:
  --help  Show this message and exit.

Commands:
  query     Query the Akvo RAG Knowledgebase directly from the CLI.
  register  Register this CKAN instance with Akvo RAG as an authorized...
  status    Check connectivity and credentials with Akvo RAG.
  sync-all  Scan all datasets in CKAN and synchronize PDF files to Akvo RAG.
```

---

### Step 2: Test Host Application Registration (`register`)
```bash
docker compose exec -it ckan ckan akvorag register \
  --admin-token "YOUR_SUPERUSER_ADMIN_TOKEN" \
  --app-name "CKAN Portal" \
  --domain "localhost:5000" \
  --kb-name "Water Knowledgebase"
```
**Expected Output**:
- Displays `[✓] App registered successfully!`
- Displays `App ID`, `App Name`, `Domain`, `Access Token`.
- Creates the initial Knowledge Base and prints the generated `knowledge_base_id`.
- Prints `ckan.ini` configuration instructions.

---

### Step 3: Test Health & Connectivity Status (`status`)
```bash
docker compose exec -it ckan ckan akvorag status
```
**Expected Output**:
```
[*] Checking Akvo RAG status at https://akvo.ngrok.dev...

[✓] Akvo RAG Connection: OK
  App ID:            app_...
  App Name:          CKAN Portal
  Status:            active
  Target KB ID:      101

Accessible Knowledge Bases (1):
  • [101] Water Knowledgebase [ACTIVE TARGET]
```

---

### Step 4: Test Bulk Document Synchronization (`sync-all`)
Ensure you have at least one CKAN dataset with a PDF uploaded (see [`qa-guide-issue-6.md`](qa-guide-issue-6.md)), then execute:
```bash
docker compose exec -it ckan ckan akvorag sync-all
```
**Expected Output**:
```
[*] Starting bulk sync to Akvo RAG Knowledge Base [101]...
  [*] Uploading sanitation_study_2026.pdf (res_123)...

--- Bulk Sync Summary ---
  Datasets Scanned:   1
  Total Resources:    2
  PDFs Identified:    1
  Successfully Synced: 1
  Skipped (Non-PDF):  1
  Errors / Missing:   0
-------------------------
```

---

### Step 5: Test Terminal Conversational Query (`query`)
Query the knowledge base directly from the CLI:
```bash
docker compose exec -it ckan ckan akvorag query "What are the main findings in the sanitation study?"
```
**Expected Output**:
```
[*] Querying Akvo RAG (KB: 101)...
Prompt: What are the main findings in the sanitation study?

--- AI Answer ---
The sanitation study highlights significant improvements in water purification...

--- Sources / Citations ---
  • sanitation_study_2026.pdf (Page 3)
-----------------
```

---

## 4. Edge Cases & Resilience Verification

| Scenario | Command | Expected Result | Verified |
| :--- | :--- | :--- | :---: |
| **Missing Admin Token** | `ckan akvorag register` (no `-t`) | Click displays error `Missing option '--admin-token' / '-t'` and exits with code 2. | [x] |
| **Invalid Token in Status** | `ckan akvorag status` (invalid token) | Outputs `[!] Connection failed: 401 Unauthorized` gracefully with exit code 1. | [x] |
| **Sync with No Token** | `ckan akvorag sync-all` (unauthenticated) | Displays clear error explaining app token is missing and guides to run register. | [x] |
| **Sync Non-PDF Resources** | `ckan akvorag sync-all` | Correctly counts and skips non-PDF files without halting execution. | [x] |
| **Missing Resource Files on Disk** | `ckan akvorag sync-all` | Warns about missing file on disk without crashing the entire batch process. | [x] |

---

## 5. Acceptance Checklist
- [x] Click CLI commands implemented under `akvorag` group (`register`, `status`, `sync-all`, `query`).
- [x] Registered via `ckan.plugins.interfaces.IClick` interface.
- [x] Automated unit test suite achieves **90% overall coverage** (88% on `cli.py`).
- [x] Manual verification steps documented and tested inside container.
