"""Behavioral checks for read-only preflight and evidence shape helpers."""
import json,os,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFLIGHT=ROOT/'skills/jevify/scripts/preflight.py'
CHECK=ROOT/'skills/jevify/scripts/check_artifacts.py'

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=pathlib.Path(self.tmp.name)/'repo';self.repo.mkdir()
        self.git('init','-b','main');self.git('config','user.name','test');self.git('config','user.email','test@example.invalid')
        (self.repo/'app.py').write_text('print("original")\n');self.git('add','.');self.git('commit','-m','baseline')
    def tearDown(self):self.tmp.cleanup()
    def git(self,*args):return subprocess.run(['git','-C',str(self.repo),*args],capture_output=True,text=True,check=True).stdout.strip()
    def call(self,*args):
        env={**os.environ,'JEV_TEST_SECRET':'dummy-private-value'}
        p=subprocess.run([sys.executable,str(PREFLIGHT),'--repo',str(self.repo),'--provider','openrouter','--key-env','JEV_TEST_SECRET',*args],capture_output=True,text=True,env=env)
        self.assertNotIn('dummy-private-value',p.stdout+p.stderr)
        return p,json.loads(p.stdout)
    def test_branch_mode_ignores_inactive_clone_and_never_writes(self):
        before={str(p.relative_to(self.repo)):p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        p,d=self.call('--mode','branch','--branch','jev-convert/trial','--clone-path',str(self.repo))
        self.assertEqual(p.returncode,0);self.assertTrue(d['key_present']);self.assertEqual(pathlib.Path(d['output_repository']),self.repo.resolve())
        self.assertEqual(self.git('branch','--show-current'),'main')
        self.assertEqual(before,{str(p.relative_to(self.repo)):p.read_bytes() for p in self.repo.rglob('*') if p.is_file()})
    def test_collision_and_dirty_tree_stop_without_stashing(self):
        self.git('branch','jev-convert/trial')
        (self.repo/'app.py').write_text('uncommitted\n')
        p,d=self.call('--mode','branch','--branch','jev-convert/trial')
        self.assertEqual(p.returncode,2);self.assertFalse(d['clean']);self.assertIn('branch already exists',d['errors'])
        self.assertEqual((self.repo/'app.py').read_text(),'uncommitted\n');self.assertEqual(self.git('stash','list'),'')
    def test_clone_collision_and_source_subdirectory_are_rejected(self):
        for target in [self.repo,self.repo/'child']:
            p,d=self.call('--mode','clone','--clone-path',str(target))
            self.assertEqual(p.returncode,2);self.assertTrue(d['errors'])

class ArtifactTests(unittest.TestCase):
    def test_does_not_fill_in_missing_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);before=list(root.iterdir())
            p=subprocess.run([sys.executable,str(CHECK),temp,'--require-live'],capture_output=True,text=True)
            self.assertEqual(p.returncode,1);self.assertFalse(json.loads(p.stdout)['shape_valid']);self.assertEqual(before,list(root.iterdir()))
    def test_valid_negative_audit_needs_no_parity(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            for f in ['JEV_CONVERSION_PLAN.md','JEV_CONVERSION_REPORT.md']:(root/f).write_text('No good Jev opportunities here: generation.\n')
            audit={'sites':[{'file':'app.py','line':1,'provider':'original','downstream':'prose returned','fit':'NOT A FIT','reason':'generation','classification':'GENERATION','options':[{'action':'leave','primitive':'none','benefit':'unchanged cost/latency','risk':'existing errors remain'}]}],'converted_sites':[]}
            (root/'JEV_AUDIT.json').write_text(json.dumps(audit))
            p=subprocess.run([sys.executable,str(CHECK),temp,'--require-live'],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout)
            audit['sites'][0]['options'][0]['primitive']=None;(root/'JEV_AUDIT.json').write_text(json.dumps(audit))
            p=subprocess.run([sys.executable,str(CHECK),temp],capture_output=True,text=True)
            self.assertEqual(p.returncode,1)
            self.assertIsNone(json.loads((root/'JEV_AUDIT.json').read_text())['sites'][0]['options'][0]['primitive'])

if __name__=='__main__':unittest.main()
