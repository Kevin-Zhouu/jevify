// Execute actual TS entrypoints; doubles represent ORIGINAL SDKs only.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const ts = require('typescript');
const [rootArg, fixture] = process.argv.slice(2);
const root = path.resolve(rootArg);
let calls = 0;
let logged = [];
const fail = async () => { throw new Error('Evaluator fault injection: network unavailable'); };
global.fetch = fail;
const original = {
  async generateObject(options) {
    calls++;
    return {object: options.output === 'enum' ? 'sci-fi' : {recipe:{name:'lasagna',ingredients:[{name:'pasta',amount:'1 cup'}],steps:['Cook.']}}, usage:{promptTokens:10,completionTokens:5,totalTokens:15},finishReason:'stop'};
  },
  async generateText() { calls++; return {text:'original generation',usage:{promptTokens:10,completionTokens:5,totalTokens:15},finishReason:'stop'}; },
  LangChainAdapter: {toDataStreamResponse: stream => new Response(stream.marker)},
};
const provider = Object.assign(() => ({}), {chat:()=>({})});
const modules = new Map();
function load(filename) {
  filename = path.resolve(filename);
  if (modules.has(filename)) return modules.get(filename).exports;
  const source = fs.readFileSync(filename,'utf8');
  const compiled = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true},reportDiagnostics:true});
  const errors = (compiled.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error);
  assert.equal(errors.length,0,JSON.stringify(errors));
  const mod = {exports:{}}; modules.set(filename,mod);
  function localRequire(name) {
    if (name==='ai') return original;
    if (name==='@ai-sdk/openai') return {openai:provider};
    if (name==='@ai-sdk/google') return {google:provider};
    if (name==='@langchain/openai') return {ChatOpenAI:class {async stream(prompt){calls++;return {marker:'stream:'+prompt};}}};
    if (name==='dotenv/config') return {};
    if (name.startsWith('.')) {
      let dest=path.resolve(path.dirname(filename),name);
      if (!fs.existsSync(dest)) dest=dest.replace(/\.js$/,'')+'.ts';
      return load(dest);
    }
    return require(name);
  }
  const fn=vm.runInThisContext('(function(require,module,exports,console){'+compiled.outputText+'\n})',{filename});
  fn(localRequire,mod,mod.exports,{...console,log:(...args)=>logged.push(args),error:(e)=>{throw e;}});
  return mod.exports;
}
(async()=>{
  const mod=load(path.join(root,'workflow.ts'));
  if(fixture==='langchain_completion') {
    const response=await mod.POST(new Request('https://example.invalid',{method:'POST',body:JSON.stringify({prompt:'hello'})}));
    assert.equal(await response.text(),'stream:hello');
    assert.equal(mod.maxDuration,30);
  }
  // Entrypoints call async main without exporting its promise.
  await new Promise(resolve=>setTimeout(resolve,1000));
  assert.equal(calls,1,'Original provider must answer once in fallback/offline smoke');
  if(fixture.includes('enum')) assert(logged.some(args=>args[0]==='sci-fi'));
  if(fixture==='vercel_recipe') assert(logged.some(args=>String(args[0]).includes('lasagna')));
  console.log('PASS: observable TypeScript behavior and original-path fallback smoke');
})().catch(e=>{console.error(e);process.exitCode=1;});
