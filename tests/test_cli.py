"""
Unit tests for CKAN Akvo RAG Click CLI commands.
"""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
import pytest

from ckanext.akvorag.cli import akvorag
from ckanext.akvorag.client import AkvoRAGAuthError, AkvoRAGError


@pytest.fixture
def cli_runner():
    return CliRunner()


def test_cli_register_success(cli_runner):
    with patch("ckanext.akvorag.cli.AkvoRAGClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.register_app.return_value = {
            "app_id": "app_ckan_123",
            "access_token": "tok_access_secret_123",
        }
        mock_client.create_knowledge_base.return_value = {
            "id": 101,
            "name": "CKAN Knowledge Base",
        }
        mock_client_cls.return_value = mock_client

        result = cli_runner.invoke(
            akvorag,
            [
                "register",
                "--admin-token",
                "super_secret_admin",
                "--app-name",
                "ckan_portal",
                "--domain",
                "localhost:5000",
            ],
        )

        assert result.exit_code == 0
        assert "App registered successfully!" in result.output
        assert "app_ckan_123" in result.output
        assert "tok_access_secret_123" in result.output
        assert "ID: 101" in result.output
        mock_client.register_app.assert_called_once()


def test_cli_register_failure(cli_runner):
    with patch("ckanext.akvorag.cli.AkvoRAGClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.register_app.side_effect = AkvoRAGAuthError("Invalid superuser token")
        mock_client_cls.return_value = mock_client

        result = cli_runner.invoke(
            akvorag,
            ["register", "--admin-token", "bad_token"],
        )

        assert result.exit_code == 1
        assert "Registration failed" in result.output


def test_cli_status_success(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client, \
         patch("ckanext.akvorag.cli._get_target_kb_id") as mock_get_kb_id:

        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.app_token = "tok_valid_app"
        mock_client.get_me.return_value = {
            "app_id": "app_ckan_123",
            "app_name": "CKAN Portal",
            "status": "active",
        }
        mock_client.list_knowledge_bases.return_value = [
            {"id": 101, "name": "CKAN Portal KB"},
            {"id": 102, "name": "Secondary KB"},
        ]
        mock_get_client.return_value = mock_client
        mock_get_kb_id.return_value = 101

        result = cli_runner.invoke(akvorag, ["status"])

        assert result.exit_code == 0
        assert "Akvo RAG Connection: OK" in result.output
        assert "app_ckan_123" in result.output
        assert "CKAN Portal" in result.output
        assert "[101] CKAN Portal KB [ACTIVE TARGET]" in result.output


def test_cli_status_no_token(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.app_token = None
        mock_get_client.return_value = mock_client

        result = cli_runner.invoke(akvorag, ["status"])

        assert result.exit_code == 1
        assert "No app token configured" in result.output


def test_cli_status_error(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.base_url = "https://akvo.ngrok.dev"
        mock_client.app_token = "tok_abc"
        mock_client.get_me.side_effect = AkvoRAGError("Server Unavailable")
        mock_get_client.return_value = mock_client

        result = cli_runner.invoke(akvorag, ["status"])

        assert result.exit_code == 1
        assert "Connection failed" in result.output


def test_cli_sync_all_success(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client, \
         patch("ckanext.akvorag.cli._get_target_kb_id") as mock_get_kb_id, \
         patch("ckan.plugins.toolkit.get_action") as mock_get_action, \
         patch("ckanext.akvorag.cli.get_resource_file_path") as mock_get_path:

        mock_client = MagicMock()
        mock_client.app_token = "tok_valid"
        mock_client.submit_upload_job.return_value = {"job_id": "job_123"}
        mock_get_client.return_value = mock_client
        mock_get_kb_id.return_value = 101

        # Mock packages
        def get_action_side_effect(action_name):
            if action_name == "package_list":
                return lambda ctx, data: ["dataset-01"]
            if action_name == "package_show":
                return lambda ctx, data: {
                    "id": "dataset-01",
                    "title": "Dataset 01",
                    "resources": [
                        {"id": "res-pdf-01", "name": "report.pdf", "format": "PDF"},
                        {"id": "res-csv-02", "name": "data.csv", "format": "CSV"},
                    ],
                }
            return MagicMock()

        mock_get_action.side_effect = get_action_side_effect
        mock_get_path.return_value = "/var/lib/ckan/resources/res-pdf-01.pdf"

        result = cli_runner.invoke(akvorag, ["sync-all"])

        assert result.exit_code == 0
        assert "Bulk Sync Summary" in result.output
        assert "Datasets Scanned:   1" in result.output
        assert "Total Resources:    2" in result.output
        assert "PDFs Identified:    1" in result.output
        assert "Successfully Synced: 1" in result.output
        assert "Skipped (Non-PDF):  1" in result.output
        mock_client.submit_upload_job.assert_called_once()


def test_cli_sync_all_missing_token_or_kb(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client, \
         patch("ckanext.akvorag.cli._get_target_kb_id") as mock_get_kb_id:

        mock_client = MagicMock()
        mock_client.app_token = None
        mock_get_client.return_value = mock_client
        mock_get_kb_id.return_value = None

        result = cli_runner.invoke(akvorag, ["sync-all"])
        assert result.exit_code == 1
        assert "Akvo RAG app token is not configured" in result.output

        # With token but missing KB ID
        mock_client.app_token = "tok_123"
        result2 = cli_runner.invoke(akvorag, ["sync-all"])
        assert result2.exit_code == 1
        assert "No target Knowledge Base ID configured" in result2.output


def test_cli_query_success(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client, \
         patch("ckanext.akvorag.cli._get_target_kb_id") as mock_get_kb_id:

        mock_client = MagicMock()
        mock_client.app_token = "tok_valid"
        mock_client.submit_chat_job.return_value = {
            "answer": "According to the water quality report, the pH level is 7.2.",
            "citations": [
                {"document_name": "water_quality_2026.pdf", "page": 4}
            ],
        }
        mock_get_client.return_value = mock_client
        mock_get_kb_id.return_value = 101

        result = cli_runner.invoke(akvorag, ["query", "What is the water pH level?"])

        assert result.exit_code == 0
        assert "AI Answer" in result.output
        assert "pH level is 7.2" in result.output
        assert "water_quality_2026.pdf (Page 4)" in result.output


def test_cli_query_failure(cli_runner):
    with patch("ckanext.akvorag.cli._get_configured_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.app_token = "tok_valid"
        mock_client.submit_chat_job.side_effect = AkvoRAGError("LLM Provider Timeout")
        mock_get_client.return_value = mock_client

        result = cli_runner.invoke(akvorag, ["query", "Hello?"])

        assert result.exit_code == 1
        assert "Query failed: LLM Provider Timeout" in result.output
