"""
Template helper functions for ckanext-akvorag.
Exposes Akvo RAG configuration and widget metadata to Jinja templates.
"""

import os
import logging
from typing import Optional, Dict, Any

import ckan.plugins.toolkit as toolkit

logger = logging.getLogger(__name__)


def akvorag_get_endpoint() -> str:
    """Return the configured Akvo RAG base endpoint URL."""
    return (
        toolkit.config.get("ckanext.akvorag.base_url")
        or os.environ.get("AKVO_RAG_BASE_URL")
        or "https://akvo.ngrok.dev"
    ).rstrip("/")


def akvorag_get_kb_id() -> Optional[int]:
    """Return the configured target Knowledge Base ID, or None if unconfigured."""
    kb_id_str = (
        toolkit.config.get("ckanext.akvorag.knowledge_base_id")
        or os.environ.get("AKVO_RAG_KNOWLEDGE_BASE_ID")
    )
    if kb_id_str:
        try:
            return int(kb_id_str)
        except (ValueError, TypeError):
            logger.warning("Invalid ckanext.akvorag.knowledge_base_id: %s", kb_id_str)
    return None


def akvorag_get_app_token() -> Optional[str]:
    """Return the configured application access token, or None if unconfigured."""
    return (
        toolkit.config.get("ckanext.akvorag.app_token")
        or os.environ.get("AKVO_RAG_APP_TOKEN")
        or None
    )


def akvorag_is_configured() -> bool:
    """Check if Akvo RAG is properly configured with an endpoint and app token."""
    token = akvorag_get_app_token()
    endpoint = akvorag_get_endpoint()
    return bool(token and endpoint)


def akvorag_get_ws_url() -> str:
    """Return the configured or derived WebSocket URL for Akvo RAG real-time chat."""
    ws_url = (
        toolkit.config.get("ckanext.akvorag.ws_url")
        or os.environ.get("AKVO_RAG_WS_URL")
    )
    if ws_url:
        return ws_url.rstrip("/")
    endpoint = akvorag_get_endpoint()
    if endpoint.startswith("https://"):
        return endpoint.replace("https://", "wss://", 1) + "/ws/chat"
    elif endpoint.startswith("http://"):
        return endpoint.replace("http://", "ws://", 1) + "/ws/chat"
    return f"wss://{endpoint}/ws/chat"


def akvorag_get_widget_config() -> Dict[str, Any]:
    """Return a dictionary of widget configuration parameters suitable for serialization."""
    site_title = toolkit.config.get("ckan.site_title") or "CKAN Portal"
    return {
        "endpoint": akvorag_get_endpoint(),
        "wsUrl": akvorag_get_ws_url(),
        "knowledgeBaseId": akvorag_get_kb_id(),
        "isConfigured": akvorag_is_configured(),
        "title": f"{site_title} AI Assistant",
    }
