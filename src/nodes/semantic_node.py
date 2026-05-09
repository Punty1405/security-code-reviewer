from src.schemas import AgentState

def semantic_review(state: AgentState) -> AgentState:
    """
    Node 3: LLM-based semantic review (skeleton)
    """

    print("Node 3: Running semantic review...")

    # TODO: Call OpenAI, validate Bandit findings, find new issues
    # For now, return empty findings
    return {
        'validated_bandit': [],
        'rejected_bandit': [],
        'semantic_only': []
    }
