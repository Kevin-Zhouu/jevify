"""Recompute metrics from recorded live rows; Python 3.10+. No inference."""
import json
import math
import statistics
from pathlib import Path
root = Path(__file__).resolve().parent.parent
path = root / 'JEV_PARITY.json'
evidence = json.loads(path.read_text())
rows = evidence['sites'][0]['rows']
def summarize(rows):
    def percentile(key, q):
        return sorted(r[key] for r in rows)[math.ceil(len(rows) * q) - 1]
    curve = []
    for threshold in [0, .5, .7, .8, .9, .95, 1]:
        accepted = [r for r in rows if r['confidence'] >= threshold]
        curve.append(dict(threshold=threshold, accepted=len(accepted), agreement=sum(r['jev_answer'] == r['original_answer'] for r in accepted) / len(accepted) if accepted else None, fallback_fraction=1-len(accepted)/len(rows)))
    return dict(n=len(rows), raw_agreement=sum(r['jev_answer'] == r['original_answer'] for r in rows)/len(rows), curve=curve,
        jev_p50_ms=percentile('latency_ms', .5), jev_p95_ms=percentile('latency_ms', .95),
        original_p50_ms=percentile('original_latency_ms', .5), original_p95_ms=percentile('original_latency_ms', .95),
        mean_jev_cost_usd=statistics.mean(r['cost_usd'] for r in rows),
        mean_original_cost_usd=statistics.mean(r['original_cost_usd'] for r in rows),
        expected_cascade_cost_usd=statistics.mean(r['cost_usd'] + r['fallback_taken'] * r['original_cost_usd'] for r in rows),
        expected_cascade_latency_ms=statistics.mean(r['latency_ms'] + r['fallback_taken'] * r['original_latency_ms'] for r in rows),
        mean_original_latency_ms=statistics.mean(r['original_latency_ms'] for r in rows))
evidence['metrics'] = {name: summarize(group) for name, group in [('all', rows), ('calibration', [r for r in rows if r['split']=='calibration']), ('confirmation', [r for r in rows if r['split']=='confirmation'])]}
path.write_text(json.dumps(evidence, indent=2)+'\n')
