from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    # i/p
    zip_path: str
    diff_text: str

    # Node 1
    bandit_findings: List[Dict]

    # Node 2
    changed_files: List[str]
    file_contexts: List[str]
    dependencies: List[str]

    # Node 3
    validated_bandit: List[Dict]
    rejected_bandit: List[Dict]
    semantic_only: List[Dict]

    # Node 4
    final_json: Dict
    final_markdown: str

