from src.schemas import AgentState

def retrieve_context(state: AgentState) -> AgentState:
    """
    Node 2: Retrieve the code context (skeleton)
    """

    print("Node 2: Retrieving context...")

    # TODO: Parse diff, read files, AST parse for imports
    # For now, return empty context
    return {
        "changed_files": [],
        "file_contents": {},
        "dependencies": {}
    }