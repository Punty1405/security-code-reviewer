"""Check eval metrics meet minimum thresholds"""
import json
import sys

with open('eval/results.json') as f:
    data = json.load(f)

metrics = data['metrics']['semantic_reviewer']

f1 = metrics['f1']
recall = metrics['recall']

if f1 < 0.95:
    print(f'❌ F1 {f1:.3f} below threshold 0.95')
    sys.exit(1)

if recall < 0.95:
    print(f'❌ Recall {recall:.3f} below threshold 0.95')
    sys.exit(1)

print(f'✓ Metrics pass: F1={f1:.3f}, Recall={recall:.3f}')