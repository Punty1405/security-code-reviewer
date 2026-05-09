import pytest
from unittest.mock import patch
from src.graph import build_graph
from tests.fixtures.test_data import create_test_zip

def test_full_dag_execution():
    """Test complete DAG execution end-to-end"""
    
    zip_path, diff_text = create_test_zip()
    
    # Mock LLM call to avoid API costs
    mock_llm_response = """{
  "validated_bandit": [{"bandit_id": "B602", "reasoning": "Valid shell=True issue"}],
  "rejected_bandit": [],
  "semantic_only": []
}"""
    
    with patch('src.nodes.semantic_node.call_llm') as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        # Build and run graph
        app = build_graph()
        result = app.invoke({
            "zip_path": zip_path,
            "diff_text": diff_text
        })
        
        # Verify all state keys exist
        assert "zip_path" in result
        assert "diff_text" in result
        assert "bandit_findings" in result
        assert "changed_files" in result
        assert "file_contents" in result
        assert "dependencies" in result
        assert "validated_bandit" in result
        assert "rejected_bandit" in result
        assert "semantic_only" in result
        assert "final_json" in result
        assert "final_markdown" in result
        
        # Verify Node 1 (Bandit) found issues
        assert len(result["bandit_findings"]) > 0
        assert result["bandit_findings"][0]["cwe_id"] == 78
        
        # Verify Node 2 (Context) parsed files
        assert "src/routes.py" in result["changed_files"]
        assert "src/routes.py" in result["file_contents"]
        
        # Verify Node 3 (Semantic) categorized findings
        assert len(result["validated_bandit"]) == 1
        
        # Verify Node 4 (Reconciler) formatted output
        assert "summary" in result["final_json"]
        assert "## Security Review" in result["final_markdown"]

def test_dag_with_no_vulnerabilities():
    """Test DAG with clean code (no findings)"""
    
    # Create ZIP with clean code
    import tempfile
    import zipfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    src_dir = temp_path / "src"
    src_dir.mkdir()
    
    clean_code = """def hello():
    return "Hello World"
"""
    
    (src_dir / "clean.py").write_text(clean_code)
    
    diff_text = """diff --git a/src/clean.py b/src/clean.py
--- a/src/clean.py
+++ b/src/clean.py
"""
    
    zip_path = temp_path / "clean.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(str(src_dir / "clean.py"), "src/clean.py")
    
    mock_llm_response = """{
  "validated_bandit": [],
  "rejected_bandit": [],
  "semantic_only": []
}"""
    
    with patch('src.nodes.semantic_node.call_llm') as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        app = build_graph()
        result = app.invoke({
            "zip_path": str(zip_path),
            "diff_text": diff_text
        })
        
        # Should complete with no findings
        assert result["bandit_findings"] == []
        assert result["final_json"]["summary"]["total_findings"] == 0
        assert "No security issues found" in result["final_markdown"]