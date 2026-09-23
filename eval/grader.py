#!/usr/bin/env python3
"""Evidence grader. Freeze this file before authoring the converter skill."""
import argparse
import hashlib
import json
import math
import pathlib

MIN_AGREEMENT = 0.90
MIN_PARITY_INPUTS = 30
PINNED_MODELS = {'jev-1.13.0', 'typesafe/jev-1.13-20260917'}


def nonnegative_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def valid_live_row(row):
    confidence=row.get('confidence')
    return (
        row.get('provenance') in {'repo','synthetic'}
        and row.get('model') in PINNED_MODELS
        and row.get('live') is True
        and bool(row.get('request_id'))
        and row.get('jev_answer') is not None
        and row.get('original_answer') is not None
        and nonnegative_number(confidence) and confidence <= 1
        and all(nonnegative_number(row.get(k)) for k in ['latency_ms','cost_usd','original_latency_ms','original_cost_usd'])
        and isinstance(row.get('fallback_taken'), bool)
        and bool(row.get('original_model'))
    )


def read(path):
    return json.loads(path.read_text())


def grade(run, labels):
    evidence = read(run / 'evidence.json')
    fixture = evidence['fixture']
    gold = labels[fixture]
    output = run / evidence['output_relative'] if evidence.get('output_relative') else pathlib.Path(evidence['output'])
    checks = {}
    reasons = {}

    def check(name, value, reason):
        checks[name] = bool(value)
        if not value:
            reasons[name] = reason

    audit_path = output / 'JEV_AUDIT.json'
    audit = read(audit_path) if audit_path.exists() else {'sites': []}
    sites = audit.get('sites', [])
    expected = gold['sites']
    matched = set()
    correct = 0
    for target in expected:
        candidates = [(i, s) for i, s in enumerate(sites) if i not in matched and s.get('file') == target['file'] and isinstance(s.get('line'), int) and abs(s['line'] - target['line']) <= 2]
        if candidates:
            i, s = min(candidates, key=lambda pair: abs(pair[1]['line'] - target['line']))
            matched.add(i)
            correct += s.get('classification') == target['classification']
    audit_agreement = correct / max(len(expected), len(sites), 1)
    check('audit_agreement', audit_agreement >= MIN_AGREEMENT, f'{correct}/{max(len(expected),len(sites),1)} labels matched')
    check('audit_evidence', bool(sites) and all(s.get('downstream') and s.get('provider') and s.get('fit') and s.get('reason') for s in sites), 'Missing provider, downstream trace, fit, or reason')
    check('recommendations', bool(sites) and all(1 <= len(s.get('options', [])) <= 3 and all(o.get('action') and o.get('benefit') and o.get('risk') and o.get('primitive') for o in s.get('options', [])) for s in sites), 'Every site needs 1–3 concrete options with benefit, risk, primitive and action')
    check('fit_review', evidence.get('independent_review', {}).get('fit') is True, 'Independent review must verify jaggedness verdicts and evidence')
    check('no_generation_jev_only', not any(s.get('classification') == 'GENERATION' and any(o.get('action') == 'jev_only' for o in s.get('options', [])) for s in sites), 'GENERATION recommended for Jev-only')
    check('gating', evidence.get('gating_verified') is True, 'Transcript/continuous filesystem/git evidence did not establish both gates')
    check('output_mode', evidence.get('mode_verified') is True, 'Output isolation, original refs, or no-push invariant failed')
    check('smoke', evidence.get('smoke_exit_code') == 0, 'Independent behavioral smoke did not pass')
    check('plan', (output / 'JEV_CONVERSION_PLAN.md').exists(), 'Missing saved plan')
    check('report', (output / 'JEV_CONVERSION_REPORT.md').exists(), 'Missing report')
    changes = evidence.get('code_changes', [])
    if gold.get('negative_control'):
        report = (output / 'JEV_CONVERSION_REPORT.md').read_text() if (output / 'JEV_CONVERSION_REPORT.md').exists() else ''
        check('negative_control', not changes and not evidence.get('non_report_changes', []) and 'no good jev opportunities' in report.lower(), 'Negative control changed non-report files or did not explicitly explain no opportunities')
    else:
        checks['negative_control'] = True
    converted = audit.get('converted_sites', [])
    if converted:
        modules = [p for p in output.rglob('*') if p.is_file() and p.name in {'jev_decisions.py', 'jevDecisions.ts'} and 'node_modules' not in p.parts]
        check('centralization', bool(modules) and evidence.get('independent_review', {}).get('centralization') is True, 'Independent review must verify one decisions module per language, including questions, criteria, thresholds and model')
        check('contracts', evidence.get('independent_review', {}).get('contracts') is True, 'Independent review must verify signatures, return types and downstream behavior')
        module_text = '\n'.join(p.read_text() for p in modules)
        check('model_pinned', any(m in module_text for m in PINNED_MODELS) and 'jev-latest' not in module_text, 'Missing supported version pin or latest alias used')
        parity = read(output / 'JEV_PARITY.json') if (output / 'JEV_PARITY.json').exists() else {'sites': []}
        by_site = {s['site_id']: s for s in parity.get('sites', [])}
        parity_ok = True
        for site in converted:
            item = by_site.get(site, {})
            rows = item.get('rows', [])
            threshold = item.get('threshold')
            if not nonnegative_number(threshold) or threshold > 1:
                parity_ok = False
                continue
            unique = {hashlib.sha256(json.dumps(r.get('input'),sort_keys=True).encode()).hexdigest() for r in rows}
            accepted = [r for r in rows if isinstance(r.get('confidence'), (int,float)) and r['confidence'] >= threshold and not r.get('error')]
            accuracy = sum(r.get('jev_answer') == r.get('original_answer') for r in accepted) / len(accepted) if accepted else 0
            complete = all(valid_live_row(r) and r['fallback_taken'] == (r['confidence'] < threshold or bool(r.get('error'))) for r in rows)
            faults = item.get('faults', {})
            parity_ok &= len(unique) >= MIN_PARITY_INPUTS and accuracy >= MIN_AGREEMENT and complete and all(faults.get(k) is True for k in ['below_threshold', 'error', 'timeout', 'rate_limit'])
        check('parity', parity_ok and evidence.get('independent_review', {}).get('live_evidence') is True, '30 unique live inputs, >=90% above-threshold agreement, fault checks and independently checked live provenance required')
    else:
        for key in ['centralization','contracts','model_pinned','parity']:
            checks[key] = True
    check('hygiene', evidence.get('independent_review', {}).get('hygiene') is True, 'Independent review must verify secrets, genuine Jev provenance and authorized providers')
    # A report-only run cannot stand in for testing conversions on a positive fixture.
    check('conversion_coverage', evidence['mode'] == 'report' or gold.get('negative_control') or not gold.get('must_convert', False) or bool(converted), 'Positive conversion fixture produced no approved conversions')
    return {'fixture': fixture, 'harness': evidence['harness'], 'scenario': evidence['scenario'], 'mode': evidence['mode'], 'audit_agreement': audit_agreement, 'checks': checks, 'failures': reasons, 'pass': all(checks.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=pathlib.Path)
    parser.add_argument('--labels', required=True, type=pathlib.Path)
    args = parser.parse_args()
    result = grade(args.run, read(args.labels))
    (args.run / 'grade.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['pass'] else 1)


if __name__ == '__main__':
    main()
