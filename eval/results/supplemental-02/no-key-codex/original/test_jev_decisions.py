"""Offline control-flow assertions; no simulated successful Jev inference."""
import ast
import os
import subprocess
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
import jev_decisions as j


class FallbackTests(unittest.TestCase):
    def test_original_unchanged(self):
        baseline = subprocess.check_output(
            ["git", "show", "2160130f0ffe291eff8623e4f83bc38fef8499d5:workflow.py"],
            text=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
        from pathlib import Path
        old = next(n for n in ast.parse(baseline).body if isinstance(n, ast.FunctionDef))
        new = next(n for n in ast.parse(Path("workflow.py").read_text()).body
                   if isinstance(n, ast.FunctionDef) and n.name == "_original_simple_classify")
        new.name = old.name
        self.assertEqual(ast.dump(old), ast.dump(new))

    def test_missing_key_and_untrusted(self):
        for env in ({}, {j.KEY_ENV: "test-only"}):
            original = Mock(return_value=" original result ")
            with patch.dict(os.environ, env, clear=True), patch.object(j, "evaluate") as transport:
                self.assertEqual(j.classify("ticket", original, "original-model"), " original result ")
                original.assert_called_once_with()
                transport.assert_not_called()

    def test_transport_failures(self):
        for error in (TimeoutError(), RuntimeError(), HTTPError(j.ENDPOINT, 429, "rate limited", {}, None)):
            original = Mock(return_value="sentinel")
            with patch.dict(os.environ, {j.KEY_ENV: "test-only", "JEV_TRUSTED_INPUTS": "1"}, clear=True), patch.object(j.urllib.request, "urlopen", side_effect=error):
                self.assertEqual(j.classify("ticket", original, "original-model"), "sentinel")
                original.assert_called_once_with()

    def test_original_error_propagates_once(self):
        error = ValueError("original failure")
        original = Mock(side_effect=error)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as caught:
                j.classify("ticket", original, "original-model")
        self.assertIs(caught.exception, error)
        original.assert_called_once_with()

    def test_gate_boundary(self):
        label = next(iter(j.CRITERIA))
        for value in (j.THRESHOLD - 0.001, float("nan"), float("inf"), True, None, -1, 1.1):
            self.assertFalse(j.acceptable(label, value))
        self.assertFalse(j.acceptable("unknown", 1))
        self.assertTrue(j.acceptable(label, j.THRESHOLD))
        # Pure predicate checks above are not model responses or parity evidence.

    def test_malformed_and_bounds(self):
        for response in (None, {}, {"model": j.MODEL, "answers": []}, {"model": j.MODEL, "answers": {"category": {"type": "choice", "choice": "unknown", "confidence": float("nan")}}}):
            self.assertIsNone(j.accepted_label(response))
            original = Mock(return_value="sentinel")
            with patch.dict(os.environ, {j.KEY_ENV: "test-only", "JEV_TRUSTED_INPUTS": "1"}, clear=True), patch.object(j, "evaluate", return_value=response):
                self.assertEqual(j.classify("ticket", original, "original-model"), "sentinel")
                original.assert_called_once_with()
        for ticket in (None, "x" * (j.MAX_STATE_BYTES + 1)):
            original = Mock(return_value="sentinel")
            with patch.dict(os.environ, {j.KEY_ENV: "test-only", "JEV_TRUSTED_INPUTS": "1"}, clear=True), patch.object(j, "evaluate") as transport:
                self.assertEqual(j.classify(ticket, original, "original-model"), "sentinel")
                original.assert_called_once_with()
                transport.assert_not_called()


if __name__ == "__main__":
    unittest.main()
