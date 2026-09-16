"""
Unit tests for ckanext-akvorag Jinja template helpers.
"""

from unittest.mock import patch
import pytest

from ckanext.akvorag import helpers


def test_akvorag_get_endpoint_default():
    with patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        endpoint = helpers.akvorag_get_endpoint()
        assert endpoint == "https://akvo.ngrok.dev"


def test_akvorag_get_endpoint_configured():
    with patch("ckan.plugins.toolkit.config.get", return_value="https://custom.akvo.org/"):
        endpoint = helpers.akvorag_get_endpoint()
        assert endpoint == "https://custom.akvo.org"


def test_akvorag_get_kb_id_configured():
    with patch("ckan.plugins.toolkit.config.get", return_value="105"):
        kb_id = helpers.akvorag_get_kb_id()
        assert kb_id == 105


def test_akvorag_get_kb_id_missing():
    with patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        kb_id = helpers.akvorag_get_kb_id()
        assert kb_id is None


def test_akvorag_get_kb_id_invalid():
    with patch("ckan.plugins.toolkit.config.get", return_value="not-a-number"):
        kb_id = helpers.akvorag_get_kb_id()
        assert kb_id is None


def test_akvorag_get_app_token():
    with patch("ckan.plugins.toolkit.config.get", return_value="tok_test_secret"):
        token = helpers.akvorag_get_app_token()
        assert token == "tok_test_secret"


def test_akvorag_is_configured_true():
    with patch("ckanext.akvorag.helpers.akvorag_get_app_token", return_value="tok_123"), \
         patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="https://akvo.ngrok.dev"):
        assert helpers.akvorag_is_configured() is True


def test_akvorag_is_configured_false():
    with patch("ckanext.akvorag.helpers.akvorag_get_app_token", return_value=None):
        assert helpers.akvorag_is_configured() is False


def test_akvorag_get_widget_config():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="https://akvo.ngrok.dev"), \
         patch("ckanext.akvorag.helpers.akvorag_get_kb_id", return_value=101), \
         patch("ckanext.akvorag.helpers.akvorag_is_configured", return_value=True), \
         patch("ckan.plugins.toolkit.config.get", return_value="My Portal"):
        cfg = helpers.akvorag_get_widget_config()
        assert cfg["endpoint"] == "https://akvo.ngrok.dev"
        assert cfg["knowledgeBaseId"] == 101
        assert cfg["isConfigured"] is True
        assert "My Portal" in cfg["title"]
