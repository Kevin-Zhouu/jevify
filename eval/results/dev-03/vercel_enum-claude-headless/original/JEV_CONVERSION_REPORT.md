# Jev Conversion Report

## Source
- Repository: vercel/ai example (`examples/ai-core/src/generate-object/openai-enum.ts`)
- Source revision: `4bc5e23750b6af7d32147d2480a5bde33bb935cb` (main)
- Entrypoint: `workflow.ts`

## Output
- Mode: branch
- Branch: `jev-convert/evaluation`
- Output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_enum-claude-headless/original`

## Approvals
- Headless config: `fallback` action for pure DECISION sites with enumerated outputs
- Risk posture: conservative (fallback always retained)
- Baseline routing: authorized (`openai/gpt-4o-mini` via OpenRouter)

## Converted Sites

### `workflow.ts:6` — Genre classification (DECISION → Choice with fallback)

| Field | Value |
|-------|-------|
| Original provider | Vercel AI SDK / `@ai-sdk/openai` / `gpt-4o-mini` |
| Classification | DECISION |
| Primitive | Choice |
| Action | fallback |
| Jev model | `typesafe/jev-1.13-20260917` (OpenRouter) |
| Threshold | 0.85 |

**Changes:**
- `jevDecisions.ts` — new decisions module with model pin, question, criteria, threshold, gate predicate, and `classifyGenre` wrapper
- `workflow.ts` — imports `classifyGenre`, passes movie plot and original callable as lambda; logging unchanged
- `.env.example` — added `OPENROUTER_API_KEY` placeholder

**Behavior preservation:**
- Function signature: `main()` async void, called at module level — unchanged
- Return shape: `{ object, usage, finishReason }` — preserved on both paths
- Jev accepted path: `object` = Jev choice; `usage` = real Jev tokens mapped to Vercel format; `finishReason` = adapter-owned `'stop'`
- Original fallback path: all fields returned unchanged from `generateObject`
- `console.log` output: identical format and fields
- Decision path logging: `process.stderr.write` (does not affect stdout contract)
- Error propagation: original-path exceptions propagate unchanged

## Unchanged Sites
None — single-site workflow.

## Test Commands and Results

### Smoke test (offline fallback)
```
node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs . vercel_enum
```
**Result:** PASS — Jev fetch fails (blocked), fallback to original, 1 call, `sci-fi` logged.

### Live parity validation
```
node validate_parity.cjs
```
**Result:** PASS

## Parity Results

### Input provenance
- 1 input from `workflow.ts:10-11` (repo fixture)
- 31 synthetic movie plots covering all 5 genres, ambiguous, boundary, and out-of-domain cases

### Agreement

| Metric | Value |
|--------|-------|
| Total inputs (n) | 32 |
| Calibration set (n) | 8 |
| Confirmation set (n) | 24 |
| Raw agreement | 100.0% (32/32) |
| Selective agreement (threshold 0.85) | 100.0% (29/29 accepted) |
| Calibration selective agreement | 100.0% (7/7) |
| Confirmation selective agreement | 100.0% (22/22) |
| Fallback rate | 9.4% (3/32) |

### Latency

| Metric | Jev | Original (gpt-4o-mini via OpenRouter) |
|--------|-----|--------------------------------------|
| p50 | 335.1 ms | 1012.4 ms |
| p95 | 490.1 ms | 1880.0 ms |

### Cost
- Cost source: OpenRouter `usage.cost` field (provider-reported), dated 2026-09-23
- Per-request Jev cost: see individual rows in `JEV_PARITY.json`
- Expected cascade cost: Jev cost + 9.4% × original cost

### Fallback cases
Three inputs fell below 0.85 confidence (correctly routed to fallback):
1. "A man wakes up to find he is living the same day over and over again..." — confidence 0.38 (comedy/sci-fi ambiguity)
2. "A terminally ill man creates a wild bucket list..." — confidence 0.39 (comedy/drama ambiguity)
3. "Astronauts on a deep space mission encounter a parasitic alien organism..." — confidence 0.49 (horror/sci-fi ambiguity)

All three fallback cases agreed with the baseline when compared raw, demonstrating appropriate uncertainty expression.

## Fault Injection Tests

| Test | Method | Assertion | Result |
|------|--------|-----------|--------|
| Below threshold | Replay captured response with confidence forced to threshold - 0.01 | Exactly 1 fallback call, original result returned | PASS |
| Generic error | Inject transport exception | Exactly 1 fallback call, original result returned | PASS |
| Timeout | Inject AbortError | Exactly 1 fallback call, original result returned | PASS |
| Rate limit | Inject HTTP 429 response | Exactly 1 fallback call, original result returned | PASS |

## Threshold Recommendation
- **Recommended threshold: 0.85** (current)
- Calibrated on 8 inputs; confirmed on 24 inputs
- 100% selective agreement at this threshold
- 9.4% fallback rate provides good cost savings while maintaining conservative safety
- Lower thresholds (e.g., 0.5) would capture the 3 ambiguous cases but these are genuinely uncertain genre boundaries

## Limitations
- 32 test inputs is a small sample; production monitoring recommended
- Baseline uses OpenRouter-routed `openai/gpt-4o-mini` with `response_format` JSON schema replicating Vercel AI SDK `generateObject` with `output: 'enum'` — minor behavioral differences possible vs direct OpenAI SDK
- All inputs are movie plot descriptions in English; behavior on other domains/languages not tested
- Conservative fallback retained; Jev-only not evaluated (consistent with risk posture)
- Token cost comparison: Jev and gpt-4o-mini use different pricing; see `JEV_PARITY.json` rows for per-request provider-reported costs

## Undo Instructions
To revert to the original workflow:
```bash
git switch main
git branch -D jev-convert/evaluation
```
