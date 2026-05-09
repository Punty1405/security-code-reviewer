import pytest
from src.nodes.reconciler_node import reconcile_findings, format_json, format_markdown

def test_reconciler_formats_findings():
    """Test that reconciler formats findings correctly"""
    
    state = {
        "validated_bandit": [
            {"bandit_id": "B602", "reasoning": "Real issue"}
        ],
        "rejected_bandit": [
            {"bandit_id": "B404", "reasoning": "False positive"}
        ],
        "semantic_only": [
            {"cwe": "CWE-89", "file": "routes.py", "line": 10, "description": "SQL injection"}
        ]
    }
    
    result = reconcile_findings(state)
    
    # Should have both formats
    assert "final_json" in result
    assert "final_markdown" in result
    
    # Check JSON structure
    assert "summary" in result["final_json"]
    assert "findings" in result["final_json"]
    assert result["final_json"]["summary"]["total_findings"] == 2  # validated + semantic

def test_format_json_structure():
    """Test JSON formatting structure"""
    
    findings = [{"bandit_id": "B602", "reasoning": "test"}]
    rejected = [{"bandit_id": "B404", "reasoning": "fp"}]
    
    result = format_json(findings, rejected)
    
    assert "summary" in result
    assert result["summary"]["total_findings"] == 1
    assert result["summary"]["rejected_false_positives"] == 1
    assert result["findings"] == findings
    assert result["rejected"] == rejected

def test_format_markdown_with_findings():
    """Test Markdown formatting with findings"""
    
    findings = [{"bandit_id": "B602", "reasoning": "Real issue"}]
    rejected = [{"bandit_id": "B404", "reasoning": "False positive"}]
    
    md = format_markdown(findings, rejected)
    
    assert "## Security Review" in md
    assert "Issues Found" in md
    assert "B602" in md
    assert "False Positives Filtered" in md
    assert "B404" in md

def test_format_markdown_no_findings():
    """Test Markdown with no findings"""
    
    md = format_markdown([], [])
    
    assert "## Security Review" in md
    assert "No security issues found" in md

def test_format_markdown_semantic_finding():
    """Test Markdown formatting of semantic-only finding"""
    
    findings = [
        {"cwe": "CWE-89", "file": "routes.py", "line": 10, "description": "SQL injection"}
    ]
    
    md = format_markdown(findings, [])
    
    assert "CWE-89" in md
    assert "routes.py:10" in md
    assert "SQL injection" in md