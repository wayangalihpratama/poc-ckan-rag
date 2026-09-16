"""
Akvo RAG Client Library
Interfaces with Akvo RAG's multi-tenant /api/v1/apps endpoints.
"""

import os
import re
import json
import logging
from typing import Any, Dict, List, Optional, Union
import requests

logger = logging.getLogger(__name__)


class AkvoRAGError(Exception):
    """Base exception for Akvo RAG API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AkvoRAGAuthError(AkvoRAGError):
    """Authentication or authorization error (401/403)."""
    pass


class AkvoRAGNotFoundError(AkvoRAGError):
    """Resource not found (404)."""
    pass


class AkvoRAGValidationError(AkvoRAGError):
    """Validation or bad request error (400/422)."""
    pass


class AkvoRAGClient:
    """Client for Akvo RAG Host Application APIs."""

    def __init__(
        self,
        base_url: str = "https://akvo.ngrok.dev",
        app_token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the Akvo RAG Client.

        :param base_url: Base URL of Akvo RAG instance (e.g. https://akvo.ngrok.dev)
        :param app_token: Application-scoped Bearer token (tok_...)
        :param timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.timeout = timeout

    def _get_headers(self, custom_token: Optional[str] = None) -> Dict[str, str]:
        """Construct authorization headers."""
        token = custom_token or self.app_token
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle HTTP responses and raise domain-specific exceptions."""
        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code in (200, 201, 202):
            return data

        error_message = (
            data.get("detail") or data.get("message") or response.text
            if isinstance(data, dict)
            else str(data)
        )

        if response.status_code in (401, 403):
            raise AkvoRAGAuthError(
                f"Akvo RAG Auth Error ({response.status_code}): {error_message}",
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code == 404:
            raise AkvoRAGNotFoundError(
                f"Akvo RAG Not Found ({response.status_code}): {error_message}",
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code in (400, 422):
            raise AkvoRAGValidationError(
                f"Akvo RAG Validation Error ({response.status_code}): {error_message}",
                status_code=response.status_code,
                response_data=data,
            )
        else:
            raise AkvoRAGError(
                f"Akvo RAG Request Failed ({response.status_code}): {error_message}",
                status_code=response.status_code,
                response_data=data,
            )

    def register_app(
        self,
        app_name: str,
        domain: str,
        superuser_token: str,
        default_chat_prompt: Optional[str] = None,
        chat_callback: Optional[str] = None,
        upload_callback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new Host Application using Superuser Admin credentials.
        Calls POST /api/v1/apps/register.
        """
        url = f"{self.base_url}/api/v1/apps/register"
        payload = {
            "app_name": app_name,
            "domain": domain,
            "default_chat_prompt": default_chat_prompt or "You are a helpful CKAN knowledge assistant.",
            "chat_callback": chat_callback or f"https://{domain}/api/3/action/akvorag_chat_callback",
            "upload_callback": upload_callback or f"https://{domain}/api/3/action/akvorag_upload_callback",
        }
        headers = self._get_headers(custom_token=superuser_token)
        headers["Content-Type"] = "application/json"

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        result = self._handle_response(response)
        
        # If token was returned, update local client token
        if isinstance(result, dict) and "access_token" in result:
            self.app_token = result["access_token"]

        return result

    def get_me(self) -> Dict[str, Any]:
        """
        Validate authentication and retrieve registered app metadata.
        Calls GET /api/v1/apps/me.
        """
        url = f"{self.base_url}/api/v1/apps/me"
        response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

    def list_knowledge_bases(self) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        List all accessible Knowledge Bases for the authenticated application.
        Calls GET /api/v1/apps/knowledge-bases.
        """
        url = f"{self.base_url}/api/v1/apps/knowledge-bases"
        response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

    def create_knowledge_base(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Knowledge Base.
        Calls POST /api/v1/apps/knowledge-bases.
        """
        url = f"{self.base_url}/api/v1/apps/knowledge-bases"
        payload = {"name": name, "description": description or ""}
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        return self._handle_response(response)

    def submit_upload_job(
        self,
        file_path: str,
        filename: Optional[str] = None,
        kb_id: Optional[int] = None,
        callback_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit an asynchronous document upload job.
        Calls POST /api/v1/apps/jobs.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for upload: {file_path}")

        url = f"{self.base_url}/api/v1/apps/jobs"
        actual_filename = filename or os.path.basename(file_path)

        payload_dict = {
            "job": "upload",
            "knowledge_base_id": kb_id,
            "callback_params": callback_params or {},
        }

        with open(file_path, "rb") as f:
            files = [
                ("files", (actual_filename, f, "application/pdf")),
            ]
            data = {"payload": json.dumps(payload_dict)}
            headers = self._get_headers()
            # Let requests set multipart boundary automatically
            response = requests.post(
                url,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )

        return self._handle_response(response)

    def submit_chat_job(
        self,
        prompt: str,
        kb_ids: List[int],
        chats: Optional[List[Dict[str, str]]] = None,
        callback_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit a chat/question answering job.
        Calls POST /api/v1/apps/jobs.
        """
        url = f"{self.base_url}/api/v1/apps/jobs"
        payload_dict = {
            "job": "chat",
            "knowledge_base_ids": kb_ids,
            "prompt": prompt,
            "chats": chats or [],
            "callback_params": callback_params or {},
        }
        data = {"payload": json.dumps(payload_dict)}
        headers = self._get_headers()
        response = requests.post(url, data=data, headers=headers, timeout=self.timeout)
        return self._handle_response(response)

    def list_documents(self, kb_id: int, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List documents in a Knowledge Base.
        Calls GET /api/v1/apps/documents?kb_id={kb_id}&search={search}.
        """
        url = f"{self.base_url}/api/v1/apps/documents"
        params = {"kb_id": kb_id}
        if search:
            params["search"] = search
        response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.timeout)
        result = self._handle_response(response)
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        elif isinstance(result, list):
            return result
        return []

    def delete_document(
        self,
        kb_id: int,
        doc_id: Optional[Union[int, str]] = None,
        document_id: Optional[Union[int, str]] = None,
    ) -> Dict[str, Any]:
        """
        Delete a document from a Knowledge Base by document ID.
        Calls DELETE /api/v1/apps/documents?kb_id={kb_id}&doc_id={doc_id}.
        """
        target_id = doc_id if doc_id is not None else document_id
        if target_id is None:
            raise AkvoRAGValidationError("Missing required document ID for deletion.")
        url = f"{self.base_url}/api/v1/apps/documents"
        params = {"kb_id": kb_id, "doc_id": target_id}
        response = requests.delete(url, params=params, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

    def delete_document_by_name(self, kb_id: int, filename: str) -> List[Dict[str, Any]]:
        """
        Find and delete documents from a Knowledge Base matching a filename.
        Supports exact match, case-insensitive match, and normalized alphanumeric matching.
        """
        clean_name = os.path.basename(filename).strip()
        docs = self.list_documents(kb_id=kb_id)

        def _normalize(s: str) -> str:
            stem = s.rsplit(".", 1)[0] if "." in s else s
            return re.sub(r"[^a-zA-Z0-9]", "", stem).lower()

        norm_target = _normalize(clean_name)
        results = []
        for doc in docs:
            doc_filename = os.path.basename(doc.get("file_name", "")).strip()
            norm_doc = _normalize(doc_filename)

            is_match = (
                doc_filename.lower() == clean_name.lower()
                or doc_filename.lower().endswith(clean_name.lower())
                or clean_name.lower().endswith(doc_filename.lower())
                or (norm_target and norm_target == norm_doc)
                or (
                    norm_target
                    and len(norm_target) >= 5
                    and (norm_target in norm_doc or norm_doc in norm_target)
                )
            )

            if is_match:
                doc_id = doc.get("id")
                if doc_id is not None:
                    res = self.delete_document(kb_id=kb_id, doc_id=doc_id)
                    results.append(res)
        return results
