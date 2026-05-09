from typing import TypedDict, List, Dict, Annotated
import operator

class AgentState(TypedDict):
    # i/p
    zip_path: str
    diff_text: str

    # Node 1
    bandit_findings: Annotated[List[Dict], operator.add]

    # Node 2
    changed_files: Annotated[List[str], operator.add]
    file_contents: Annotated[Dict[str, str], operator.or_] # filepath -> content
    dependencies: Annotated[Dict[str, List[str]], operator.or_] # filepath -> imports

    # Node 3
    validated_bandit: Annotated[List[Dict], operator.add]
    rejected_bandit: Annotated[List[Dict], operator.add]
    semantic_only: Annotated[List[Dict], operator.add]

    # Node 4
    final_json: Dict
    final_markdown: str
