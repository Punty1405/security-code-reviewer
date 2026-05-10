import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List
from src.graph import build_graph

def create_example_zip(example: Dict) -> tuple[str, str]:
    """
    Create ZIP and diff from ground truth example
    """

    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Create Source directory
    src_dir = temp_path / 'src'
    src_dir.mkdir(parents=True, exist_ok=True)

    # Writing vulnerable code to the file
    framework = example['framework']
    filename = f"{framework}_routes.py"
    code_file = src_dir / filename
    code_file.write_text(example['vulnerable_code'])


    # Create sample diff (to show file was added / modified)
    diff_text = f"""diff --git a/src/{filename} b/src/{filename}
new file mode 100644
--- /dev/null
+++ b/src/{filename}
@@ -0,0 +1,{len(example['vulnerable_code'].splitlines())} @@
+{chr(10).join(example['vulnerable_code'].splitlines())}
"""

    zip_path = temp_path / 'example.zip'
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(str(code_file), f"src/{filename}")
    
    return str(zip_path), diff_text


def run_agent_on_example(example: Dict, app) -> Dict:
    """
    Running agent on single example - return results
    """

    try:
        # Create example zip and diff text
        zip_path, diff_text = create_example_zip(example)

        # Run the agent
        result = app.invoke({
            'zip_path': zip_path,
            'diff_text': diff_text
        })

        return {
            'success': True,
            'bandit_findings': result['bandit_findings'],
            'validated_bandit': result['validated_bandit'],
            'rejected_bandit': result['rejected_bandit'],
            'semantic_only': result['semantic_only']
        }
    
    except Exception as e:
        print(f"Error running the example {example['id']}: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_eval(examples: List[Dict], max_examples: int=None) -> List[Dict]:
    """
    Run agent on all examples
    """

    if max_examples:
        examples = examples[:max_examples]
    
    print(f"Running eval on {len(examples)} examples...")

    app = build_graph()
    results = []

    for i, example in enumerate(examples, 1):
        print(f"    [{i}/{len(examples)}]: {example['id']}...", end=" ")

        result = run_agent_on_example(example, app)

        results.append({
            'example_id': example['id'],
            'cwe': example['cwe'],
            'example_line': example['vulnerability_line'],
            'agent_result': result
        })

        if result['success']:
            total_findings = (
                len(result['validated_bandit']) +
                len(result['semantic_only'])
            )

            print(f"    {total_findings} findings")
        else:
            print(" error")

    return results

