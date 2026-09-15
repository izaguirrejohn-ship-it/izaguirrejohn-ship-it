'use strict';
const $ = id => document.getElementById(id);
const samples = {
  review: {file:'review-events.json', asOf:'2026-09-15T12:00:00Z', note:'The problems in this sample are deliberately introduced. These are not real events.'},
  clean: {file:'clean-events.json', asOf:'2026-09-15T12:00:00Z', note:'A fictional event with two sources that describe the same instants using different UTC offsets.'},
  lisbon: {file:'normalized-events.json', asOf:'2026-09-15T14:44:41Z', note:'Three actual public listings, normalized for this dated case study. A passing result does not verify availability.'},
  local: {file:'collected-local-times.json', asOf:'2026-09-15T14:44:41Z', note:'Our intermediate import of public listings. Displayed local times have no UTC offsets yet; these findings concern our data representation.'}
};
const titles = {
  REQUIRED_TEXT:'A detail is missing', MISSING_TIMESTAMP:'A time is missing', INVALID_TIMESTAMP:'A timestamp needs attention',
  INVALID_EVENT:'An event record is malformed', INVALID_SOURCE:'A source record is malformed', MISSING_SOURCES:'Source evidence is missing',
  DUPLICATE_EVENT_ID:'An event ID is repeated', DUPLICATE_SOURCE_ID:'A source ID is repeated', INVALID_SOURCE_URL:'A source URL needs attention',
  FUTURE_SOURCE_CHECK:'A source check is in the future', INVALID_EVENT_INTERVAL:'The event time range is invalid', INVALID_SOURCE_INTERVAL:'A source time range is invalid',
  EVENT_DATE_MISMATCH:'The event and a source disagree', SOURCE_DATE_CONFLICT:'Sources disagree on a date', STALE_SOURCE:'A source needs a fresh check',
  UNSUPPORTED_EVENT_END:'The end time needs source support', UNKNOWN_FIELD:'An unfamiliar field needs review', EMPTY_FEED:'No events to check'
};
let worker = null, timer = null, runId = 0, sampleId = 0, busy = false, latest = null;

function badge(text, state='ready') { $('status-badge').textContent=text; $('status-badge').dataset.state=state; }
function clearReport(message='Input changed. Check the feed again.') {
  latest=null; $('report').hidden=true; $('empty-state').hidden=false;
  $('status').textContent=message; badge('READY');
}
function setBusy(value) {
  busy=value; $('run').disabled=value; $('cancel').hidden=!value;
  document.querySelectorAll('.sample, #feed, #as-of, #age').forEach(el=>el.disabled=value);
  $('run').firstChild.textContent=value?'Checking… ':'Check this feed ';
}
async function loadSample(key) {
  const token=++sampleId; clearReport('Loading the example…'); $('run').disabled=true;
  try {
    const response=await fetch('data/'+samples[key].file);
    if(!response.ok) throw new Error('Could not load this example. Please try again.');
    const input=await response.text(); if(token!==sampleId) return;
    $('feed').value=input; $('as-of').value=samples[key].asOf; $('age').value='7';
    $('sample-note').textContent=samples[key].note;
    document.querySelectorAll('.sample').forEach(el=>{const selected=el.dataset.sample===key;el.classList.toggle('selected',selected);el.setAttribute('aria-pressed',String(selected));});
    clearReport('Example ready. Check the feed to see the findings.'); $('run').disabled=false;
  } catch(error) { if(token===sampleId){$('status').textContent=error.message; badge('LOAD ERROR','error');} }
}
function stopWorker(message) {
  runId++; worker?.terminate(); worker=null; clearTimeout(timer); setBusy(false); clearReport(message); badge('STOPPED');
}
function render(result) {
  latest=result; const report=result.report;
  $('empty-state').hidden=true; $('report').hidden=false;
  badge(report.status==='pass'?'PASS':report.status==='review'?'REVIEW':'NEEDS REVIEW',report.status);
  $('status').textContent=report.status==='pass'?'No issues found by the configured checks.':'Check complete. Review the findings below.';
  $('events-count').textContent=report.summary.events; $('errors-count').textContent=report.summary.errors; $('warnings-count').textContent=report.summary.warnings;
  $('report-context').textContent=`${report.summary.sources} source records · Reference: ${report.as_of} · Age limit: ${report.max_source_age_days} days`;
  const list=$('findings'); list.replaceChildren();
  if(!report.issues.length){const p=document.createElement('p');p.className='no-findings';p.textContent='The supplied records are consistent with these checks. Source truth and event availability still need editorial verification.';list.append(p);}
  for(const [index, issue] of report.issues.entries()) {
    const details=document.createElement('details');details.className='finding';details.open=index===0;
    const summary=document.createElement('summary'), title=document.createElement('strong'), severity=document.createElement('span');
    title.textContent=titles[issue.code]||issue.code;severity.className='severity '+issue.severity;severity.textContent=issue.severity;
    summary.append(title,severity);details.append(summary);
    const action=document.createElement('p');action.textContent=issue.message;details.append(action);
    const location=document.createElement('p');location.className='location';location.textContent=(issue.event_id||'Feed')+' · '+issue.path;
    const code=document.createElement('code');code.textContent=issue.code;details.append(location,code);list.append(details);
  }
  $('runtime-note').textContent='Checked locally in your browser with the original Python rules.';
}
function run() {
  if(busy) return;
  clearReport('Loading the checker and reviewing the feed…');badge('CHECKING');setBusy(true);
  const id=++runId;
  try {
    if(!worker){worker=new Worker('worker.js?v=runtime-local-2');}
    worker.onmessage=({data})=>{
      if(data.id!==runId) return;clearTimeout(timer);setBusy(false);
      if(data.ok) render(data);
      else {if(data.errorType==='runtime') console.error('Signal Atlas runtime:',data.diagnostic);clearReport(data.error);badge(data.errorType==='runtime'?'LOAD ERROR':'INPUT ERROR','error');}
    };
    worker.onerror=()=>{stopWorker('The browser checker could not load. Check your connection and retry, or use the Python tool linked above.');badge('LOAD ERROR','error');};
    timer=setTimeout(()=>stopWorker('The check took too long. Try again or use a smaller feed.'),90000);
    worker.postMessage({id,input:$('feed').value,asOf:$('as-of').value,days:$('age').value.trim()===''?null:Number($('age').value)});
  } catch(error){stopWorker(error.message);badge('ERROR','error');}
}
function download(format) {
  if(!latest||busy) return;
  const content=format==='json'?JSON.stringify(latest.report,null,2)+'\n':latest.markdown;
  const url=URL.createObjectURL(new Blob([content],{type:format==='json'?'application/json':'text/markdown;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='signal-atlas-report.'+(format==='json'?'json':'md');a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
document.querySelectorAll('.sample').forEach(el=>el.addEventListener('click',()=>loadSample(el.dataset.sample)));
['feed','as-of','age'].forEach(id=>$(id).addEventListener('input',()=>{clearReport();if(id==='feed'){$('sample-note').textContent='Edited input. Your changes stay in this tab.';document.querySelectorAll('.sample').forEach(el=>{el.classList.remove('selected');el.setAttribute('aria-pressed','false');});}}));
$('run').addEventListener('click',run);$('cancel').addEventListener('click',()=>stopWorker('Check cancelled. Your input is preserved.'));
$('download-json').addEventListener('click',()=>download('json'));$('download-md').addEventListener('click',()=>download('markdown'));
loadSample('review');
