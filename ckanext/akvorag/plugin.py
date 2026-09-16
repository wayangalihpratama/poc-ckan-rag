"""
CKAN Akvo RAG Synchronization Plugin
Hooks into CKAN's resource and package lifecycle to synchronize PDF files with Akvo RAG.
"""

import os
import logging
from typing import Any, Dict, Optional

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.akvorag.client import AkvoRAGClient, AkvoRAGError

logger = logging.getLogger(__name__)


def is_pdf_resource(resource: Dict[str, Any]) -> bool:
    """Check if the given resource dictionary represents a PDF document."""
    res_format = (resource.get("format") or "").strip().lower()
    mimetype = (resource.get("mimetype") or "").strip().lower()
    url = (resource.get("url") or "").strip().lower()

    if res_format == "pdf" or mimetype == "application/pdf" or url.endswith(".pdf"):
        return True
    return False


def get_resource_file_path(resource: Dict[str, Any]) -> Optional[str]:
    """Resolve the absolute on-disk path for an uploaded CKAN resource."""
    res_id = resource.get("id")
    if not res_id:
        return None

    # Check for direct upload_file path if populated in context
    direct_path = resource.get("upload_file")
    if direct_path and os.path.exists(direct_path):
        return direct_path

    storage_path = toolkit.config.get("ckan.storage_path", "/var/lib/ckan")
    
    # Standard CKAN path storage pattern: storage_path/resources/xxx/xxx/xxxxxxxx
    if len(res_id) >= 6:
        candidate_path = os.path.join(
            storage_path, "resources", res_id[0:3], res_id[3:6], res_id[6:]
        )
        if os.path.exists(candidate_path):
            return candidate_path

    # Fallback to direct resources/res_id pattern
    fallback_path = os.path.join(storage_path, "resources", res_id)
    if os.path.exists(fallback_path):
        return fallback_path

    return None


def get_akvorag_client() -> Optional[AkvoRAGClient]:
    """Instantiate AkvoRAGClient using CKAN configuration."""
    base_url = (
        toolkit.config.get("ckanext.akvorag.base_url")
        or os.environ.get("AKVO_RAG_BASE_URL")
        or "https://akvo.ngrok.dev"
    )
    app_token = (
        toolkit.config.get("ckanext.akvorag.app_token")
        or os.environ.get("AKVO_RAG_APP_TOKEN")
    )

    if not app_token:
        logger.warning(
            "Akvo RAG app_token is not configured. Document synchronization skipped."
        )
        return None

    return AkvoRAGClient(base_url=base_url, app_token=app_token)


def get_configured_kb_id() -> Optional[int]:
    """Retrieve configured Knowledge Base ID."""
    kb_id_str = (
        toolkit.config.get("ckanext.akvorag.knowledge_base_id")
        or os.environ.get("AKVO_RAG_KNOWLEDGE_BASE_ID")
    )
    if kb_id_str:
        try:
            return int(kb_id_str)
        except (ValueError, TypeError):
            logger.warning("Invalid knowledge_base_id configured: %s", kb_id_str)
    return None


class AkvoRAGPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    """
    Akvo RAG Synchronization Plugin.
    Implements IResourceController and IPackageController lifecycle hooks.
    """

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # ------------------------------------------------------------------
    # ITemplateHelpers
    # ------------------------------------------------------------------
    def get_helpers(self):
        """Register custom template helper functions."""
        from ckanext.akvorag import helpers
        return {
            "akvorag_get_endpoint": helpers.akvorag_get_endpoint,
            "akvorag_get_ws_url": helpers.akvorag_get_ws_url,
            "akvorag_get_kb_id": helpers.akvorag_get_kb_id,
            "akvorag_get_app_token": helpers.akvorag_get_app_token,
            "akvorag_is_configured": helpers.akvorag_is_configured,
            "akvorag_get_widget_config": helpers.akvorag_get_widget_config,
        }

    # ------------------------------------------------------------------
    # IClick
    # ------------------------------------------------------------------
    def get_commands(self):
        """Register click CLI command groups for Akvo RAG."""
        from ckanext.akvorag.cli import akvorag
        return [akvorag]

    # ------------------------------------------------------------------
    # IConfigurer
    # ------------------------------------------------------------------
    def update_config(self, config_: toolkit.CKANConfig):
        """Register template directory and update configuration."""
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("fanstatic", "akvorag")

    # ------------------------------------------------------------------
    # IResourceController Hooks
    # ------------------------------------------------------------------
    def after_resource_create(self, context: Dict[str, Any], data_dict: Dict[str, Any]):
        """Triggered immediately after a resource is created."""
        if not is_pdf_resource(data_dict):
            logger.debug("Resource %s is not a PDF. Skipping Akvo RAG sync.", data_dict.get("id"))
            return

        client = get_akvorag_client()
        kb_id = get_configured_kb_id()
        if not client or not kb_id:
            logger.info("Akvo RAG credentials or KB ID missing. Skipping upload sync for %s", data_dict.get("id"))
            return

        file_path = get_resource_file_path(data_dict)
        if not file_path:
            logger.warning("Could not resolve local file path for resource %s", data_dict.get("id"))
            return

        try:
            filename = data_dict.get("name") or data_dict.get("url") or "document.pdf"
            if not filename.lower().endswith(".pdf"):
                filename = f"{filename}.pdf"

            callback_params = {
                "ckan_resource_id": data_dict.get("id"),
                "ckan_package_id": data_dict.get("package_id"),
                "ckan_site_url": toolkit.config.get("ckan.site_url", "http://localhost:5000"),
            }

            logger.info("Submitting PDF upload job to Akvo RAG for resource: %s", data_dict.get("id"))
            job_result = client.submit_upload_job(
                file_path=file_path,
                filename=filename,
                kb_id=kb_id,
                callback_params=callback_params,
            )
            logger.info("Akvo RAG upload job accepted: %s", job_result.get("job_id"))
        except (AkvoRAGError, Exception) as e:
            logger.error("Failed to submit upload job to Akvo RAG for resource %s: %s", data_dict.get("id"), str(e))

    def after_resource_update(self, context: Dict[str, Any], data_dict: Dict[str, Any]):
        """Triggered after a resource is modified or re-uploaded."""
        # Re-index updated resource
        self.after_resource_create(context, data_dict)

    def _delete_resource_from_akvorag(self, resource_dict: Dict[str, Any]):
        """Helper to purge a CKAN resource from Akvo RAG."""
        if not isinstance(resource_dict, dict):
            return

        client = get_akvorag_client()
        kb_id = get_configured_kb_id()
        if not client or not kb_id:
            return

        res_id = resource_dict.get("id")
        candidates = [
            resource_dict.get("name"),
            resource_dict.get("url"),
            resource_dict.get("upload"),
        ]

        deleted = False
        for cand in candidates:
            if cand and isinstance(cand, str):
                filename = os.path.basename(cand).strip()
                if filename:
                    if not filename.lower().endswith(".pdf"):
                        filename = f"{filename}.pdf"
                    try:
                        logger.info("Purging resource %s (%s) from Akvo RAG Knowledge Base %s", res_id, filename, kb_id)
                        res = client.delete_document_by_name(kb_id=kb_id, filename=filename)
                        if res:
                            deleted = True
                            break
                    except (AkvoRAGError, Exception) as e:
                        logger.error("Failed to delete document %s from Akvo RAG: %s", filename, str(e))

        if not deleted and res_id:
            try:
                client.delete_document(kb_id=kb_id, doc_id=res_id)
            except Exception as e:
                logger.debug("Direct doc_id delete skipped or not found: %s", str(e))

    def before_resource_delete(
        self,
        context: Dict[str, Any],
        resource: Dict[str, Any],
        resources: Optional[Any] = None,
    ):
        """Triggered immediately before a resource is deleted from CKAN."""
        target_res = resource
        if resources and isinstance(resources, list):
            res_id = resource.get("id") if isinstance(resource, dict) else None
            for r in resources:
                if isinstance(r, dict) and r.get("id") == res_id:
                    target_res = r
                    break
        self._delete_resource_from_akvorag(target_res)

    def after_resource_delete(self, context: Dict[str, Any], data_dict: Any):
        """Triggered after a resource is deleted from CKAN."""
        if isinstance(data_dict, list):
            # CKAN core passes remaining resources list; before_resource_delete already purged it
            return
        elif isinstance(data_dict, dict):
            self._delete_resource_from_akvorag(data_dict)

    # ------------------------------------------------------------------
    # IPackageController Hooks
    # ------------------------------------------------------------------
    def delete(self, entity: Any):
        """
        CKAN IPackageController hook triggered when a package is deleted.
        entity is the SQLAlchemy Package object containing resources.
        """
        client = get_akvorag_client()
        kb_id = get_configured_kb_id()
        if not client or not kb_id:
            return

        resources = getattr(entity, "resources", []) or []
        for resource in resources:
            try:
                raw_format = getattr(resource, "format", "")
                raw_name = getattr(resource, "name", "")
                raw_url = getattr(resource, "url", "")

                res_format = raw_format.lower() if isinstance(raw_format, str) else ""
                res_name = raw_name if isinstance(raw_name, str) else ""
                res_url = raw_url if isinstance(raw_url, str) else ""

                if res_format == "pdf" or res_name.lower().endswith(".pdf") or res_url.lower().endswith(".pdf"):
                    filename = res_name or res_url
                    filename = os.path.basename(filename).strip()
                    if filename:
                        if not filename.lower().endswith(".pdf"):
                            filename = f"{filename}.pdf"
                        logger.info("Purging package resource %s from Akvo RAG KB %s", filename, kb_id)
                        client.delete_document_by_name(kb_id=kb_id, filename=filename)
            except (AkvoRAGError, Exception) as e:
                logger.error("Failed to delete package resource from Akvo RAG: %s", str(e))

    def after_dataset_delete(self, context: Dict[str, Any], data_dict: Dict[str, Any]):
        """Triggered after an entire dataset package is deleted in CKAN 2.9+."""
        resources = data_dict.get("resources") or []
        for resource in resources:
            self.after_resource_delete(context, resource)

    def after_package_delete(self, context: Dict[str, Any], data_dict: Dict[str, Any]):
        """Fallback alias for dataset deletion."""
        self.after_dataset_delete(context, data_dict)
