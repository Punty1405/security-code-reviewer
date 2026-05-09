import tempfile
import zipfile
from pathlib import Path
import os

vulnerable_code = """
import subprocess

def process_command():
    user_input = input("Enter command: ")
    subprocess.call(user_input, shell=True)  # CWE-78
"""

diff_text = """diff --git a/src/routes.py b/src/routes.py
index 1234567..abcdefg 100644
--- a/src/routes.py
+++ b/src/routes.py
@@ -1,3 +1,6 @@
+import subprocess
 def process():
     pass
"""


def create_test_zip():
    """
    Create a test ZIP with vulnerable code
    """

    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Source file creation
    src_dir = temp_path / 'src'
    src_dir.mkdir(parents=True, exist_ok=True)

    routes_file = src_dir / 'routes.py'
    routes_file.write_text(vulnerable_code)
    
    diff_file = src_dir / 'diff.txt'
    diff_file.write_text(diff_text)

    # Verify files exist before zipping
    assert routes_file.exists(), f"routes.py not created at {routes_file}"
    assert diff_file.exists(), f"diff.txt not created at {diff_file}"

    # Create ZIP
    zip_path = temp_path / 'test.zip'

    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(str(routes_file), 'src/routes.py')
        zf.write(str(diff_file), 'diff.txt')
    
    return str(zip_path), diff_text
