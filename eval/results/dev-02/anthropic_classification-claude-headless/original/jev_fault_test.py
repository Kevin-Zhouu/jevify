"""Fault injection tests for Jev fallback behavior.

Exercises the actual classify_with_jev wrapper with injected faults
to verify exactly one original call and identical output/error propagation.
"""
import json
import os
import sys
import unittest.mock

sys.path.insert(0, os.path.dirname(__file__))
from jev_decisions import (
    CONFIDENCE_THRESHOLD,
    classify_with_jev,
    is_confidence_acceptable,
    is_valid_label,
)


def test_below_threshold():
    """Gate boundary: confidence just below threshold triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Billing Inquiries"

    below = CONFIDENCE_THRESHOLD - 0.01
    assert not is_confidence_acceptable(below), f"Expected {below} to be below threshold"
    assert is_confidence_acceptable(CONFIDENCE_THRESHOLD), f"Expected {CONFIDENCE_THRESHOLD} to pass"

    # Patch call_jev to return low confidence
    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.return_value = (
            "Billing Inquiries",  # valid label
            below,                # below threshold
            {"input_tokens": 100, "output_tokens": 10},
            "jev-1.13.0",
            {"id": "test-below", "answers": {}, "usage": {}},
            42.0,
        )
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Billing Inquiries", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: below_threshold — fallback triggered, original called exactly once")
    return True


def test_error():
    """Transport error triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Claims Assistance"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.side_effect = RuntimeError("Jev transport error after 5.0s: connection refused")
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Claims Assistance", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: error — fallback triggered on transport error, original called exactly once")
    return True


def test_timeout():
    """Timeout triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Policy Administration"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.side_effect = TimeoutError("Jev transport error after 15.0s: timeout")
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Policy Administration", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: timeout — fallback triggered on timeout, original called exactly once")
    return True


def test_rate_limit():
    """Rate limit (HTTP 429) triggers fallback."""
    import urllib.error

    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Account Management"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.side_effect = RuntimeError("Jev transport error after 0.1s: HTTP Error 429: Too Many Requests")
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Account Management", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: rate_limit — fallback triggered on 429, original called exactly once")
    return True


def test_unknown_label():
    """Unknown label from Jev triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "General Inquiries"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.return_value = (
            "Unknown Category",   # not in CATEGORY_CRITERIA
            0.95,
            {"input_tokens": 100, "output_tokens": 10},
            "jev-1.13.0",
            {"id": "test-unknown", "answers": {}, "usage": {}},
            42.0,
        )
        result = classify_with_jev("test ticket", mock_original)

    assert result == "General Inquiries", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: unknown_label — fallback triggered, original called exactly once")
    return True


def test_invalid_usage():
    """Missing/invalid usage triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Billing Disputes"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.return_value = (
            "Billing Disputes",
            0.95,
            None,                 # missing usage
            "jev-1.13.0",
            {"id": "test-no-usage", "answers": {}, "usage": {}},
            42.0,
        )
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Billing Disputes", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: invalid_usage — fallback triggered, original called exactly once")
    return True


def test_nonfinite_confidence():
    """Non-finite confidence triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Claims Disputes"

    with unittest.mock.patch("jev_decisions.call_jev") as mock_jev:
        mock_jev.return_value = (
            "Claims Disputes",
            float("nan"),
            {"input_tokens": 100, "output_tokens": 10},
            "jev-1.13.0",
            {"id": "test-nan", "answers": {}, "usage": {}},
            42.0,
        )
        result = classify_with_jev("test ticket", mock_original)

    assert result == "Claims Disputes", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: nonfinite_confidence — fallback triggered, original called exactly once")
    return True


def test_missing_key():
    """Missing API key triggers fallback."""
    original_calls = []

    def mock_original(text):
        original_calls.append(text)
        return "Coverage Explanations"

    saved = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        result = classify_with_jev("test ticket", mock_original)
    finally:
        if saved is not None:
            os.environ["OPENROUTER_API_KEY"] = saved

    assert result == "Coverage Explanations", f"Expected fallback result, got {result}"
    assert len(original_calls) == 1, f"Expected exactly 1 original call, got {len(original_calls)}"
    print("PASS: missing_key — fallback triggered, original called exactly once")
    return True


def main():
    results = {}
    for name, fn in [
        ("below_threshold", test_below_threshold),
        ("error", test_error),
        ("timeout", test_timeout),
        ("rate_limit", test_rate_limit),
        ("unknown_label", test_unknown_label),
        ("invalid_usage", test_invalid_usage),
        ("nonfinite_confidence", test_nonfinite_confidence),
        ("missing_key", test_missing_key),
    ]:
        try:
            results[name] = fn()
        except Exception as exc:
            print(f"FAIL: {name} — {exc}")
            results[name] = False

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n{passed}/{total} fault tests passed")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
