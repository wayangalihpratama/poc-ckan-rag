# QA Guide: Akvo RAG Client Library (Issue #4)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #4** ([`002_akvo_rag_client_spec.md`](../features/002_akvo_rag_client_spec.md)), which implements the `AkvoRAGClient` Python library (`ckanext/akvorag/client.py`) for interfacing with Akvo RAG's `/api/v1/apps` multi-tenant endpoints.

---

## 2. Test Execution & Coverage

### Scenario 1: Automated Unit Test Suite
**Objective**: Verify all client endpoints, authentication headers, error classes, and edge cases pass with ≥80% test coverage.

1. Execute test suite inside the container:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/test_client.py -v --cov=ckanext.akvorag.client --cov-report=term-missing
   ```

2. **Expected Output**:
   - `13 passed in ~0.3s`
   - Test Coverage: **≥95%** (currently 98%).

---

### Scenario 2: Client Interface Verification
**Objective**: Confirm all documented methods are available and callable.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `register_app(...)` | `POST /api/v1/apps/register` | Registers host app with superuser admin token. |
| `get_me()` | `GET /api/v1/apps/me` | Validates active tenant token and returns app metadata. |
| `list_knowledge_bases()` | `GET /api/v1/apps/knowledge-bases` | Retrieves accessible Knowledge Bases. |
| `create_knowledge_base(...)` | `POST /api/v1/apps/knowledge-bases` | Creates a new Knowledge Base. |
| `submit_upload_job(...)` | `POST /api/v1/apps/jobs` | Sends multipart PDF file and metadata for chunking. |
| `submit_chat_job(...)` | `POST /api/v1/apps/jobs` | Submits natural language question to RAG engine. |
| `delete_document(...)` | `DELETE /api/v1/apps/.../documents/...` | Purges document from Knowledge Base. |

---

### Scenario 3: Exception Class Mapping
**Objective**: Verify HTTP status codes are translated into domain-specific exceptions.

| HTTP Status | Exception Class | Verified Test |
| :--- | :--- | :--- |
| `401`, `403` | `AkvoRAGAuthError` | `test_register_app_unauthorized` |
| `404` | `AkvoRAGNotFoundError` | `test_error_handling_not_found` |
| `400`, `422` | `AkvoRAGValidationError` | `test_error_handling_validation_error` |
| `500+` | `AkvoRAGError` | `test_error_handling_generic_server_error` |

---

## 3. QA Sign-Off Checklist

- [ ] Automated test suite runs with 0 failures (`13/13 passed`).
- [ ] Code coverage gate achieved (98% ≥ 80%).
- [ ] Superuser token registration handles `Authorization: Bearer <SUPERUSER_TOKEN>`.
- [ ] Multipart upload correctly streams PDF files with `job: upload` JSON payload.
- [ ] Deletion endpoint correctly maps document ID and KB ID.
