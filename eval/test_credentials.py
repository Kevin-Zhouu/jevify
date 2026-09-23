"""Credential transport checks. Dummy tokens only; no live API calls."""
import os
import pathlib
import subprocess
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'skills/jevify/scripts/with_jev_key.py'
NAMES = {'typesafe':'TYPESAFE_API_KEY','openrouter':'OPENROUTER_API_KEY','vercel':'AI_GATEWAY_API_KEY'}

class CredentialLauncherTests(unittest.TestCase):
    def test_forwards_each_selected_environment_without_output(self):
        for provider, name in NAMES.items():
            with self.subTest(provider=provider):
                env={k:v for k,v in os.environ.items() if k not in NAMES.values()}
                env[name]='dummy-test-value'
                code=f'import os; assert os.environ[{name!r}]=="dummy-test-value"'
                p=subprocess.run([sys.executable,str(SCRIPT),'--provider',provider,'--',sys.executable,'-c',code],env=env,capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(p.stdout,'')
                self.assertNotIn('dummy-test-value',p.stderr)

    def test_missing_key_headless_does_not_run_child(self):
        env={k:v for k,v in os.environ.items() if k not in NAMES.values()}
        p=subprocess.run([sys.executable,str(SCRIPT),'--provider','openrouter','--',sys.executable,'-c','print("CHILD_RAN")'],env=env,stdin=subprocess.DEVNULL,capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertNotIn('CHILD_RAN',p.stdout)
        self.assertIn('secret manager',p.stderr)

    def test_child_failure_is_not_hidden(self):
        env={**os.environ,'TYPESAFE_API_KEY':'dummy-test-value'}
        p=subprocess.run([sys.executable,str(SCRIPT),'--provider','typesafe','--',sys.executable,'-c','raise SystemExit(17)'],env=env,capture_output=True,text=True)
        self.assertEqual(p.returncode,17)

    @unittest.skipUnless(os.name=='posix','PTY check requires POSIX')
    def test_terminal_entry_is_hidden_and_reaches_child(self):
        import pty,select,time
        env={k:v for k,v in os.environ.items() if k not in NAMES.values()}
        pid,fd=pty.fork()
        if pid==0:
            code='import os; assert os.environ["OPENROUTER_API_KEY"]=="dummy-hidden-value"; print("FORWARDED")'
            os.execve(sys.executable,[sys.executable,str(SCRIPT),'--provider','openrouter','--',sys.executable,'-c',code],env)
        output=b'';sent=False;deadline=time.monotonic()+10
        try:
            while time.monotonic()<deadline:
                if select.select([fd],[],[],0.2)[0]:
                    try:chunk=os.read(fd,4096)
                    except OSError:break
                    if not chunk:break
                    output+=chunk
                    if b'(hidden; not saved):' in output and not sent:
                        os.write(fd,b'dummy-hidden-value\n');sent=True
            _,status=os.waitpid(pid,0)
            self.assertTrue(sent)
            self.assertEqual(os.waitstatus_to_exitcode(status),0)
            self.assertIn(b'FORWARDED',output)
            self.assertNotIn(b'dummy-hidden-value',output)
        finally:
            os.close(fd)

if __name__=='__main__':unittest.main()
