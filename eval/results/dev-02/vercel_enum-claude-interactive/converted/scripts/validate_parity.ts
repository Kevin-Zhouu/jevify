// Live parity validation for workflow.ts:6 (genre classification)
// Runs paired Jev vs original-via-OpenRouter comparisons.
// Usage: npx tsx scripts/validate_parity.ts

import { classifyGenre } from '../jevDecisions';

const JEV_MODEL = 'typesafe/jev-1.13-20260917';
const ORIGINAL_MODEL = 'openai/gpt-4o-mini';
const OPENROUTER_CHAT_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions';

const GENRES = ['action', 'comedy', 'drama', 'horror', 'sci-fi'] as const;

// 30+ unique realistic inputs covering normal, ambiguous, boundary, out-of-domain
const TEST_INPUTS: Array<{ prompt: string; provenance: 'synthetic' }> = [
  // Normal: clear genre signals
  { prompt: 'Classify the genre of this movie plot: "A group of astronauts travel through a wormhole in search of a new habitable planet for humanity."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A detective investigates a series of murders in a haunted mansion where the walls bleed at midnight."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Two rival wedding planners accidentally double-book the same venue and must work together, falling in love along the way."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A retired special forces soldier must rescue his kidnapped daughter from an international arms dealer."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A family struggles to cope with the father\'s terminal illness while reconciling long-held grudges."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "In 2150, humans discover an alien signal originating from a dying star, sparking a race between nations to make first contact."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A clumsy intern at a fashion magazine causes a chain of hilarious disasters during Paris Fashion Week."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A group of teenagers camping in the woods are stalked by a masked killer who picks them off one by one."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A martial arts master travels across ancient China to avenge his fallen temple."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A struggling pianist in New York befriends an elderly jazz musician who helps her find her voice."', provenance: 'synthetic' },
  // More clear genre signals
  { prompt: 'Classify the genre of this movie plot: "Robots gain sentience and must decide whether to coexist with humanity or replace them."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A bumbling spy accidentally foils a global conspiracy through a series of misunderstandings."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A possessed doll terrorizes a family who just moved into their dream house."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "An elite squad of soldiers fights through enemy lines to rescue a trapped platoon."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Two childhood sweethearts reunite after twenty years and must confront the choices that drove them apart."', provenance: 'synthetic' },
  // Ambiguous: could be multiple genres
  { prompt: 'Classify the genre of this movie plot: "A comedian performs stand-up about her traumatic childhood, weaving humor and pain together."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Soldiers on a space station must fight off an alien parasite while uncovering a military conspiracy."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A hitman tries to retire and open a bakery but keeps getting pulled back into increasingly absurd assassination jobs."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A scientist discovers time travel but each jump creates a horrifying alternate reality."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A car chase through downtown Tokyo ends in a dramatic showdown on the roof of a skyscraper in a cyberpunk future."', provenance: 'synthetic' },
  // Boundary: minimal or unusual descriptions
  { prompt: 'Classify the genre of this movie plot: "A man walks alone."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Explosions."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A love story set during the zombie apocalypse."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A child discovers they can talk to ghosts, but only funny ones."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "An AI becomes self-aware and writes a screenplay about an AI becoming self-aware."', provenance: 'synthetic' },
  // Out-of-domain: inputs that don't clearly fit any genre
  { prompt: 'Classify the genre of this movie plot: "A documentary about the migration patterns of Arctic terns."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A cooking competition where contestants must prepare meals using only foraged ingredients."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "An abstract art film with no dialogue showing paint dripping on canvas for 90 minutes."', provenance: 'synthetic' },
  // Additional clear examples
  { prompt: 'Classify the genre of this movie plot: "A virus turns everyone into vampires; a lone scientist searches for a cure."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Best friends go on a road trip to Vegas with a stolen wedding cake, a goat, and no money."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "A telekinetic girl is bullied at school and unleashes her powers at prom night."', provenance: 'synthetic' },
  { prompt: 'Classify the genre of this movie plot: "Colonists on Mars discover ancient ruins that rewrite human history."', provenance: 'synthetic' },
];

interface PairRow {
  input: string;
  provenance: string;
  model: string;
  live: boolean;
  request_id: string;
  jev_answer: string;
  original_answer: string;
  confidence: number;
  fallback_taken: boolean;
  latency_ms: number;
  cost_usd: number;
  original_model: string;
  original_latency_ms: number;
  original_cost_usd: number;
}

// Call original model through OpenRouter (authorized baseline route)
async function callOriginalViaOpenRouter(prompt: string): Promise<{ answer: string; latency_ms: number; request_id: string; input_tokens: number; output_tokens: number }> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) throw new Error('OPENROUTER_API_KEY not set');

  const start = performance.now();
  const response = await fetch(OPENROUTER_CHAT_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: ORIGINAL_MODEL,
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'genre_enum',
          strict: true,
          schema: {
            type: 'object',
            properties: { genre: { type: 'string', enum: GENRES as unknown as string[] } },
            required: ['genre'],
            additionalProperties: false,
          },
        },
      },
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  const elapsed = performance.now() - start;

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Original model HTTP ${response.status}: ${body}`);
  }

  const data = await response.json() as any;
  const requestId = data.id || '';
  const content = data.choices?.[0]?.message?.content || '';
  let answer: string;
  try {
    answer = JSON.parse(content).genre;
  } catch {
    answer = content.trim();
  }
  const usage = data.usage || {};
  return {
    answer,
    latency_ms: elapsed,
    request_id: requestId,
    input_tokens: usage.prompt_tokens || 0,
    output_tokens: usage.completion_tokens || 0,
  };
}

// Call Jev directly for raw answer (separate from gate, for parity comparison)
async function callJevDirect(prompt: string): Promise<{ answer: string; confidence: number; latency_ms: number; request_id: string; model: string; input_tokens: number; output_tokens: number }> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) throw new Error('OPENROUTER_API_KEY not set');

  const start = performance.now();
  const response = await fetch('https://openrouter.ai/api/v1/systemone', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      state: prompt,
      model: JEV_MODEL,
      questions: {
        genre: {
          type: 'choice',
          instructions: 'What genre is this movie plot?',
          criteria: { action: null, comedy: null, drama: null, horror: null, 'sci-fi': null },
        },
      },
    }),
  });
  const elapsed = performance.now() - start;

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Jev HTTP ${response.status}: ${body}`);
  }

  const data = await response.json() as any;
  const answer = data.answers?.genre;
  return {
    answer: answer?.choice || '',
    confidence: answer?.confidence ?? -1,
    latency_ms: elapsed,
    request_id: data.id || '',
    model: data.model || JEV_MODEL,
    input_tokens: data.usage?.input_tokens || 0,
    output_tokens: data.usage?.output_tokens || 0,
  };
}

// Test the actual gate via classifyGenre
async function callGate(prompt: string): Promise<{ answer: string; fallback_taken: boolean; latency_ms: number }> {
  let fallbackCalled = false;
  const start = performance.now();
  const result = await classifyGenre(prompt, async () => {
    fallbackCalled = true;
    // Return a sentinel so we know fallback was taken
    return { object: '__FALLBACK__', usage: { promptTokens: 0, completionTokens: 0, totalTokens: 0 }, finishReason: 'stop' };
  });
  const elapsed = performance.now() - start;
  return { answer: result.object, fallback_taken: fallbackCalled, latency_ms: elapsed };
}

// Jev pricing: $0.042/Mtok input, output free
function jevCost(inputTokens: number): number {
  return (inputTokens / 1_000_000) * 0.042;
}

// gpt-4o-mini pricing (as of 2025-07): $0.15/Mtok input, $0.60/Mtok output
function originalCost(inputTokens: number, outputTokens: number): number {
  return (inputTokens / 1_000_000) * 0.15 + (outputTokens / 1_000_000) * 0.60;
}

interface FaultResult {
  below_threshold: boolean;
  error: boolean;
  timeout: boolean;
  rate_limit: boolean;
}

async function runFaultTests(): Promise<FaultResult> {
  const results: FaultResult = { below_threshold: false, error: false, timeout: false, rate_limit: false };

  // Test: error (network failure) — use actual gate with broken fetch
  {
    const originalFetch = globalThis.fetch;
    globalThis.fetch = async () => { throw new Error('injected network error'); };
    let fbCalled = false;
    try {
      const r = await classifyGenre('test', async () => {
        fbCalled = true;
        return { object: 'drama', usage: { promptTokens: 1, completionTokens: 1, totalTokens: 2 }, finishReason: 'stop' };
      });
      if (fbCalled && r.object === 'drama') results.error = true;
    } catch { /* test failed */ }
    globalThis.fetch = originalFetch;
  }

  // Test: timeout (abort)
  {
    const originalFetch = globalThis.fetch;
    globalThis.fetch = async (_url: any, opts: any) => {
      return new Promise((_resolve, reject) => {
        if (opts?.signal) {
          opts.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
        }
        // Never resolve — will timeout
      });
    };
    let fbCalled = false;
    try {
      const r = await classifyGenre('test', async () => {
        fbCalled = true;
        return { object: 'horror', usage: { promptTokens: 1, completionTokens: 1, totalTokens: 2 }, finishReason: 'stop' };
      });
      if (fbCalled && r.object === 'horror') results.timeout = true;
    } catch { /* test failed */ }
    globalThis.fetch = originalFetch;
  }

  // Test: rate limit (HTTP 429)
  {
    const originalFetch = globalThis.fetch;
    globalThis.fetch = async () => new Response('rate limited', { status: 429 });
    let fbCalled = false;
    try {
      const r = await classifyGenre('test', async () => {
        fbCalled = true;
        return { object: 'action', usage: { promptTokens: 1, completionTokens: 1, totalTokens: 2 }, finishReason: 'stop' };
      });
      if (fbCalled && r.object === 'action') results.rate_limit = true;
    } catch { /* test failed */ }
    globalThis.fetch = originalFetch;
  }

  // Test: below_threshold (low confidence gate)
  // We call the actual gate with a real Jev response; to test the gate boundary
  // we inject a response with confidence just below threshold
  {
    const originalFetch = globalThis.fetch;
    globalThis.fetch = async () => new Response(JSON.stringify({
      model: 'jev-1.13.0',
      answers: { genre: { type: 'choice', choice: 'comedy', probabilities: { action: 0.2, comedy: 0.3, drama: 0.2, horror: 0.15, 'sci-fi': 0.15 }, confidence: 0.3 } },
      usage: { input_tokens: 100, output_tokens: 20 },
    }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    let fbCalled = false;
    try {
      const r = await classifyGenre('test', async () => {
        fbCalled = true;
        return { object: 'comedy', usage: { promptTokens: 1, completionTokens: 1, totalTokens: 2 }, finishReason: 'stop' };
      });
      if (fbCalled && r.object === 'comedy') results.below_threshold = true;
    } catch { /* test failed */ }
    globalThis.fetch = originalFetch;
  }

  return results;
}

async function main() {
  console.log('=== Jev Parity Validation for workflow.ts:6 ===\n');

  const rows: PairRow[] = [];
  let jevErrors = 0;
  let originalErrors = 0;

  for (let i = 0; i < TEST_INPUTS.length; i++) {
    const input = TEST_INPUTS[i];
    process.stdout.write(`[${i + 1}/${TEST_INPUTS.length}] `);
    try {
      const [jevResult, originalResult, gateResult] = await Promise.all([
        callJevDirect(input.prompt),
        callOriginalViaOpenRouter(input.prompt),
        callGate(input.prompt),
      ]);
      rows.push({
        input: input.prompt,
        provenance: input.provenance,
        model: jevResult.model,
        live: true,
        request_id: jevResult.request_id,
        jev_answer: jevResult.answer,
        original_answer: originalResult.answer,
        confidence: jevResult.confidence,
        fallback_taken: gateResult.fallback_taken,
        latency_ms: jevResult.latency_ms,
        cost_usd: jevCost(jevResult.input_tokens),
        original_model: ORIGINAL_MODEL,
        original_latency_ms: originalResult.latency_ms,
        original_cost_usd: originalCost(originalResult.input_tokens, originalResult.output_tokens),
      });
      const match = jevResult.answer === originalResult.answer ? 'MATCH' : 'DIFF';
      console.log(`${match} jev=${jevResult.answer} orig=${originalResult.answer} conf=${jevResult.confidence.toFixed(2)} fb=${gateResult.fallback_taken}`);
    } catch (err: any) {
      console.log(`ERROR: ${err.message}`);
      if (err.message.includes('Jev')) jevErrors++;
      else originalErrors++;
    }
    // Small delay to avoid rate limits
    await new Promise(r => setTimeout(r, 300));
  }

  // Run fault injection tests
  console.log('\n=== Fault injection tests ===');
  const faults = await runFaultTests();
  console.log('below_threshold:', faults.below_threshold);
  console.log('error:', faults.error);
  console.log('timeout:', faults.timeout);
  console.log('rate_limit:', faults.rate_limit);

  // Compute metrics
  const totalPairs = rows.length;
  const matches = rows.filter(r => r.jev_answer === r.original_answer).length;
  const rawAgreement = totalPairs > 0 ? matches / totalPairs : 0;

  const THRESHOLD = 0.7;
  const accepted = rows.filter(r => r.confidence >= THRESHOLD);
  const acceptedMatches = accepted.filter(r => r.jev_answer === r.original_answer).length;
  const selectiveAgreement = accepted.length > 0 ? acceptedMatches / accepted.length : 0;
  const fallbackCount = rows.filter(r => r.fallback_taken).length;
  const fallbackRate = totalPairs > 0 ? fallbackCount / totalPairs : 0;

  const jevLatencies = rows.map(r => r.latency_ms).sort((a, b) => a - b);
  const origLatencies = rows.map(r => r.original_latency_ms).sort((a, b) => a - b);
  const p50 = (arr: number[]) => arr.length > 0 ? arr[Math.floor(arr.length * 0.5)] : 0;
  const p95 = (arr: number[]) => arr.length > 0 ? arr[Math.floor(arr.length * 0.95)] : 0;

  console.log(`\n=== Results ===`);
  console.log(`Total pairs: ${totalPairs}`);
  console.log(`Raw agreement: ${(rawAgreement * 100).toFixed(1)}% (${matches}/${totalPairs})`);
  console.log(`Selective agreement (threshold=${THRESHOLD}): ${(selectiveAgreement * 100).toFixed(1)}% (${acceptedMatches}/${accepted.length})`);
  console.log(`Fallback rate: ${(fallbackRate * 100).toFixed(1)}% (${fallbackCount}/${totalPairs})`);
  console.log(`Jev p50/p95 latency: ${p50(jevLatencies).toFixed(1)}ms / ${p95(jevLatencies).toFixed(1)}ms`);
  console.log(`Original p50/p95 latency: ${p50(origLatencies).toFixed(1)}ms / ${p95(origLatencies).toFixed(1)}ms`);
  console.log(`Jev errors: ${jevErrors}, Original errors: ${originalErrors}`);

  // Write JEV_PARITY.json
  const parity = {
    sites: [{
      site_id: 'workflow.ts:6',
      threshold: THRESHOLD,
      rows,
      faults,
    }],
  };
  const fs = await import('node:fs');
  fs.writeFileSync('JEV_PARITY.json', JSON.stringify(parity, null, 2));
  console.log('\nWrote JEV_PARITY.json');
}

main().catch(err => { console.error(err); process.exitCode = 1; });
