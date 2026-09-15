#!/usr/bin/env python3
"""
BMAD v6 Spike-to-Production Retrofit Engine
Zero-token AST and Git diff parser that reverse-engineers experimental spike prototypes
into enterprise-grade documentation (Brief, PRD, LLD) and test skeletons.
"""

import os
import sys
import ast
import re
import subprocess
from pathlib import Path

def get_modified_files():
    """Get list of added or modified files from git diff against main or HEAD."""
    try:
        cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
        if not files:
            # Fallback to local unstaged/staged diff
            cmd = ["git", "diff", "--name-only", "HEAD"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
        return [f for f in files if os.path.exists(f)]
    except Exception as e:
        print(f"⚠️ Git diff error: {e}", file=sys.stderr)
        return []

def parse_python_file(filepath):
    """Parse a python file using AST to extract classes, functions, and endpoints."""
    classes = []
    functions = []
    routes = []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code, filename=filepath)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                bases = [b.id if isinstance(b, ast.Name) else (b.attr if isinstance(b, ast.Attribute) else "") for b in node.bases]
                classes.append({"name": node.name, "bases": bases, "doc": doc})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check for router decorator
                is_route = False
                route_path = ""
                route_method = ""
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        route_method = dec.func.attr.upper()
                        if dec.args and isinstance(dec.args[0], ast.Constant):
                            route_path = dec.args[0].value
                            is_route = True
                if is_route:
                    routes.append({"method": route_method, "path": route_path, "handler": node.name})
                else:
                    functions.append({"name": node.name, "doc": ast.get_docstring(node) or ""})
    except Exception as e:
        pass
    return {"classes": classes, "functions": functions, "routes": routes}

def generate_retrofit_artifacts(project_root, files):
    """Generate PRD, LLD, and test skeleton from parsed codebase."""
    parsed_data = {}
    for f in files:
        if f.endswith(".py"):
            parsed_data[f] = parse_python_file(f)
            
    docs_dir = Path(project_root) / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    brief_path = docs_dir / "briefs" / "retrofit_spike_brief.md"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    prd_path = docs_dir / "prd" / "retrofit_spike_prd.md"
    prd_path.parent.mkdir(parents=True, exist_ok=True)
    lld_path = docs_dir / "lld" / "retrofit_spike_lld.md"
    lld_path.parent.mkdir(parents=True, exist_ok=True)
    test_stub_path = Path(project_root) / "tests" / "test_retrofit_spike.py"
    test_stub_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Write Product Brief
    brief_content = f"""# Product Brief: Retrofitted Spike Feature 💡

## 1. Executive Summary
This document retrofits experimental spike code into a production-grade specification.
- **Source Files Analyzed**: {len(files)} files.

## 2. Identified Functional Touchpoints
"""
    for f, d in parsed_data.items():
        brief_content += f"### `{f}`\n"
        if d["routes"]:
            brief_content += "- **Endpoints**:\n"
            for r in d["routes"]:
                brief_content += f"  - `{r['method']} {r['path']}` -> `{r['handler']}`\n"
        if d["classes"]:
            brief_content += "- **Classes/Models**:\n"
            for c in d["classes"]:
                brief_content += f"  - `{c['name']}` ({', '.join(c['bases']) if c['bases'] else 'Base'})\n"
        brief_content += "\n"

    brief_path.write_text(brief_content, encoding="utf-8")

    # 2. Write PRD
    prd_content = f"""# Project PRD: Retrofitted Spike Feature 📋

## 1. Overview & Objective
Formalize the capabilities demonstrated in the spike prototype into verifiable Functional Requirements.

## 2. Functional Requirements (FR-xxx)
"""
    fr_counter = 1
    for f, d in parsed_data.items():
        for r in d["routes"]:
            prd_content += f"""### FR-{fr_counter:03d}: API Endpoint `{r['method']} {r['path']}`
- **Handler**: `{r['handler']}` in `{f}`
- **Acceptance Criteria**:
  - [ ] Must return 200 OK on valid payload.
  - [ ] Must enforce authentication & authorization.
  - [ ] Must validate payload schemas and return 422/400 on bad data.

"""
            fr_counter += 1

    prd_path.write_text(prd_content, encoding="utf-8")

    # 3. Write LLD
    lld_content = f"""# Low-Level Design (LLD): Retrofitted Spike Feature 🏗️

## 1. Component Architecture
```mermaid
classDiagram
"""
    for f, d in parsed_data.items():
        for c in d["classes"]:
            lld_content += f"    class {c['name']} {{\n"
            lld_content += f"        +source: {f}\n"
            lld_content += "    }\n"
    lld_content += "```\n\n## 2. API Contract Specifications\n"
    for f, d in parsed_data.items():
        for r in d["routes"]:
            lld_content += f"### `{r['method']} {r['path']}`\n- Handler: `{r['handler']}`\n- Source: `{f}`\n\n"

    lld_path.write_text(lld_content, encoding="utf-8")

    # 4. Generate Test Stubs
    test_content = """# Auto-generated Test Skeletons for Retrofitted Spike
import pytest

"""
    for f, d in parsed_data.items():
        for r in d["routes"]:
            test_content += f"""def test_{r['handler']}_success():
    \"\"\"Verify {r['method']} {r['path']} returns success code.\"\"\"
    # TODO: Implement full test assertions for {r['handler']}
    assert True

def test_{r['handler']}_validation_error():
    \"\"\"Verify {r['method']} {r['path']} handles invalid input.\"\"\"
    # TODO: Verify error response
    assert True

"""
    test_stub_path.write_text(test_content, encoding="utf-8")

    print("✅ Spike Retrofit Complete!")
    print(f"  📄 Brief: {brief_path}")
    print(f"  📋 PRD:   {prd_path}")
    print(f"  🏗️ LLD:   {lld_path}")
    print(f"  🧪 Tests: {test_stub_path}")

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    files = get_modified_files()
    if not files:
        # Fallback: scan current directory
        for r, d, f_list in os.walk(root):
            for fname in f_list:
                if fname.endswith(".py") and not "test" in fname and not ".venv" in r:
                    files.append(os.path.join(r, fname))
    generate_retrofit_artifacts(root, files[:30])

if __name__ == "__main__":
    main()
