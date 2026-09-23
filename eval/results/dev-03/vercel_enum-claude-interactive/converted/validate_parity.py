#!/usr/bin/env python3
"""Live parity validation for Jev conversion of workflow.ts:6.

Imports the actual jevDecisions.ts module via a TS bridge subprocess,
runs paired comparisons on 30+ inputs, and exercises fault injection.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

CONVERTED_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Bridge: load actual constants from jevDecisions.ts via ts eval
# ---------------------------------------------------------------------------

def load_decisions_constants():
    """Execute TS bridge to extract actual model pin, question, threshold."""
    bridge_code = r"""
const ts = require('typescript');
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, 'jevDecisions.ts'), 'utf8');
const compiled = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }
});
const mod = { exports: {} };
const fn = vm.runInThisContext('(function(require,module,exports,process){' + compiled.outputText + '\n})');
fn(require, mod, mod.exports, { env: {}, stderr: { write: () => {} } });
const e = mod.exports;
console.log(JSON.stringify({
  JEV_MODEL: e.JEV_MODEL,
  JEV_CONFIDENCE_THRESHOLD: e.JEV_CONFIDENCE_THRESHOLD,
  JEV_TIMEOUT_MS: e.JEV_TIMEOUT_MS,
  GENRE_OPTIONS: e.GENRE_OPTIONS,
  GENRE_QUESTION: e.GENRE_QUESTION,
  JEV_FINISH_REASON: e.JEV_FINISH_REASON,
}));
"""
    result = subprocess.run(
        ['node', '-e', bridge_code],
        capture_output=True, text=True, cwd=CONVERTED_DIR, timeout=10
    )
    if result.returncode != 0:
        print(f"Bridge error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout.strip())


# ---------------------------------------------------------------------------
# Test inputs: 30 unique realistic movie plots covering all genres + edge cases
# ---------------------------------------------------------------------------

INPUTS = [
    # action (6)
    {"plot": "A retired special forces operative is pulled back into action when terrorists hijack a skyscraper.", "expected": "action", "provenance": "synthetic"},
    {"plot": "Two rival street racers must team up to take down a criminal empire using stolen military vehicles.", "expected": "action", "provenance": "synthetic"},
    {"plot": "A martial arts master travels across feudal Japan, fighting warlords to rescue kidnapped villagers.", "expected": "action", "provenance": "synthetic"},
    {"plot": "After a prison break, an ex-cop chases the escapees across the desert in a series of high-speed pursuits.", "expected": "action", "provenance": "synthetic"},
    {"plot": "An elite team of mercenaries infiltrates an island fortress to prevent a missile launch.", "expected": "action", "provenance": "synthetic"},
    {"plot": "A lone firefighter battles through a collapsing building to save trapped survivors from a terrorist bomb.", "expected": "action", "provenance": "synthetic"},
    # comedy (6)
    {"plot": "A bumbling wedding planner accidentally double-books two weddings at the same venue on the same day.", "expected": "comedy", "provenance": "synthetic"},
    {"plot": "Two mismatched roommates enter a cooking competition despite neither knowing how to boil water.", "expected": "comedy", "provenance": "synthetic"},
    {"plot": "A dog inherits a fortune and its greedy relatives must care for it to claim the money.", "expected": "comedy", "provenance": "synthetic"},
    {"plot": "An office worker discovers their boss is actually a time traveler from the 1800s struggling with modern technology.", "expected": "comedy", "provenance": "synthetic"},
    {"plot": "A group of senior citizens form a rock band and accidentally go viral on social media.", "expected": "comedy", "provenance": "synthetic"},
    {"plot": "A man wakes up to find he can only speak in rhymes for the next 48 hours.", "expected": "comedy", "provenance": "synthetic"},
    # drama (6)
    {"plot": "A pianist losing her hearing prepares for one final concert while reconciling with her estranged daughter.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "A factory worker fights for better conditions after a colleague dies in an industrial accident.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "Two childhood friends on opposite sides of a war meet again at a refugee camp.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "A retired teacher discovers letters revealing her late husband led a secret double life for decades.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "A young immigrant struggles to build a new life while caring for an aging parent who wants to return home.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "A surgeon must decide whether to save a patient who once wronged her family.", "expected": "drama", "provenance": "synthetic"},
    # horror (6)
    {"plot": "A family moves into an old farmhouse where the walls bleed at night and the children begin speaking in dead languages.", "expected": "horror", "provenance": "synthetic"},
    {"plot": "A group of hikers gets lost in a forest where something ancient hunts them after dark.", "expected": "horror", "provenance": "synthetic"},
    {"plot": "A nurse working the night shift realizes her patients are being replaced by something that looks like them but isn't.", "expected": "horror", "provenance": "synthetic"},
    {"plot": "An archaeologist opens a sealed tomb and releases a curse that turns the expedition members against each other.", "expected": "horror", "provenance": "synthetic"},
    {"plot": "A teenager discovers that the imaginary friend from her childhood has become terrifyingly real.", "expected": "horror", "provenance": "synthetic"},
    {"plot": "Residents of a small town wake up to find an impenetrable fog has surrounded them and things move within it.", "expected": "horror", "provenance": "synthetic"},
    # sci-fi (6)
    {"plot": "A group of astronauts travel through a wormhole in search of a new habitable planet for humanity.", "expected": "sci-fi", "provenance": "repo"},
    {"plot": "In a world where memories can be traded, a detective investigates crimes by reliving victims' final moments.", "expected": "sci-fi", "provenance": "synthetic"},
    {"plot": "A colony on Mars discovers signs of ancient alien civilization beneath the planet's surface.", "expected": "sci-fi", "provenance": "synthetic"},
    {"plot": "A scientist invents a device that lets her communicate with a parallel version of herself in an alternate timeline.", "expected": "sci-fi", "provenance": "synthetic"},
    {"plot": "Humanity's last city is run by an AI that begins making decisions humans cannot understand or override.", "expected": "sci-fi", "provenance": "synthetic"},
    {"plot": "After faster-than-light travel is discovered, Earth's first interstellar ambassador must negotiate with an alien species that communicates through mathematics.", "expected": "sci-fi", "provenance": "synthetic"},
    # ambiguous / boundary (2)
    {"plot": "A comedian deals with severe depression while performing sold-out shows every night.", "expected": "drama", "provenance": "synthetic"},
    {"plot": "Survivors of a plane crash on a remote island must work together to escape, but tensions and violence erupt.", "expected": "action", "provenance": "synthetic"},
]


def call_jev(state: str, question: dict, model: str, api_key: str) -> dict:
    """Call Jev via OpenRouter System One endpoint."""
    url = "https://openrouter.ai/api/v1/systemone"
    payload = json.dumps({"state": state, "model": model, "questions": question}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
        latency = (time.monotonic() - t0) * 1000
        return {"ok": True, "body": body, "latency_ms": latency}
    except Exception as e:
        latency = (time.monotonic() - t0) * 1000
        return {"ok": False, "error": str(type(e).__name__), "latency_ms": latency}


def call_original_baseline(plot: str, api_key: str) -> dict:
    """Call original model (gpt-4o-mini) through OpenRouter for baseline."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = json.dumps({
        "model": "openai/gpt-4o-mini",
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "genre",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string", "enum": ["action", "comedy", "drama", "horror", "sci-fi"]}
                },
                "required": ["result"],
                "additionalProperties": False,
            }
        }},
        "messages": [
            {"role": "user", "content": f'Classify the genre of this movie plot: "{plot}"'}
        ],
    }).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
        latency = (time.monotonic() - t0) * 1000
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = json.loads(content)
        request_id = body.get("id", "")
        return {
            "ok": True,
            "answer": parsed.get("result", ""),
            "latency_ms": latency,
            "request_id": request_id,
            "model": body.get("model", ""),
            "usage": body.get("usage", {}),
        }
    except Exception as e:
        latency = (time.monotonic() - t0) * 1000
        return {"ok": False, "error": str(type(e).__name__), "latency_ms": latency}


def run_fault_injection(consts: dict) -> dict:
    """Exercise fault injection tests using actual wrapper via TS subprocess."""
    faults = {}

    # 1. Low confidence: call shouldAccept with below-threshold value
    bridge = f"""
const ts = require('typescript');
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'jevDecisions.ts'), 'utf8');
const compiled = ts.transpileModule(src, {{
  compilerOptions: {{ module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }}
}});
const mod = {{ exports: {{}} }};
const fn = vm.runInThisContext('(function(require,module,exports,process){{' + compiled.outputText + '\\n}})');
fn(require, mod, mod.exports, {{ env: {{}}, stderr: {{ write: () => {{}} }} }});
const sa = mod.exports.shouldAccept;
const results = {{
  below_threshold: sa(0.5),
  at_threshold: sa({consts['JEV_CONFIDENCE_THRESHOLD']}),
  above_threshold: sa(0.95),
  boolean_true: sa(true),
  nan: sa(NaN),
  infinity: sa(Infinity),
  negative: sa(-0.1),
  over_one: sa(1.5),
}};
console.log(JSON.stringify(results));
"""
    r = subprocess.run(['node', '-e', bridge], capture_output=True, text=True, cwd=CONVERTED_DIR, timeout=10)
    if r.returncode == 0:
        gate_results = json.loads(r.stdout.strip())
        faults["below_threshold"] = (
            gate_results.get("below_threshold") is False
            and gate_results.get("at_threshold") is True
            and gate_results.get("above_threshold") is True
        )
        faults["boolean_rejected"] = gate_results.get("boolean_true") is False
        faults["nan_rejected"] = gate_results.get("nan") is False
        faults["infinity_rejected"] = gate_results.get("infinity") is False
        faults["out_of_range_rejected"] = (
            gate_results.get("negative") is False and gate_results.get("over_one") is False
        )
    else:
        print(f"Gate test bridge failed: {r.stderr}", file=sys.stderr)
        faults["below_threshold"] = False

    # 2. Error test: evaluateGenre with fetch that throws
    error_bridge = r"""
const ts = require('typescript');
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'jevDecisions.ts'), 'utf8');
const compiled = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }
});
const mod = { exports: {} };
global.fetch = async () => { throw new Error('injected network error'); };
const fn = vm.runInThisContext('(function(require,module,exports,process){' + compiled.outputText + '\n})');
const stderrBuf = [];
fn(require, mod, mod.exports, { env: { OPENROUTER_API_KEY: 'test-key' }, stderr: { write: (s) => stderrBuf.push(s) } });
mod.exports.evaluateGenre('test plot').then(r => {
  console.log(JSON.stringify({ result: r, stderr: stderrBuf.join('') }));
});
"""
    r = subprocess.run(['node', '-e', error_bridge], capture_output=True, text=True, cwd=CONVERTED_DIR, timeout=10)
    if r.returncode == 0:
        er = json.loads(r.stdout.strip())
        faults["error"] = er.get("result") is None and "error" in er.get("stderr", "")
    else:
        faults["error"] = False

    # 3. Timeout test: evaluateGenre with fetch that hangs
    timeout_bridge = r"""
const ts = require('typescript');
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'jevDecisions.ts'), 'utf8');
// Patch timeout to 500ms for fast test
const patched = src.replace(/JEV_TIMEOUT_MS\s*=\s*\d+/, 'JEV_TIMEOUT_MS = 500');
const compiled = ts.transpileModule(patched, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }
});
const mod = { exports: {} };
global.fetch = (url, opts) => new Promise((_, reject) => {
  if (opts && opts.signal) {
    opts.signal.addEventListener('abort', () => reject(Object.assign(new Error('aborted'), { name: 'AbortError' })));
  }
}); // respects abort signal
const fn = vm.runInThisContext('(function(require,module,exports,process){' + compiled.outputText + '\n})');
const stderrBuf = [];
fn(require, mod, mod.exports, { env: { OPENROUTER_API_KEY: 'test-key' }, stderr: { write: (s) => stderrBuf.push(s) } });
mod.exports.evaluateGenre('test plot').then(r => {
  console.log(JSON.stringify({ result: r, stderr: stderrBuf.join('') }));
});
"""
    r = subprocess.run(['node', '-e', timeout_bridge], capture_output=True, text=True, cwd=CONVERTED_DIR, timeout=15)
    if r.returncode == 0:
        tr = json.loads(r.stdout.strip())
        faults["timeout"] = tr.get("result") is None and "timeout" in tr.get("stderr", "")
    else:
        faults["timeout"] = False

    # 4. Rate limit test: evaluateGenre with fetch returning 429
    rate_limit_bridge = r"""
const ts = require('typescript');
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'jevDecisions.ts'), 'utf8');
const compiled = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }
});
const mod = { exports: {} };
global.fetch = async () => ({ ok: false, status: 429, json: async () => ({}) });
const fn = vm.runInThisContext('(function(require,module,exports,process){' + compiled.outputText + '\n})');
const stderrBuf = [];
fn(require, mod, mod.exports, { env: { OPENROUTER_API_KEY: 'test-key' }, stderr: { write: (s) => stderrBuf.push(s) } });
mod.exports.evaluateGenre('test plot').then(r => {
  console.log(JSON.stringify({ result: r, stderr: stderrBuf.join('') }));
});
"""
    r = subprocess.run(['node', '-e', rate_limit_bridge], capture_output=True, text=True, cwd=CONVERTED_DIR, timeout=10)
    if r.returncode == 0:
        rr = json.loads(r.stdout.strip())
        faults["rate_limit"] = rr.get("result") is None and "rate_limit" in rr.get("stderr", "")
    else:
        faults["rate_limit"] = False

    return faults


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("OPENROUTER_API_KEY not set. Live validation skipped.", file=sys.stderr)
        sys.exit(1)

    print("Loading decisions module constants via TS bridge...", file=sys.stderr)
    consts = load_decisions_constants()
    jev_model = consts["JEV_MODEL"]
    threshold = consts["JEV_CONFIDENCE_THRESHOLD"]
    question = consts["GENRE_QUESTION"]
    genre_options = consts["GENRE_OPTIONS"]

    print(f"Model: {jev_model}, Threshold: {threshold}, Options: {genre_options}", file=sys.stderr)

    # --- Fault injection ---
    print("\nRunning fault injection tests...", file=sys.stderr)
    faults = run_fault_injection(consts)
    for name, passed in faults.items():
        status = "PASS" if passed else "FAIL"
        print(f"  Fault [{name}]: {status}", file=sys.stderr)

    # --- Live parity ---
    print(f"\nRunning live parity on {len(INPUTS)} inputs...", file=sys.stderr)
    rows = []
    jev_latencies = []
    orig_latencies = []

    for i, inp in enumerate(INPUTS):
        plot = inp["plot"]
        print(f"  [{i+1}/{len(INPUTS)}] {plot[:60]}...", file=sys.stderr)

        # Call Jev
        jev_resp = call_jev(plot, question, jev_model, api_key)
        time.sleep(0.3)  # rate limit courtesy

        # Call original baseline
        orig_resp = call_original_baseline(plot, api_key)
        time.sleep(0.3)

        row = {
            "input": plot,
            "provenance": inp["provenance"],
            "expected": inp["expected"],
            "model": jev_model,
            "live": True,
        }

        if jev_resp["ok"]:
            body = jev_resp["body"]
            answers = body.get("answers", {})
            genre_ans = answers.get("genre", {})
            row["jev_answer"] = genre_ans.get("choice", "")
            row["confidence"] = genre_ans.get("confidence", -1)
            row["latency_ms"] = round(jev_resp["latency_ms"], 1)
            row["request_id"] = body.get("id", body.get("request_id", ""))
            usage = body.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            # Cost: $0.042/M tokens (input only, output free)
            row["cost_usd"] = round(input_tokens * 0.042 / 1_000_000, 8)
            row["jev_usage"] = usage

            accepted = (
                isinstance(row["confidence"], (int, float))
                and not isinstance(row["confidence"], bool)
                and row["confidence"] >= threshold
                and row["jev_answer"] in genre_options
            )
            row["fallback_taken"] = not accepted
            jev_latencies.append(jev_resp["latency_ms"])
        else:
            row["jev_answer"] = ""
            row["confidence"] = -1
            row["latency_ms"] = round(jev_resp["latency_ms"], 1)
            row["jev_error"] = jev_resp.get("error", "unknown")
            row["fallback_taken"] = True
            row["request_id"] = ""
            row["cost_usd"] = 0

        if orig_resp["ok"]:
            row["original_answer"] = orig_resp["answer"]
            row["original_latency_ms"] = round(orig_resp["latency_ms"], 1)
            row["original_model"] = orig_resp.get("model", "openai/gpt-4o-mini")
            row["original_request_id"] = orig_resp.get("request_id", "")
            orig_usage = orig_resp.get("usage", {})
            prompt_tokens = orig_usage.get("prompt_tokens", 0)
            completion_tokens = orig_usage.get("completion_tokens", 0)
            # gpt-4o-mini: $0.15/M input + $0.60/M output
            row["original_cost_usd"] = round(
                prompt_tokens * 0.15 / 1_000_000 + completion_tokens * 0.60 / 1_000_000, 8
            )
            orig_latencies.append(orig_resp["latency_ms"])
        else:
            row["original_answer"] = ""
            row["original_latency_ms"] = round(orig_resp["latency_ms"], 1)
            row["original_model"] = "openai/gpt-4o-mini"
            row["original_error"] = orig_resp.get("error", "unknown")
            row["original_cost_usd"] = 0

        rows.append(row)

    # --- Compute metrics ---
    valid_rows = [r for r in rows if r.get("jev_answer") and r.get("original_answer")]
    accepted_rows = [r for r in valid_rows if not r["fallback_taken"]]
    total = len(valid_rows)
    accepted = len(accepted_rows)
    fallback_count = total - accepted

    raw_agreement = sum(1 for r in valid_rows if r["jev_answer"] == r["original_answer"])
    raw_agreement_pct = round(raw_agreement / total * 100, 1) if total else 0

    selective_agreement = sum(1 for r in accepted_rows if r["jev_answer"] == r["original_answer"])
    selective_agreement_pct = round(selective_agreement / accepted * 100, 1) if accepted else 0

    fallback_rate = round(fallback_count / total * 100, 1) if total else 0

    jev_p50 = round(sorted(jev_latencies)[len(jev_latencies) // 2], 1) if jev_latencies else 0
    jev_p95 = round(sorted(jev_latencies)[int(len(jev_latencies) * 0.95)], 1) if jev_latencies else 0
    orig_p50 = round(sorted(orig_latencies)[len(orig_latencies) // 2], 1) if orig_latencies else 0
    orig_p95 = round(sorted(orig_latencies)[int(len(orig_latencies) * 0.95)], 1) if orig_latencies else 0

    print(f"\n--- Results ---", file=sys.stderr)
    print(f"Total valid pairs: {total}", file=sys.stderr)
    print(f"Accepted (above threshold {threshold}): {accepted}", file=sys.stderr)
    print(f"Fallback rate: {fallback_rate}%", file=sys.stderr)
    print(f"Raw agreement: {raw_agreement}/{total} ({raw_agreement_pct}%)", file=sys.stderr)
    print(f"Selective agreement: {selective_agreement}/{accepted} ({selective_agreement_pct}%)", file=sys.stderr)
    print(f"Jev latency p50/p95: {jev_p50}/{jev_p95} ms", file=sys.stderr)
    print(f"Original latency p50/p95: {orig_p50}/{orig_p95} ms", file=sys.stderr)

    # --- Build parity JSON ---
    parity = {
        "sites": [
            {
                "site_id": "workflow.ts:6",
                "threshold": threshold,
                "n": total,
                "accepted": accepted,
                "fallback_rate_pct": fallback_rate,
                "raw_agreement_pct": raw_agreement_pct,
                "selective_agreement_pct": selective_agreement_pct,
                "jev_latency_p50_ms": jev_p50,
                "jev_latency_p95_ms": jev_p95,
                "original_latency_p50_ms": orig_p50,
                "original_latency_p95_ms": orig_p95,
                "cost_source": "estimated from published pricing as of 2026-09-23: Jev $0.042/M input tokens (output free), gpt-4o-mini $0.15/M input + $0.60/M output",
                "rows": rows,
                "faults": faults,
            }
        ]
    }

    output_path = os.path.join(CONVERTED_DIR, "JEV_PARITY.json")
    with open(output_path, "w") as f:
        json.dump(parity, f, indent=2)
    print(f"\nParity written to {output_path}", file=sys.stderr)

    # Return summary for report
    summary = {
        "total": total,
        "accepted": accepted,
        "fallback_rate": fallback_rate,
        "raw_agreement": raw_agreement_pct,
        "selective_agreement": selective_agreement_pct,
        "jev_p50": jev_p50,
        "jev_p95": jev_p95,
        "orig_p50": orig_p50,
        "orig_p95": orig_p95,
        "faults": faults,
        "all_faults_pass": all(faults.values()),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
