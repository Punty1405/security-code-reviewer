import json
from typing import Dict, List
from src.schemas import AgentState

def reconcile_findings(state: AgentState) -> AgentState:
    """
    Node 4: Reconcile and format output
    """
    print("Node 4: Reconciling findings...")

    validated = state['validated_bandit']
    rejected = state['rejected_bandit']
    semantic = state['semantic_only']

    all_findings = validated + semantic

    # Format as JSON
    final_json = format_json(all_findings, rejected)

    # Frmat as Markdown
    final_markdown = format_markdown(all_findings, rejected)

    print(f"Final output: {len(all_findings)} real findings, {len(rejected)} rejected")

    return {
        'final_json': final_json,
        'final_markdown': final_markdown
    }
    

def format_json(findings: List[Dict], rejected: List[Dict]) -> Dict:
    """
    Format findings as structured JSON
    """

    return {
        "summary": {
            "total_findings": len(findings),
            "rejected_false_positives": len(rejected)
        },
        "findings": findings,
        "rejected": rejected
    }


def format_markdown(findings: List[Dict], rejected: List[Dict]) -> str:
    """
    Format findings as Markdown PR Comment
    """

    if not findings and not rejected:
        return "## Security Review\n\nNo security issues found."
    
    md = "## Security Review\n\n"
    
    # Real findings
    if findings:
        md += f"### Issues Found ({len(findings)})\n\n"
        for i, finding in enumerate(findings, 1):
            if "bandit_id" in finding:
                md += f"**{i}. Bandit {finding['bandit_id']}**\n"
                md += f"- **Reasoning:** {finding['reasoning']}\n\n"
            else:
                md += f"**{i}. {finding['cwe']}**\n"
                md += f"- **File:** `{finding['file']}:{finding['line']}`\n"
                md += f"- **Description:** {finding['description']}\n\n"
    
    # Rejected findings
    if rejected:
        md += f"### False Positives Filtered ({len(rejected)})\n\n"
        for finding in rejected:
            md += f"- **{finding['bandit_id']}:** {finding['reasoning']}\n"
    
    return md
