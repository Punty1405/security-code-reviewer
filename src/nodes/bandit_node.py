import subprocess
import json
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List
from src.schemas import AgentState


def run_bandit(state: AgentState) -> AgentState:
    """
    Node 1: Execute static analysis on the code
    """
    print("Node 1: Running Bandit...")

    zip_path = state['zip_path']

    # Extract zip file to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)

        # Find all the py files in src/ directory
        src_dir = temp_path / 'src'
        if not src_dir.exists():
            print("Warning: no src/ directory in ZIP")
            return {"bandit_findings": []}

        python_files = list(src_dir.rglob("*.py"))
        if not python_files:
            print("Warning: no python files found")
            return {"bandit_findings": []}
        
        print(f"Found {len(python_files)} Python files")

        findings = run_bandit_analysis(python_files)

        return {
            "bandit_findings": findings
        }

def run_bandit_analysis(file_paths: List[Path]) -> List[Dict]:
    """
    Run Bandit analysis and parse the results
    """
    try:
        # Run Bandit with JSON output
        cmd = ['bandit', '-f', 'json', '-r'] + [str(f) for f in file_paths]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False #Bandit returns non-zero if issues found
        )

        # Parsing JSON output
        bandit_output = json.loads(result.stdout)

        # Extract findings from results array
        raw_findings = bandit_output.get('results', [])

        print(f"Bandit found {len(raw_findings)} issues")

        # Parse and filter findings
        findings = parse_bandit_findings(raw_findings)

        return findings
    
    except subprocess.CalledProcessError as e:
        print(f"Bandit execution failed: {e}")
        return []
    except json.JSONDecoderError as e:
        print(f"Failed to parse Bandit JSON: {e}")
        return []

def parse_bandit_findings(raw_findings: List[Dict]) -> List[Dict]:
    """
    Parse the raw Bandit Findings and filter for CWE-89 / 78 / 22
    """
    TARGET_CWES = {78, 89, 22} # Command Injection, SQL Injection, Path Traversal

    filtered_findings = []

    for finding in raw_findings:
        # Extract Issue ID
        cwe_info = finding.get("issue_cwe", {})
        cwe_id = cwe_info.get("id") if cwe_info else None

        # Filter to target CWEs only
        if cwe_id not in TARGET_CWES:
            continue
        
        parsed = {
            "filename": finding.get("filename"),
            "line_number": finding.get("line_number"),
            "issue_text": finding.get("issue_text"),
            "severity": finding.get("issue_severity"),
            "confidence": finding.get("issue_confidence"),
            "test_id": finding.get("test_id"),
            "cwe_id": cwe_id,
        }

        filtered_findings.append(parsed)

    print(f"Filtered to {len(filtered_findings)} findings (CWE-89/78/22 only)")
    return filtered_findings