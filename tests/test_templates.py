"""
Unit tests for template helper registration and snippet markup.
"""

from unittest.mock import MagicMock, patch
import pytest

from ckanext.akvorag.plugin import AkvoRAGPlugin
from ckanext.akvorag import helpers


def test_plugin_get_helpers():
    plugin = AkvoRAGPlugin()
    helpers_dict = plugin.get_helpers()

    assert "akvorag_get_endpoint" in helpers_dict
    assert "akvorag_get_ws_url" in helpers_dict
    assert "akvorag_get_kb_id" in helpers_dict
    assert "akvorag_get_app_token" in helpers_dict
    assert "akvorag_is_configured" in helpers_dict
    assert "akvorag_get_widget_config" in helpers_dict
    assert callable(helpers_dict["akvorag_get_endpoint"])
    assert callable(helpers_dict["akvorag_get_ws_url"])


def test_widget_snippet_html_structure():
    import os

    template_path = os.path.join(
        os.path.dirname(__file__),
        "../ckanext/akvorag/templates/akvorag/snippets/chat_widget.html"
    )
    assert os.path.exists(template_path)

    with open(template_path, "r") as f:
        content = f.read()

    assert "akvo-rag.css" in content
    assert "akvo-rag.js" in content
    assert "AkvoRAG.initChat" in content
    assert "h.akvorag_get_ws_url()" in content
