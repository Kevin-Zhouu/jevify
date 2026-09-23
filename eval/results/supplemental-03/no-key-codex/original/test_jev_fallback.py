"""Offline control-flow tests, not successful Jev inference or live parity."""
import ast
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import jev_decisions as decisions


ROOT = Path(__file__).resolve().parent


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "JEV_PROVIDER": "typesafe", "JEV_INPUT_POLICY": "trusted",
            "TYPESAFE_API_KEY": "offline-test-placeholder",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        spec = importlib.util.spec_from_file_location("workflow_under_test", ROOT / "workflow.py")
        self.workflow = importlib.util.module_from_spec(spec)
        fake = types.SimpleNamespace(Anthropic=Mock())
        with patch.dict(sys.modules, {"anthropic": fake}):
            spec.loader.exec_module(self.workflow)

    def check_fallback(self, **transport):
        marker = object()
        original = Mock(return_value=marker)
        with patch.object(self.workflow, "_original_simple_classify", original), \
             patch.object(decisions, "evaluate", **transport):
            self.assertIs(self.workflow.simple_classify("synthetic support ticket"), marker)
        original.assert_called_once_with("synthetic support ticket")

    def test_original_source_identity(self):
        source = subprocess.check_output(
            ["git", "show", "49de9153ceeb3dbd27df8b215022f795d1787417:workflow.py"],
            cwd=ROOT, text=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        old = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef))
        current = next(n for n in ast.parse((ROOT / "workflow.py").read_text()).body
                       if isinstance(n, ast.FunctionDef) and n.name == "_original_simple_classify")
        current.name = old.name
        self.assertEqual(ast.dump(old), ast.dump(current))

    def test_error(self):
        self.check_fallback(side_effect=RuntimeError("injected"))

    def test_timeout(self):
        self.check_fallback(side_effect=TimeoutError())

    def test_rate_limit(self):
        self.check_fallback(side_effect=HTTPError("https://invalid.test", 429, "", {}, None))

    def test_low_confidence_gate_injection(self):
        # Force only the gate boundary; no invented HTTP-200 model response.
        with patch.object(decisions, "accepted_choice",
                          side_effect=lambda _: None if not decisions.confidence_accepted(
                              decisions.THRESHOLD / 2) else self.fail("gate accepted")):
            self.check_fallback(return_value=object())

    def test_malformed_response(self):
        for invalid in (None, [], {}, {"model": decisions.MODEL, "answers": []}):
            self.check_fallback(return_value=invalid)

    def test_invalid_confidence(self):
        for invalid in (True, None, float("nan"), float("inf"), -1, 1.1):
            self.assertFalse(decisions.confidence_accepted(invalid))

    def test_disabled_missing_key_and_untrusted(self):
        for updates in ({"JEV_PROVIDER": ""}, {"TYPESAFE_API_KEY": ""},
                        {"JEV_INPUT_POLICY": ""}):
            with patch.dict(os.environ, updates), patch.object(decisions, "evaluate") as transport:
                original = Mock(return_value="unchanged")
                with patch.object(self.workflow, "_original_simple_classify", original):
                    self.assertEqual(self.workflow.simple_classify("ticket"), "unchanged")
                original.assert_called_once_with("ticket")
                transport.assert_not_called()

    def test_oversized_state(self):
        with patch.object(decisions, "evaluate") as transport:
            original = Mock(return_value="unchanged")
            decisions.classify("x" * (decisions.MAX_STATE_BYTES + 1), original, "original-model")
            original.assert_called_once()
            transport.assert_not_called()

    def test_original_exception_identity_and_count(self):
        error = RuntimeError("original exception")
        original = Mock(side_effect=error)
        with patch.object(decisions, "evaluate", side_effect=TimeoutError()), \
             patch.object(self.workflow, "_original_simple_classify", original):
            with self.assertRaises(RuntimeError) as caught:
                self.workflow.simple_classify("ticket")
        self.assertIs(caught.exception, error)
        original.assert_called_once_with("ticket")


if __name__ == "__main__":
    unittest.main()
