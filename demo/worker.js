/* The browser executes the original Python checker; no JavaScript rule copy. */
import {loadPyodide} from './runtime/pyodide.mjs';
const PYODIDE_URL = 'runtime/';
let ready;
async function initialize() {
  const py = await loadPyodide({indexURL: PYODIDE_URL});
  const response = await fetch('check_events.py');
  if (!response.ok) throw new Error('Could not load the checker source.');
  py.FS.writeFile('check_events.py', await response.text());
  py.runPython('from check_events import check_feed, parse_timestamp, render_markdown, unique_object, reject_constant, InputError\nimport json');
  return py;
}
self.onmessage = async ({data}) => {
  const {id, input, asOf, days} = data;
  let errorType = 'input';
  try {
    if (typeof input !== 'string' || new TextEncoder().encode(input).length > 250000) throw new Error('Use a JSON feed smaller than 250 KB.');
    if (!Number.isInteger(days) || days < 0 || days > 36500) throw new Error('Source age must be a whole number from 0 to 36500.');
    errorType = 'runtime';
    if (!ready) ready = initialize().catch(error => { ready = null; throw error; });
    const py = await ready;
    errorType = 'input';
    py.globals.set('input_text', input);
    py.globals.set('reference_time', asOf);
    py.globals.set('age_limit', days);
    const output = py.runPython(`
payload = json.loads(input_text, object_pairs_hook=unique_object, parse_constant=reject_constant)
if isinstance(payload, dict) and isinstance(payload.get('events'), list) and len(payload['events']) > 500:
    raise InputError('The browser demo accepts at most 500 events.')
report = check_feed(payload, as_of=parse_timestamp(reference_time), max_source_age_days=age_limit)
json.dumps({'report': report, 'markdown': render_markdown(report)})
`);
    self.postMessage({id, ok: true, ...JSON.parse(output)});
  } catch(error) {
    const lines = String(error.message || error).trim().split('\n');
    self.postMessage({id, ok: false, errorType, diagnostic: errorType === 'runtime' ? String(error) : undefined, error: errorType === 'runtime'
      ? 'The checker could not load. Check your connection and retry, or use the Python tool linked above.'
      : lines.at(-1) || 'The checker could not complete. Please retry.'});
  }
};
