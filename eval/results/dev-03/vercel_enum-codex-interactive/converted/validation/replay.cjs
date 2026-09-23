// Offline assertions against genuine saved responses and the final decisions module.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),ts=require('typescript');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'jevDecisions.ts'),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const mod={exports:{}};vm.runInThisContext('(function(require,module,exports){'+compiled+'\n})')(require,mod,mod.exports);
const d=mod.exports, evidence=JSON.parse(fs.readFileSync(path.join(root,'JEV_PARITY.json'),'utf8'));
const nativeFetch=global.fetch,key=process.env.OPENROUTER_API_KEY;
const sentinel={object:'sentinel',usage:{promptTokens:1,completionTokens:2,totalTokens:3},finishReason:'stop'};
(async()=>{
  // Placeholder enables offline replay only; it is never sent to a network.
  process.env.OPENROUTER_API_KEY='offline-placeholder';
  try{
    for(const row of evidence.sites[0].rows){
      global.fetch=async()=>new Response(JSON.stringify(row.response));
      let calls=0;const out=await d.withGenreFallback({prompt:row.input},async()=>{calls++;return sentinel;});
      assert.equal(calls,row.fallback_taken?1:0);
      assert.deepEqual(out,row.fallback_taken?sentinel:d.parseGenre(row.response).result);
      const req=row.original_request;
      const adapted={...req,model:row.original_model};
      assert.deepEqual({...adapted,model:d.ORIGINAL_MODEL},req);
    }
    const captured=evidence.sites[0].rows[0].response;
    for(const confidence of [NaN,Infinity,-Infinity,true,-0.1,1.1]){
      const body=structuredClone(captured);body.answers.genre.confidence=confidence;
      global.fetch=async()=>({ok:true,json:async()=>body});
      let calls=0;assert.equal(await d.withGenreFallback({prompt:'fault injection'},async()=>{calls++;return sentinel;}),sentinel);assert.equal(calls,1);
    }
    // Confirm the timeout remains active after headers, until the body is read.
    global.fetch=async(_url,init)=>({ok:true,json:()=>new Promise((_,reject)=>init.signal.addEventListener('abort',()=>reject(new DOMException('injected body abort','AbortError')),{once:true}))});
    let calls=0;const start=performance.now();
    assert.equal(await d.withGenreFallback({prompt:'body timeout'},async()=>{calls++;return sentinel;}),sentinel);
    assert.equal(calls,1);assert(performance.now()-start>=d.TIMEOUT_MS-100);
    console.log('PASS: 30 captured-response replays, transport namespace identity, invalid numeric confidence, body-read timeout');
  }finally{global.fetch=nativeFetch;if(key===undefined)delete process.env.OPENROUTER_API_KEY;else process.env.OPENROUTER_API_KEY=key;}
})().catch(e=>{console.error('Replay failed:',e.name);process.exitCode=1;});
