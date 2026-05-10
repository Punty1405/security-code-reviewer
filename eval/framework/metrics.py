from typing import Dict, List

def extract_agent_cwes(agent_result: Dict) -> List[str]:
    """
    Extract CWE ID from agent findings
    """

    cwes = []

    # From validated bandit findings
    for finding in agent_result.get("validated_bandit", []):
        # map back to original bandit finding to get CWE
        # extracting from bandit_findings for now
        pass
    
    # From semantic-only findings
    for finding in agent_result.get('semantic_only', []):
        if 'cwe' in finding:
            cwes.append(finding['cwe'])

    
    # From Bandit findings directly
    for finding in agent_result.get("bandit_findings", []):
        if 'cwe_id' in finding:
            cwes.append(f"CWE-{finding['cwe_id']}")

    return cwes


def calculate_metrics(results: List[Dict]) -> Dict:
    """
    Calculate precision, recall and F1 score for eval results
    """

    # Separate successful and failed runs
    successful = [r for r in results if r['agent_result']['success']]
    failed = [r for r in results if not r['agent_result']['success']]

    # Calculating for Bandit baseline
    bandit_tp = 0
    bandit_fp = 0
    bandit_fn = 0

    # Calculate for Semantic viewer (validated + semantic_only)
    semantic_tp = 0
    semantic_fp = 0
    semantic_fn = 0

    for result in successful:
        expected_cwe = result['cwe']
        agent = result['agent_result']

        # for Bandit
        bandit_cwes = [f"CWE-{f['cwe_id']}" for f in agent.get('bandit_findings', [])]

        if expected_cwe in bandit_cwes:
            bandit_tp += 1
        else:
            bandit_fn += 1

        # Bandit finding wrong CWE - bandit false positives
        bandit_fp += len([c for c in bandit_cwes if c!=expected_cwe])

        # For Semntic
        semantic_cwes = []

        # Get the CWEs from validated bandit findings
        for v in agent.get('validated_bandit', []):
            # Mapping back to bandit finding to test_id
            bandit_id = v.get('bandit_id')
            matching_bandit = [f for f in agent.get('bandit_findings', []) if f.get("test_id")==bandit_id]

            if matching_bandit:
                semantic_cwes.append(f"CWE-{matching_bandit[0]['cwe_id']}")
        
        # Get the CWEs for semantic-only findings
        for s in agent.get('semantic_only', []):
            if 'cwe' in s:
                semantic_cwes.append(s['cwe'])

        
        if expected_cwe in semantic_cwes:
            semantic_tp += 1
        else:
            semantic_fn += 1

        # Semantic false positives
        semantic_fp += len([c for c in semantic_cwes if c!=expected_cwe])

    
    # calculate precision, recall and F1
    def calc_prf(tp, fp, fn):
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        return precision, recall, f1

    bandit_p, bandit_r, bandit_f1 = calc_prf(bandit_tp, bandit_fp, bandit_fn)
    semantic_p, semantic_r, semantic_f1 = calc_prf(semantic_tp, semantic_fp, semantic_fn)

    return {
        "total_examples": len(results),
        "successful_runs": len(successful),
        "failed_runs": len(failed),
        "bandit_baseline": {
            "true_positives": bandit_tp,
            "false_positives": bandit_fp,
            "false_negatives": bandit_fn,
            "precision": round(bandit_p, 3),
            "recall": round(bandit_r, 3),
            "f1": round(bandit_f1, 3)
        },
        "semantic_reviewer": {
            "true_positives": semantic_tp,
            "false_positives": semantic_fp,
            "false_negatives": semantic_fn,
            "precision": round(semantic_p, 3),
            "recall": round(semantic_r, 3),
            "f1": round(semantic_f1, 3)
        },
        "improvement": {
            "precision_gain": round(semantic_p - bandit_p, 3),
            "recall_gain": round(semantic_r - bandit_r, 3),
            "f1_gain": round(semantic_f1 - bandit_f1, 3)
        }
    }