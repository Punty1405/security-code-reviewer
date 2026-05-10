# Security Code Reviewer - Evaluation Report

## Summary

| Metric | Value |
|--------|-------|
| Total Examples | 75 |
| Successful Runs | 75 |
| Failed Runs | 0 |
| Success Rate | 100.0% |

## Performance Comparison

### Bandit Baseline

| Metric | Value |
|--------|-------|
| True Positives | 46 |
| False Positives | 0 |
| False Negatives | 29 |
| **Precision** | **1.000** |
| **Recall** | **0.613** |
| **F1 Score** | **0.760** |

### Semantic Reviewer (LLM-based)

| Metric | Value |
|--------|-------|
| True Positives | 75 |
| False Positives | 2 |
| False Negatives | 0 |
| **Precision** | **0.974** |
| **Recall** | **1.000** |
| **F1 Score** | **0.987** |

### Improvement

| Metric | Gain |
|--------|------|
| Precision | -0.026 |
| Recall | +0.387 |
| F1 Score | +0.227 |

## Analysis by CWE Type

| CWE | Total | Bandit Found | Semantic Found | Bandit Recall | Semantic Recall |
|-----|-------|--------------|----------------|---------------|-----------------|
| CWE-22 | 25 | 0 | 25 | 0.0% | 100.0% |
| CWE-78 | 25 | 23 | 25 | 92.0% | 100.0% |
| CWE-89 | 25 | 23 | 25 | 92.0% | 100.0% |

## Key Findings

1. **Semantic reviewer achieved perfect recall (100%)** - caught all 75 vulnerabilities
2. **Bandit missed 29 cases** (38.7% of total)
3. **Recall improvement: +38.7 percentage points**
4. **Minimal precision cost: 2 false positives** (out of 77 total findings)

## Conclusion

The semantic reviewer (Architecture B: validate Bandit + find new) demonstrates significant value:
- **Perfect recall**: Catches all vulnerabilities including the 29 cases Bandit misses
- **High precision**: Maintains 97.4% precision with only 2 false positives
- **Strong F1 improvement**: +22.7 percentage points over Bandit baseline

The trade-off is extremely favorable for security review use cases where missing a vulnerability (false negative) is more costly than investigating a false positive.

### Architecture Validation

The parallel DAG architecture (Node 1: Bandit + Node 2: Context → Node 3: Semantic Review → Node 4: Reconcile) successfully achieves the design goal: augment static analysis with LLM reasoning to catch evasion techniques while maintaining high precision.
