"""
Unit tests for AkvoRAGClient
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import requests

from ckanext.akvorag.client import (
    AkvoRAGClient,
    AkvoRAGError,
    AkvoRAGAuthError,
    AkvoRAGNotFoundError,
    AkvoRAGValidationError,
)


@pytest.fixture
def client():
    return AkvoRAGClient(base_url="https://akvo.ngrok.dev", app_token="tok_test_12345")


def test_client_init():
    client_slash = AkvoRAGClient(base_url="https://akvo.ngrok.dev///", app_token="tok_abc")
    assert client_slash.base_url == "https://akvo.ngrok.dev"
    assert client_slash.app_token == "tok_abc"
    headers = client_slash._get_headers()
    assert headers["Authorization"] == "Bearer tok_abc"


@patch("requests.post")
def test_register_app_success(mock_post):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "app_id": "app_123",
        "client_id": "ac_456",
        "access_token": "tok_new_registered_789",
        "scopes": ["jobs.write", "kb.read", "kb.write", "apps.read"],
        "knowledge_bases": [{"knowledge_base_id": 101, "is_default": True}],
    }
    mock_post.return_value = mock_response

    client = AkvoRAGClient(base_url="https://akvo.ngrok.dev")
    result = client.register_app(
        app_name="ckan_portal",
        domain="localhost:5000",
        superuser_token="super_admin_secret",
    )

    assert result["app_id"] == "app_123"
    assert result["access_token"] == "tok_new_registered_789"
    assert client.app_token == "tok_new_registered_789"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://akvo.ngrok.dev/api/v1/apps/register"
    assert kwargs["headers"]["Authorization"] == "Bearer super_admin_secret"


@patch("requests.post")
def test_register_app_unauthorized(mock_post):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid admin token"}
    mock_post.return_value = mock_response

    client = AkvoRAGClient(base_url="https://akvo.ngrok.dev")
    with pytest.raises(AkvoRAGAuthError) as exc_info:
        client.register_app(
            app_name="ckan_portal",
            domain="localhost:5000",
            superuser_token="wrong_token",
        )
    assert "Akvo RAG Auth Error (401)" in str(exc_info.value)


@patch("requests.get")
def test_get_me_success(mock_get, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "app_id": "app_123",
        "app_name": "ckan_portal",
        "status": "active",
    }
    mock_get.return_value = mock_response

    me = client.get_me()
    assert me["app_name"] == "ckan_portal"
    assert me["status"] == "active"
    mock_get.assert_called_once_with(
        "https://akvo.ngrok.dev/api/v1/apps/me",
        headers={"Accept": "application/json", "Authorization": "Bearer tok_test_12345"},
        timeout=30,
    )


@patch("requests.get")
def test_list_knowledge_bases(mock_get, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"knowledge_base_id": 101, "name": "CKAN Default KB", "is_default": True}
    ]
    mock_get.return_value = mock_response

    kbs = client.list_knowledge_bases()
    assert len(kbs) == 1
    assert kbs[0]["knowledge_base_id"] == 101


@patch("requests.post")
def test_create_knowledge_base(mock_post, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "knowledge_base_id": 102,
        "name": "Water Management KB",
        "description": "Reports on water quality",
    }
    mock_post.return_value = mock_response

    kb = client.create_knowledge_base(name="Water Management KB", description="Reports on water quality")
    assert kb["knowledge_base_id"] == 102
    assert kb["name"] == "Water Management KB"


@patch("requests.post")
def test_submit_upload_job_success(mock_post, client, tmp_path):
    # Create temporary PDF file
    test_pdf = tmp_path / "report.pdf"
    test_pdf.write_bytes(b"%PDF-1.4 test document content")

    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "job_id": "job_upload_999",
        "status": "PENDING",
    }
    mock_post.return_value = mock_response

    result = client.submit_upload_job(
        file_path=str(test_pdf),
        filename="custom_report.pdf",
        kb_id=101,
        callback_params={"ckan_resource_id": "res-123", "ckan_package_id": "pkg-456"},
    )

    assert result["job_id"] == "job_upload_999"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://akvo.ngrok.dev/api/v1/apps/jobs"
    payload_sent = json.loads(kwargs["data"]["payload"])
    assert payload_sent["job"] == "upload"
    assert payload_sent["knowledge_base_id"] == 101
    assert payload_sent["callback_params"]["ckan_resource_id"] == "res-123"


def test_submit_upload_job_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        client.submit_upload_job(
            file_path="/non/existent/path/to/missing.pdf",
            kb_id=101,
        )


@patch("requests.post")
def test_submit_chat_job_success(mock_post, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "job_id": "job_chat_111",
        "response": "Water quality was optimal in 2024.",
        "citations": [{"document_name": "report.pdf", "page_number": 1, "snippet": "optimal"}],
    }
    mock_post.return_value = mock_response

    res = client.submit_chat_job(
        prompt="What is the water quality status?",
        kb_ids=[101],
        chats=[{"role": "user", "content": "Hi"}],
    )

    assert res["response"] == "Water quality was optimal in 2024."
    mock_post.assert_called_once()


@patch("requests.get")
def test_list_documents_success(mock_get, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total": 2,
        "data": [
            {"id": 1, "file_name": "report.pdf"},
            {"id": 2, "file_name": "data.pdf"},
        ],
    }
    mock_get.return_value = mock_response

    res = client.list_documents(kb_id=101, search="report.pdf")
    assert len(res) == 2
    assert res[0]["file_name"] == "report.pdf"
    mock_get.assert_called_once_with(
        "https://akvo.ngrok.dev/api/v1/apps/documents",
        params={"kb_id": 101, "search": "report.pdf"},
        headers={"Accept": "application/json", "Authorization": "Bearer tok_test_12345"},
        timeout=30,
    )


@patch("requests.delete")
def test_delete_document_success(mock_delete, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "DELETED", "document_id": 244}
    mock_delete.return_value = mock_response

    res = client.delete_document(kb_id=101, doc_id=244)
    assert res["status"] == "DELETED"
    mock_delete.assert_called_once_with(
        "https://akvo.ngrok.dev/api/v1/apps/documents",
        params={"kb_id": 101, "doc_id": 244},
        headers={"Accept": "application/json", "Authorization": "Bearer tok_test_12345"},
        timeout=30,
    )


def test_delete_document_by_name(client):
    with patch.object(client, "list_documents") as mock_list, \
         patch.object(client, "delete_document") as mock_delete:
        mock_list.return_value = [
            {"id": 10, "file_name": "test_report.pdf"},
            {"id": 20, "file_name": "other_file.pdf"},
        ]
        mock_delete.return_value = {"success": True}

        results = client.delete_document_by_name(kb_id=101, filename="test_report.pdf")
        assert len(results) == 1
        mock_delete.assert_called_once_with(kb_id=101, doc_id=10)


def test_delete_document_by_name_normalized(client):
    with patch.object(client, "list_documents") as mock_list, \
         patch.object(client, "delete_document") as mock_delete:
        mock_list.return_value = [
            {"id": 99, "file_name": "Hydroponics-Manual-COMFSM__2___1_-1.pdf"},
        ]
        mock_delete.return_value = {"success": True}

        results = client.delete_document_by_name(
            kb_id=101, filename="Hydroponics-Manual-COMFSM (2) (1)-1.pdf"
        )
        assert len(results) == 1
        mock_delete.assert_called_once_with(kb_id=101, doc_id=99)


@patch("requests.get")
def test_error_handling_not_found(mock_get, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Knowledge base not found"}
    mock_get.return_value = mock_response

    with pytest.raises(AkvoRAGNotFoundError) as exc_info:
        client.get_me()
    assert "Akvo RAG Not Found (404)" in str(exc_info.value)


@patch("requests.post")
def test_error_handling_validation_error(mock_post, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 422
    mock_response.json.return_value = {"detail": [{"loc": ["body", "domain"], "msg": "field required"}]}
    mock_post.return_value = mock_response

    with pytest.raises(AkvoRAGValidationError) as exc_info:
        client.create_knowledge_base(name="")
    assert "Akvo RAG Validation Error (422)" in str(exc_info.value)


@patch("requests.get")
def test_error_handling_generic_server_error(mock_get, client):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 500
    mock_response.json.return_value = {"message": "Internal Server Error"}
    mock_get.return_value = mock_response

    with pytest.raises(AkvoRAGError) as exc_info:
        client.get_me()
    assert "Akvo RAG Request Failed (500)" in str(exc_info.value)
