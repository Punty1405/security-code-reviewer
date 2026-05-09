import json
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent)

def convert_gemini_to_ground_truth(gemini_data, cwe, start_id):
    """Convert Gemini JSON to ground truth format"""
    
    # Handle both single object and array
    if isinstance(gemini_data, dict):
        examples = [gemini_data]
    else:
        examples = gemini_data
    
    ground_truth = []
    
    for i, ex in enumerate(examples, start=start_id):
        framework = ex['framework']
        entry = {
            "id": f"{cwe.lower().replace('-', '_')}_{framework}_{i:03d}",
            "cwe": cwe,
            "framework": framework,
            "severity": "high",
            "vulnerability_type": ex.get('endpoint_purpose', 'Path Traversal'),
            "vulnerable_code": ex['vulnerable_code'],
            "fixed_code": ex['fixed_code'],
            "vulnerability_line": ex['vulnerability_line'],
            "description": ex['description']
        }
        ground_truth.append(entry)
    
    return ground_truth

if __name__ == "__main__":
    all_examples = []
    
    # Process all uploaded files
    files = [
        'eval/gemini-code-1778359622569.json',
        'eval/gemini-code-1778359668691.json'
    ]
    
    current_id = 1
    for file_path in files:
        with open(file_path) as f:
            data = json.load(f)
        examples = convert_gemini_to_ground_truth(data, 'CWE-22', current_id)
        all_examples.extend(examples)
        current_id += len(examples)
    
    # Write to ground truth file
    with open('eval/ground_truth/cwe_22_path_traversal.json', 'w') as f:
        json.dump(all_examples, f, indent=2)
    
    print(f"Converted {len(all_examples)} CWE-22 examples")