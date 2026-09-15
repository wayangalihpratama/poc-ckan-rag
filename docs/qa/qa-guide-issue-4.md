# QA Guide: Akvo RAG Client Library (Issue #4)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #4** ([`002_akvo_rag_client_spec.md`](../features/002_akvo_rag_client_spec.md)), which implements the `AkvoRAGClient` Python library (`ckanext/akvorag/client.py`) for interfacing with Akvo RAG's `/api/v1/apps` multi-tenant endpoints.

---

## 2. Automated Test Execution & Coverage

### Scenario 1: Automated Unit Test Suite
**Objective**: Verify all client endpoints, authentication headers, error classes, and edge cases pass with ≥80% test coverage.

1. Execute test suite inside the container:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/test_client.py -v --cov=ckanext.akvorag.client --cov-report=term-missing
   ```

2. **Expected Output**:
   - `13 passed in ~0.3s`
   - Test Coverage: **98%** (exceeds the 80% coverage mandate).

---

## 3. Manual Testing Walkthrough (Step-by-Step) 🧪

You can test `AkvoRAGClient` manually from your host machine or directly inside the running CKAN Docker container.

### Method A: Interactive Python Shell inside Docker (Recommended)

1. Open an interactive Python shell inside the CKAN container:
   ```bash
   docker compose exec -it ckan python
   ```

2. Import the client and initialize it:
   ```python
   from ckanext.akvorag.client import AkvoRAGClient, AkvoRAGError

   # Initialize client (uses https://akvo.ngrok.dev by default)
   client = AkvoRAGClient(base_url="https://akvo.ngrok.dev", app_token="your_app_token_here")
   print("Client initialized:", client.base_url)
   ```

3. **Test App Registration** (if you have the superuser admin token):
   ```python
   registration = client.register_app(
       app_name="ckan_manual_test",
       domain="localhost:5000",
       superuser_token="YOUR_SUPERUSER_ADMIN_TOKEN"
   )
   print("Registration Result:", registration)
   # Client app_token is now automatically set to the returned access_token
   print("Active App Token:", client.app_token)
   ```

4. **Test Token Validation (`/me`)**:
   ```python
   me = client.get_me()
   print("Current App Status:", me)
   # Expected: {"app_id": "...", "app_name": "...", "status": "active", ...}
   ```

5. **Test Listing Knowledge Bases**:
   ```python
   kbs = client.list_knowledge_bases()
   print("Accessible Knowledge Bases:", kbs)
   ```

6. **Test Document Upload Job**:
   ```python
   # Create a dummy test PDF inside the container
   with open("/tmp/test_report.pdf", "wb") as f:
       f.write(b"%PDF-1.4 test document content for QA manual verification")

   # Submit upload job
   upload_job = client.submit_upload_job(
       file_path="/tmp/test_report.pdf",
       filename="test_report.pdf",
       kb_id=101,  # Use your target KB ID
       callback_params={"test_source": "manual_qa"}
   )
   print("Upload Job Submitted:", upload_job)
   # Expected: {"job_id": "job_...", "status": "PENDING" or "SUBMITTED"}
   ```

7. **Test Chat / Question Answering Job**:
   ```python
   chat_job = client.submit_chat_job(
       prompt="What is this test document about?",
       kb_ids=[101]
   )
   print("Chat Response:", chat_job)
   ```

8. **Test Document Deletion**:
   ```python
   delete_result = client.delete_document(kb_id=101, document_id="doc_example_id")
   print("Delete Result:", delete_result)
   ```

---

### Method B: One-Liner Quick Health Check from Terminal

Run this quick command to verify the library imports and validates parameters cleanly:

```bash
docker compose exec -T ckan python -c "
from ckanext.akvorag.client import AkvoRAGClient
client = AkvoRAGClient(base_url='https://akvo.ngrok.dev')
print('✅ AkvoRAGClient initialized successfully for:', client.base_url)
"
```

---

## 4. Exception Class Mapping

| HTTP Status | Exception Class | Verified Test |
| :--- | :--- | :--- |
| `401`, `403` | `AkvoRAGAuthError` | `test_register_app_unauthorized` |
| `404` | `AkvoRAGNotFoundError` | `test_error_handling_not_found` |
| `400`, `422` | `AkvoRAGValidationError` | `test_error_handling_validation_error` |
| `500+` | `AkvoRAGError` | `test_error_handling_generic_server_error` |

---

## 5. QA Sign-Off Checklist

- [ ] Automated test suite runs with 0 failures (`13/13 passed`).
- [ ] Code coverage gate achieved (98% ≥ 80%).
- [ ] Manual interactive Python shell test succeeds in container.
- [ ] Superuser token registration handles `Authorization: Bearer <SUPERUSER_TOKEN>`.
- [ ] Multipart upload correctly streams PDF files with `job: upload` JSON payload.
- [ ] Deletion endpoint correctly maps document ID and KB ID.
