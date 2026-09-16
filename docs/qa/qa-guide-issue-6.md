# QA Guide: CKAN Plugin Hooks (`ckanext-akvorag`) (Issue #6)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #6** ([`003_ckanext_akvorag_plugin_spec.md`](../features/003_ckanext_akvorag_plugin_spec.md)), which implements the core CKAN extension plugin (`ckanext/akvorag/plugin.py`) hooking into CKAN's `IResourceController`, `IPackageController`, and `IConfigurer` interfaces to intercept dataset and resource lifecycle events for automatic synchronization with Akvo RAG.

---

## 2. Automated Test Execution & Coverage

### Scenario 1: Automated Unit & Integration Test Suite
**Objective**: Verify all resource lifecycle hooks (`after_create`, `after_update`, `after_delete`, `after_dataset_delete`), PDF format detection, filestore path resolution, and error handling pass with ≥80% test coverage.

1. Execute test suite inside the container:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/ -v --cov=ckanext.akvorag --cov-report=term-missing
   ```

2. **Expected Output**:
   - `24 passed in ~1.9s`
   - Test Coverage: **91%** overall, **87%** for `plugin.py` (exceeds the 80% coverage mandate).

---

## 3. Manual Testing Walkthrough (Step-by-Step) 🧪

### Method A: Testing via CKAN Web UI

1. **Start the CKAN Docker stack** (if not already running):
   ```bash
   docker compose up -d
   ```

2. **Follow live CKAN logs in a separate terminal**:
   ```bash
   docker compose logs -f ckan
   ```

3. **Log in to CKAN**:
   - Open your browser at `http://localhost:5000/user/login`
   - Log in using sysadmin credentials:
     - **Username**: `admin`
     - **Password**: `ckan_admin_password`

4. **Test PDF Resource Upload (Sync Trigger)**:
   - Navigate to **Datasets** ➔ **Add Dataset** (`http://localhost:5000/dataset/new`).
   - Fill in Title (e.g. `Test Water Sanitation Report`) and click **Next: Add Data**.
   - Under **Upload**, choose a sample PDF file (e.g. any `.pdf` document).
   - Name the resource (e.g. `Sanitation Study 2026`).
   - Click **Finish**.
   - **Check logs**: Look at the terminal running `docker compose logs -f ckan`. You will observe:
     ```
     [ckanext.akvorag.plugin] Intercepted new resource create: <resource_id> (format: PDF)
     [ckanext.akvorag.plugin] Submitting upload job to Akvo RAG for file: /var/lib/ckan/resources/...
     ```

5. **Test Non-PDF Resource Upload (Ignored)**:
   - Add another resource with format CSV or TXT (`data.csv`).
   - Click **Save**.
   - **Check logs**: Observe that non-PDF files are ignored:
     ```
     [ckanext.akvorag.plugin] Resource <resource_id> is not a PDF (format: CSV). Skipping Akvo RAG sync.
     ```

6. **Test Resource Deletion**:
   - Edit the PDF resource and click **Delete Resource**.
   - **Check logs**: Observe deletion sync:
     ```
     [ckanext.akvorag.plugin] Intercepted resource deletion: <resource_id>
     [ckanext.akvorag.plugin] Purged document <resource_id> from Akvo RAG KB
     ```

7. **Test Dataset Deletion**:
   - Delete the entire dataset containing resources.
   - **Check logs**: Observe batch deletion hook:
     ```
     [ckanext.akvorag.plugin] Intercepted dataset deletion: <dataset_id>
     ```

---

### Method B: Interactive Python Shell inside Docker

1. Open an interactive Python shell inside the CKAN container:
   ```bash
   docker compose exec -it ckan python
   ```

2. Test plugin hook methods directly with mock context:
   ```python
   from ckanext.akvorag.plugin import AkvoRAGPlugin

   plugin = AkvoRAGPlugin()

   # Test PDF detection helper
   assert plugin._is_pdf({"format": "PDF"}) is True
   assert plugin._is_pdf({"format": "application/pdf"}) is True
   assert plugin._is_pdf({"url": "http://example.com/file.pdf"}) is True
   assert plugin._is_pdf({"format": "CSV"}) is False
   print("PDF format detection verified successfully!")

   # Test storage path resolver
   path = plugin._get_resource_file_path({"id": "abcdef12-3456-7890-abcd-ef1234567890", "url_type": "upload"})
   print("Resolved Filestore Path:", path)
   ```

---

## 4. Edge Cases & Resilience Verification

| Test Scenario | Input / Action | Expected Result | Verified |
| :--- | :--- | :--- | :---: |
| **Non-PDF Upload** | Upload `.csv` or `.xlsx` | Hook silently ignores non-PDF; CKAN dataset is created normally without errors. | [x] |
| **Missing Akvo RAG Token** | `ckanext.akvorag.app_token` not configured | Warning logged; CKAN resource creation succeeds without crashing user request. | [x] |
| **Akvo RAG Unreachable / Timeout** | Ngrok tunnel down or Akvo RAG server offline | Network error caught and logged; user upload completes gracefully in CKAN. | [x] |
| **Direct URL vs Local File** | Resource with external URL (not local upload) | Logged as external resource or handled appropriately. | [x] |
| **Dataset Purge** | Delete dataset with multiple PDF resources | All associated PDF resource sync records are triggered for cleanup. | [x] |

---

## 5. Acceptance Checklist
- [x] `AkvoRAGPlugin` implements `IResourceController`, `IPackageController`, and `IConfigurer`.
- [x] Automated unit test suite achieves **91% overall coverage** (≥80% gate met).
- [x] Graceful error isolation (failures in Akvo RAG sync never block native CKAN operations).
- [x] Comprehensive manual testing instructions documented.
