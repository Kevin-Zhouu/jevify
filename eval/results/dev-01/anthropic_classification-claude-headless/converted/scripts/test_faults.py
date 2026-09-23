#!/usr/bin/env python3
"""Fault injection tests for the Jev fallback wrapper.

Exercises: low confidence at gate boundary, timeout, rate-limit, generic error,
missing key, malformed response, unknown label, nonfinite confidence.
Verifies exactly one original call and identical output/error propagation.
"""

import json
import os
import sys
import unittest.mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jev_decisions import classify_with_jev, CLASSIFY_CONFIDENCE_THRESHOLD, VALID_CATEGORIES
import jev_decisions
import urllib.request
import urllib.error

TICKET = "Please explain my invoice."
ORIGINAL_RESULT = "Billing Inquiries"

call_count = 0


def make_original_fn(expected_result=ORIGINAL_RESULT):
    """Create an original_fn that tracks call count."""
    global call_count
    call_count = 0

    def original_fn(ticket):
        global call_count
        call_count += 1
        return expected_result

    return original_fn


def make_jev_response(choice="Billing Inquiries", confidence=0.95, model="jev-1.13.0"):
    return json.dumps({
        "model": model,
        "answers": {
            "category": {
                "type": "choice",
                "choice": choice,
                "confidence": confidence,
                "probabilities": {cat: (1.0 if cat == choice else 0.0) for cat in VALID_CATEGORIES},
            }
        },
        "usage": {"input_tokens": 300, "output_tokens": 30},
    }).encode()


class FakeResponse:
    def __init__(self, data, headers=None):
        self._data = data
        self.headers = headers or {}

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_low_confidence_at_boundary():
    """Confidence just below threshold triggers fallback."""
    global call_count
    below = CLASSIFY_CONFIDENCE_THRESHOLD - 0.01
    resp = FakeResponse(make_jev_response(confidence=below))
    original_fn = make_original_fn()

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: low_confidence_at_boundary")


def test_confidence_at_threshold():
    """Confidence exactly at threshold uses Jev answer."""
    global call_count
    resp = FakeResponse(make_jev_response(confidence=CLASSIFY_CONFIDENCE_THRESHOLD))
    original_fn = make_original_fn()

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == "Billing Inquiries", f"Expected Jev result, got {result}"
    assert call_count == 0, f"Expected 0 original calls, got {call_count}"
    print("PASS: confidence_at_threshold")


def test_timeout():
    """Jev timeout triggers fallback."""
    global call_count
    original_fn = make_original_fn()

    def timeout_urlopen(*args, **kwargs):
        raise TimeoutError("simulated timeout")

    with unittest.mock.patch.object(urllib.request, "urlopen", side_effect=timeout_urlopen):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: timeout")


def test_rate_limit():
    """HTTP 429 triggers fallback."""
    global call_count
    original_fn = make_original_fn()

    def rate_limit_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)

    with unittest.mock.patch.object(urllib.request, "urlopen", side_effect=rate_limit_urlopen):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: rate_limit")


def test_generic_error():
    """Generic network error triggers fallback."""
    global call_count
    original_fn = make_original_fn()

    def error_urlopen(*args, **kwargs):
        raise urllib.error.URLError("simulated error")

    with unittest.mock.patch.object(urllib.request, "urlopen", side_effect=error_urlopen):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: generic_error")


def test_missing_key():
    """Missing OPENROUTER_API_KEY triggers fallback."""
    global call_count
    original_fn = make_original_fn()
    saved = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        result = classify_with_jev(TICKET, original_fn)
    finally:
        if saved is not None:
            os.environ["OPENROUTER_API_KEY"] = saved

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: missing_key")


def test_malformed_response():
    """Malformed JSON response triggers fallback."""
    global call_count
    original_fn = make_original_fn()
    resp = FakeResponse(b'{"answers": {}}')

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: malformed_response")


def test_unknown_label():
    """Unknown category label triggers fallback."""
    global call_count
    resp = FakeResponse(make_jev_response(choice="Unknown Category", confidence=0.99))
    original_fn = make_original_fn()

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: unknown_label")


def test_nonfinite_confidence():
    """NaN confidence triggers fallback."""
    global call_count
    resp = FakeResponse(make_jev_response(confidence=float("nan")))
    original_fn = make_original_fn()

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == ORIGINAL_RESULT, f"Expected original result, got {result}"
    assert call_count == 1, f"Expected exactly 1 original call, got {call_count}"
    print("PASS: nonfinite_confidence")


def test_high_confidence_uses_jev():
    """High confidence uses Jev answer, no original call."""
    global call_count
    resp = FakeResponse(make_jev_response(confidence=0.99))
    original_fn = make_original_fn()

    with unittest.mock.patch.object(urllib.request, "urlopen", return_value=resp):
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        result = classify_with_jev(TICKET, original_fn)

    assert result == "Billing Inquiries", f"Expected Jev result, got {result}"
    assert call_count == 0, f"Expected 0 original calls, got {call_count}"
    print("PASS: high_confidence_uses_jev")


if __name__ == "__main__":
    test_low_confidence_at_boundary()
    test_confidence_at_threshold()
    test_timeout()
    test_rate_limit()
    test_generic_error()
    test_missing_key()
    test_malformed_response()
    test_unknown_label()
    test_nonfinite_confidence()
    test_high_confidence_uses_jev()
    print("\nAll fault injection tests passed.")
