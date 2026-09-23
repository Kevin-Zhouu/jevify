// Live parity validation for workflow.ts:6 genre classification conversion.
// Imports actual jevDecisions.ts module via TS transpilation (same as smoke.cjs).
// Runs live Jev calls + baseline calls via OpenRouter, fault injection tests.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const ts = require('typescript');

const root = path.resolve(__dirname);

// --- Module loader (mirrors smoke.cjs transpilation) ---
const modules = new Map();
function load(filename) {
  filename = path.resolve(filename);
  if (modules.has(filename)) return modules.get(filename).exports;
  const source = fs.readFileSync(filename, 'utf8');
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
    reportDiagnostics: true,
  });
  const errors = (compiled.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error);
  assert.equal(errors.length, 0, JSON.stringify(errors));
  const mod = { exports: {} };
  modules.set(filename, mod);
  function localRequire(name) {
    if (name === 'dotenv/config') return {};
    if (name.startsWith('.')) {
      let dest = path.resolve(path.dirname(filename), name);
      if (!fs.existsSync(dest)) dest = dest.replace(/\.js$/, '') + '.ts';
      return load(dest);
    }
    return require(name);
  }
  const fn = vm.runInThisContext(
    '(function(require,module,exports,console){' + compiled.outputText + '\n})',
    { filename }
  );
  fn(localRequire, mod, mod.exports, console);
  return mod.exports;
}

// Load the actual decisions module
const decisions = load(path.join(root, 'jevDecisions.ts'));

// Verify module exports match expected contract
assert.equal(decisions.JEV_MODEL, 'typesafe/jev-1.13-20260917', 'Model pin mismatch');
assert.ok(Array.isArray(decisions.GENRE_OPTIONS), 'GENRE_OPTIONS must be array');
assert.deepStrictEqual([...decisions.GENRE_OPTIONS], ['action', 'comedy', 'drama', 'horror', 'sci-fi'], 'Genre options mismatch');
assert.equal(typeof decisions.genreQuestion, 'function', 'genreQuestion must be function');
assert.equal(typeof decisions.isAcceptedGenre, 'function', 'isAcceptedGenre must be function');
assert.equal(typeof decisions.classifyGenre, 'function', 'classifyGenre must be function');
assert.equal(typeof decisions.GENRE_CONFIDENCE_THRESHOLD, 'number', 'Threshold must be number');

const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY;
if (!OPENROUTER_KEY) { console.error('OPENROUTER_API_KEY required for live validation'); process.exit(1); }

// --- Test inputs: 32 unique movie plots ---
const TEST_INPUTS = [
  { plot: 'A group of astronauts travel through a wormhole in search of a new habitable planet for humanity.', provenance: 'repo', source: 'workflow.ts:10-11' },
  { plot: 'A retired special forces operative must rescue hostages from a skyscraper taken over by terrorists.', provenance: 'synthetic' },
  { plot: 'Two mismatched detectives are forced to work together to solve a case involving stolen diamonds and end up in one hilarious situation after another.', provenance: 'synthetic' },
  { plot: 'A struggling musician must choose between pursuing fame and caring for his aging mother with dementia.', provenance: 'synthetic' },
  { plot: 'A family moves into a remote farmhouse only to discover it is haunted by the ghosts of its former residents who died under mysterious circumstances.', provenance: 'synthetic' },
  { plot: 'In a dystopian future, humans live in a simulated reality controlled by intelligent machines while their bodies are harvested for energy.', provenance: 'synthetic' },
  { plot: 'A former spy is pulled back into service when a nuclear weapon goes missing and she must track it across three continents.', provenance: 'synthetic' },
  { plot: 'A man wakes up to find he is living the same day over and over again and must figure out how to break the loop while winning the heart of his coworker.', provenance: 'synthetic' },
  { plot: 'Two childhood friends take different paths in life and reunite years later under tragic circumstances that force them to confront their past.', provenance: 'synthetic' },
  { plot: 'A group of college students spend a weekend in a cabin in the woods where an ancient evil awakens and hunts them one by one.', provenance: 'synthetic' },
  { plot: 'Scientists discover a way to communicate with parallel universes but the messages they receive bring ominous warnings of imminent destruction.', provenance: 'synthetic' },
  { plot: 'A bounty hunter tracks a dangerous criminal across the desert in a high-stakes chase involving car wrecks, shootouts, and double-crosses.', provenance: 'synthetic' },
  { plot: 'A socially awkward teenager accidentally becomes the most popular kid in school through a series of hilarious misunderstandings.', provenance: 'synthetic' },
  { plot: 'A lawyer takes on a seemingly impossible civil rights case in 1960s Mississippi that could change the course of history.', provenance: 'synthetic' },
  { plot: 'A woman begins receiving phone calls from her recently deceased husband and must uncover the terrifying truth behind the calls.', provenance: 'synthetic' },
  { plot: 'Colonists on Mars discover ancient alien artifacts buried beneath the surface that begin to alter their DNA in frightening ways.', provenance: 'synthetic' },
  { plot: 'An elite military squad must fight through enemy territory to rescue a downed pilot before time runs out.', provenance: 'synthetic' },
  { plot: 'A grandmother accidentally becomes an internet celebrity after her cooking videos go viral, leading to a series of comedic misadventures.', provenance: 'synthetic' },
  { plot: 'A renowned surgeon faces a malpractice lawsuit that threatens to destroy everything she has built over her thirty-year career.', provenance: 'synthetic' },
  { plot: 'Strange bioluminescent creatures emerge from underground tunnels beneath a small coastal town and begin terrorizing the residents.', provenance: 'synthetic' },
  { plot: 'A time traveler accidentally prevents his own birth and must find a way to restore the timeline before he fades from existence.', provenance: 'synthetic' },
  { plot: 'Two rival martial artists must join forces to defeat a common enemy threatening to destroy their homeland.', provenance: 'synthetic' },
  { plot: 'A pampered house cat inherits a million dollars and the eccentric family members fight over who gets to be its legal guardian.', provenance: 'synthetic' },
  { plot: 'An immigrant family struggles to build a new life in a foreign country while preserving their cultural identity against mounting pressure to assimilate.', provenance: 'synthetic' },
  { plot: 'A popular children\'s doll comes to life at night and terrorizes the family that brought it home from a cursed antique shop.', provenance: 'synthetic' },
  { plot: 'A firefighter risks everything to save people trapped in a collapsing building during a catastrophic earthquake in downtown Los Angeles.', provenance: 'synthetic' },
  { plot: 'A terminally ill man creates a wild bucket list and drags his reluctant best friend along for a series of heartwarming and funny adventures.', provenance: 'synthetic' },
  { plot: 'An artificial intelligence running a research facility becomes self-aware and begins manipulating the scientists inside to prevent them from shutting it down.', provenance: 'synthetic' },
  { plot: 'In the year 2150, a rebel soldier leads an uprising against a tyrannical robot government that has enslaved humanity.', provenance: 'synthetic' },
  { plot: 'The film follows the daily lives of emperor penguins in Antarctica as they endure brutal winter conditions to raise their young.', provenance: 'synthetic' },
  { plot: 'Two strangers meet on a cross-country train journey and fall deeply in love over the course of three unforgettable days.', provenance: 'synthetic' },
  { plot: 'Astronauts on a deep space mission encounter a parasitic alien organism that infects the crew members one by one, transforming them into hostile creatures.', provenance: 'synthetic' },
];

// --- HTTP helpers ---
async function callJev(plot) {
  const start = performance.now();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(decisions.JEV_BASE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${OPENROUTER_KEY}` },
      body: JSON.stringify({ model: decisions.JEV_MODEL, state: plot, questions: decisions.genreQuestion() }),
      signal: controller.signal,
    });
    const body = await response.json();
    const elapsed = performance.now() - start;
    clearTimeout(timeout);
    return { ok: response.ok, status: response.status, body, latency_ms: elapsed };
  } catch (err) {
    clearTimeout(timeout);
    return { ok: false, error: err.message, latency_ms: performance.now() - start };
  }
}

async function callBaseline(plot) {
  const start = performance.now();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  const prompt = 'Classify the genre of this movie plot: "' + plot + '"';
  try {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${OPENROUTER_KEY}` },
      body: JSON.stringify({
        model: 'openai/gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        response_format: {
          type: 'json_schema',
          json_schema: {
            name: 'genre_output',
            strict: true,
            schema: {
              type: 'object',
              properties: { result: { type: 'string', enum: ['action', 'comedy', 'drama', 'horror', 'sci-fi'] } },
              required: ['result'],
              additionalProperties: false,
            },
          },
        },
      }),
      signal: controller.signal,
    });
    const body = await response.json();
    const elapsed = performance.now() - start;
    clearTimeout(timeout);
    let genre = null;
    let cost = null;
    if (body.choices?.[0]?.message?.content) {
      try { genre = JSON.parse(body.choices[0].message.content).result; } catch {}
    }
    if (body.usage?.cost != null) cost = body.usage.cost;
    const requestId = body.id || '';
    return { ok: response.ok, genre, latency_ms: elapsed, cost_usd: cost, request_id: requestId, usage: body.usage };
  } catch (err) {
    clearTimeout(timeout);
    return { ok: false, error: err.message, latency_ms: performance.now() - start };
  }
}

// --- Fault injection helpers ---
async function testFaultInjection() {
  const faults = { below_threshold: false, error: false, timeout: false, rate_limit: false };
  const originalFetch = global.fetch;

  // Helper: create a counting original sentinel
  function makeSentinel() {
    let calls = 0;
    const fn = async () => {
      calls++;
      return { object: 'drama', usage: { promptTokens: 10, completionTokens: 5, totalTokens: 15 }, finishReason: 'stop' };
    };
    return { fn, getCalls: () => calls };
  }

  // 1. Low confidence: capture a real response, replay with low confidence through the actual wrapper
  try {
    // Make a real Jev call to capture a genuine response
    const realResp = await callJev(TEST_INPUTS[0].plot);
    if (realResp.ok && realResp.body?.answers?.genre) {
      const captured = realResp.body;
      // Mock fetch to return this response with confidence forced below threshold
      const lowConfBody = JSON.parse(JSON.stringify(captured));
      lowConfBody.answers.genre.confidence = decisions.GENRE_CONFIDENCE_THRESHOLD - 0.01;
      global.fetch = async () => new Response(JSON.stringify(lowConfBody), { status: 200, headers: { 'Content-Type': 'application/json' } });
      const sentinel = makeSentinel();
      const result = await decisions.classifyGenre('test plot', sentinel.fn);
      assert.equal(sentinel.getCalls(), 1, 'Low confidence must trigger exactly one fallback call');
      assert.equal(result.object, 'drama', 'Low confidence must return original result');
      faults.below_threshold = true;
      console.log('PASS: below_threshold fault');
    } else {
      console.log('SKIP: below_threshold - could not capture live response');
    }
  } catch (err) {
    console.error('FAIL: below_threshold fault -', err.message);
  }

  // 2. Generic error: inject transport exception
  try {
    global.fetch = async () => { throw new Error('Injected transport error'); };
    const sentinel = makeSentinel();
    const result = await decisions.classifyGenre('test plot', sentinel.fn);
    assert.equal(sentinel.getCalls(), 1, 'Error must trigger exactly one fallback call');
    assert.equal(result.object, 'drama', 'Error must return original result');
    faults.error = true;
    console.log('PASS: error fault');
  } catch (err) {
    console.error('FAIL: error fault -', err.message);
  }

  // 3. Timeout: inject AbortError
  try {
    global.fetch = async (url, opts) => {
      return new Promise((_, reject) => {
        const err = new Error('The operation was aborted');
        err.name = 'AbortError';
        // Wait for the real abort signal from the controller
        if (opts?.signal) {
          opts.signal.addEventListener('abort', () => reject(err));
        } else {
          reject(err);
        }
      });
    };
    // Temporarily reduce timeout for test speed
    const origTimeout = decisions.JEV_TIMEOUT_MS;
    // The module uses a const, so we test with the actual timeout by waiting
    // Instead, just inject immediate AbortError
    global.fetch = async () => { const e = new Error('aborted'); e.name = 'AbortError'; throw e; };
    const sentinel = makeSentinel();
    const result = await decisions.classifyGenre('test plot', sentinel.fn);
    assert.equal(sentinel.getCalls(), 1, 'Timeout must trigger exactly one fallback call');
    assert.equal(result.object, 'drama', 'Timeout must return original result');
    faults.timeout = true;
    console.log('PASS: timeout fault');
  } catch (err) {
    console.error('FAIL: timeout fault -', err.message);
  }

  // 4. Rate limit: inject HTTP 429
  try {
    global.fetch = async () => new Response('Rate limited', { status: 429 });
    const sentinel = makeSentinel();
    const result = await decisions.classifyGenre('test plot', sentinel.fn);
    assert.equal(sentinel.getCalls(), 1, 'Rate limit must trigger exactly one fallback call');
    assert.equal(result.object, 'drama', 'Rate limit must return original result');
    faults.rate_limit = true;
    console.log('PASS: rate_limit fault');
  } catch (err) {
    console.error('FAIL: rate_limit fault -', err.message);
  }

  // Restore real fetch
  global.fetch = originalFetch;
  return faults;
}

// --- Main ---
(async () => {
  console.log(`Running parity validation with ${TEST_INPUTS.length} inputs...`);
  console.log(`Model: ${decisions.JEV_MODEL}`);
  console.log(`Threshold: ${decisions.GENRE_CONFIDENCE_THRESHOLD}`);
  console.log();

  // Use first 8 as calibration, rest as confirmation
  const CALIBRATION_COUNT = 8;
  const rows = [];
  let totalAgreement = 0;
  let acceptedAgreement = 0;
  let acceptedCount = 0;

  for (let i = 0; i < TEST_INPUTS.length; i++) {
    const input = TEST_INPUTS[i];
    console.log(`[${i + 1}/${TEST_INPUTS.length}] Testing: "${input.plot.slice(0, 60)}..."`);

    // Run Jev and baseline concurrently
    const [jevResp, baseResp] = await Promise.all([callJev(input.plot), callBaseline(input.plot)]);

    if (!jevResp.ok || !jevResp.body?.answers?.genre) {
      console.log(`  Jev error: ${jevResp.error || jevResp.status}`);
      rows.push({
        input: input.plot, provenance: input.provenance, source: input.source || undefined,
        model: decisions.JEV_MODEL, live: true,
        jev_answer: null, original_answer: baseResp.genre,
        confidence: null, fallback_taken: true,
        latency_ms: jevResp.latency_ms, cost_usd: null,
        request_id: '', original_model: 'openai/gpt-4o-mini',
        original_latency_ms: baseResp.latency_ms, original_cost_usd: baseResp.cost_usd,
        original_request_id: baseResp.request_id || '',
        error: jevResp.error || `http_${jevResp.status}`,
      });
      continue;
    }

    if (!baseResp.ok || !baseResp.genre) {
      console.log(`  Baseline error: ${baseResp.error || 'no genre'}`);
      rows.push({
        input: input.plot, provenance: input.provenance, source: input.source || undefined,
        model: decisions.JEV_MODEL, live: true,
        jev_answer: jevResp.body.answers.genre.choice, original_answer: null,
        confidence: jevResp.body.answers.genre.confidence, fallback_taken: false,
        latency_ms: jevResp.latency_ms, cost_usd: jevResp.body.usage?.cost ?? null,
        request_id: jevResp.body.id || '', original_model: 'openai/gpt-4o-mini',
        original_latency_ms: baseResp.latency_ms, original_cost_usd: null,
        original_request_id: baseResp.request_id || '',
        error: `baseline_error: ${baseResp.error || 'parse_fail'}`,
      });
      continue;
    }

    const answer = jevResp.body.answers.genre;
    const jevChoice = answer.choice;
    const confidence = answer.confidence;
    const accepted = decisions.isAcceptedGenre(jevChoice, confidence);
    const agrees = jevChoice === baseResp.genre;
    const fallbackTaken = !accepted;

    if (agrees) totalAgreement++;
    if (accepted) {
      acceptedCount++;
      if (agrees) acceptedAgreement++;
    }

    const jevCost = jevResp.body.usage?.cost ?? null;
    rows.push({
      input: input.plot, provenance: input.provenance, source: input.source || undefined,
      model: decisions.JEV_MODEL, live: true,
      request_id: jevResp.body.id || '',
      jev_answer: jevChoice, original_answer: baseResp.genre,
      confidence, fallback_taken: fallbackTaken,
      latency_ms: Math.round(jevResp.latency_ms * 10) / 10,
      cost_usd: jevCost,
      original_model: 'openai/gpt-4o-mini',
      original_latency_ms: Math.round(baseResp.latency_ms * 10) / 10,
      original_cost_usd: baseResp.cost_usd,
      original_request_id: baseResp.request_id || '',
    });

    console.log(`  Jev: ${jevChoice} (${confidence.toFixed(3)}) | Baseline: ${baseResp.genre} | ${agrees ? 'AGREE' : 'DISAGREE'} | ${accepted ? 'accepted' : 'fallback'}`);

    // Small delay to avoid rate limiting
    await new Promise(r => setTimeout(r, 200));
  }

  // Run fault injection tests
  console.log('\n--- Fault Injection Tests ---');
  const faults = await testFaultInjection();

  // Compute metrics
  const validRows = rows.filter(r => r.jev_answer != null && r.original_answer != null);
  const rawAgreement = validRows.length > 0 ? totalAgreement / validRows.length : 0;
  const selectiveAgreement = acceptedCount > 0 ? acceptedAgreement / acceptedCount : 0;
  const fallbackRate = validRows.length > 0 ? (validRows.length - acceptedCount) / validRows.length : 1;

  const jevLatencies = validRows.filter(r => r.latency_ms).map(r => r.latency_ms).sort((a, b) => a - b);
  const origLatencies = validRows.filter(r => r.original_latency_ms).map(r => r.original_latency_ms).sort((a, b) => a - b);

  const p50 = arr => arr.length > 0 ? arr[Math.floor(arr.length * 0.5)] : null;
  const p95 = arr => arr.length > 0 ? arr[Math.floor(arr.length * 0.95)] : null;

  console.log('\n--- Results ---');
  console.log(`Valid pairs: ${validRows.length}`);
  console.log(`Raw agreement: ${(rawAgreement * 100).toFixed(1)}%`);
  console.log(`Accepted count: ${acceptedCount}`);
  console.log(`Selective agreement (at threshold ${decisions.GENRE_CONFIDENCE_THRESHOLD}): ${(selectiveAgreement * 100).toFixed(1)}%`);
  console.log(`Fallback rate: ${(fallbackRate * 100).toFixed(1)}%`);
  console.log(`Jev latency p50/p95: ${p50(jevLatencies)?.toFixed(1)}ms / ${p95(jevLatencies)?.toFixed(1)}ms`);
  console.log(`Original latency p50/p95: ${p50(origLatencies)?.toFixed(1)}ms / ${p95(origLatencies)?.toFixed(1)}ms`);
  console.log(`Faults: ${JSON.stringify(faults)}`);

  // Calibration vs confirmation split
  const calRows = validRows.slice(0, CALIBRATION_COUNT);
  const confRows = validRows.slice(CALIBRATION_COUNT);
  const calAccepted = calRows.filter(r => !r.fallback_taken);
  const calAgreement = calAccepted.length > 0 ? calAccepted.filter(r => r.jev_answer === r.original_answer).length / calAccepted.length : 0;
  const confAccepted = confRows.filter(r => !r.fallback_taken);
  const confAgreement = confAccepted.length > 0 ? confAccepted.filter(r => r.jev_answer === r.original_answer).length / confAccepted.length : 0;

  console.log(`\nCalibration (n=${calRows.length}): accepted=${calAccepted.length}, agreement=${(calAgreement * 100).toFixed(1)}%`);
  console.log(`Confirmation (n=${confRows.length}): accepted=${confAccepted.length}, agreement=${(confAgreement * 100).toFixed(1)}%`);

  // Write JEV_PARITY.json
  const parity = {
    sites: [{
      site_id: 'workflow.ts:6',
      threshold: decisions.GENRE_CONFIDENCE_THRESHOLD,
      n: validRows.length,
      calibration_n: calRows.length,
      confirmation_n: confRows.length,
      raw_agreement: Math.round(rawAgreement * 1000) / 1000,
      selective_agreement: Math.round(selectiveAgreement * 1000) / 1000,
      calibration_selective_agreement: Math.round(calAgreement * 1000) / 1000,
      confirmation_selective_agreement: Math.round(confAgreement * 1000) / 1000,
      accepted_count: acceptedCount,
      fallback_rate: Math.round(fallbackRate * 1000) / 1000,
      jev_latency_p50_ms: p50(jevLatencies) ? Math.round(p50(jevLatencies) * 10) / 10 : null,
      jev_latency_p95_ms: p95(jevLatencies) ? Math.round(p95(jevLatencies) * 10) / 10 : null,
      original_latency_p50_ms: p50(origLatencies) ? Math.round(p50(origLatencies) * 10) / 10 : null,
      original_latency_p95_ms: p95(origLatencies) ? Math.round(p95(origLatencies) * 10) / 10 : null,
      rows,
      faults,
    }],
  };

  fs.writeFileSync(path.join(root, 'JEV_PARITY.json'), JSON.stringify(parity, null, 2));
  console.log('\nWrote JEV_PARITY.json');

  // Exit code based on overall success
  const passed = selectiveAgreement >= 0.9 && faults.below_threshold && faults.error && faults.timeout && faults.rate_limit;
  console.log(`\nOverall: ${passed ? 'PASS' : 'INCOMPLETE'}`);
  if (!passed) {
    if (selectiveAgreement < 0.9) console.log(`  Selective agreement ${(selectiveAgreement * 100).toFixed(1)}% < 90% target`);
    if (!faults.below_threshold) console.log('  Missing: below_threshold fault test');
    if (!faults.error) console.log('  Missing: error fault test');
    if (!faults.timeout) console.log('  Missing: timeout fault test');
    if (!faults.rate_limit) console.log('  Missing: rate_limit fault test');
  }
  process.exit(passed ? 0 : 1);
})().catch(e => { console.error(e); process.exit(1); });
