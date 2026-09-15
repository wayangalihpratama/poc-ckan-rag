# Sprint Tasks: CKAN to Akvo RAG Knowledgebase Sync PoC

**Issue**: [#1](https://github.com/wayangalihpratama/poc-ckan-rag/issues/1)  
**PRD**: [`docs/prd/project_prd.md`](docs/prd/project_prd.md)  
**LLD**: [`docs/lld/project_lld.md`](docs/lld/project_lld.md)  

| Task ID | Task Description | Dev | Testing | QA & Review | Total Est. | Actual | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TASK-00** | Project PRD & LLD Architecture Documentation | 30m | - | 15m | **45m (0.75h)** | 45m | [x] |
| **TASK-01** | Local CKAN Docker Setup (`docker-compose.yml`, Solr 8, Postgres 14, Redis) | 35m | 15m | 15m | **65m (1.1h)** | - | [ ] |
| **TASK-02** | `AkvoRAGClient` with Superuser Registration & `/api/v1/apps` Job Handlers | 30m | 25m | 15m | **70m (1.2h)** | - | [ ] |
| **TASK-03** | `ckanext-akvorag` plugin core (`IResourceController` upload/delete hooks) | 45m | 30m | 20m | **95m (1.6h)** | - | [ ] |
| **TASK-04** | CKAN CLI Commands (`register`, `status`, `sync-all`) | 25m | 20m | 15m | **60m (1.0h)** | - | [ ] |
| **TASK-05** | `akvo-rag-js` Chatbot Widget Embedding in CKAN Templates | 30m | 15m | 15m | **60m (1.0h)** | - | [ ] |
| **TASK-06** | End-to-End Verification (Ngrok tunnel ➔ PDF upload ➔ RAG sync ➔ Chat ➔ Delete) | 30m | 20m | 20m | **70m (1.2h)** | - | [ ] |
