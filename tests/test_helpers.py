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


def test_akvorag_get_ws_url_default():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="https://akvo.ngrok.dev"), \
         patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        ws_url = helpers.akvorag_get_ws_url()
        assert ws_url == "wss://akvo.ngrok.dev/ws/chat"


def test_akvorag_get_ws_url_configured():
    with patch("ckan.plugins.toolkit.config.get", return_value="ws://custom.local:8000/ws/chat"):
        ws_url = helpers.akvorag_get_ws_url()
        assert ws_url == "ws://custom.local:8000/ws/chat"


def test_akvorag_get_ws_url_http():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="http://localhost:8000"), \
         patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        ws_url = helpers.akvorag_get_ws_url()
        assert ws_url == "ws://localhost:8000/ws/chat"


def test_akvorag_get_ws_url_bare_host():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="myrag.org"), \
         patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        ws_url = helpers.akvorag_get_ws_url()
        assert ws_url == "wss://myrag.org/ws/chat"


def test_akvorag_get_widget_config_default():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="https://akvo.ngrok.dev"), \
         patch("ckanext.akvorag.helpers.akvorag_get_ws_url", return_value="wss://akvo.ngrok.dev/ws/chat"), \
         patch("ckanext.akvorag.helpers.akvorag_get_kb_id", return_value=101), \
         patch("ckanext.akvorag.helpers.akvorag_is_configured", return_value=True), \
         patch("ckan.plugins.toolkit.config.get", return_value=None), \
         patch.dict("os.environ", {}, clear=True):
        cfg = helpers.akvorag_get_widget_config()
        assert cfg["endpoint"] == "https://akvo.ngrok.dev"
        assert cfg["wsUrl"] == "wss://akvo.ngrok.dev/ws/chat"
        assert cfg["knowledgeBaseId"] == 101
        assert cfg["isConfigured"] is True
        assert cfg["title"] == "Akvo AI"


def test_akvorag_get_widget_config_custom_title():
    with patch("ckanext.akvorag.helpers.akvorag_get_endpoint", return_value="https://akvo.ngrok.dev"), \
         patch("ckanext.akvorag.helpers.akvorag_get_ws_url", return_value="wss://akvo.ngrok.dev/ws/chat"), \
         patch("ckanext.akvorag.helpers.akvorag_get_kb_id", return_value=101), \
         patch("ckanext.akvorag.helpers.akvorag_is_configured", return_value=True), \
         patch("ckan.plugins.toolkit.config.get", return_value="Custom Bot"):
        cfg = helpers.akvorag_get_widget_config()
        assert cfg["title"] == "Custom Bot"
