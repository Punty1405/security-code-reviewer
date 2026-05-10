from openai import OpenAI
from typing import Dict, List
import json
from src.config import OPENAI_API_KEY
from src.schemas import AgentState

client=OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a security code reviewer specializing in Python vulnerabilities.

CRITICAL RULES:
1. VALIDATE = Real security issue that attackers can exploit
2. REJECT = False positive (safe code that Bandit flagged incorrectly)

Analyze code for:
- CWE-89: SQL Injection (f-strings in queries, string concatenation with user input)
- CWE-78: Command Injection (subprocess/os.popen with user input, shell=True)
- CWE-22: Path Traversal (open/pathlib with unsanitized user paths)

For each Bandit finding:
- If user input reaches dangerous sink WITHOUT sanitization → VALIDATE
- If code is provably safe (hardcoded values, proper parameterization) → REJECT
- Ignore Bandit's confidence/severity - analyze the actual code

Examples:
- subprocess.call(user_input, shell=True) → VALIDATE (command injection)
- f"SELECT * FROM users ORDER BY {sort_by}" → VALIDATE (SQL injection)
- cursor.execute("SELECT * WHERE id = ?", (user_id,)) → REJECT (parameterized)

Also find NEW vulnerabilities Bandit missed.

OUTPUT FORMAT (JSON only, no other text):
{{
  "validated_bandit": [
    {{"bandit_id": "test_id from Bandit", "reasoning": "why valid"}}
  ],
  "rejected_bandit": [
    {{"bandit_id": "test_id from Bandit", "reasoning": "why false positive"}}
  ],
  "semantic_only": [
    {{"cwe": "CWE-XX", "file": "filepath", "line": 123, "description": "issue description"}}
  ]
}}
"""

def semantic_review(state: AgentState) -> AgentState:
    """
    Node 3: LLM-based semantic review
    """
    print("Node 3: Running semantic review...")

    bandit_findings = state['bandit_findings']
    file_contents = state['file_contents']
    changed_files = state['changed_files']

    response = call_llm(bandit_findings, file_contents, changed_files)

    # parse the LLM response
    findings = parse_llm_response(response)

    return findings


def call_llm(bandit_findings: List[Dict], file_contents: Dict[str, str], changed_files: List[str]) -> str:
    """
    Call Open AI API
    """

    user_prompt = f"""
        FILES TO REVIEW:
        {json.dumps(file_contents, indent=2)}

        BANDIT FINDINGS TO VALIDATE:
        {json.dumps(bandit_findings, indent=2)}
        """

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


def parse_llm_response(response: str) -> Dict:
    """
    Parse LLM JSON Response
    """
    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        findings = json.loads(response.strip())

        return {
        'validated_bandit': findings.get('validated_bandit', []),
        'rejected_bandit': findings.get('rejected_bandit', []),
        'semantic_only': findings.get('semantic_only', [])
        }
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response: {e}")
        print(f"Response as follows: {response}")
        return {
            'validated_bandit': [],
            'rejected_bandit': [],
            'semantic_only': []
            }
