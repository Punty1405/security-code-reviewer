"""Generate test ZIP files and diffs from eval examples"""

import json
import zipfile
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def create_test_case_1():
    """Test case 1: Mixed CWE-89 and CWE-78"""
    
    # Load examples
    with open(str(BASE_DIR) + '/eval/ground_truth/cwe_89_sql_injection.json') as f:
        cwe_89 = json.load(f)
    with open(str(BASE_DIR) + '/eval/ground_truth/cwe_78_command_injection.json') as f:
        cwe_78 = json.load(f)
    
    # Pick examples
    examples = {
        'src/admin_routes.py': cwe_89[0],  # cwe_89_fastapi_001
        'src/network_utils.py': cwe_78[1],  # cwe_78_flask_002
        'src/product_routes.py': cwe_89[1], # cwe_89_flask_002
    }
    
    # Create temp directory
    test_dir = Path('test_data/test_case_1')
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create source directory
    src_dir = test_dir / 'src'
    src_dir.mkdir(exist_ok=True)
    
    # Write files
    for filepath, example in examples.items():
        file_path = test_dir / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(example['vulnerable_code'])
        print(f"Created: {file_path}")
    
    # Create ZIP
    zip_path = Path('test_data/test_case_1.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filepath in examples.keys():
            file_path = test_dir / filepath
            zipf.write(file_path, filepath)
    
    print(f"\nZIP created: {zip_path}")
    
    # Generate diff
    diff_lines = []
    for filepath, example in examples.items():
        vuln_line = example['vulnerability_line']
        code_lines = example['vulnerable_code'].split('\n')
        
        # Create minimal diff showing the vulnerable line
        diff_lines.append(f"diff --git a/{filepath} b/{filepath}")
        diff_lines.append(f"index 0000000..1111111 100644")
        diff_lines.append(f"--- a/{filepath}")
        diff_lines.append(f"+++ b/{filepath}")
        diff_lines.append(f"@@ -{vuln_line},1 +{vuln_line},1 @@")
        diff_lines.append(f"+{code_lines[vuln_line - 1]}")  # -1 for 0-indexing
        diff_lines.append("")
    
    diff_text = '\n'.join(diff_lines)
    diff_path = Path('test_data/test_case_1_diff.txt')
    diff_path.write_text(diff_text)
    
    print(f"Diff created: {diff_path}")
    print(f"\nExpected findings:")
    for filepath, example in examples.items():
        print(f"  - {filepath}: {example['cwe']} (line {example['vulnerability_line']})")
    
    return zip_path, diff_path

if __name__ == '__main__':
    print("Creating test case 1...")
    zip_path, diff_path = create_test_case_1()
    
    print(f"\n{'='*60}")
    print("Test data ready!")
    print(f"{'='*60}")
    print(f"\nUpload to FastAPI:")
    print(f"  ZIP file: {zip_path}")
    print(f"  Diff text: Copy from {diff_path}")