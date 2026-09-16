"""
Unit tests for AkvoRAGPlugin lifecycle hooks
"""

import os
import pytest
from unittest.mock import patch, MagicMock

import ckan.plugins.toolkit as toolkit
from ckanext.akvorag.plugin import (
    AkvoRAGPlugin,
    is_pdf_resource,
    get_resource_file_path,
    get_akvorag_client,
    get_configured_kb_id,
)


def test_is_pdf_resource():
    assert is_pdf_resource({"format": "PDF"}) is True
    assert is_pdf_resource({"format": "pdf"}) is True
    assert is_pdf_resource({"mimetype": "application/pdf"}) is True
    assert is_pdf_resource({"url": "https://example.com/report.pdf"}) is True
    assert is_pdf_resource({"format": "CSV"}) is False
    assert is_pdf_resource({"mimetype": "text/csv"}) is False
    assert is_pdf_resource({}) is False


def test_get_resource_file_path(tmp_path):
    res_id = "abc123def456"
    storage_dir = tmp_path / "resources" / res_id[0:3] / res_id[3:6]
    storage_dir.mkdir(parents=True)
    dummy_file = storage_dir / res_id[6:]
    dummy_file.write_bytes(b"%PDF dummy data")

    with patch.dict(toolkit.config, {"ckan.storage_path": str(tmp_path)}):
        resolved = get_resource_file_path({"id": res_id})
        assert resolved == str(dummy_file)


def test_get_resource_file_path_direct_upload(tmp_path):
    direct_file = tmp_path / "custom.pdf"
    direct_file.write_bytes(b"%PDF direct")
    resolved = get_resource_file_path({"id": "123", "upload_file": str(direct_file)})
    assert resolved == str(direct_file)


def test_get_resource_file_path_missing(tmp_path):
    with patch.dict(toolkit.config, {"ckan.storage_path": str(tmp_path)}):
        assert get_resource_file_path({"id": "nonexistent_id_12345"}) is None
        assert get_resource_file_path({}) is None


def test_get_akvorag_client():
    with patch.dict(toolkit.config, {"ckanext.akvorag.app_token": "tok_configured"}):
        client = get_akvorag_client()
        assert client is not None
        assert client.app_token == "tok_configured"

    with patch.dict(toolkit.config, {"ckanext.akvorag.app_token": ""}):
        with patch.dict(os.environ, {"AKVO_RAG_APP_TOKEN": ""}):
            assert get_akvorag_client() is None


def test_get_configured_kb_id():
    with patch.dict(toolkit.config, {"ckanext.akvorag.knowledge_base_id": "105"}):
        assert get_configured_kb_id() == 105

    with patch.dict(toolkit.config, {"ckanext.akvorag.knowledge_base_id": "invalid"}):
        assert get_configured_kb_id() is None


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
@patch("ckanext.akvorag.plugin.get_resource_file_path")
def test_after_resource_create_pdf(mock_get_path, mock_get_kb, mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.submit_upload_job.return_value = {"job_id": "job_123"}
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101
    mock_get_path.return_value = str(tmp_path / "water_report.pdf")

    plugin = AkvoRAGPlugin()
    data_dict = {
        "id": "res_001",
        "package_id": "pkg_001",
        "name": "Water Quality Report",
        "format": "PDF",
    }

    plugin.after_resource_create(context={}, data_dict=data_dict)

    mock_client.submit_upload_job.assert_called_once_with(
        file_path=str(tmp_path / "water_report.pdf"),
        filename="Water Quality Report.pdf",
        kb_id=101,
        callback_params={
            "ckan_resource_id": "res_001",
            "ckan_package_id": "pkg_001",
            "ckan_site_url": "http://localhost:5000",
        },
    )


@patch("ckanext.akvorag.plugin.get_akvorag_client")
def test_after_resource_create_csv_ignored(mock_get_client):
    plugin = AkvoRAGPlugin()
    data_dict = {"id": "res_002", "format": "CSV"}
    plugin.after_resource_create(context={}, data_dict=data_dict)
    mock_get_client.assert_not_called()


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_before_resource_delete(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    resource_to_delete = {"id": "res_001"}
    resources_list = [
        {"id": "res_001", "name": "water_survey.pdf", "format": "PDF"},
        {"id": "res_002", "name": "metadata.json", "format": "JSON"},
    ]

    plugin.before_resource_delete(context={}, resource=resource_to_delete, resources=resources_list)
    mock_client.delete_document_by_name.assert_called_once_with(kb_id=101, filename="water_survey.pdf")


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_after_resource_delete_with_list(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    # When CKAN core passes the list of remaining resources
    plugin.after_resource_delete(context={}, data_dict=[{"id": "res_002"}])
    mock_client.delete_document.assert_not_called()
    mock_client.delete_document_by_name.assert_not_called()


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_after_resource_delete_with_filename(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    plugin.after_resource_delete(context={}, data_dict={"id": "res_001", "name": "Report.pdf"})

    mock_client.delete_document_by_name.assert_called_once_with(kb_id=101, filename="Report.pdf")


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_after_resource_delete_with_only_id(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    plugin.after_resource_delete(context={}, data_dict={"id": "res_001"})

    mock_client.delete_document.assert_called_once_with(kb_id=101, doc_id="res_001")


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_delete_entity_package(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    mock_entity = MagicMock()
    res1 = MagicMock()
    res1.format = "pdf"
    res1.name = "annual_report.pdf"
    res2 = MagicMock()
    res2.format = "csv"
    res2.name = "data.csv"
    mock_entity.resources = [res1, res2]

    plugin.delete(mock_entity)
    mock_client.delete_document_by_name.assert_called_once_with(kb_id=101, filename="annual_report.pdf")


@patch("ckanext.akvorag.plugin.get_akvorag_client")
@patch("ckanext.akvorag.plugin.get_configured_kb_id")
def test_after_dataset_and_package_delete(mock_get_kb, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_get_kb.return_value = 101

    plugin = AkvoRAGPlugin()
    package_dict = {
        "id": "pkg_001",
        "resources": [{"id": "res_001", "name": "doc1.pdf"}, {"id": "res_002", "name": "doc2.pdf"}],
    }

    plugin.after_dataset_delete(context={}, data_dict=package_dict)
    assert mock_client.delete_document_by_name.call_count == 2

    plugin.after_package_delete(context={}, data_dict=package_dict)
    assert mock_client.delete_document_by_name.call_count == 4


def test_update_config():
    plugin = AkvoRAGPlugin()
    config = {}
    with patch("ckan.plugins.toolkit.add_template_directory") as mock_add_tmpl, \
         patch("ckan.plugins.toolkit.add_public_directory") as mock_add_pub, \
         patch("ckan.plugins.toolkit.add_resource") as mock_add_res:
        plugin.update_config(config)
        mock_add_tmpl.assert_called_once()
        mock_add_pub.assert_called_once()
        mock_add_res.assert_called_once()


def test_get_commands():
    plugin = AkvoRAGPlugin()
    cmds = plugin.get_commands()
    assert len(cmds) == 1
    assert cmds[0].name == "akvorag"

