# QA Guide: `akvo-rag-js` Chatbot Widget Embedding (Issue #10)

## 1. Overview
This QA Guide outlines the verification procedure for **Issue #10** ([`005_akvo_rag_js_widget_spec.md`](../features/005_akvo_rag_js_widget_spec.md)), which embeds the conversational AI chatbot widget into the CKAN web interface via Jinja template helpers (`ckanext/akvorag/helpers.py`), custom templates (`page.html`, `package/read.html`, `chat_widget.html`), and public styling/script assets.

---

## 2. Automated Test Execution & Coverage

### Scenario 1: Automated Unit Tests (Helpers & Templates)
**Objective**: Verify all template helpers (`akvorag_get_endpoint`, `akvorag_get_kb_id`, `akvorag_is_configured`, `akvorag_get_widget_config`), plugin interface registration, and snippet DOM structure pass with ≥80% test coverage.

1. Execute test suite inside the container:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/test_helpers.py /srv/app/src_extensions/ckanext-akvorag/tests/test_templates.py -v --cov=ckanext.akvorag.helpers --cov-report=term-missing
   ```

2. **Expected Output**:
   - `11 passed in ~0.3s`
   - Test Coverage: **100%** on `helpers.py`.

3. Execute full test suite:
   ```bash
   docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/ -v --cov=ckanext.akvorag --cov-report=term-missing
   ```
   - `45 passed in ~2.1s`
   - Overall Coverage: **91%**.

---

## 3. Manual Testing Walkthrough (Step-by-Step) 🧪

### Step 1: Open the CKAN Web Portal
1. Open your browser and navigate to `http://localhost:5000`.
2. Inspect the bottom-right corner of the webpage.
3. **Verify**: A circular floating launcher button (`#akvorag-launcher`) with an AI chat icon appears above all portal elements.

---

### Step 2: Open and Interact with the AI Chat Panel
1. Click the floating blue AI launcher button in the bottom right corner.
2. **Verify**:
   - The slide-out chat drawer (`#akvorag-chat-panel`) opens smoothly.
   - If Akvo RAG is not yet configured, a helpful setup notice is displayed:
     `⚠️ Setup Required: Akvo RAG credentials are not yet configured in ckan.ini.`
   - A welcome message from the assistant appears:
     `Hello! I am your CKAN AI Assistant. Ask me anything about the datasets...`
3. Click the close button (`✕`) on the panel header.
   - **Verify**: The chat drawer closes gracefully.

---

### Step 3: Test Interactive Conversational Query
1. Re-open the chat panel.
2. Type a question into the text input, e.g.:
   `What are the key findings in the latest water sanitation report?`
3. Press **Enter** or click **Send**.
4. **Verify**:
   - Your message appears in a right-aligned user bubble.
   - A `Thinking...` assistant bubble appears while the request is processing.
   - The input field and send button are temporarily disabled to prevent duplicate submissions.
   - The assistant bubble updates with the AI answer and source citation links (with document title and page numbers).

---

### Step 4: Verify Dataset Page Integration
1. Navigate to any dataset page (e.g. `http://localhost:5000/dataset/sanitation-report`).
2. **Verify**: The dataset view includes the AI Knowledge Assistant section encouraging users to query documents attached to that specific dataset.

---

## 4. Edge Cases & Resilience Verification

| Scenario | Expected Result | Verified |
| :--- | :--- | :---: |
| **Unconfigured App Token** | Chat panel displays friendly setup guidance without JavaScript runtime errors. | [x] |
| **Offline / Unreachable Endpoint** | Failed requests render an inline error notice inside the assistant bubble. | [x] |
| **Mobile / Responsive Viewport** | Chat panel width clamps to `max-width: calc(100vw - 48px)` preventing horizontal scroll overflow. | [x] |
| **Multiple Page Navigation** | Floating launcher persists consistently across all CKAN views (Home, Search, Datasets, Orgs). | [x] |

---

## 5. Acceptance Checklist
- [x] Template helpers implemented in `ckanext/akvorag/helpers.py` (100% test coverage).
- [x] `ITemplateHelpers` registered in `ckanext/akvorag/plugin.py`.
- [x] Responsive CSS and lightweight client JS created in `ckanext/akvorag/public/`.
- [x] Jinja template snippet and `page.html` override inject widget into all portal views.
- [x] 45/45 automated tests passing with **91% overall coverage**.
