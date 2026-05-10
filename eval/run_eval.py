"""
Main evaluation script - runs full eval pipeline
"""

import time
import json
from pathlib import Path

from eval.framework.loader import load_ground_truth
from eval.framework.runner import run_eval
from eval.framework.metrics import calculate_metrics
from eval.framework.report import generate_report

def main(max_examples: int=None):
    """
    Run complete evaluation pipeline
    """

    print("="*70)
    print("SECURITY CODE REVIEWER - EVALUATION PIPELINE")
    print("="*70)

    start = time.time()

    # Loading ground truth
    print("[1/4] Ground Truth Loading...")
    examples = load_ground_truth()
    print(f"     Loaded {len(examples)} examples...")

    # Run Evaluation
    print(f"[2/4] Running agent on examples ({max_examples} or all)...")
    results = run_eval(examples, max_examples)

    # Calculate metrics
    print("[3/4] Calculating Metrics...")
    metrics = calculate_metrics(results)

    # Save results
    results_path = 'eval/results.json'
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w') as f:
        json.dump({'metrics': metrics, 'results': results}, f, indent=2)
    print(f"        Results saved to {results_path}")

    # Generating the report
    print("[4/4] Generating the markdown report")
    report_path = generate_report(results_path)

    elapsed = time.time() - start

    # Summary
    print("\n" + "="*70)
    print(f"EVALUATION COMPLETE ({elapsed:.1f}s)")
    print("="*70)
    print(f"\nResults: {results_path}")
    print(f"Report:  {report_path}")
    print(f"\nKey Metrics:")
    print(f"  Bandit Baseline:    P={metrics['bandit_baseline']['precision']:.3f} R={metrics['bandit_baseline']['recall']:.3f} F1={metrics['bandit_baseline']['f1']:.3f}")
    print(f"  Semantic Reviewer:  P={metrics['semantic_reviewer']['precision']:.3f} R={metrics['semantic_reviewer']['recall']:.3f} F1={metrics['semantic_reviewer']['f1']:.3f}")
    print(f"  Improvement:        ΔP={metrics['improvement']['precision_gain']:+.3f} ΔR={metrics['improvement']['recall_gain']:+.3f} ΔF1={metrics['improvement']['f1_gain']:+.3f}")
    print()


if __name__=='__main__':
    import sys

    # argv as optional max limit on number of examples to be run
    max_examples = int(sys.argv[1]) if len(sys.argv) > 1 and isinstance(sys.argv[1], int) else None

    main(max_examples)