const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const cp = require('node:child_process');
const assert = require('node:assert/strict');
const ts = require('typescript');
const { generateObject } = require('ai');
const { createOpenAI } = require('@ai-sdk/openai');
const root = path.resolve(__dirname, '..');
const nativeFetch = global.fetch;
const warnings = [];
function load(source, imports = {}) {
  const mod = {exports:{}};
  const compiled = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}});
  vm.runInThisContext('(function(require,module,exports,console){'+compiled.outputText+'\n})')(name=>imports[name] ?? require(name),mod,mod.exports,{...console,warn:s=>warnings.push(s)});
  return mod.exports;
}
const decisions = load(fs.readFileSync(path.join(root,'jevDecisions.ts'),'utf8'));
const source = cp.execFileSync('git',['show','6013ff5396ee175c76aa5feddd7e93d903e667a7:workflow.ts'],{cwd:root,encoding:'utf8'});
async function capture(src, converted) {
  let options; const logs=[];
  const imports = {'dotenv/config':{},'@ai-sdk/openai':{openai:(id,settings)=>({id,settings})},ai:{generateObject:async o=>{options=o;return {object:'sci-fi',usage:{promptTokens:1,completionTokens:2,totalTokens:3},finishReason:'stop'};}},'./jevDecisions':{genreWithFallback:async(o,f)=>f(o)}};
  const oldLog=console.log;console.log=(...a)=>logs.push(a);
  try { const module=load(src.replace('main().catch(console.error);','export { main };'),imports);await module.main(); } finally {console.log=oldLog;}
  assert.deepEqual(logs,[['sci-fi'],[],['Token usage:',{promptTokens:1,completionTokens:2,totalTokens:3}],['Finish reason:','stop']]);
  return options;
}
const synthetic = [
'A retired soldier fights mercenaries to rescue his kidnapped daughter.',
'Two inept roommates accidentally enter a cooking contest and cause hilarious chaos.',
'A widow reconnects with her estranged son while grieving her husband.',
'Campers discover a murderous ghost stalking their remote cabin.',
'A scientist builds a time machine and visits Earth a thousand years ahead.',
'A police officer races through the city to stop a terrorist attack.',
'A nervous best man loses the wedding rings and invents increasingly absurd excuses.',
'A young musician struggles with family expectations and personal loss.',
'A cursed doll terrorizes the family that buys it.',
'A robot develops consciousness on a distant space station.',
'A spy escapes assassins while protecting stolen intelligence.',
'Two rival chefs swap identities during a disastrous restaurant opening.',
'A father and daughter rebuild their relationship after years apart.',
'An unseen creature hunts students inside an abandoned hospital.',
'A colony on Mars discovers intelligent life beneath the surface.',
'A stunt driver pursues a criminal convoy across the desert.',
'A clumsy detective solves a mystery through a series of ridiculous accidents.',
'A teacher helps a troubled student confront a difficult home life.',
'A family trapped in a haunted hotel must survive until dawn.',
'Engineers travel through time to prevent a planetary catastrophe.',
'A grieving astronaut hears the voice of her dead child in an alien transmission.',
'A zombie learns to tell jokes while trying to fit into a suburban neighborhood.',
'A bank robber questions his loyalty while fleeing police with his brother.',
'A lonely scientist falls in love with an artificial intelligence.',
'A comedian returns home to care for his dying mother.',
'A detective battles an alien invasion while making wisecracks.',
'Two siblings inherit a house whose walls whisper their darkest secrets.',
'A medieval farmer patiently grows wheat and attends a village market.',
'An instructional film explains how to assemble a wooden shelf.',
'A silent film follows clouds drifting over an empty ocean.',
'A concert film documents a pianist performing on stage.',
'A documentary explores the history of railway timetables.',
'A pair of lovers try to escape a city ruled by robots.',
'A hapless vampire opens a bakery and struggles with early mornings.',
'A boxer confronts his abusive childhood while training for a final fight.',
];
async function faults() {
  const saved=process.env.OPENROUTER_API_KEY;
  const sentinel={object:'drama',usage:{promptTokens:2,completionTokens:3,totalTokens:5},finishReason:'length'};
  const opts={prompt:'A movie plot'};
  async function check(transport,missing=false) {
    global.fetch=transport;
    if(missing) delete process.env.OPENROUTER_API_KEY;else process.env.OPENROUTER_API_KEY=saved || 'fault-test-placeholder';
    let calls=0;assert.equal(await decisions.genreWithFallback(opts,async o=>{assert.equal(o,opts);calls++;return sentinel;}),sentinel);assert.equal(calls,1);
    const error=new Error('original sentinel');calls=0;
    await assert.rejects(decisions.genreWithFallback(opts,async()=>{calls++;throw error;}),e=>e===error);assert.equal(calls,1);
  }
  try {
    await check(async()=>{throw new Error('transport');});
    await check(async()=>new Response('',{status:429}));
    await check(async()=>new Response('{}'));
    await check(async()=>{throw Error('must not fetch');},true);
    await check((_url,{signal})=>new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('timeout','AbortError')))));
    for(const x of [0,decisions.THRESHOLD-0.01,NaN,Infinity,true,-1,1.1]) assert.equal(decisions.confidenceAccepted(x),false);
    assert.equal(decisions.confidenceAccepted(decisions.THRESHOLD),true);
    return {below_threshold:true,error:true,timeout:true,rate_limit:true,missing_key:true,malformed:true,original_exception_identity:true};
  } finally { if(saved===undefined)delete process.env.OPENROUTER_API_KEY;else process.env.OPENROUTER_API_KEY=saved;global.fetch=nativeFetch; }
}
(async()=>{
  const original=await capture(source);
  assert.deepEqual(await capture(fs.readFileSync(path.join(root,'workflow.ts'),'utf8')),original);
  const report={sites:[{site_id:'workflow.ts:6',primitive:'Choice',threshold:decisions.THRESHOLD,rows:[],errors:[],faults:await faults()}],baseline_adapter:'ai@4.3.19 and @ai-sdk/openai@1.3.24; captured original generateObject options and SDK parser. Only baseline HTTP endpoint, auth and model namespace change; synthetic inputs replace quoted plot only.',cost_basis:'provider-reported usage.cost; unknown remains null',threshold_selection:'0.9 fixed before measurement; first 16 calibration, remainder confirmation; no tuning',source_sha:'6013ff5396ee175c76aa5feddd7e93d903e667a7'};
  const site=report.sites[0];
  const inputs=[original.prompt.match(/"([\s\S]*)"$/)[1],...synthetic];
  function save(){fs.writeFileSync(path.join(root,'JEV_PARITY.json'),JSON.stringify(report,null,2)+'\n');}
  save();
  for(let i=0;i<inputs.length;i++) {
    const prompt=original.prompt.replace(/"[\s\S]*"$/,'"'+inputs[i]+'"');
    let baselineRaw,jevRaw,baselineRequest,originalResult,baselineMs,jevMs;
    const provider=createOpenAI({apiKey:'evaluation-transport-placeholder',fetch:async(url,init)=>{
      const body=JSON.parse(init.body);assert.equal(body.model,'gpt-4o-mini');baselineRequest=structuredClone(body);body.model='openai/gpt-4o-mini';
      const response=await nativeFetch('https://openrouter.ai/api/v1/chat/completions',{...init,body:JSON.stringify(body),headers:{Authorization:'Bearer '+process.env.OPENROUTER_API_KEY,'Content-Type':'application/json'},signal:AbortSignal.timeout(30000)});
      if(!response.ok)throw new Error('baseline_http_'+response.status);
      baselineRaw=await response.clone().json();return response;
    }});
    try {
      const started=performance.now();
      originalResult=await generateObject({...original,prompt,model:provider(original.model.id,original.model.settings),maxRetries:0});
      baselineMs=performance.now()-started;
      assert(original.enum.includes(originalResult.object));
    } catch(e) {site.errors.push({index:i,stage:'baseline',kind:/baseline_http_\d+/.exec(e.message)?.[0] || e.name});}
    global.fetch=async(url,init)=>{const response=await nativeFetch(url,init);if(response.ok)jevRaw=await response.clone().json();return response;};
    let fallbackTaken=false;
    const start=performance.now();
    const converted=await decisions.genreWithFallback({prompt},async()=>{fallbackTaken=true;return originalResult;});jevMs=performance.now()-start;
    global.fetch=nativeFetch;
    if(!jevRaw) site.errors.push({index:i,stage:'jev',kind:warnings.at(-1).split('reason=')[1],latency_ms:jevMs});
    if(originalResult && jevRaw) {
      const d=decisions.parseDecision(jevRaw);
      assert.equal(fallbackTaken,!decisions.confidenceAccepted(d.confidence));
      assert.deepEqual(converted,fallbackTaken?originalResult:d.result);
      site.rows.push({input:inputs[i],provenance:i===0?'repo':'synthetic',source:i===0?'workflow.ts:11-13':'validation/run.cjs synthetic movie plots',split:i<16?'calibration':'confirmation',live:true,model:jevRaw.model,request_id:jevRaw.id,jev_answer:d.result.object,original_answer:originalResult.object,confidence:d.confidence,fallback_taken:fallbackTaken,latency_ms:jevMs,cost_usd:jevRaw.usage.cost??null,original_model:'openai/gpt-4o-mini',original_request_id:baselineRaw.id,original_latency_ms:baselineMs,original_cost_usd:baselineRaw.usage?.cost??null,jev_response:jevRaw,original_response:baselineRaw,original_request:baselineRequest});
    }
    save();console.log(JSON.stringify({completed:i+1,pairs:site.rows.length,errors:site.errors.length}));
    // Access failure cannot be repaired by repeating 36 identical unauthorized calls.
    if(i===0 && (site.errors.some(e=>/http_(401|402|403|404)/.test(e.kind)) || !jevRaw))break;
  }
  global.fetch=nativeFetch;
  report.status=site.rows.length>=30?'measured':'incomplete';save();
})().catch(e=>{console.error('Validation failed:',e.name);process.exitCode=1;});
