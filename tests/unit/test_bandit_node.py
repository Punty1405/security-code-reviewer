import pytest
from src.nodes.bandit_node import run_bandit, parse_bandit_findings
from tests.fixtures.test_data import create_test_zip

def test_bandit_finds_vulnerabilities():
    """
    Test that bandit finds CWE-78 vulnerabilities in test file
    """

    zip_path, diff_text = create_test_zip()

    state = {
        'zip_path': zip_path,
        'diff_text': diff_text
    }

    result = run_bandit(state)

    # At least 1 CWE-78 found
    assert 'bandit_findings' in result
    assert len(result['bandit_findings']) > 0

    # Structure validation
    finding = result['bandit_findings'][0]
    assert 'cwe_id' in finding
    assert 'test_id' in finding
    assert 'severity' in finding


def test_bandit_filters_to_target_cwes():
    """Test that only CWE-89/78/22 are kept"""
    raw_findings = [
        {"issue_cwe": {"id": 78}, "test_id": "B602"},  # Keep
        {"issue_cwe": {"id": 89}, "test_id": "B608"},  # Keep
        {"issue_cwe": {"id": 79}, "test_id": "B201"},  # Filter out
    ]

    filtered = parse_bandit_findings(raw_findings)

    assert len(filtered) == 2
    assert all(f['cwe_id'] in {78, 89, 22} for f in filtered)