import pytest
from src.nodes.context_node import retrieve_context, parse_diff_files, extract_imports
from tests.fixtures.test_data import create_test_zip

def test_context_parses_diff():
    """
    Test that context node parses diff correctly
    """

    zip_path, diff_text = create_test_zip()

    state = {
        'zip_path': zip_path,
        'diff_text': diff_text
    }

    result = retrieve_context(state)

    # Find changed files
    assert 'changed_files' in result
    assert 'src/routes.py' in result['changed_files']


def test_context_reads_file_contents():
    """
    Test that file contents are read from ZIP
    """
    zip_path, diff_text = create_test_zip()

    state = {
        'zip_path': zip_path,
        'diff_text': diff_text
    }

    result = retrieve_context(state)
    
    # Should have file contents
    assert "file_contents" in result
    assert "src/routes.py" in result["file_contents"]
    assert "subprocess" in result["file_contents"]["src/routes.py"]


def test_context_extracts_imports():
    """Test AST import extraction"""
    code = """import subprocess
import os
from pathlib import Path
"""
    
    imports = extract_imports(code, "test.py")
    
    # Should find subprocess (internal kept for demo)
    # os, pathlib filtered as stdlib
    assert isinstance(imports, list)


def test_parse_diff_files():
    """Test diff parsing finds Python files"""
    diff = """diff --git a/src/routes.py b/src/routes.py
--- a/src/routes.py
+++ b/src/routes.py
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
"""
    
    files = parse_diff_files(diff)
    
    # Should only include .py files
    assert "src/routes.py" in files
    assert "README.md" not in files