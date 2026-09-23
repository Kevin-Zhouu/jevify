// Only replay genuine recorded Jev responses; mutations below are fault injection.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),ts=require('typescript');
const root=path.resolve(__dirname,'..');
function load(file,imports={},logs=[]) {
 const m={exports:{}};const s=ts.transpileModule(fs.readFileSync(path.join(root,file),'utf8').replace('main().catch(console.error);','export { main };'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 vm.runInThisContext('(function(require,module,exports,console){'+s+'\n})')(n=>imports[n]??require(n),m,m.exports,{log:(...a)=>logs.push(a),warn:()=>{},error:e=>{throw e;}});return m.exports;
}
(async()=>{
 const evidence=JSON.parse(fs.readFileSync(path.join(root,'JEV_PARITY.json'))),site=evidence.sites[0],d=load('jevDecisions.ts');
 const row=site.rows.find(r=>!r.fallback_taken);assert(row,'Requires a captured accepted live response');
 const raw=row.jev_response,opts={prompt:row.input,output:'enum',enum:Object.keys(d.QUESTIONS.genre.criteria)};
 process.env.OPENROUTER_API_KEY ||= 'replay-placeholder';
 global.fetch=async()=>new Response(JSON.stringify(raw));let calls=0;
 const logs=[];
 const entry=load('workflow.ts',{'dotenv/config':{},'@ai-sdk/openai':{openai:()=>({})},ai:{generateObject:async()=>{calls++;throw Error('unexpected fallback');}},'./jevDecisions':d},logs);
 await entry.main();assert.equal(calls,0);
 assert.deepEqual(logs,[[raw.answers.genre.choice],[],['Token usage:',{promptTokens:raw.usage.input_tokens,completionTokens:raw.usage.output_tokens,totalTokens:raw.usage.input_tokens+raw.usage.output_tokens}],['Finish reason:','stop']]);
 const sentinel={object:'horror',usage:{promptTokens:9,completionTokens:2,totalTokens:11},finishReason:'length'};
 async function rejected(mutate){const fault=structuredClone(raw);mutate(fault);global.fetch=async()=>({ok:true,json:async()=>fault});calls=0;assert.equal(await d.genreWithFallback(opts,async()=>{calls++;return sentinel;}),sentinel);assert.equal(calls,1);const e=new Error('original failure');calls=0;await assert.rejects(d.genreWithFallback(opts,async()=>{calls++;throw e;}),x=>x===e);assert.equal(calls,1);}
 await rejected(x=>x.answers.genre.confidence=d.THRESHOLD-0.01);
 await rejected(x=>x.answers.genre.confidence=NaN);
 await rejected(x=>x.answers.genre.confidence=true);
 await rejected(x=>x.answers.genre.choice='unknown');
 await rejected(x=>delete x.usage);
 await rejected(x=>x.usage.input_tokens=-1);
 await rejected(x=>x.usage.output_tokens=Infinity);
 await rejected(x=>x.model='unexpected');
 site.faults={...site.faults,below_threshold:true,unknown_option:true,nonfinite:true,missing_usage:true,wrong_model:true,accepted_stdout_replay:true};
 evidence.replay_note='Accepted-path stdout replays genuine recorded response. Mutated copies are injected failures, not live model measurements.';
 fs.writeFileSync(path.join(root,'JEV_PARITY.json'),JSON.stringify(evidence,null,2)+'\n');
 console.log('PASS: complete accepted stdout, low-confidence fallback, metadata rejection and exactly-once original error propagation');
})().catch(e=>{console.error(e.name+': '+e.message);process.exitCode=1;});
