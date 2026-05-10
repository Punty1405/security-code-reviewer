import json
from pathlib import Path
from typing import List, Dict

def load_ground_truth(cwe_types=None) -> List[Dict]:
    """
    Load ground truth examples from JSON files
    """

    ground_truth_dir = Path('eval/ground_truth')

    if cwe_types is None:
        cwe_types = ['CWE-89', 'CWE-78', 'CWE-22']

    all_examples = []

    file_map = {
            "CWE-89": "cwe_89_sql_injection.json",
            "CWE-78": "cwe_78_command_injection.json",
            "CWE-22": "cwe_22_path_traversal.json"
        }

    for cwe in cwe_types:
        file_path = ground_truth_dir / file_map[cwe]

        if not file_path.exists():
            print(f"Warning: {file_path} not found")
            continue
        
        with open(file_path, 'r') as f:
            examples = json.load(f)
            all_examples.extend(examples)
        
    print(f"Loaded {len(all_examples)} ground truth examples")
    return all_examples


def create_test_case(example: Dict) -> Dict:
    """
    Convert ground truth example to test case format
    """
    return {
        'id': example['id'],
        'cwe': example['cwe'],
        'framework': example['framework'],
        'code': example['code'],
        'expected_finding': {
            'cwe': example['cwe'],
            'line': example['line'],
            'description': example['description']
        }
    }