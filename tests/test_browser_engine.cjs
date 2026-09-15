/* Exercise the actual worker handler and Pyodide engine without a browser UI.
 * Node supplies worker APIs and serves the same-origin Python file from disk.
 * The Python runtime and worker evaluation path are real, not mocked results.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {loadPyodide} = require('pyodide');
const root = path.resolve(__dirname, '..');
const project = path.join(root, 'projects/signal-atlas-data-quality');
const messages = [];
const context = vm.createContext({
  TextEncoder, console,
  self: {postMessage: message => messages.push(message)},
  // The official Node package supplies the same pinned Pyodide version.
  importScripts: url => assert.equal(url, 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js'),
  loadPyodide: () => loadPyodide(),
  fetch: async url => {
    assert.equal(url, 'check_events.py', 'The worker must not fetch event source URLs');
    return {ok: true, text: async () => fs.readFileSync(path.join(project, url), 'utf8')};
  }
});
vm.runInContext(fs.readFileSync(path.join(root, 'demo/worker.js'), 'utf8'), context);
async function check(input, asOf='2026-09-15T12:00:00Z', days=7) {
  const id=messages.length+1;
  await context.self.onmessage({data:{id,input,asOf,days}});
  const result=messages.at(-1);
  assert.equal(result.id,id);
  return result;
}
async function main() {
  const cases=[
    ['examples/clean-events.json','examples/reports/clean.json','2026-09-15T12:00:00Z'],
    ['examples/review-events.json','examples/reports/review.json','2026-09-15T12:00:00Z'],
    ['case-study/collected-local-times.json','case-study/before-report.json','2026-09-15T14:44:41Z'],
    ['case-study/normalized-events.json','case-study/after-report.json','2026-09-15T14:44:41Z']
  ];
  for(const [input, expected, asOf] of cases){
    const result=await check(fs.readFileSync(path.join(project,input),'utf8'),asOf);
    assert.equal(result.ok,true,result.error);
    assert.deepEqual(JSON.parse(JSON.stringify(result.report)),JSON.parse(fs.readFileSync(path.join(project,expected),'utf8')));
    assert.match(result.markdown,/# Signal Atlas/);
    console.log('PASS worker/native parity: '+input);
  }
  for(const [label, input, asOf, days] of [
    ['duplicate keys','{"schema_version":1,"schema_version":1,"events":[]}',undefined,7],
    ['nonstandard JSON','{"schema_version":1,"events":[],"x":NaN}',undefined,7],
    ['missing offset','{"schema_version":1,"events":[]}','2026-09-15T12:00:00',7],
    ['invalid policy','{"schema_version":1,"events":[]}',undefined,null],
    ['oversized input',' '.repeat(250001),undefined,7],
    ['too many events',JSON.stringify({schema_version:1,events:Array(501).fill({})}),undefined,7]
  ]){
    const result=await check(input,asOf,days);
    assert.equal(result.ok,false,label+' should fail');
    assert.ok(result.error);
    console.log('PASS worker rejection: '+label);
  }
  console.log('10 worker checks passed with Pyodide 314.0.7. Browser layout and interaction remain separate checks.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
