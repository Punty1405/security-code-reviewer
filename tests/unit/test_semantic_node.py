import pytest
from unittest.mock import patch, MagicMock
from src.nodes.semantic_node import semantic_review, parse_llm_response

def test_semantic_review_with_mock_llm():
    """Test semantic review with mocked LLM response"""
    
    state = {
        "bandit_findings": [
            {"test_id": "B602", "issue_text": "shell=True", "cwe_id": 78}
        ],
        "file_contents": {"src/routes.py": "import subprocess"},
        "changed_files": ["src/routes.py"]
    }
    
    # Mock LLM response
    mock_response = """{
  "validated_bandit": [{"bandit_id": "B602", "reasoning": "Real issue"}],
  "rejected_bandit": [],
  "semantic_only": []
}"""
    
    with patch('src.nodes.semantic_node.call_llm') as mock_llm:
        mock_llm.return_value = mock_response
        
        result = semantic_review(state)
        
        # Should have categorized findings
        assert "validated_bandit" in result
        assert "rejected_bandit" in result
        assert "semantic_only" in result
        assert len(result["validated_bandit"]) == 1

def test_parse_llm_response_valid_json():
    """Test parsing valid LLM JSON response"""
    response = """{
  "validated_bandit": [{"bandit_id": "B602", "reasoning": "test"}],
  "rejected_bandit": [],
  "semantic_only": []
}"""
    
    result = parse_llm_response(response)
    
    assert len(result["validated_bandit"]) == 1
    assert result["validated_bandit"][0]["bandit_id"] == "B602"

def test_parse_llm_response_with_markdown_fences():
    """Test parsing JSON with markdown code fences"""
    response = """```json
{
  "validated_bandit": [],
  "rejected_bandit": [],
  "semantic_only": []
}
```"""
    
    result = parse_llm_response(response)
    
    assert result["validated_bandit"] == []

def test_parse_llm_response_invalid_json():
    """Test handling of invalid JSON"""
    response = "This is not JSON"
    
    result = parse_llm_response(response)
    
    # Should return empty findings on error
    assert result["validated_bandit"] == []
    assert result["rejected_bandit"] == []
    assert result["semantic_only"] == []