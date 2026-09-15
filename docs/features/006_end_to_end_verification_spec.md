# Feature Spec 006: End-to-End Verification Suite & Runbook

## Overview
Defines the end-to-end (E2E) integration test harness, verification script, and step-by-step runbook to validate the complete lifecycle:
1. Ngrok HTTPS tunnel activation.
2. CKAN host app registration with superuser token.
3. PDF upload in CKAN ➔ automatic Akvo RAG ingestion into ChromaDB.
4. AI Chatbot query via `akvo-rag-js` returning grounded source citations.
5. PDF deletion in CKAN ➔ automatic vector purge.

---

## E2E Verification Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Tester as Developer / QA
    participant Ngrok as ngrok (https://akvo.ngrok.dev)
    participant CKAN as Local CKAN (Docker)
    participant Plugin as ckanext-akvorag
    participant RAG as Akvo RAG (~/Sites/akvo-rag)
    participant Chroma as ChromaDB Vector Store

    Note over Tester,Chroma: Step 1: Tunnel & Registration
    Tester->>Ngrok: Launch tunnel (`ngrok http 8000 --url=akvo.ngrok.dev`)
    Tester->>CKAN: Execute `ckan akvorag register --admin-token <SUPERUSER_TOKEN>`
    CKAN->>RAG: POST /api/v1/apps/register
    RAG-->>CKAN: Returns access_token & kb_id

    Note over Tester,Chroma: Step 2: PDF Upload & Ingest
    Tester->>CKAN: Upload `sample_water_report.pdf`
    CKAN->>Plugin: Hook: `after_resource_create`
    Plugin->>RAG: POST /api/v1/apps/jobs (file=@sample_water_report.pdf)
    RAG->>Chroma: Ingest & Embed Chunks

    Note over Tester,Chroma: Step 3: Chat Query
    Tester->>CKAN: Ask: "What was the pH level in the 2024 report?"
    CKAN->>RAG: POST /api/v1/apps/jobs (job: "chat")
    RAG-->>Tester: Returns answer + citation (`sample_water_report.pdf`, p. 3)

    Note over Tester,Chroma: Step 4: Deletion & Purge
    Tester->>CKAN: Delete `sample_water_report.pdf` resource
    CKAN->>Plugin: Hook: `after_resource_delete`
    Plugin->>RAG: DELETE /api/v1/apps/knowledge-bases/{kb_id}/documents/{doc_id}
    RAG->>Chroma: Purge vectors
    Tester->>CKAN: Re-ask question ➔ Verify knowledge is purged
```

---

## 1. Technical Deliverables

### 1.1 E2E Test Runner Script
**File**: `/tests/e2e_verification.py`
- Automates the 4-step lifecycle validation against live running services.
- Outputs a clean test report with timestamps and assertion statuses.

### 1.2 Sample Test Artifacts
**Directory**: `/tests/fixtures/`
- `sample_water_report.pdf`: Standard test PDF containing verifiable facts and tables.

---

## 2. Verification Runbook Steps

```bash
# 1. Start Akvo RAG
cd ~/Sites/akvo-rag && ./dc.sh up -d

# 2. Expose via Ngrok
ngrok http 8000 --url=akvo.ngrok.dev

# 3. Start CKAN
cd /Users/galihpratama/Dev/poc-ckan-rag && docker compose up -d

# 4. Run E2E Verification Script
pytest tests/e2e_verification.py -v
```

---

## 3. Vibe Coding Estimation ⏱️

| Subtask | Dev | Testing | QA & Review | Total |
| :--- | :---: | :---: | :---: | :---: |
| E2E Test Harness Script & Fixture Preparation | 15m | 10m | 10m | **35m** |
| Live Service Verification & Edge Case Auditing | 15m | 10m | 10m | **35m** |
| **TOTAL** | **30m** | **20m** | **20m** | **70m (1.2h)** |
