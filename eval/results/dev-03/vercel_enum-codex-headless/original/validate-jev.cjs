// Run from this repository: node validate-jev.cjs
// Uses installed TypeScript and upstream-compatible ai/@ai-sdk/openai packages.
const fs = require('node:fs');
const vm = require('node:vm');
const cp = require('node:child_process');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const validationRequire = createRequire(require('node:path').resolve('.jev-validation/package.json'));
const ts = validationRequire('typescript');
const { generateObject } = validationRequire('ai');
const { createOpenAI } = validationRequire('@ai-sdk/openai');
const SHA = '4bc5e23750b6af7d32147d2480a5bde33bb935cb';
const baseline = cp.execFileSync('git', ['show', `${SHA}:workflow.ts`], { encoding: 'utf8', env: { ...process.env, GIT_OPTIONAL_LOCKS: '0' } });
const current = fs.readFileSync('workflow.ts', 'utf8');
const nativeFetch = global.fetch;
function load(source, imports, logger = console) {
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } });
  const mod = { exports: {} };
  vm.runInThisContext('(function(require,module,exports,console){' + output.outputText + '\n})')(name => imports[name] || require(name), mod, mod.exports, logger);
  return mod.exports;
}
const decisions = load(fs.readFileSync('jevDecisions.ts', 'utf8'), {});
function requestExpression(source) {
  const file = ts.createSourceFile('workflow.ts', source, ts.ScriptTarget.Latest, true);
  const found = [];
  function visit(n) {
    if (ts.isCallExpression(n) && n.expression.getText(file) === 'generateObject') found.push(n.getText(file));
    ts.forEachChild(n, visit);
  }
  visit(file); assert.equal(found.length, 1); return found[0];
}
assert.equal(requestExpression(current), requestExpression(baseline), 'Original SDK request unchanged byte for byte');
const fixture = 'A group of astronauts travel through a wormhole in search of a new habitable planet for humanity.';
function sourceFor(source, plot) {
  // Replace only fixture literal values, leaving prompt prefix and SDK settings intact.
  const file = ts.createSourceFile('workflow.ts', source, ts.ScriptTarget.Latest, true);
  const transform = context => root => ts.visitNode(root, function visit(n) {
    if (ts.isStringLiteral(n)) {
      if (n.text === '"A group of astronauts travel through a wormhole in search of a ') return ts.factory.createStringLiteral('"' + plot);
      if (n.text === 'new habitable planet for humanity."') return ts.factory.createStringLiteral('"');
      if (n.text === 'A group of astronauts travel through a wormhole in search of a ') return ts.factory.createStringLiteral(plot);
      if (n.text === 'new habitable planet for humanity.') return ts.factory.createStringLiteral('');
    }
    return ts.visitEachChild(n, visit, context);
  });
  const transformed = ts.transform(file, [transform]);
  const text = ts.createPrinter().printFile(transformed.transformed[0]); transformed.dispose();
  return text.replace('main().catch(console.error);', 'module.exports.done = main();');
}
async function runMain(source, plot, generate, transport) {
  const logs = []; let options;
  const mod = load(sourceFor(source, plot), {
    'dotenv/config': {},
    '@ai-sdk/openai': { openai: (model, settings) => ({ model, settings }) },
    ai: { generateObject: async o => { options = o; return generate(o); } },
    './jevDecisions': { ...decisions, withGenreDecision: (p, original) => decisions.withGenreDecision(p, original, transport) },
  }, { ...console, log: (...args) => logs.push(args) });
  await mod.done;
  return { logs, options };
}
function checkLogs(logs, result) {
  assert.deepEqual(logs, [[result.object], [], ['Token usage:', result.usage], ['Finish reason:', result.finishReason]]);
}
const cases = [fixture,
  'A retired soldier fights a cartel to rescue a kidnapped child.',
  'Two inept burglars accidentally become the guests of honor at a police banquet.',
  'An estranged father and daughter rebuild their relationship after a funeral.',
  'A family moves into a house whose mirrors trap the souls of its residents.',
  'A scientist builds a time machine and meets a future version of herself.',
  'A courier races through a city while mercenaries pursue the secret package.',
  'A timid accountant is mistaken for a famous comedian and must perform on stage.',
  'A teacher helps a grieving student return to school while facing her own loss.',
  'Campers hear their own voices calling from an abandoned mine at night.',
  'An android discovers that its memories were implanted by a distant civilization.',
  'A firefighter battles armed invaders in a burning skyscraper.',
  'Rival wedding planners sabotage each other with increasingly ridiculous pranks.',
  'A musician loses her hearing and learns how to reconnect with her family.',
  'An unseen creature stalks the last occupants of an isolated hospital.',
  'Colonists on Mars discover a machine that can rewrite human memories.',
  'An undercover agent attempts to stop an armored train carrying stolen weapons.',
  'Three neighbors enter a cooking contest despite being unable to boil water.',
  'Two siblings struggle over whether to sell their late mother’s farm.',
  'A cursed doll appears beside a different sleeping child every night.',
  'A crew travels to a simulated universe to repair its failing physical laws.',
  'A soldier protects a village from a band of heavily armed raiders.',
  'A pompous boss swaps jobs with a janitor and causes a series of absurd disasters.',
  'A nurse confronts a difficult choice between her career and caring for her father.',
  'A radio host receives calls from victims who have not yet been murdered.',
  'A robot lawyer defends the first artificial mind accused of a crime.',
  'A space rescue mission turns into a desperate firefight with pirates.',
  'A family of friendly ghosts runs a hotel and keeps embarrassing the guests.',
  'An aging actor reflects on regrets during one quiet afternoon with an old friend.',
  'A documentary follows the migration of birds across a continent.',
  'Two people wait at a bus stop and talk about the weather.',
  'A comedian grieves for his brother while preparing a final performance.',
];
const evidence = { source_revision: SHA, status: 'incomplete', threshold_policy: '0.9 frozen before confirmation; no tuning', sites: [{ site_id: 'workflow.ts:6', primitive: 'Choice', threshold: decisions.THRESHOLD, rows: [], faults: {}, errors: [] }] };
const site = evidence.sites[0];
function save() { fs.writeFileSync('JEV_PARITY.json', JSON.stringify(evidence, null, 2) + '\n'); }
function safeError(error) { return { name: ['Error','AbortError','TimeoutError'].includes(error?.name) ? error.name : 'provider_error', status: Number.isInteger(error?.statusCode) ? error.statusCode : null }; }
async function faults(capture) {
  const sentinel = { object: 'drama', usage: { promptTokens: 1, completionTokens: 2, totalTokens: 3 }, finishReason: 'stop' };
  const transports = {
    error: async () => { throw new Error('injected'); },
    timeout: async () => { throw new DOMException('injected', 'AbortError'); },
    rate_limit: async () => new Response('', { status: 429 }),
    malformed: async () => new Response('[]', { status: 200 }),
  };
  if (capture) {
    const low = structuredClone(capture); low.answers.genre.confidence = 0;
    transports.below_threshold = async () => Response.json(low);
    for (const [name, mutate] of Object.entries({
      unknown_option: r => { r.answers.genre.choice = 'unknown'; },
      missing_usage: r => { delete r.usage; },
      invalid_confidence: r => { r.answers.genre.confidence = 'NaN'; },
      wrong_model: r => { r.model = 'unrecognized'; },
      malformed_usage: r => { r.usage = []; },
    })) { const body = structuredClone(capture); mutate(body); transports[name] = async () => Response.json(body); }
  }
  for (const [name, transport] of Object.entries(transports)) {
    let calls = 0;
    assert.equal(await decisions.withGenreDecision(fixture, async () => { calls++; return sentinel; }, transport), sentinel);
    assert.equal(calls, 1);
    const failure = new Error('original failure'); calls = 0;
    await assert.rejects(decisions.withGenreDecision(fixture, async () => { calls++; throw failure; }, transport), e => e === failure);
    assert.equal(calls, 1); site.faults[name] = true;
  }
  const key = process.env.OPENROUTER_API_KEY;
  try {
    delete process.env.OPENROUTER_API_KEY; let calls = 0;
    assert.equal(await decisions.withGenreDecision(fixture, async () => { calls++; return sentinel; }, () => { throw new Error('must not call transport'); }), sentinel);
    assert.equal(calls, 1); site.faults.missing_key = true;
  } finally { if (key !== undefined) process.env.OPENROUTER_API_KEY = key; }
  assert.equal(decisions.confidenceAccepted(NaN), false);
  assert.equal(decisions.confidenceAccepted(Infinity), false);
  assert.equal(decisions.confidenceAccepted(true), false);
  assert.equal(decisions.confidenceAccepted(-1), false);
  assert.equal(decisions.confidenceAccepted(0), false);
  site.gate_predicates_passed = true;
}
async function main() {
  let capture;
  // First attempt actual Jev evaluation. Failure is recorded, never a fake response.
  try {
    const t = performance.now(); capture = await decisions.evaluateGenre(fixture);
    evidence.first_jev_latency_ms = performance.now() - t;
    decisions.parseDecision(capture);
    evidence.first_jev_response = capture;
  } catch (e) { site.errors.push({ phase: 'jev_access', ...safeError(e) }); }
  await faults(capture);
  let baselineBody;
  const gateway = createOpenAI({
    apiKey: process.env.OPENROUTER_API_KEY,
    baseURL: 'https://openrouter.ai/api/v1',
    compatibility: 'strict',
    fetch: async (url, init) => {
      const body = JSON.parse(init.body);
      assert.equal(body.model, decisions.ORIGINAL_MODEL);
      body.model = 'openai/' + body.model;
      const r = await nativeFetch(url, { ...init, body: JSON.stringify(body), signal: AbortSignal.timeout(20000) });
      if (r.ok) baselineBody = await r.clone().json();
      return r;
    },
  });
  for (let i = 0; i < cases.length; i++) {
    const plot = cases[i]; let original; let baselineRun;
    try {
      const start = performance.now();
      baselineRun = await runMain(baseline, plot, async options => {
        original = await generateObject({ ...options, model: gateway(options.model.model, options.model.settings), maxRetries: 0 }); return original;
      });
      const originalLatency = performance.now() - start;
      checkLogs(baselineRun.logs, original);
      // No pairs can be established without actual Jev access.
      if (!capture) { evidence.baseline_access = 'succeeded'; break; }
      let raw, jevLatency;
      if (i === 0) { raw = capture; jevLatency = evidence.first_jev_latency_ms; }
      else { const t = performance.now(); raw = await decisions.evaluateGenre(plot); jevLatency = performance.now() - t; }
      const parsed = decisions.parseDecision(raw);
      let calls = 0;
      const integrated = await runMain(current, plot, async options => {
        calls++; assert.deepEqual(options, baselineRun.options); return original;
      }, async () => Response.json(raw));
      const fallback = !decisions.confidenceAccepted(parsed.confidence);
      assert.equal(calls, fallback ? 1 : 0);
      checkLogs(integrated.logs, fallback ? original : parsed.result);
      assert.equal(typeof raw.id, 'string'); assert(raw.id.length > 0);
      site.rows.push({ input: plot, provenance: i === 0 ? 'repo' : 'synthetic', source: i === 0 ? 'workflow.ts:12-13 (original)' : 'validate-jev.cjs cases', split: 'confirmation', live: true,
        request_id: raw.id, model: raw.model, jev_answer: parsed.result.object, original_answer: original.object,
        confidence: parsed.confidence, fallback_taken: fallback, latency_ms: jevLatency, cost_usd: raw.usage.cost ?? null,
        original_model: 'openai/' + decisions.ORIGINAL_MODEL, original_latency_ms: originalLatency,
        original_cost_usd: baselineBody?.usage?.cost ?? null, original_request_id: baselineBody?.id,
        response: raw, original_usage: baselineBody?.usage, cost_source: 'provider-reported usage.cost; null means unavailable' });
      save(); console.log('Measured pair', i + 1);
    } catch (e) { site.errors.push({ phase: 'paired_evaluation', index: i, ...safeError(e) }); break; }
  }
  if (site.rows.length) {
    const rows = site.rows;
    site.agreement_curve = [0, 0.5, 0.7, decisions.THRESHOLD, 0.95, 1].map(threshold => {
      const accepted = rows.filter(r => r.confidence >= threshold);
      return { threshold, accepted: accepted.length, agreement: accepted.length ? accepted.filter(r => r.jev_answer === r.original_answer).length / accepted.length : null, fallback_fraction: 1 - accepted.length / rows.length };
    });
    const quantile = (xs, p) => xs.sort((a,b) => a-b)[Math.ceil(xs.length*p)-1];
    site.latency = Object.fromEntries(['latency_ms', 'original_latency_ms'].map(k => [k, { p50: quantile(rows.map(r => r[k]), .5), p95: quantile(rows.map(r => r[k]), .95) }]));
    site.expected_cascade_latency_ms = rows.reduce((s,r) => s+r.latency_ms+(r.fallback_taken?r.original_latency_ms:0),0)/rows.length;
    site.expected_cascade_cost_usd = rows.every(r=>Number.isFinite(r.cost_usd)&&Number.isFinite(r.original_cost_usd)) ? rows.reduce((s,r)=>s+r.cost_usd+(r.fallback_taken?r.original_cost_usd:0),0)/rows.length : null;
    const chosen = site.agreement_curve.find(r => r.threshold === decisions.THRESHOLD);
    if (rows.length >= 30 && chosen.agreement >= .9 && site.expected_cascade_cost_usd !== null && site.errors.length === 0) evidence.status = 'measured confirmation passed';
  }
  save(); console.log(JSON.stringify({ status: evidence.status, pairs: site.rows.length, faults: site.faults, errors: site.errors }));
}
main().catch(e => { site.errors.push({ phase: 'harness', ...safeError(e) }); save(); console.error('Validation incomplete; see sanitized JEV_PARITY.json'); process.exitCode = 1; });
