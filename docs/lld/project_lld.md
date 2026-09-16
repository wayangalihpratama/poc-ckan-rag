# Project LLD: CKAN to Akvo RAG Knowledgebase Sync & AI Assistant

## 1. System Architecture & Topology

```mermaid
flowchart TD
    subgraph HostApp["1. Local CKAN (Docker Environment)"]
        direction TB
        CKAN_UI["CKAN Web UI & Portal"]
        CKAN_EXT["ckanext-akvorag (Plugin)"]
        CKAN_FS["CKAN Filestore (PDF Documents)"]
        
        CKAN_UI -->|"Document Upload / Delete"| CKAN_EXT
        CKAN_EXT -->|"Fetch File"| CKAN_FS
    end

    subgraph ChatFrontend["2. AI Chat Frontend"]
        WIDGET["akvo-rag-js Chat Widget<br/>(Embedded in CKAN)"]
    end

    subgraph Tunnel["3. Public HTTPS Gateway"]
        NGROK["ngrok Tunnel<br/>(https://akvo.ngrok.dev)"]
    end

    subgraph AkvoRAG["4. Akvo RAG Platform (Backend)"]
        direction TB
        RAG_API["Akvo RAG /api/v1/apps API<br/>(Tenant Token Auth)"]
        RAG_WORKER["Ingestion & Embedding Worker"]
        CHROMA[("ChromaDB Vector Store<br/>+ MinIO Document Storage")]

        RAG_API -->|"Process Upload Job"| RAG_WORKER
        RAG_WORKER -->|"Store Embeddings"| CHROMA
    end

    %% Cross-layer connections
    CKAN_EXT -->|"REST API Jobs & Sync (Bearer tok_...)"| NGROK
    WIDGET -->|"Interactive Chat Stream"| NGROK
    CKAN_UI -.->|"Mounts & Renders"| WIDGET
    NGROK -->|"Forward to Port 8000"| RAG_API
```

---

## 2. Sequence Diagrams

### 2.1 App Registration (One-time Setup)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Admin / Setup CLI
    participant Ext as ckanext-akvorag (CLI)
    participant RAG as Akvo RAG (https://akvo.ngrok.dev)

    Admin->>Ext: Run `ckan akvorag register`
    Note over Ext,RAG: Uses AKVO_RAG_SUPERUSER_TOKEN for authorization
    Ext->>RAG: POST /api/v1/apps/register (app_name: "ckan_portal", domain: "localhost:5000")
    RAG-->>Ext: Returns access_token (tok_...) & default knowledge_base_id
    Ext->>Ext: Persist credentials to CKAN config (ckan.ini / env)
```

### 2.2 Document Upload & Lifecycle Sync
```mermaid
sequenceDiagram
    autonumber
    actor User as CKAN User
    participant CKAN as CKAN Web & Filestore
    participant Ext as ckanext-akvorag (IResourceController)
    participant RAG as Akvo RAG (https://akvo.ngrok.dev)
    participant Worker as Vector Worker & ChromaDB

    User->>CKAN: Upload PDF resource (e.g. water_quality.pdf)
    CKAN->>Ext: after_resource_create(data_dict)
    Ext->>Ext: Check if format/mimetype == "pdf"
    Ext->>RAG: POST /api/v1/apps/jobs (job: "upload", Bearer tok_..., file=@water_quality.pdf)
    RAG->>Worker: Parse PDF, Chunk text, Generate Embeddings
    Worker-->>RAG: Store in ChromaDB
    RAG-->>Ext: Webhook / Async status (COMPLETED)

    opt Document Deletion
        User->>CKAN: Delete resource / dataset
        CKAN->>Ext: after_resource_delete(data_dict)
        Ext->>RAG: DELETE /api/v1/apps/knowledge-bases/{kb_id}/documents/{doc_id}
        RAG->>Worker: Purge vectors matching resource_id from ChromaDB
    end
```

### 2.3 AI Chat Interaction (`akvo-rag-js`)
```mermaid
sequenceDiagram
    autonumber
    actor User as Portal User
    participant Widget as akvo-rag-js Widget (Embedded in CKAN)
    participant RAG as Akvo RAG (https://akvo.ngrok.dev)

    User->>Widget: Ask question: "What are the latest water quality findings?"
    Widget->>RAG: Stream Chat Query (Knowledge Base ID + Prompt)
    RAG-->>Widget: Streamed Answer with Citations & Source Document links
    Widget-->>User: Display formatted response with highlighted citations
```

---

## 3. Component Details & Data Contracts

### 3.1 CKAN Plugin (`ckanext/akvorag/plugin.py`)
- Implements: `IResourceController`, `IPackageController`, `IConfigurer`, `ITemplateHelpers`, `IClick`.
- Hook definitions:
  - `after_resource_create(context, data_dict)`
  - `after_resource_update(context, data_dict)`
  - `before_resource_delete(context, resource, resources)`
  - `after_resource_delete(context, data_dict)`
  - `delete(entity)` (PackageController)
  - `after_dataset_delete(context, data_dict)`

### 3.2 Akvo RAG Client (`ckanext/akvorag/client.py`)
- Encapsulates `/api/v1/apps` REST interactions:
  - `register_app(app_name, domain, superuser_token)` ➔ `tok_...`, `knowledge_base_id`
  - `submit_upload_job(file_path, filename, callback_params)` ➔ `job_id`
  - `delete_document(kb_id, document_id)` ➔ status
  - `delete_document_by_name(kb_id, filename)` ➔ status
  - `get_me()` ➔ app status
  - `submit_chat_job(prompt, kb_id)` ➔ answer + citations

### 3.3 CLI Interface (`ckanext/akvorag/cli.py`)
- `ckan akvorag register`: Registers the host application and provisions a default KB.
- `ckan akvorag status`: Checks connection, token validity, and active KB configuration.
- `ckan akvorag sync-all`: Bulk-scans existing PDF resources across all datasets.
- `ckan akvorag query`: Direct CLI conversational Q&A over the knowledgebase.

### 3.4 Frontend Integration (`akvo-rag-js`)
- Embedded in CKAN layout via Jinja template extension (`ckanext/akvorag/templates/`).
- Initialized with target Knowledge Base ID, public endpoint, and WebSocket streaming URL.

---

## 4. Verification & Testing Strategy

### 4.1 Automated Test Suite
- `pytest tests/test_client.py`: Unit tests mocking Akvo RAG `/api/v1/apps` responses.
- `pytest tests/test_plugin.py`: Unit tests for `IResourceController` and `IPackageController` hook execution.
- `pytest tests/test_helpers.py`: Unit tests for template helper functions and URL resolvers.
- `pytest tests/test_templates.py`: Unit tests for template rendering and widget snippets.
- `pytest tests/test_cli.py`: Click CLI runner tests for all 4 commands.
- `pytest tests/test_e2e.py`: Hermetic end-to-end integration tests with mocked API backends.

### 4.2 End-to-End Verification
- Complete verification loop: Start ngrok ➔ Register CKAN app ➔ Upload PDF ➔ Verify vector chunking in Akvo RAG ➔ Query via `akvo-rag-js` ➔ Delete PDF in CKAN ➔ Verify vector purge.

---

## 5. Implementation Task Mapping & Vibe Coding Time Estimation ⏱️

| Task ID | Implementation Area & Feature Spec | Touchpoint Files / Deliverables | Dev | Testing | QA & Review | Total Est. |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **TASK-01** | **[Local CKAN Docker Environment](docs/features/001_local_ckan_docker_spec.md)** | `docker-compose.yml`, `Dockerfile`, `.env.example`, `ckan.ini` | 35m | 15m | 15m | **65m (1.1h)** |
| **TASK-02** | **[Akvo RAG Client Library](docs/features/002_akvo_rag_client_spec.md)** | `ckanext/akvorag/client.py`, `tests/test_client.py` | 30m | 25m | 15m | **70m (1.2h)** |
| **TASK-03** | **[Core CKAN Plugin Hooks](docs/features/003_ckanext_akvorag_plugin_spec.md)** | `ckanext/akvorag/plugin.py`, `tests/test_plugin.py` | 45m | 30m | 20m | **95m (1.6h)** |
| **TASK-04** | **[CKAN Click CLI Commands](docs/features/004_ckan_cli_commands_spec.md)** | `ckanext/akvorag/cli.py`, `tests/test_cli.py` | 25m | 20m | 15m | **60m (1.0h)** |
| **TASK-05** | **[akvo-rag-js UI Embedding](docs/features/005_akvo_rag_js_widget_spec.md)** | `ckanext/akvorag/templates/`, `ckanext/akvorag/fanstatic/` | 30m | 15m | 15m | **60m (1.0h)** |
| **TASK-06** | **[End-to-End Verification Runbook](docs/features/006_end_to_end_verification_spec.md)** | End-to-end integration test & verification runbook | 30m | 20m | 20m | **70m (1.2h)** |
| **TOTAL** | **Full PoC Implementation** | | **195m** | **125m** | **100m** | **420m (7.0h)** |
