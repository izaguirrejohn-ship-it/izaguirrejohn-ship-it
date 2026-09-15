/* Compare the browser worker's real Python outputs with the native compiler.
 * Only the module import and worker/file APIs are supplied by this harness.
 * This is not a browser-loading, layout or interaction test.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const {loadPyodide}=require('pyodide');
const root=path.resolve(__dirname,'..');
const compilerDir=path.join(root,'projects/nivqra-authority-review/skills/nivqra-authority-review/scripts');
const messages=[];
const context=vm.createContext({TextEncoder,console,self:{postMessage:message=>messages.push(message)},
  loadPyodide:()=>loadPyodide(),
  fetch:async url=>{assert.equal(url,'compile_review.py','The worker may fetch only its published compiler source');return {ok:true,text:async()=>fs.readFileSync(path.join(compilerDir,url),'utf8')};}
});
const source=fs.readFileSync(path.join(root,'demo/nivqra/worker.js'),'utf8');
const browserImport="import {loadPyodide} from '../runtime/pyodide.mjs';";
assert.ok(source.includes(browserImport));
vm.runInContext(source.replace(browserImport,''),context);
async function review(input){const id=messages.length+1;await context.self.onmessage({data:{id,input}});const result=messages.at(-1);assert.equal(result.id,id);return result;}
function native(input){return JSON.parse(execFileSync('python3',['-c','import json,sys;sys.path.insert(0,sys.argv[1]);from compile_review import build;print(json.dumps(build(json.loads(sys.stdin.read()))))',compilerDir],{input,encoding:'utf8'}));}
async function main(){
  const cases=['procurement','approval-gap','conflicting-boundaries'].map(name=>[name,fs.readFileSync(path.join(root,'demo/nivqra/data',name+'.json'),'utf8')]);
  cases.push(['blank',JSON.stringify({schema_version:1,mandate:{},evidence:{}})]);
  for(const [name,input] of cases){const result=await review(input);assert.equal(result.ok,true,result.error);assert.deepEqual(JSON.parse(JSON.stringify(result.files)),native(input));const draft=JSON.parse(result.files['mandate-draft.json']);const scenarios=JSON.parse(result.files['scenario-tests.json']);assert.equal(draft.active,false);assert.equal(draft.runtime_verified,false);assert.equal(scenarios.live_actions,false);assert.ok(scenarios.cases.every(item=>item.status==='not_run'));
    const decisions=draft.findings.filter(item=>item.severity==='decision');
    if(name==='procurement'){assert.equal(decisions.length,0);assert.equal(scenarios.cases.length,15);}
    if(name==='approval-gap'){assert.deepEqual(decisions.map(item=>item.fields),[['new_counterparty_approval_owner']]);assert.ok(draft.mandate.approval_owner);assert.equal(draft.mandate.new_counterparty_approval_owner,null);}
    if(name==='conflicting-boundaries')assert.deepEqual(decisions.map(item=>item.code),['category_conflict','unreachable_amount_review']);
    if(name==='blank'){assert.ok(Object.values(draft.mandate).every(value=>value===null));assert.deepEqual(draft.evidence,{});}
    console.log('PASS NIVQRA worker/native file parity: '+name);
  }
  for(const [name,input] of [
    ['malformed JSON','{broken'],
    ['duplicate keys','{"schema_version":1,"schema_version":1,"mandate":{},"evidence":{}}'],
    ['runtime command',JSON.stringify({schema_version:1,mandate:{active:true},evidence:{}})],
    ['unsupported currency',JSON.stringify({schema_version:1,mandate:{currency:'USD'},evidence:{}})],
    ['boolean as money',JSON.stringify({schema_version:1,mandate:{per_action_limit_cents:true},evidence:{}})],
    ['unsafe money','{"schema_version":1,"mandate":{"per_action_limit_cents":9007199254740991},"evidence":{}}'],
    ['missing date offset',JSON.stringify({schema_version:1,mandate:{valid_from:'2026-09-15T09:00:00'},evidence:{}})],
    ['oversized brief',' '.repeat(250001)]
  ]){const result=await review(input);assert.equal(result.ok,false,name);assert.equal(result.errorType,'input');assert.ok(result.error);console.log('PASS NIVQRA worker rejection: '+name);}
  console.log('12 NIVQRA worker checks passed. All generated authority remains inactive.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
