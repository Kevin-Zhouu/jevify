// Portable proof helpers: Node 18+, built-ins only; no model calls or policy.
const assert = require('node:assert/strict');
const vm = require('node:vm');
const {createRequire} = require('node:module');

function loadCommonJS(source, filename, imports = {}, logger = console) {
  // For TS/ESM, transpile the ACTUAL source with the project's existing loader
  // first. Do not rewrite the source's prompt or output schema. Approved code
  // execution only; this is not a security sandbox.
  const localRequire = createRequire(filename);
  const module = {exports: {}};
  vm.runInThisContext('(function(require,module,exports,console){' + source + '\n})', {filename})(
    name => Object.hasOwn(imports, name) ? imports[name] : localRequire(name),
    module, module.exports, logger);
  return module.exports;
}

async function assertFallbackOnce(invoke) {
  // invoke(original) must execute the ACTUAL public wrapper under one forced
  // transport fault or rejection. Keep monkeypatches active until it settles.
  const sentinel = Object.freeze({originalSentinel: true});
  const failure = new Error('original exception identity sentinel');
  for (const raises of [false, true]) {
    let calls = 0;
    const original = async (...args) => {
      calls++;
      if (raises) throw failure;
      return sentinel;
    };
    if (raises) await assert.rejects(() => invoke(original), error => error === failure);
    else assert.equal(await invoke(original), sentinel, 'Original return value changed');
    assert.equal(calls, 1, 'Original must be called exactly once');
  }
  return true;
}

function responseCost(response, estimate, estimateSource) {
  const value = response?.usage?.cost;
  const valid = x => typeof x === 'number' && Number.isFinite(x) && x >= 0;
  if (valid(value)) return {cost_usd: value, cost_source: 'provider-reported usage.cost'};
  if (valid(estimate) && estimateSource) return {cost_usd: estimate, cost_source: 'estimated: ' + estimateSource};
  return {cost_usd: null, cost_source: 'unknown; validation economics incomplete'};
}
module.exports = {loadCommonJS, assertFallbackOnce, responseCost};
