const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const ts = require('typescript');
const ai = require('ai');
const { createOpenAI } = require('@ai-sdk/openai');
const ROOT = path.resolve(__dirname, '..');
process.chdir(ROOT);
const SOURCE_SHA = '6013ff5396ee175c76aa5feddd7e93d903e667a7';
const originalSource = execFileSync('git', ['show', SOURCE_SHA + ':workflow.ts'], { encoding:'utf8', env:{...process.env,GIT_OPTIONAL_LOCKS:'0'} });
const convertedSource = fs.readFileSync('workflow.ts', 'utf8');
const initialPlot = 'A group of astronauts travel through a wormhole in search of a new habitable planet for humanity.';
function compile(source, requires, output = console) {
  const compiled = ts.transpileModule(source, { compilerOptions:{ module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022 },reportDiagnostics:true });
  assert.equal((compiled.diagnostics || []).filter(d=>d.category===ts.DiagnosticCategory.Error).length,0);
  const mod={exports:{}};
  vm.runInThisContext('(function(require,module,exports,console){'+compiled.outputText+'\n})')(requires,mod,mod.exports,output);
  return mod.exports;
}
const decisions = compile(fs.readFileSync('jevDecisions.ts','utf8'), require);
function workflow(source, plot, generateObject, openai, stderr=[]) {
  // Change only the input fixture; leave original instructions, enum and parsing in the real SDK.
  const originalLiteral = `'"A group of astronauts travel through a wormhole in search of a ' +\n      'new habitable planet for humanity."'`;
  const convertedLiteral = `'A group of astronauts travel through a wormhole in search of a ' +\n    'new habitable planet for humanity.'`;
  if (source.includes(originalLiteral)) source=source.replace(originalLiteral,JSON.stringify('"'+plot+'"'));
  else { assert(source.includes(convertedLiteral)); source=source.replace(convertedLiteral,JSON.stringify(plot)); }
  assert(source.includes('main().catch(console.error);'));
  source=source.replace('main().catch(console.error);','export { main };');
  const logs=[];
  const mod=compile(source, name=> {
    if(name==='ai') return {generateObject};
    if(name==='@ai-sdk/openai') return {openai};
    if(name==='dotenv/config') return {};
    if(name==='./jevDecisions') return decisions;
    throw new Error('Unexpected import');
  }, {...console,log:(...args)=>logs.push(args),error:e=>stderr.push(e)});
  return {run:mod.main,logs};
}
function checkDiagnostics(logs, result) {
  assert.deepEqual(logs,[[result.object],[],['Token usage:',result.usage],['Finish reason:',result.finishReason]]);
}
async function faults(replay) {
  const oldFetch=global.fetch, key=process.env.OPENROUTER_API_KEY;
  const sentinel={object:'sci-fi',usage:{promptTokens:10,completionTokens:5,totalTokens:15},finishReason:'stop'};
  const result={};
  try {
    process.env.OPENROUTER_API_KEY=key||'fault-test-placeholder';
    const variants={
      error:async()=>{throw new Error('injected');},
      timeout:async()=>{throw new DOMException('injected','TimeoutError');},
      rate_limit:async()=>new Response('',{status:429}),
      server_error:async()=>new Response('',{status:503}),
      malformed:async()=>new Response('{',{status:200}),
      invalid_schema:async()=>Response.json({}),
    };
    for (const [name,transport] of Object.entries(variants)) {
      global.fetch=transport; let calls=0;
      assert.strictEqual(await decisions.genreWithFallback(initialPlot,async()=>{calls++;return sentinel;}),sentinel);
      assert.equal(calls,1);
      const originalError=new Error('original error sentinel'); calls=0;
      await assert.rejects(decisions.genreWithFallback(initialPlot,async()=>{calls++;throw originalError;}),e=>e===originalError);
      assert.equal(calls,1); result[name]=true;
    }
    delete process.env.OPENROUTER_API_KEY;let calls=0;
    global.fetch=async()=>{throw new Error('must not call');};
    assert.strictEqual(await decisions.genreWithFallback(initialPlot,async()=>{calls++;return sentinel;}),sentinel);assert.equal(calls,1);result.missing_key=true;
    for(const confidence of [0,decisions.THRESHOLD-0.01,NaN,Infinity,-1,1.1,true,undefined]) {
      calls=0;assert.equal(decisions.confident(confidence),false);
      assert.strictEqual(await decisions.chooseAnswer({confidence},async()=>{calls++;return sentinel;}),sentinel);assert.equal(calls,1);
    }
    result.below_threshold=true;
    process.env.OPENROUTER_API_KEY=key||'fault-test-placeholder';
    global.fetch=async()=>{throw new Error('offline');};
    let captured;
    const original = async options=>{captured=options;return sentinel;};
    const base=workflow(originalSource,initialPlot,original,(model,settings)=>({model,settings}));await base.run();const baselineOptions=captured;
    const converted=workflow(convertedSource,initialPlot,original,(model,settings)=>({model,settings}));await converted.run();
    assert.deepEqual(captured,baselineOptions);assert.deepEqual(converted.logs,base.logs);checkDiagnostics(converted.logs,sentinel);result.original_request_and_stdout=true;
    if (replay) {
      global.fetch=async()=>Response.json(replay);calls=0;
      const accepted=workflow(convertedSource,initialPlot,async()=>{calls++;return sentinel;},()=>({}));await accepted.run();
      assert.equal(calls,0);checkDiagnostics(accepted.logs,decisions.parseDecision(replay).result);result.accepted_diagnostics=true;
      for(const mutate of [r=>delete r.usage,r=>r.usage.input_tokens=-1,r=>r.answers.genre.choice='unknown',r=>r.answers.genre.confidence=null,r=>r.model='unversioned',r=>r.answers.genre.probabilities={}]) {
        const invalid=structuredClone(replay);mutate(invalid);global.fetch=async()=>Response.json(invalid);calls=0;
        assert.strictEqual(await decisions.genreWithFallback(initialPlot,async()=>{calls++;return sentinel;}),sentinel);assert.equal(calls,1);
      }
      result.invalid_live_response_variants=true;
    }
  } finally { global.fetch=oldFetch;if(key===undefined)delete process.env.OPENROUTER_API_KEY;else process.env.OPENROUTER_API_KEY=key; }
  return result;
}
const plots=[initialPlot,
'A retired soldier fights mercenaries to rescue hostages from a skyscraper.',
'Two incompetent friends accidentally swap suitcases and cause a string of hilarious misunderstandings.',
'A grieving father and his estranged daughter slowly rebuild their relationship.',
'A family moves into a house haunted by a murderous ghost.',
'An android discovers memories implanted by a corporation on a distant colony.',
'A stunt driver races through a city while evading armed criminals.',
'A shy accountant impersonates a celebrity at a chaotic wedding.',
'A musician struggles with failure and reconciles with her mother.',
'Teenagers camping in the woods are stalked by a supernatural creature.',
'A scientist builds a machine that opens a portal to a parallel universe.',
'A detective battles a gang to stop a bombing on a moving train.',
'A disastrous amateur theater production becomes a series of comic mishaps.',
'Two siblings argue over their childhood home after their parents die.',
'A possessed doll terrorizes the residents of an isolated orphanage.',
'A generation ship receives a signal from an extinct alien civilization.',
'A bodyguard protects a diplomat during a relentless citywide pursuit.',
'A chef and a food critic become accidental roommates with absurd consequences.',
'A nurse cares for her aging mentor while facing a difficult family decision.',
'An ancient curse traps travelers in a village where nobody survives the night.',
'Explorers on Mars uncover a machine that changes human memories.',
'A rescue team must fight pirates aboard a hijacked cargo vessel.',
'A competitive neighborhood gardening contest descends into slapstick sabotage.',
'A divorced couple meet again to support their son through a personal crisis.',
'A sleep researcher is pursued by a monster that appears in her dreams.',
'Human diplomats negotiate with artificial minds living inside a simulated world.',
'Clumsy vampire hunters bicker while trying to save a town from monsters.',
'A soldier returning from war struggles to connect with his family.',
'An astronaut in a failing spaceship hears a terrifying voice from outside.',
'A documentary follows the seasonal migration of birds.',
'A person waits quietly at a bus stop.',
'A pair of thieves exchange jokes while escaping a heavily guarded vault.',
'A ghost helps a lonely child reconnect with her grieving father.',
'A robot comedian performs at a disastrous interplanetary talent show.',
'A lawyer uncovers corruption and must decide whether to sacrifice her career.',
'A chef prepares a meal with ingredients from the garden.'
];
async function live() {
  const evidence={source_sha:SOURCE_SHA,status:'incomplete',baseline_adapter:'Original workflow executed with real installed AI SDK; same model via explicitly authorized OpenRouter transport; no production provider change.',sites:[{site_id:'workflow.ts:6',threshold:decisions.THRESHOLD,rows:[],errors:[],faults:{}}]};
  const site=evidence.sites[0];
  const write=()=>fs.writeFileSync('JEV_PARITY.json',JSON.stringify(evidence,null,2)+'\n');
  let replay;
  const realFetch=global.fetch;
  for(let i=0;i<plots.length;i++) {
    const plot=plots[i];
    try {
      const start=performance.now();const d=await decisions.evaluateGenre(plot);const latency_ms=performance.now()-start;
      let wire,baselineRaw;
      const provider=createOpenAI({apiKey:process.env.OPENROUTER_API_KEY,baseURL:'https://openrouter.ai/api/v1',fetch:async(url,options)=>{
        const body=JSON.parse(options.body);assert.equal(body.model,'gpt-4o-mini');wire=structuredClone(body);body.model='openai/gpt-4o-mini';
        const response=await realFetch(url,{...options,body:JSON.stringify(body),signal:AbortSignal.timeout(30000)});
        if(!response.ok) throw new Error('baseline_http_'+response.status);
        baselineRaw=await response.clone().json();return response;
      }});
      let baselineResult;
      const baseline=workflow(originalSource,plot,async options=>{baselineResult=await ai.generateObject({...options,maxRetries:0});return baselineResult;},provider);
      const baseStart=performance.now();await baseline.run();const original_latency_ms=performance.now()-baseStart;
      assert.equal(wire.model,'gpt-4o-mini');assert(wire.messages.some(m=>m.content==='Classify the genre of this movie plot: "'+plot+'"'));
      checkDiagnostics(baseline.logs,baselineResult);
      let calls=0;const finalResult=await decisions.chooseAnswer(d,async()=>{calls++;return baselineResult;});
      const fallback_taken=!decisions.confident(d.confidence);assert.equal(calls,Number(fallback_taken));
      assert.equal(finalResult.object,fallback_taken?baselineResult.object:d.result.object);
      assert.equal(typeof d.raw.id,'string');assert(d.raw.id.length>0);assert.equal(typeof baselineRaw.id,'string');
      assert.equal(typeof d.raw.usage.cost,'number');assert.equal(typeof baselineRaw.usage.cost,'number');
      site.rows.push({input:plot,provenance:i===0?'repo':'synthetic',source:i===0?'workflow.ts:12-13':'validation/check.cjs plots',split:i%2===0?'calibration':'confirmation',model:d.raw.model,live:true,request_id:d.raw.id,jev_answer:d.result.object,original_answer:baselineResult.object,confidence:d.confidence,fallback_taken,latency_ms,cost_usd:d.raw.usage.cost,usage:d.raw.usage,original_model:'openai/gpt-4o-mini',original_request_id:baselineRaw.id,original_latency_ms,original_cost_usd:baselineRaw.usage.cost,original_usage:baselineRaw.usage,cost_source:'provider-reported usage.cost',jev_response:d.raw,baseline_request:wire});
      if(!fallback_taken&&!replay)replay=d.raw;
      write();console.log('Paired input '+(i+1)+'/'+plots.length);
    } catch(e) {
      const reason=/^(baseline_http_\d+|http_\d+|invalid_response|invalid_usage|rate_limit|missing_key)$/.test(e.message)?e.message:e.name;
      site.errors.push({input_index:i,reason});write();console.log('Live measurement blocked: '+reason);break;
    }
  }
  site.faults=await faults(replay);
  const rows=site.rows;
  const summarize=rows=>({n:rows.length,raw_agreement:rows.length?rows.filter(r=>r.jev_answer===r.original_answer).length/rows.length:null,curve:[0,0.5,0.7,0.8,0.9,0.95,1].map(threshold=>{const accepted=rows.filter(r=>r.confidence>=threshold);return {threshold,accepted:accepted.length,selective_agreement:accepted.length?accepted.filter(r=>r.jev_answer===r.original_answer).length/accepted.length:null,fallback_fraction:rows.length?1-accepted.length/rows.length:null};})});
  site.metrics={all:summarize(rows),calibration:summarize(rows.filter(r=>r.split==='calibration')),confirmation:summarize(rows.filter(r=>r.split==='confirmation'))};
  const quantile=(values,p)=>values.length?[...values].sort((a,b)=>a-b)[Math.ceil(p*values.length)-1]:null;
  const mean=values=>values.length?values.reduce((a,b)=>a+b,0)/values.length:null;
  site.metrics.latency_ms={jev_p50:quantile(rows.map(r=>r.latency_ms),.5),jev_p95:quantile(rows.map(r=>r.latency_ms),.95),original_p50:quantile(rows.map(r=>r.original_latency_ms),.5),original_p95:quantile(rows.map(r=>r.original_latency_ms),.95),estimated_cascade_mean:mean(rows.map(r=>r.latency_ms+(r.fallback_taken?r.original_latency_ms:0)))};
  site.metrics.cost_usd={jev_mean:mean(rows.map(r=>r.cost_usd)),original_mean:mean(rows.map(r=>r.original_cost_usd)),estimated_cascade_mean:mean(rows.map(r=>r.cost_usd+(r.fallback_taken?r.original_cost_usd:0)))};
  evidence.status=rows.length===plots.length?'measured':'incomplete';write();
  console.log(JSON.stringify({status:evidence.status,n:rows.length,metrics:site.metrics,faults:site.faults},null,2));
}
(async()=>{if(process.argv.includes('--live')) await live();else {const prior=fs.existsSync('JEV_PARITY.json')?JSON.parse(fs.readFileSync('JEV_PARITY.json','utf8')):null;const replay=prior?.sites[0]?.rows.find(r=>!r.fallback_taken)?.jev_response;console.log(JSON.stringify(await faults(replay),null,2));}})().catch(e=>{console.error('Validation failed: '+e.name);process.exitCode=1;});
