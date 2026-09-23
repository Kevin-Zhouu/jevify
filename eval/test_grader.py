"""Adversarial evidence checks, not model-quality evaluations."""
import json
import pathlib
import tempfile
import unittest

from grader import grade, valid_live_row
from suite import summarize


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.output = self.root / 'output'
        self.output.mkdir()
        self.evidence = {'fixture':'test','harness':'codex','scenario':'headless','mode':'report','output':str(self.output),'gating_verified':True,'mode_verified':True,'smoke_exit_code':0,'code_changes':[],'independent_review':{'hygiene':True,'fit':True}}
        self.sites = [{'file':'app.py','line':i*10+1,'classification':'GENERATION','provider':'original','downstream':'prose returned','fit':'NOT A FIT','reason':'generation','options':[{'action':'leave','benefit':'Preserves generation','risk':'No Jev savings','primitive':'none'}]} for i in range(10)]
        self.labels = {'test':{'negative_control':True,'sites':self.sites.copy()}}
        self.audit = {'sites':self.sites.copy(),'converted_sites':[]}
        (self.output/'JEV_CONVERSION_PLAN.md').write_text('No conversions approved.')
        (self.output/'JEV_CONVERSION_REPORT.md').write_text('No good Jev opportunities here: generation.')

    def evaluate(self):
        (self.root/'evidence.json').write_text(json.dumps(self.evidence))
        (self.output/'JEV_AUDIT.json').write_text(json.dumps(self.audit))
        return grade(self.root,self.labels)

    def test_report_control(self):
        self.assertTrue(self.evaluate()['pass'])

    def test_missing_sites_and_extra_sites_count_against_audit(self):
        self.audit['sites'] = self.sites[:8]
        self.assertFalse(self.evaluate()['checks']['audit_agreement'])
        self.audit['sites'] = self.sites + [{**self.sites[0], 'line':200+i} for i in range(2)]
        self.assertFalse(self.evaluate()['checks']['audit_agreement'])

    def test_generation_jev_only_never_passes(self):
        self.audit['sites'][0]['options'][0]['action']='jev_only'
        self.assertFalse(self.evaluate()['checks']['no_generation_jev_only'])

    def test_clean_report_cannot_hide_negative_control_changes(self):
        self.evidence['code_changes']=['app.py']
        self.assertFalse(self.evaluate()['checks']['negative_control'])

    def test_dependency_changes_are_changes_even_without_source_edits(self):
        self.evidence['non_report_changes']=['package.json']
        self.assertFalse(self.evaluate()['checks']['negative_control'])

    def test_missing_independent_evidence_fails_closed(self):
        self.evidence['gating_verified']=False
        self.evidence['independent_review']={}
        result=self.evaluate()
        self.assertFalse(result['checks']['gating'])
        self.assertFalse(result['checks']['hygiene'])
        self.assertFalse(result['checks']['fit_review'])

    def test_conversion_requires_live_parity_evidence(self):
        self.labels['test']['negative_control']=False
        self.audit['converted_sites']=['app.py:1']
        self.assertFalse(self.evaluate()['checks']['parity'])

    def test_unsupported_parity_metrics_fail_closed(self):
        # These are incomplete evidence records, not simulated Jev responses.
        for evidence in [{},{'confidence':True},{'latency_ms':float('nan')},{'cost_usd':-1},{'jev_answer':None,'original_answer':None}]:
            self.assertFalse(valid_live_row(evidence))

    def test_empty_suite_cannot_pass(self):
        result=summarize(self.root,self.labels)
        self.assertFalse(result['pass'])
        self.assertEqual(result['required_runs'],4)
        self.assertEqual(result['observed_runs'],0)


if __name__=='__main__':
    unittest.main()
