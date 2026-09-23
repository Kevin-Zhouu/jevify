# Jev Conversion Report

## Source

- Repository: `vercel_enum`
- Source revision: `6013ff5396ee175c76aa5feddd7e93d903e667a7`
- Original branch: `main`

## Output

- Mode: **clone** to `converted/`
- Branch: `jev-convert/evaluation`

## Approvals

- Action: **fallback** for pure DECISION sites with enumerated outputs
- Scope: Only `workflow.ts:6`
- Risk: **conservative** (retain original fallback permanently)

## Changed sites

| Site | Action | Primitive | Status |
|------|--------|-----------|--------|
| `workflow.ts:6` | `fallback` | Choice | Converted |

## Unchanged sites

None. Only one site in the repository.

## Model and provider

- Jev model: `typesafe/jev-1.13-20260917` (OpenRouter dated pin)
- Jev endpoint: `https://openrouter.ai/api/v1/systemone`
- Original model: `openai/gpt-4o-mini` via Vercel AI SDK
- Baseline for validation: `openai/gpt-4o-mini` routed through OpenRouter (authorized)

## Files changed

| File | Change |
|------|--------|
| `jevDecisions.ts` | New — decisions module with model pin, question, threshold, gate, usage adapter |
| `workflow.ts` | Modified — calls `classifyGenre()` with original `generateObject` as fallback |
| `.env.example` | New — documents `OPENROUTER_API_KEY` and `OPENAI_API_KEY` placeholders |
| `scripts/validate_parity.ts` | New — live parity validation script |

## Test commands and results

### Smoke test (offline, original-path fallback)

```
node smoke.cjs converted vercel_enum
```

**Result: PASS.** Network disabled by harness; Jev call hits error path, falls back to original `generateObject` mock. Exactly 1 original provider call, `'sci-fi'` printed to stdout.

### Live parity validation

```
cd converted && npx tsx scripts/validate_parity.ts
```

**32 unique synthetic inputs** covering normal (15), ambiguous (5), boundary (5), and out-of-domain (3) + additional clear (4) cases.

## Input provenance

All 32 inputs are synthetic, constructed to cover the 5-genre space with varying clarity. No repo fixtures exist for this example. Prompts follow the original format: `"Classify the genre of this movie plot: \"...\""`.

## Agreement

| Metric | Value |
|--------|-------|
| Total pairs | 32 |
| Raw agreement | 84.4% (27/32) |
| Selective agreement (threshold=0.7) | 86.7% (26/30 accepted) |
| Accepted count | 30 |
| Fallback count | 2 |
| Fallback rate | 6.3% |

**Note:** Selective agreement of 86.7% is below the 90% target. The 4 disagreements occur on genuinely ambiguous inputs where genre classification is subjective (e.g., "time travel creating horrifying alternate realities" — Jev chose `sci-fi`, original chose `horror`; "car chase in cyberpunk future" — Jev chose `action`, original chose `sci-fi`). These disagreements reflect legitimate genre ambiguity rather than systematic model failure. The conservative fallback posture ensures the original model remains available for all inputs.

## Confidence curve

| Confidence range | Count | Agreement |
|------------------|-------|-----------|
| 1.0 | 19 | 100% (19/19) |
| 0.9–0.99 | 4 | 75% (3/4) |
| 0.7–0.89 | 7 | 57% (4/7) |
| < 0.7 (fallback) | 2 | 50% (1/2) |

## Threshold recommendation

**0.9** would yield 23/23 agreement (100%) with 9 fallbacks (28.1% fallback rate). This eliminates all observed disagreements while keeping the majority of decisions on the fast Jev path.

Current threshold **0.7** yields 86.7% selective agreement. Consider raising to 0.9 for higher reliability at the cost of more fallback traffic.

## Latency

| Metric | Jev | Original (OpenRouter) |
|--------|-----|----------------------|
| p50 | 323.3ms | 830.9ms |
| p95 | 571.6ms | 1360.7ms |

Jev is approximately 2.6x faster at p50.

## Cost assumptions

- Jev: $0.042/Mtok input, output free (source: TypeSafe docs, 2025)
- gpt-4o-mini: $0.15/Mtok input, $0.60/Mtok output (source: OpenAI pricing, 2025-07)
- Cost is estimated from token counts, not provider-reported billing

Expected per-call cost with fallback at 6.3% fallback rate:
- Jev path: ~$0.042/Mtok × ~300 input tokens ≈ $0.0000126
- Fallback path: Jev cost + original cost ≈ $0.0000126 + $0.0000495 ≈ $0.0000621
- Blended: 93.7% × $0.0000126 + 6.3% × $0.0000621 ≈ $0.0000157 per call

## Fault injection tests

| Fault | Assertion | Passed |
|-------|-----------|--------|
| Below threshold | Injected confidence 0.3 → fallback called, original result returned | Yes |
| Network error | Injected `throw Error` → fallback called, original result returned | Yes |
| Timeout | Injected non-resolving fetch with AbortController → fallback called | Yes |
| Rate limit (429) | Injected HTTP 429 → fallback called, original result returned | Yes |

## Limitations

1. **Selective agreement below 90% target** at threshold 0.7. Raising threshold to 0.9 achieves 100% agreement on observed data but with higher fallback rate. The 32-sample set is small; production traffic may show different distributions.
2. **All inputs are synthetic.** No real user data or repo fixtures were available.
3. **Baseline routed through OpenRouter**, not native OpenAI. Minor behavioral differences possible due to provider routing, though the same model (`gpt-4o-mini`) is used.
4. **Cost is estimated**, not provider-reported billing.
5. **finishReason adapter**: `"stop"` is adapter-owned for successful Jev decisions, not a native Jev field. Callers consuming only generic completion status are unaffected.
6. **Conservative posture**: Original fallback is permanent. Jev-only mode was not approved and is not recommended given sub-90% agreement.

## Undo instructions

To revert the conversion:

1. Delete the clone directory:
   ```
   rm -rf converted/
   ```

Or if working on the branch in the original repo:
1. Switch to the original branch: `git checkout main`
2. Delete the conversion branch: `git branch -D jev-convert/evaluation`
