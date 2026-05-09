from langgraph.graph import StateGraph, START, END
from src.schemas import AgentState
from src.nodes.bandit_node import run_bandit
from src.nodes.context_node import retrieve_context
from src.nodes.semantic_node import semantic_review
from src.nodes.reconciler_node import reconcile_findings
import json

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

    # Creating a proper diff
    test_diff = """diff --git a/src/routes.py b/src/routes.py
index 1234567..abcdefg 100644
--- a/src/routes.py
+++ b/src/routes.py
@@ -1,3 +1,4 @@
+import subprocess
 def process():
     pass
"""

    # Run with dummy input
    result = app.invoke({
        "zip_path": "/tmp/test.zip",
        "diff_text": test_diff
    })

    print("\n=== FINAL OUTPUT ===")
    print("\nJSON:")
    print(json.dumps(result['final_json'], indent=2))
    print("\nMarkdown:")
    print(result['final_markdown'])