# QA Guide: Local CKAN Docker Environment (Issue #2)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #2** ([`001_local_ckan_docker_spec.md`](../features/001_local_ckan_docker_spec.md)), which establishes the local CKAN 2.10 multi-container Docker environment (CKAN Web, PostgreSQL 14, Apache Solr 8, and Redis 7) with `ckanext-akvorag` extension mounting.

---

## 2. Prerequisites
- **Operating System**: macOS (Apple Silicon or Intel) / Linux / Windows with Docker Desktop.
- **Docker Engine**: Version 20.10+ (Docker Compose v2+).
- **Required Available Ports**: `5000` (CKAN), `5432` (Postgres), `8983` (Solr), `6379` (Redis).

---

## 3. User Authentication & First User Setup Guide 👤

### 3.1 Default Pre-Configured Sysadmin
The container initialization automatically creates a default administrator user:
- **Login URL**: **[http://localhost:5000/user/login](http://localhost:5000/user/login)**
- **Username**: `admin`
- **Password**: `ckan_admin_password`
- **Email**: `admin@akvo.org`

---

### 3.2 How to Create a New User via CLI
To provision an additional user or create your own custom account:

```bash
# 1. Create the user
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user add <username> email=<email@example.com> password=<password>

# 2. (Optional) Promote to Sysadmin / Superuser
docker compose exec -T ckan ckan -c /srv/app/ckan.ini sysadmin add <username>
```

#### Example:
```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user add galih email=galih@akvo.org password=mysecurepassword
docker compose exec -T ckan ckan -c /srv/app/ckan.ini sysadmin add galih
```

---

### 3.3 Password Reset & API Token Generation
```bash
# Reset password for any existing user
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user setpass <username>

# Generate an API Token for programmatic API access
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user token create admin local-dev-token
```

---

## 4. Step-by-Step QA Test Scenarios

### Scenario 1: Clean Startup & Healthchecks
**Objective**: Verify all 4 containers start and pass health checks.

1. Launch the stack:
   ```bash
   docker compose up -d
   ```
2. Verify container statuses:
   ```bash
   docker compose ps
   ```
   **Expected Output**:
   | Container Name | Service | State / Health |
   | :--- | :--- | :--- |
   | `ckan_db` | `db` | `Up (healthy)` |
   | `ckan_solr` | `solr` | `Up (healthy)` |
   | `ckan_redis` | `redis` | `Up` |
   | `ckan_web` | `ckan` | `Up` |

---

### Scenario 2: CKAN Status API Verification
**Objective**: Confirm CKAN 2.10.4 is serving and that `ckanext-akvorag` is registered.

1. Execute curl request against CKAN Action API:
   ```bash
   curl -s http://localhost:5000/api/3/action/status_show | python3 -m json.tool
   ```
2. **Expected Output**:
   ```json
   {
       "help": "http://localhost:5000/api/3/action/help_show?name=status_show",
       "success": true,
       "result": {
           "site_title": "CKAN RAG Knowledge Portal",
           "site_description": "CKAN Knowledgebase and Document Portal",
           "site_url": "http://localhost:5000",
           "extensions": [
               "stats",
               "text_view",
               "image_view",
               "datastore",
               "akvorag"
           ],
           "ckan_version": "2.10.4"
       }
   }
   ```
   - `success` must be `true`.
   - `extensions` must include `"akvorag"`.

---

### Scenario 3: Apache Solr 8 Core Health
**Objective**: Confirm Solr search core is initialized and accepting queries.

1. Execute ping request to Solr:
   ```bash
   curl -s "http://localhost:8983/solr/ckan/admin/ping?wt=json"
   ```
2. **Expected Output**:
   ```json
   {"responseHeader":{"zkConnected":null,"status":0,"QTime":1,"params":{"wt":"json"}},"status":"OK"}
   ```

---

### Scenario 4: PostgreSQL Database & DataStore Initialization
**Objective**: Verify database schemas for CKAN metadata and DataStore exist.

1. Check databases in PostgreSQL:
   ```bash
   docker compose exec -T db psql -U ckan_default -d ckan_default -c "\dt"
   ```
   **Expected Result**: Lists CKAN core tables (e.g., `user`, `package`, `resource`, `group`).

2. Check DataStore database:
   ```bash
   docker compose exec -T db psql -U ckan_default -d datastore_default -c "SELECT current_database();"
   ```
   **Expected Result**: Returns `datastore_default`.

---

### Scenario 5: Web UI Login Verification
**Objective**: Confirm authentication works via browser.

1. Open **[http://localhost:5000/user/login](http://localhost:5000/user/login)** in your browser.
2. Enter credentials (`admin` / `ckan_admin_password`).
3. Click **Log In**.
4. **Expected Result**: 
   - Successfully redirects to dashboard / dataset catalog.
   - Admin toolbar (Sysadmin ribbon and settings) is visible in top navigation.

---

### Scenario 6: Extension Mounting & Editable Development Mode
**Objective**: Verify source changes in `./ckanext/akvorag` are reflected inside the container without rebuilding the image.

1. Check container mount:
   ```bash
   docker compose exec -T ckan pip list | grep ckanext-akvorag
   ```
   **Expected Output**:
   ```
   ckanext-akvorag 0.1.0 /srv/app/src_extensions/ckanext-akvorag
   ```

---

### Scenario 7: Dataset & File Upload Smoke Test
**Objective**: Create a dataset and upload a test file in CKAN UI.

1. While logged in as `admin`, navigate to `http://localhost:5000/dataset/new`.
2. Enter:
   - **Title**: `Test Knowledgebase Dataset`
   - **Description**: `Smoke test dataset for CKAN Docker environment`
3. Click **Next: Add Data**.
4. Upload a sample file (e.g. any PDF or CSV).
5. Click **Finish**.
6. **Expected Result**: Dataset is created and search index finds it immediately.

---

## 5. QA Sign-Off Checklist

- [ ] All 4 containers start cleanly via `docker compose up -d`.
- [ ] First user / sysadmin login works at `http://localhost:5000/user/login`.
- [ ] CKAN API `status_show` returns `ckan_version: 2.10.4` and `extensions: [..., "akvorag"]`.
- [ ] Solr 8 ping responds with `status: OK`.
- [ ] Postgres contains `ckan_default` and `datastore_default`.
- [ ] Volume mount links `./ckanext/akvorag` to `/srv/app/src_extensions/ckanext-akvorag`.
- [ ] Manual dataset creation succeeds.

---

## 6. Troubleshooting & Useful Commands

| Issue | Remediation |
| :--- | :--- |
| **Port Conflict (5000/5432/8983)** | Update `CKAN_PORT`, `POSTGRES_PORT`, or `SOLR_PORT` in `.env`. |
| **View CKAN Logs** | `docker compose logs -f ckan` |
| **Reset / Re-initialize Database** | `docker compose down -v && docker compose up -d` |
| **Create New Admin User** | `docker compose exec -T ckan ckan -c /srv/app/ckan.ini user add <user> email=<email> password=<pass>`<br/>`docker compose exec -T ckan ckan -c /srv/app/ckan.ini sysadmin add <user>` |
