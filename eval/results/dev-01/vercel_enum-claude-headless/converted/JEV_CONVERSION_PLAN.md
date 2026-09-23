# Jev Conversion Plan

## Source
- **Repository**: vercel/ai examples (vercel_enum)
- **Source revision**: `709e2e2a68c8c389ace54287a676237fe8b561f2`
- **Output mode**: branch `jev-convert/evaluation` (cloned to converted/)
- **Risk posture**: conservative (fallback always retained)
- **Provider**: OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin**: `typesafe/jev-1.13-20260917`

## Audit

| Site | Provider | Downstream | Classification | Fit | Selected Option |
|------|----------|-----------|----------------|-----|-----------------|
| `workflow.ts:6` | Vercel AI SDK / OpenAI gpt-4o-mini | `result.object` (genre enum) logged; `result.usage` and `result.finishReason` also logged | DECISION | FIT | **fallback** (Choice) |

### Site: workflow.ts:6 — generateObject with enum output

**Input**: Fixed hardcoded movie plot prompt (trusted, benign, small context).

**Output**: One of `['action', 'comedy', 'drama', 'horror', 'sci-fi']` — a pure closed-set label selection.

**Observable contract**:
- `result.object`: genre string (stdout)
- `result.usage`: `{promptTokens, completionTokens, totalTokens}` (stdout)
- `result.finishReason`: string (stdout)

**Options presented**:
1. **fallback** (Choice) — Try Jev Choice first; on high confidence accept Jev answer with real Jev usage mapped to Vercel SDK shape. On low confidence, error, or missing key, fall back to original generateObject unchanged. Conservative: fallback always retained.
2. **leave** — No change.

## Headless Approval Resolution

Config approval predicate: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."

- `workflow.ts:6` is a pure DECISION site with enumerated outputs → **approved for fallback**.

## Selected Plan

1. Create `jevDecisions.ts` — single decisions module owning model pin, question definition, criteria, threshold, and HTTP adapter (dependency-free, using Node fetch against OpenRouter System One endpoint).
2. Modify `workflow.ts` — try Jev classification first; accept on confidence ≥ threshold; preserve `result.object`, `result.usage` shape (mapped from Jev usage), and `result.finishReason`; fall back to original on any failure/low-confidence/missing key.
3. Diagnostic logging via `process.stderr.write` (non-intrusive; does not alter stdout contract).

## Preflight Facts
- Git clean, no untracked files
- Branch `jev-convert/evaluation` created in clone at converted/
- Original ref: `main` at `709e2e2a`
- No package.json in project; dependency-free HTTP adapter used (no new framework)
