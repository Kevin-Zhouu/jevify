// Executes original source and actual converted modules. No credential logging.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const cp = require('node:child_process');
const assert = require('node:assert/strict');
const ts = require('typescript');
const {generateObject} = require('ai');
const {createOpenAI} = require('@ai-sdk/openai');
const root = path.resolve(__dirname, '..');
const source = cp.execFileSync('git', ['show', '4bc5e23750b6af7d32147d2480a5bde33bb935cb:workflow.ts'], {cwd: root, encoding:'utf8'});
const converted = fs.readFileSync(path.join(root,'workflow.ts'),'utf8');
const nativeFetch = global.fetch;
function compile(source, requireFn, consoleFn = console) {
  const result = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022},reportDiagnostics:true});
  assert.equal((result.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error).length,0);
  const mod = {exports:{}};
  vm.runInThisContext('(function(require,module,exports,console){'+result.outputText+'\n})')(requireFn,mod,mod.exports,consoleFn);
  return mod.exports;
}
const decision = compile(fs.readFileSync(path.join(root,'jevDecisions.ts'),'utf8'),require);
function optionsText(s) {
  const tree = ts.createSourceFile('workflow.ts',s,ts.ScriptTarget.Latest,true);
  let result;
  function visit(n) {
    if(ts.isCallExpression(n) && ['generateObject','withGenreFallback'].includes(n.expression.getText(tree))) result=n.arguments[0].getText(tree);
    ts.forEachChild(n,visit);
  }
  visit(tree); return result;
}
assert.equal(optionsText(source), optionsText(converted), 'Exact original request expression preserved');
assert.equal(converted.replace("import { withGenreFallback } from './jevDecisions';\n",'').replace('await withGenreFallback({','await generateObject({').replace('}, generateObject);','});'),source,'Only wrapper wiring changed');
function fixtureSource(s, plot) {
  if(plot === undefined) return s;
  const tree = ts.createSourceFile('workflow.ts',s,ts.ScriptTarget.Latest,true);
  let target;
  function visit(n) {
    if(ts.isPropertyAssignment(n)&&n.name.getText(tree)==='prompt') target=n.initializer;
    ts.forEachChild(n,visit);
  }
  visit(tree);
  // Preserve prefix and quote framing from original AST; replace only fixture literals.
  const literals=[];
  function collect(n){if(ts.isStringLiteral(n))literals.push(n);else ts.forEachChild(n,collect);}
  collect(target);
  const first=literals[1], last=literals.at(-1);
  return s.slice(0,first.getStart(tree))+JSON.stringify('"'+plot+'"')+s.slice(last.end);
}
// Entrypoint loader with explicit completion instead of fire-and-forget main().
async function runEntry(s, plot, sdk, wrapper=decision.withGenreFallback) {
  const logs=[];
  const mod=compile(fixtureSource(s,plot).replace('main().catch(console.error);','module.exports.completion = main();'),name=>{
    if(name==='ai')return {generateObject:sdk};
    if(name==='@ai-sdk/openai')return {openai:(name,settings)=>({name,settings})};
    if(name==='dotenv/config')return {};
    if(name==='./jevDecisions')return {...decision,withGenreFallback:wrapper};
    throw new Error('Unexpected import');
  },{...console,log:(...args)=>logs.push(args)});
  await mod.completion; return logs;
}
const plots = [
'A retired soldier battles kidnappers across a city to rescue his daughter.',
'A police officer boards a speeding train to stop armed terrorists.',
'A stunt driver races through enemy roadblocks carrying a witness to safety.',
'A team of commandos storms a fortress and rescues trapped hostages.',
'A martial artist confronts the gang that destroyed her village.',
'Two inept roommates accidentally swap jobs and cause a chain of hilarious misunderstandings.',
'A nervous best man loses the wedding rings during a ridiculous bachelor weekend.',
'A grumpy chef and a cheerful rival compete in an absurd village cooking contest.',
'A substitute teacher mistakes a school play for a real criminal conspiracy, with comic results.',
'A family vacation goes wrong when their caravan rolls into a nudist convention.',
'An estranged father and daughter slowly rebuild trust after a family funeral.',
'A young pianist struggles with grief and poverty while caring for her sick mother.',
'A factory closure forces three generations of a family to confront their shattered dreams.',
'A divorced couple must reconcile their differences while raising their son.',
'An aging athlete faces retirement and finds meaning in mentoring a troubled child.',
'Teenagers trapped in an abandoned asylum are stalked by a murderous ghost.',
'A family moves into a house whose walls whisper the names of future victims.',
'A cursed doll terrorizes a babysitter during a stormy night.',
'Campers discover that something in the forest is wearing the faces of their missing friends.',
'A priest investigates a possession as terrifying supernatural deaths spread through town.',
'Engineers on a distant space colony discover an artificial intelligence rewriting their memories.',
'A scientist invents a time machine and becomes stranded in a future ruled by robots.',
'A linguist aboard an orbital station makes first contact with an alien civilization.',
'Clones on a mining moon discover they are being replaced whenever they question their orders.',
'A pilot travels faster than light to warn Earth about a collapsing star.',
'Two bumbling astronauts accidentally awaken an alien and try to hide it from their captain.',
'A haunted comedian uses jokes to cope with a ghost that threatens his family.',
'A soldier returns home from war and struggles quietly to reconnect with his children.',
'A documentary observes bees pollinating an orchard through the seasons.',
'A silent experimental film shows changing colors and ocean waves without any characters.'
];
const sentinel={object:'sci-fi',usage:{promptTokens:10,completionTokens:5,totalTokens:15},finishReason:'stop'};
const evidence={date:new Date().toISOString(),source_revision:'4bc5e23750b6af7d32147d2480a5bde33bb935cb',sdk_versions:{ai:require('ai/package.json').version,openai:require('@ai-sdk/openai/package.json').version},baseline_adapter:'Original entrypoint options + real AI SDK parser; authorized transport/auth/model namespace only',split:{calibration:0,confirmation:plots.length,threshold_frozen_before_measurement:true},sites:[{site_id:'workflow.ts:6',primitive:'Choice',threshold:decision.THRESHOLD,rows:[],faults:{},errors:[]}],assertions:[]};
const site=evidence.sites[0];
const save=()=>fs.writeFileSync(path.join(root,'JEV_PARITY.json'),JSON.stringify(evidence,null,2)+'\n');
function diagnostics(logs,expected){assert.deepEqual(logs,[[expected.object],[],['Token usage:',expected.usage],['Finish reason:',expected.finishReason]]);}
async function fault(name,fetcher,body) {
  global.fetch=fetcher;
  let calls=0;
  const result=await decision.withGenreFallback({prompt:'benign movie plot'},async()=>{calls++;return sentinel;});
  assert.equal(calls,1); assert.equal(result,sentinel);
  const failure=new Error('original sentinel'); calls=0;
  await assert.rejects(decision.withGenreFallback({prompt:'benign movie plot'},async()=>{calls++;throw failure;}),error=>error===failure);
  assert.equal(calls,1);
  site.faults[name]=true;
}
(async()=>{
  try {
    await fault('error',async()=>{throw new Error('injected transport failure');});
    await fault('timeout',async()=>{throw new DOMException('injected abort','AbortError');});
    await fault('rate_limit',async()=>new Response('',{status:429}));
    await fault('malformed',async()=>new Response('[]',{status:200}));
    const key=process.env.OPENROUTER_API_KEY;
    try{delete process.env.OPENROUTER_API_KEY;await fault('missing_key',async()=>{throw new Error('must not call');});}
    finally{if(key!==undefined)process.env.OPENROUTER_API_KEY=key;}
    global.fetch=async()=>{throw new Error('injected offline');};
    let n=0;
    diagnostics(await runEntry(converted,undefined,async()=>{n++;return sentinel;}),sentinel);assert.equal(n,1);
    evidence.assertions.push('Source identity, complete offline stdout, original error identity and exactly-once fallback passed');
    save();
    if(!key){site.errors.push({stage:'setup',reason:'missing_key'});return;}
    for(const [index,plot] of plots.entries()){
      let originalOptions, originalResult, originalBody, requestBody, originalLatency;
      try{
        const sdk=async options=>{
          originalOptions=options;
          const provider=createOpenAI({apiKey:key,baseURL:'https://openrouter.ai/api/v1',fetch:async(url,init)=>{
            const body=JSON.parse(init.body); assert.equal(body.model,decision.ORIGINAL_MODEL);
            requestBody=body;
            const adapted={...body,model:'openai/'+body.model};
            const res=await nativeFetch(url,{...init,body:JSON.stringify(adapted),signal:AbortSignal.timeout(30000)});
            if(!res.ok){const e=new Error('baseline_http');e.status=res.status;throw e;}
            originalBody=await res.clone().json();return res;
          }});
          const start=performance.now();
          originalResult=await generateObject({...options,model:provider(options.model.name,options.model.settings),maxRetries:0});
          originalLatency=performance.now()-start; return originalResult;
        };
        diagnostics(await runEntry(source,plot,sdk),originalResult);
      } catch(error){site.errors.push({index,stage:'baseline',status:error.status||error.statusCode||null,type:error.name});}
      let raw, jevStatus, jevLatency, calls=0, output, supplied;
      global.fetch=async(url,init)=>{
        const start=performance.now();
        try{const res=await nativeFetch(url,init);jevStatus=res.status;if(res.ok)raw=await res.clone().json();return res;}
        finally{jevLatency=performance.now()-start;}
      };
      const logs=await runEntry(converted,plot,async(options)=>{calls++;assert.deepEqual(options,originalOptions);return originalResult||sentinel;},async(options,original)=>{
        supplied=options; output=await decision.withGenreFallback(options,original); return output;
      });
      diagnostics(logs,output); assert.deepEqual(supplied,originalOptions);
      if(!raw){site.errors.push({index,stage:'jev',status:jevStatus||null,reason:'no_successful_response'});save();break;}
      const parsed=decision.parseGenre(raw);
      const accepted=decision.acceptsConfidence(parsed.confidence);
      assert.equal(calls,accepted?0:1);
      if(accepted)assert.deepEqual(output,parsed.result);else assert.equal(output,originalResult||sentinel);
      if(!originalResult){save();break;}
      assert.equal(typeof raw.id,'string');assert(raw.id.length>0);
      site.rows.push({input:plot,provenance:'synthetic',source:'validation/validate.cjs plots',live:true,request_id:raw.id,model:raw.model,jev_answer:raw.answers.genre.choice,original_answer:originalResult.object,confidence:parsed.confidence,fallback_taken:calls===1,latency_ms:jevLatency,cost_usd:raw.usage.cost??null,original_model:'openai/'+decision.ORIGINAL_MODEL,original_latency_ms:originalLatency,original_cost_usd:originalBody?.usage?.cost??null,cost_source:'provider-reported usage.cost; null means unavailable',response:raw,original_response:{id:originalBody.id,model:originalBody.model,usage:originalBody.usage,choices:originalBody.choices},original_request:requestBody,stdout:logs});
      save(); console.log('Live pair '+(index+1)+' complete');
    }
    const capture=site.rows[0]?.response;
    if(capture){
      const changed=structuredClone(capture);changed.answers.genre.confidence=decision.THRESHOLD/2;
      await fault('below_threshold',async()=>new Response(JSON.stringify(changed)));
      for(const [name,mutate] of Object.entries({unknown_option:b=>b.answers.genre.choice='invalid',missing_usage:b=>delete b.usage,wrong_model:b=>b.model='invalid',nonfinite:b=>b.answers.genre.confidence=null,array_usage:b=>b.usage=[]})){
        const value=structuredClone(capture);mutate(value);await fault(name,async()=>new Response(JSON.stringify(value)));
      }
      const accepted=site.rows.find(r=>!r.fallback_taken);
      if(accepted){
        global.fetch=async()=>new Response(JSON.stringify(accepted.response));
        let count=0;const result=await decision.withGenreFallback({prompt:accepted.input},async()=>{count++;return sentinel;});
        assert.equal(count,0);assert.deepEqual(result,decision.parseGenre(accepted.response).result);
        evidence.assertions.push('Accepted wrapper path replayed actual live response');
      }
    }
    const rows=site.rows;
    const mean=a=>a.length?a.reduce((s,n)=>s+n,0)/a.length:null;
    const quantile=(a,q)=>a.length?[...a].sort((x,y)=>x-y)[Math.ceil(a.length*q)-1]:null;
    site.summary={n:rows.length,raw_agreement:mean(rows.map(r=>Number(r.jev_answer===r.original_answer))),curve:[0,0.5,0.7,decision.THRESHOLD,0.95,1].map(threshold=>{const a=rows.filter(r=>r.confidence>=threshold);return {threshold,accepted:a.length,agreement:mean(a.map(r=>Number(r.jev_answer===r.original_answer))),fallback_fraction:rows.length?1-a.length/rows.length:null};}),jev_latency_ms:{p50:quantile(rows.map(r=>r.latency_ms),.5),p95:quantile(rows.map(r=>r.latency_ms),.95)},original_latency_ms:{p50:quantile(rows.map(r=>r.original_latency_ms),.5),p95:quantile(rows.map(r=>r.original_latency_ms),.95)},mean_expected_cascade_latency_ms:mean(rows.map(r=>r.latency_ms+(r.fallback_taken?r.original_latency_ms:0))),mean_original_cost_usd:rows.every(r=>r.original_cost_usd!==null)?mean(rows.map(r=>r.original_cost_usd)):null,mean_expected_cascade_cost_usd:rows.every(r=>r.cost_usd!==null&&r.original_cost_usd!==null)?mean(rows.map(r=>r.cost_usd+(r.fallback_taken?r.original_cost_usd:0))):null};
    console.log(JSON.stringify(site.summary));
  }finally{global.fetch=nativeFetch;save();}
})().catch(error=>{site.errors.push({stage:'assertion_or_execution',type:error.name,code:error.code||null});save();console.error('Validation failed; sanitized error type:',error.name,'code:',error.code||'none');process.exitCode=1;});
