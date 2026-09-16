"""
CKAN Akvo RAG CLI Commands
Provides administrative commands for app registration, health status, bulk document sync, and querying.
"""

import sys
import logging
from typing import Optional, List

import click
import ckan.plugins.toolkit as toolkit

from ckanext.akvorag.client import AkvoRAGClient, AkvoRAGError
from ckanext.akvorag.plugin import is_pdf_resource, get_resource_file_path

logger = logging.getLogger(__name__)


def _get_configured_client(
    base_url_override: Optional[str] = None,
    app_token_override: Optional[str] = None,
) -> AkvoRAGClient:
    """Helper to get an initialized AkvoRAGClient from CKAN config or overrides."""
    base_url = (
        base_url_override
        or toolkit.config.get("ckanext.akvorag.base_url")
        or "https://akvo.ngrok.dev"
    )
    app_token = (
        app_token_override
        or toolkit.config.get("ckanext.akvorag.app_token")
        or None
    )
    return AkvoRAGClient(base_url=base_url, app_token=app_token)


def _get_target_kb_id(kb_id_override: Optional[int] = None) -> Optional[int]:
    """Helper to get target KB ID from parameter override or CKAN config."""
    if kb_id_override is not None:
        return kb_id_override
    kb_id_str = toolkit.config.get("ckanext.akvorag.knowledge_base_id")
    if kb_id_str:
        try:
            return int(kb_id_str)
        except ValueError:
            pass
    return None


@click.group()
def akvorag():
    """Akvo RAG management and synchronization CLI commands."""
    pass


@akvorag.command()
@click.option(
    "--admin-token",
    "-t",
    required=True,
    help="Akvo RAG superuser admin token for registering the host app.",
)
@click.option(
    "--app-name",
    "-n",
    default=None,
    help="Host application name (defaults to ckan.site_title or 'ckan-portal').",
)
@click.option(
    "--domain",
    "-d",
    default=None,
    help="Host domain name (defaults to ckan.site_url or 'localhost:5000').",
)
@click.option(
    "--base-url",
    "-u",
    default=None,
    help="Akvo RAG base URL (defaults to ckanext.akvorag.base_url or https://akvo.ngrok.dev).",
)
@click.option(
    "--kb-name",
    default=None,
    help="Name of default Knowledge Base to create (e.g. 'CKAN Knowledge Base').",
)
def register(
    admin_token: str,
    app_name: Optional[str],
    domain: Optional[str],
    base_url: Optional[str],
    kb_name: Optional[str],
):
    """Register this CKAN instance with Akvo RAG as an authorized client application."""
    site_title = toolkit.config.get("ckan.site_title", "CKAN Portal")
    site_url = toolkit.config.get("ckan.site_url", "localhost:5000")

    resolved_app_name = app_name or site_title or "ckan-portal"
    resolved_domain = (domain or site_url).replace("http://", "").replace("https://", "").strip("/")

    client = _get_configured_client(base_url_override=base_url)

    click.secho(f"[*] Registering app '{resolved_app_name}' with Akvo RAG at {client.base_url}...", fg="cyan")

    try:
        reg_result = client.register_app(
            app_name=resolved_app_name,
            domain=resolved_domain,
            superuser_token=admin_token,
        )
    except AkvoRAGError as err:
        click.secho(f"[!] Registration failed: {err}", fg="red", err=True)
        sys.exit(1)

    app_id = reg_result.get("app_id") or reg_result.get("id")
    access_token = reg_result.get("access_token")

    click.secho("\n[✓] App registered successfully!", fg="green", bold=True)
    click.echo(f"  App ID:       {app_id}")
    click.echo(f"  App Name:     {resolved_app_name}")
    click.echo(f"  Domain:       {resolved_domain}")
    click.echo(f"  Access Token: {access_token}")

    # Create initial Knowledge Base if requested
    kb_id = None
    if kb_name or resolved_app_name:
        target_kb_name = kb_name or f"{resolved_app_name} KB"
        click.secho(f"\n[*] Creating initial Knowledge Base '{target_kb_name}'...", fg="cyan")
        try:
            kb_res = client.create_knowledge_base(
                name=target_kb_name,
                description=f"Auto-generated knowledge base for {resolved_app_name}",
            )
            kb_id = kb_res.get("id") or kb_res.get("kb_id")
            click.secho(f"[✓] Knowledge Base created (ID: {kb_id})", fg="green")
        except AkvoRAGError as err:
            click.secho(f"[!] Warning: Failed to create initial knowledge base: {err}", fg="yellow")

    click.secho("\n--- Configuration Instructions ---", fg="yellow", bold=True)
    click.echo("Update your ckan.ini with the following credentials:")
    click.echo(f"  ckanext.akvorag.base_url = {client.base_url}")
    click.echo(f"  ckanext.akvorag.app_token = {access_token}")
    if kb_id:
        click.echo(f"  ckanext.akvorag.knowledge_base_id = {kb_id}")
    click.echo("----------------------------------\n")


@akvorag.command()
@click.option(
    "--base-url",
    "-u",
    default=None,
    help="Akvo RAG base URL override.",
)
@click.option(
    "--app-token",
    "-t",
    default=None,
    help="Akvo RAG app token override.",
)
def status(base_url: Optional[str], app_token: Optional[str]):
    """Check connectivity and credentials with Akvo RAG."""
    client = _get_configured_client(base_url_override=base_url, app_token_override=app_token)
    target_kb_id = _get_target_kb_id()

    click.secho(f"[*] Checking Akvo RAG status at {client.base_url}...", fg="cyan")

    if not client.app_token:
        click.secho(
            "[!] Error: No app token configured. Set 'ckanext.akvorag.app_token' in ckan.ini or run 'ckan akvorag register'.",
            fg="red",
            err=True,
        )
        sys.exit(1)

    try:
        me_info = client.get_me()
    except AkvoRAGError as err:
        click.secho(f"[!] Connection failed: {err}", fg="red", err=True)
        sys.exit(1)

    click.secho("\n[✓] Akvo RAG Connection: OK", fg="green", bold=True)
    click.echo(f"  App ID:            {me_info.get('app_id', me_info.get('id', 'N/A'))}")
    click.echo(f"  App Name:          {me_info.get('app_name', me_info.get('name', 'N/A'))}")
    click.echo(f"  Status:            {me_info.get('status', 'active')}")
    click.echo(f"  Target KB ID:      {target_kb_id or 'Not Configured'}")

    # List Knowledge Bases
    try:
        kbs = client.list_knowledge_bases()
        kb_list = kbs if isinstance(kbs, list) else kbs.get("knowledge_bases", kbs.get("items", []))
        click.secho(f"\nAccessible Knowledge Bases ({len(kb_list)}):", fg="cyan", bold=True)
        for kb in kb_list:
            kb_item_id = kb.get("id") or kb.get("kb_id")
            kb_item_name = kb.get("name") or "Unnamed"
            is_target = " [ACTIVE TARGET]" if target_kb_id and str(target_kb_id) == str(kb_item_id) else ""
            click.echo(f"  • [{kb_item_id}] {kb_item_name}{is_target}")
    except AkvoRAGError as err:
        click.secho(f"[!] Could not list knowledge bases: {err}", fg="yellow")


@akvorag.command(name="sync-all")
@click.option(
    "--kb-id",
    "-k",
    type=int,
    default=None,
    help="Target Knowledge Base ID (defaults to ckanext.akvorag.knowledge_base_id).",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Force re-sync of all PDF resources.",
)
def sync_all(kb_id: Optional[int], force: bool):
    """Scan all datasets in CKAN and synchronize PDF files to Akvo RAG."""
    client = _get_configured_client()
    target_kb_id = _get_target_kb_id(kb_id_override=kb_id)

    if not client.app_token:
        click.secho("[!] Error: Akvo RAG app token is not configured.", fg="red", err=True)
        sys.exit(1)

    if not target_kb_id:
        click.secho("[!] Error: No target Knowledge Base ID configured.", fg="red", err=True)
        sys.exit(1)

    click.secho(f"[*] Starting bulk sync to Akvo RAG Knowledge Base [{target_kb_id}]...", fg="cyan")

    try:
        packages = toolkit.get_action("package_list")({}, {})
    except Exception as err:
        click.secho(f"[!] Failed to list CKAN packages: {err}", fg="red", err=True)
        sys.exit(1)

    total_datasets = len(packages)
    total_resources = 0
    pdf_count = 0
    synced_count = 0
    skipped_count = 0
    error_count = 0

    for pkg_id in packages:
        try:
            pkg = toolkit.get_action("package_show")({}, {"id": pkg_id})
        except Exception as err:
            logger.warning("Could not fetch dataset %s: %s", pkg_id, err)
            continue

        resources: List[dict] = pkg.get("resources", [])
        total_resources += len(resources)

        for res in resources:
            if not is_pdf_resource(res):
                skipped_count += 1
                continue

            pdf_count += 1
            res_id = res.get("id")
            res_name = res.get("name") or res.get("filename") or f"{res_id}.pdf"
            file_path = get_resource_file_path(res)

            if not file_path:
                click.secho(f"  [!] Missing file on disk for PDF resource: {res_name} ({res_id})", fg="yellow")
                error_count += 1
                continue

            try:
                click.echo(f"  [*] Uploading {res_name} ({res_id})...")
                client.submit_upload_job(
                    file_path=file_path,
                    filename=res_name,
                    kb_id=target_kb_id,
                    callback_params={
                        "ckan_resource_id": res_id,
                        "ckan_package_id": pkg.get("id"),
                        "source": "ckan_sync_all",
                    },
                )
                synced_count += 1
            except AkvoRAGError as err:
                click.secho(f"  [!] Failed to sync {res_name}: {err}", fg="red")
                error_count += 1

    click.secho("\n--- Bulk Sync Summary ---", fg="green", bold=True)
    click.echo(f"  Datasets Scanned:   {total_datasets}")
    click.echo(f"  Total Resources:    {total_resources}")
    click.echo(f"  PDFs Identified:    {pdf_count}")
    click.echo(f"  Successfully Synced: {synced_count}")
    click.echo(f"  Skipped (Non-PDF):  {skipped_count}")
    click.echo(f"  Errors / Missing:   {error_count}")
    click.echo("-------------------------\n")


@akvorag.command()
@click.argument("prompt")
@click.option(
    "--kb-id",
    "-k",
    type=int,
    default=None,
    help="Target Knowledge Base ID (defaults to ckanext.akvorag.knowledge_base_id).",
)
def query(prompt: str, kb_id: Optional[int]):
    """Query the Akvo RAG Knowledgebase directly from the CLI."""
    client = _get_configured_client()
    target_kb_id = _get_target_kb_id(kb_id_override=kb_id)

    if not client.app_token:
        click.secho("[!] Error: Akvo RAG app token is not configured.", fg="red", err=True)
        sys.exit(1)

    kb_ids = [target_kb_id] if target_kb_id else None

    click.secho(f"[*] Querying Akvo RAG (KB: {target_kb_id or 'All'})...", fg="cyan")
    click.echo(f"Prompt: {prompt}\n")

    try:
        response = client.submit_chat_job(prompt=prompt, kb_ids=kb_ids)
    except AkvoRAGError as err:
        click.secho(f"[!] Query failed: {err}", fg="red", err=True)
        sys.exit(1)

    answer = response.get("answer") or response.get("response") or response.get("content") or str(response)
    click.secho("--- AI Answer ---", fg="green", bold=True)
    click.echo(answer)

    citations = response.get("citations") or response.get("sources") or []
    if citations:
        click.secho("\n--- Sources / Citations ---", fg="cyan", bold=True)
        for cite in citations:
            doc_name = cite.get("document_name") or cite.get("filename") or cite.get("title") or "Unknown Document"
            page = cite.get("page")
            page_info = f" (Page {page})" if page else ""
            click.echo(f"  • {doc_name}{page_info}")
    click.echo("-----------------\n")

