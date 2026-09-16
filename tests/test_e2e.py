"""
End-to-End (E2E) Integration Verification Suite for CKAN to Akvo RAG Knowledgebase Sync.
Tests the complete document lifecycle from App Registration, PDF Upload, RAG Chat Query, to Deletion/Purge.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner

from ckanext.akvorag.client import AkvoRAGClient
from ckanext.akvorag.plugin import AkvoRAGPlugin
from ckanext.akvorag.cli import akvorag
from ckanext.akvorag import helpers


@pytest.fixture
def sample_pdf_path():
    path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_water_report.pdf")
    assert os.path.exists(path), f"Fixture PDF missing at {path}"
    return path


def test_e2e_full_lifecycle_hermetic(sample_pdf_path):
    """
    E2E Scenario: Full Document Lifecycle
    1. App Registration with Superuser Token
    2. Knowledge Base Creation
    3. Document Ingestion Job Submission
    4. Conversational Chat Query & Source Citation
    5. Document Purge & Deletion
    """
    with patch("requests.Session.send") as mock_send:
        # Step 1: Registration Mock
        reg_response = MagicMock()
        reg_response.status_code = 200
        reg_response.json.return_value = {
            "app_id": "app_e2e_test",
            "app_name": "CKAN E2E Portal",
            "access_token": "tok_e2e_access_token_12345",
        }

        # Step 2: KB Creation Mock
        kb_response = MagicMock()
        kb_response.status_code = 200
        kb_response.json.return_value = {
            "id": 201,
            "name": "CKAN Water KB",
            "description": "E2E Knowledge Base",
        }

        # Step 3: Ingestion Job Mock
        upload_response = MagicMock()
        upload_response.status_code = 200
        upload_response.json.return_value = {
            "job_id": "job_upload_e2e_888",
            "status": "SUBMITTED",
            "document_id": "doc_water_report_01",
        }

        # Step 4: Chat Query Mock
        chat_response = MagicMock()
        chat_response.status_code = 200
        chat_response.json.return_value = {
            "job_id": "job_chat_e2e_999",
            "status": "COMPLETED",
            "answer": "The average pH level of the monitored reservoir was 7.35 according to the 2026 report.",
            "citations": [
                {
                    "document_name": "sample_water_report.pdf",
                    "page": 1,
                    "snippet": "The average pH level of the monitored reservoir was 7.35.",
                }
            ],
        }

        # Step 5: Deletion Mock
        delete_response = MagicMock()
        delete_response.status_code = 200
        delete_response.json.return_value = {
            "status": "SUCCESS",
            "message": "Document purged from knowledge base vectors.",
        }

        mock_send.side_effect = [
            reg_response,
            kb_response,
            upload_response,
            chat_response,
            delete_response,
        ]

        # -------------------------------------------------------------
        # 1. Initialize Client & Register App
        # -------------------------------------------------------------
        client = AkvoRAGClient(base_url="https://akvo.ngrok.dev")
        reg = client.register_app(
            app_name="CKAN E2E Portal",
            domain="localhost:5000",
            superuser_token="super_secret_admin_token",
        )
        assert reg["app_id"] == "app_e2e_test"
        assert client.app_token == "tok_e2e_access_token_12345"

        # -------------------------------------------------------------
        # 2. Create Knowledge Base
        # -------------------------------------------------------------
        kb = client.create_knowledge_base(name="CKAN Water KB")
        assert kb["id"] == 201

        # -------------------------------------------------------------
        # 3. Submit Document Ingestion Job
        # -------------------------------------------------------------
        upload_job = client.submit_upload_job(
            file_path=sample_pdf_path,
            filename="sample_water_report.pdf",
            kb_id=201,
            callback_params={"ckan_resource_id": "res_e2e_01", "dataset_id": "pkg_e2e_01"},
        )
        assert upload_job["job_id"] == "job_upload_e2e_888"
        assert upload_job["status"] == "SUBMITTED"

        # -------------------------------------------------------------
        # 4. Perform Natural Language Query
        # -------------------------------------------------------------
        chat_job = client.submit_chat_job(
            prompt="What is the average pH level of the reservoir?",
            kb_ids=[201],
        )
        assert "7.35" in chat_job["answer"]
        assert len(chat_job["citations"]) == 1
        assert chat_job["citations"][0]["document_name"] == "sample_water_report.pdf"

        # -------------------------------------------------------------
        # 5. Purge Document
        # -------------------------------------------------------------
        del_result = client.delete_document(kb_id=201, document_id="doc_water_report_01")
        assert del_result["status"] == "SUCCESS"


def test_e2e_plugin_hooks_and_cli_integration(sample_pdf_path):
    """
    E2E Scenario: CKAN Plugin Hooks & CLI Workflow
    Verifies that CKAN plugin hooks intercept resource events and CLI commands work cohesively.
    """
    runner = CliRunner()

    with patch("ckanext.akvorag.plugin.get_akvorag_client") as mock_get_client, \
         patch("ckanext.akvorag.plugin.get_configured_kb_id", return_value=301), \
         patch("ckanext.akvorag.plugin.get_resource_file_path", return_value=sample_pdf_path):

        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.app_token = "tok_e2e_test"
        mock_client.submit_upload_job.return_value = {"job_id": "job_111"}
        mock_client.delete_document.return_value = {"status": "SUCCESS"}
        mock_get_client.return_value = mock_client

        plugin = AkvoRAGPlugin()

        # 1. Trigger after_resource_create hook
        resource_data = {
            "id": "res_e2e_pdf_01",
            "name": "sample_water_report.pdf",
            "format": "PDF",
            "package_id": "pkg_e2e_water",
        }
        plugin.after_resource_create(context={}, data_dict=resource_data)
        mock_client.submit_upload_job.assert_called_once()

        # 2. Trigger after_resource_delete hook
        plugin.after_resource_delete(context={}, data_dict=resource_data)
        mock_client.delete_document.assert_called_once_with(kb_id=301, document_id="res_e2e_pdf_01")


def test_e2e_resilience_and_graceful_degradation():
    """
    E2E Scenario: Resilience when Akvo RAG is unreachable or unconfigured.
    Ensures CKAN plugin and UI helpers degrade gracefully without exceptions.
    """
    plugin = AkvoRAGPlugin()

    with patch("ckanext.akvorag.plugin.get_akvorag_client", return_value=None):
        # Resource create when unconfigured should not raise
        plugin.after_resource_create(context={}, data_dict={"id": "res_1", "format": "PDF"})

        # Resource delete when unconfigured should not raise
        plugin.after_resource_delete(context={}, data_dict={"id": "res_1"})

        # Package delete when unconfigured should not raise
        plugin.after_package_delete(
            context={},
            data_dict={"id": "pkg_1", "resources": [{"id": "res_1"}]},
        )

    # UI Helpers should return safe fallbacks
    with patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        assert helpers.akvorag_is_configured() is False
        assert helpers.akvorag_get_kb_id() is None
        assert helpers.akvorag_get_endpoint() == "https://akvo.ngrok.dev"
        widget_cfg = helpers.akvorag_get_widget_config()
        assert widget_cfg["isConfigured"] is False
