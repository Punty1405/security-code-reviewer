import re
from pathlib import Path
from typing import Dict, List, Set
import zipfile
import tempfile
import ast
from src.schemas import AgentState

def retrieve_context(state: AgentState) -> AgentState:
    """
    Node 2: Retrieve the code Context and Dependencies
    """
    print("Node 2: Retrieving context...")

    diff_text = state['diff_text']
    zip_path = state['zip_path']

    # Parsing the diff to find all changed files
    changed_files = parse_diff_files(diff_text)
    print(f"Found {len(changed_files)} changed files")

    # Extract ZIP and read files
    file_contents = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Read each changed file
        for filepath in changed_files:
            full_path = temp_path / filepath

            if full_path.exists():
                file_contents[filepath] = full_path.read_text()
            else:
                print(f"Warning: {filepath} not found in ZIP")
        
        dependencies = parse_dependencies(file_contents)

    result = {
        "changed_files": changed_files,
        "file_contents": file_contents,
        "dependencies": dependencies
    }

    print(f"Node 2 returning: changed_files={len(changed_files)}, file_contents={len(file_contents)}, dependencies={len(dependencies)}")

    return result


def parse_diff_files(diff_text: str) -> List[str]:
    """
    Extract file paths from diff
    """
    # Diff format: diff --git a/path/to/file b/path/to/file
    # Or: +++ b/path/to/file

    files = set()

    # Match lines like: +++ b/src/routes.py
    for line in diff_text.split('\n'):
        line = line.strip()
        if line.startswith('+++') or line.startswith('---'):
            # Extract path after 'b/' or 'a/'
            match = re.search(r'[ab]/(.*)', line)
            if match:
                filepath = match.group(1)
                # Get only py files
                if filepath.endswith('.py'):
                    files.add(filepath)

    return sorted(list(files))


def parse_dependencies(file_contents: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Parse imports using AST
    """

    dependencies = {}

    for filepath, content in file_contents.items():
        imports = extract_imports(content, filepath)
        dependencies[filepath] = imports

    return dependencies


def extract_imports(code: str, source_file: str) -> List[str]:
    """
    Extract import statements from Python code
    """

    try:
        tree = ast.parse(code)
    except SyntaxError:
        print(f"Syntax error in {source_file} skipping")
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            if node.module: # Skip "from . import" cases
                imports.append(node.module)
    
    # Filter to internal imports only (skip stdlib and external packages)
    internal_imports = filter_internal_imports(imports, source_file)

    return internal_imports


def filter_internal_imports(imports: List[str], source_file: str) -> List[str]:
    """
    Keep only internal imports (files in the project)
    """
    internal = []

    # simple heuristic: relative imports or starts with project structure
    for imp in imports:
        
        # Skip stdlib (subprocess, os, sys etc.)
        if imp in ['subprocess', 'os', 'sys', 're', 'json', 'pathlib', 'typing']:
            continue

        # Skip common external packages
        if imp in ['requests', 'flask', 'fastapi', 'pydantic']:
            continue
        
        # Keep anything that 'looks' like project code
        # Ideally, we should check if the file exists in ZIP as well
        internal.append(imp)
    
    return internal
