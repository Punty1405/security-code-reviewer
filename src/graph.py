from langgraph.graph import StateGraph, START, END
from src.schemas import AgentState
from src.nodes.bandit_node import run_bandit
from src.nodes.context_node import retrieve_context
from src.nodes.semantic_node import semantic_review
from src.nodes.reconciler_node import reconcile_findings

def build_graph():
    """
    Build the 4-node security review DAG
    """

    # Graph created
    graph = StateGraph(AgentState)

    # Nodes added
    graph.add_node("bandit", run_bandit)
    graph.add_node("context", retrieve_context)
    graph.add_node("semantic", semantic_review)
    graph.add_node("reconciler", reconcile_findings)

    # Edges added
    graph.add_edge(START, "bandit")
    graph.add_edge(START, "context")
    graph.add_edge("bandit", "semantic")
    graph.add_edge("context", "semantic")
    graph.add_edge("semantic", "reconciler")
    graph.add_edge("reconciler", END)

    # compile
    return graph.compile()

if __name__=='__main__':
    # Test the graph structure
    app = build_graph()

    # Run with dummy input
    result = app.invoke({
        "zip_path": "/tmp/test.zip",
        "diff_text": "dummy diff"
    })

    print("\n=== Graph executed successfully ===")
    print(f"Final state keys: {result.keys()}")

