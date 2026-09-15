#!/usr/bin/env python3
"""
Living Architecture Map AST Generator (BMAD-v6)
Deterministic, zero-token AST scanner that extracts models, routes, and components
to generate or update docs/architecture_map.md with live Mermaid diagrams.
"""

import ast
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

IGNORED_DIRS = {
    ".git", ".agent", ".agents", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".next", "dist", "build", "vendor",
    "storage", ".idea", ".vscode", "coverage", ".coverage"
}


class PythonASTScanner:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.models: Dict[str, Dict[str, Any]] = {}
        self.routes: List[Dict[str, Any]] = []

    def scan(self):
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        self._scan_file(file_path)
                    except Exception:
                        pass

    def _scan_file(self, file_path: Path):
        rel_path = file_path.relative_to(self.root_dir).as_posix()
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))
        except Exception:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._extract_class_model(node, rel_path)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._extract_route(node, rel_path)

    def _extract_class_model(self, node: ast.ClassDef, rel_path: str):
        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)

        is_model = any(b in {"Base", "SQLModel", "Model", "DeclarativeBase", "BaseModel", "Document", "Schema"} for b in base_names)
        is_sqlmodel_table = any(kw.arg == "table" and getattr(kw.value, "value", False) is True for kw in node.keywords)

        # Also accept classes with fields in model/schema/entity folders or files
        if not is_model and not is_sqlmodel_table:
            if not any(k in rel_path.lower() for k in ["model", "schema", "entity", "dto"]):
                return

        fields = []
        table_name = node.name.upper()

        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                            table_name = stmt.value.value.upper()

            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                field_name = stmt.target.id
                field_type = ast.unparse(stmt.annotation) if hasattr(ast, "unparse") else "Any"
                val_str = ast.unparse(stmt.value) if stmt.value and hasattr(ast, "unparse") else ""
                is_pk = "primary_key=True" in val_str or field_name == "id"
                fields.append({"name": field_name, "type": field_type, "is_pk": is_pk})

            elif isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and stmt.value:
                        val_str = ast.unparse(stmt.value) if hasattr(ast, "unparse") else ""
                        if any(k in val_str for k in ["Column(", "Field(", "mapped_column("]):
                            is_pk = "primary_key=True" in val_str or target.id == "id"
                            col_type = "string"
                            if "Integer" in val_str or "int" in val_str:
                                col_type = "int"
                            elif "DateTime" in val_str or "timestamp" in val_str.lower():
                                col_type = "timestamp"
                            elif "Boolean" in val_str or "bool" in val_str:
                                col_type = "bool"
                            elif "UUID" in val_str:
                                col_type = "uuid"
                            fields.append({"name": target.id, "type": col_type, "is_pk": is_pk})

        if fields:
            self.models[node.name] = {
                "table_name": table_name,
                "fields": fields,
                "file": rel_path
            }

    def _extract_route(self, node: ast.AST, rel_path: str):
        for dec in getattr(node, "decorator_list", []):
            dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else ""
            match = re.search(r'(?:router|app|api_router)\.(get|post|put|delete|patch)\((?:["\']([^"\']+)["\'])?', dec_str, re.IGNORECASE)
            if match:
                method = match.group(1).upper()
                path = match.group(2) if match.group(2) else "/"
                docstring = ast.get_docstring(node) or ""
                summary = docstring.strip().split("\n")[0] if docstring else getattr(node, "name", "")
                self.routes.append({
                    "method": method,
                    "path": path,
                    "handler": getattr(node, "name", ""),
                    "summary": summary,
                    "file": rel_path
                })


class TypeScriptRouteScanner:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.routes: List[Dict[str, Any]] = []

    def scan(self):
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                if file in ("route.ts", "route.js"):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.root_dir).as_posix()
                    parts = rel_path.split("/")
                    if "app" in parts:
                        idx = parts.index("app")
                        route_parts = parts[idx+1:-1]
                        route_url = "/" + "/".join(route_parts)
                    else:
                        route_url = "/" + "/".join(parts[:-1])

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            if re.search(rf'export\s+(?:async\s+)?function\s+{method}\b', content):
                                self.routes.append({
                                    "method": method,
                                    "path": route_url,
                                    "handler": method.lower(),
                                    "summary": f"Next.js App Route {method} {route_url}",
                                    "file": rel_path
                                })
                    except Exception:
                        pass


class LaravelRouteScanner:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.routes: List[Dict[str, Any]] = []

    def scan(self):
        routes_dir = self.root_dir / "routes"
        if not routes_dir.exists():
            return
        for file in ["api.php", "web.php"]:
            route_file = routes_dir / file
            if route_file.exists():
                try:
                    with open(route_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    prefix = "/api" if file == "api.php" else ""
                    pattern = r'Route::(get|post|put|delete|patch)\(\s*[\'"]([^\'"]+)[\'"]'
                    for match in re.finditer(pattern, content):
                        method = match.group(1).upper()
                        path = prefix + ("/" if not match.group(2).startswith("/") else "") + match.group(2)
                        self.routes.append({
                            "method": method,
                            "path": path,
                            "handler": "closure/controller",
                            "summary": f"Laravel Route {method} {path}",
                            "file": f"routes/{file}"
                        })
                except Exception:
                    pass


def detect_components(root_dir: Path) -> List[Dict[str, str]]:
    components = []
    for b_candidate in ["backend", "api", "server", "app"]:
        p = root_dir / b_candidate
        if p.exists() and p.is_dir():
            components.append({
                "name": "Backend API",
                "dir": f"{b_candidate}/",
                "responsibility": "Core backend services and API handlers"
            })
            break

    for f_candidate in ["frontend", "web", "client", "ui", "src"]:
        p = root_dir / f_candidate
        if p.exists() and p.is_dir():
            components.append({
                "name": "Frontend Web",
                "dir": f"{f_candidate}/",
                "responsibility": "User interface, client routing, and state"
            })
            break

    if (root_dir / "docs").exists():
        components.append({
            "name": "Documentation",
            "dir": "docs/",
            "responsibility": "System architecture, PRDs, LLDs, and specs"
        })

    if not components:
        components.append({
            "name": "Core Application",
            "dir": "./",
            "responsibility": "Primary workspace source code"
        })

    return components


def generate_mermaid_er(models: Dict[str, Dict[str, Any]]) -> str:
    if not models:
        return "```mermaid\nerDiagram\n    SYSTEM {\n        string status \"Ready\"\n    }\n```"

    lines = ["```mermaid", "erDiagram"]
    for model_name, data in models.items():
        table_name = data.get("table_name", model_name).upper()
        lines.append(f"    {table_name} {{")
        for f in data.get("fields", [])[:8]:
            ftype = f.get("type", "string").lower()
            if "int" in ftype:
                ftype = "int"
            elif "str" in ftype or "text" in ftype:
                ftype = "string"
            elif "bool" in ftype:
                ftype = "bool"
            elif "time" in ftype or "date" in ftype:
                ftype = "timestamp"
            elif "uuid" in ftype:
                ftype = "uuid"
            else:
                ftype = "string"

            pk_label = " PK" if f.get("is_pk") else ""
            lines.append(f"        {ftype} {f['name']}{pk_label}")
        lines.append("    }")

    lines.append("```")
    return "\n".join(lines)


def generate_architecture_map(root_dir: Path, output_file: Path):
    print(f"🔍 Scanning workspace AST at {root_dir}...")

    py_scanner = PythonASTScanner(root_dir)
    py_scanner.scan()

    ts_scanner = TypeScriptRouteScanner(root_dir)
    ts_scanner.scan()

    laravel_scanner = LaravelRouteScanner(root_dir)
    laravel_scanner.scan()

    all_routes = py_scanner.routes + ts_scanner.routes + laravel_scanner.routes
    models = py_scanner.models
    components = detect_components(root_dir)

    print(f"✅ Found {len(models)} database/schema models and {len(all_routes)} API routes.")

    existing_content = ""
    granular_lld_section = "- [ ] [Core System Architecture](docs/lld/project_lld.md) — Covers System Architecture & Foundation\n"
    spike_log_section = "| Spike Name | Branch | Retrospective PRD | Retrospective LLD | Sign-Off Date |\n|------------|--------|-------------------|-------------------|---------------|\n"

    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_content = f.read()

            lld_match = re.search(r'## 5\. Granular LLD Registry\s*\n\s*>.*?\n\n(.*?)(?=\n---\n|\n## |\Z)', existing_content, re.DOTALL)
            if lld_match and lld_match.group(1).strip():
                granular_lld_section = lld_match.group(1).strip() + "\n"

            spike_match = re.search(r'## Retrospective Spike Log.*?\n\s*>.*?\n\n(.*?)(?=\n---\n|\n## |\Z)', existing_content, re.DOTALL)
            if spike_match and spike_match.group(1).strip():
                spike_log_section = spike_match.group(1).strip() + "\n"
        except Exception:
            pass

    date_str = datetime.now().strftime("%Y-%m-%d")
    mermaid_er = generate_mermaid_er(models)

    component_rows = []
    for c in components:
        component_rows.append(f"| {c['name']} | `{c['dir']}` | {c['responsibility']} | `docs/lld/project_lld.md` |")
    component_table = "\n".join(component_rows)

    if all_routes:
        route_rows = []
        for r in all_routes[:50]:
            summary = r['summary'].replace("|", "-")
            route_rows.append(f"| `{r['method']}` | `{r['path']}` | {summary} | [`{r['file']}`]({r['file']}) |")
        routes_table = "\n".join(route_rows)
    else:
        routes_table = "| `GET` | `/health` | System health check endpoint | `app/main.py` |"

    content = f"""# System Architecture Map — Living Index 🗺️

> **Global Index & Shared Component Registry**
> Owner: Winston (Architect) & Paige (Tech Writer) | References: `docs/lld/`
> Status: `Living Document (AST Generated)` | Last Sync: {date_str}

---

## 1. System Summary & Components

| Component Name | Directory Location | Responsibility | Primary LLD |
|----------------|--------------------|----------------|-------------|
{component_table}

---

## 2. Global Database Schema (Entity-Relationship)

{mermaid_er}

---

## 3. Discovered API Routes & Endpoints Catalog

| Method | Path | Summary | Defined In |
|:-------|:-----|:--------|:-----------|
{routes_table}

---

## 4. Shared API Standards & Prefixes

**Standard Error Payload Format**:
```json
{{
  "success": false,
  "error": {{
    "code": "ERROR_CODE_NAME",
    "message": "Human readable reason",
    "details": {{}}
  }}
}}
```

---

## 5. Granular LLD Registry

> Index of all active Low-Level Designs.

{granular_lld_section}

---

## Retrospective Spike Log (Spike Retrofits)

> Record of experimental spikes merged into main with verified retrospective documentation.

{spike_log_section}
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✨ Architecture Map successfully written to: {output_file}")


if __name__ == "__main__":
    workspace_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    target_output = Path(sys.argv[2]) if len(sys.argv) > 2 else workspace_root / "docs" / "architecture_map.md"
    generate_architecture_map(workspace_root, target_output)
