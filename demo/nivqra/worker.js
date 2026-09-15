/* Execute the published authoring compiler, with no duplicate decision engine. */
import {loadPyodide} from '../runtime/pyodide.mjs';
let ready;
async function initialize(){
  const py=await loadPyodide({indexURL:'../runtime/'});
  const response=await fetch('compile_review.py');
  if(!response.ok)throw new Error('Could not load the authoring source.');
  py.FS.writeFile('compile_review.py',await response.text());
  py.runPython(`from compile_review import build, InputError, reject_constant
import json
def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise InputError('Duplicate JSON key: ' + key)
        obj[key] = value
    return obj
`);
  return py;
}
self.onmessage=async({data})=>{
  const {id,input}=data;let errorType='input';
  try{
    if(typeof input!=='string'||new TextEncoder().encode(input).length>250000)throw new Error('Use a brief smaller than 250 KB.');
    errorType='runtime';
    if(!ready)ready=initialize().catch(error=>{ready=null;throw error;});
    const py=await ready;errorType='input';
    py.globals.set('input_text',input);
    const files=JSON.parse(py.runPython(`payload = json.loads(input_text, object_pairs_hook=unique_object, parse_constant=reject_constant)
files = build(payload)
json.dumps(files, ensure_ascii=False)
`));
    self.postMessage({id,ok:true,files});
  }catch(error){const lines=String(error.message||error).trim().split('\n');self.postMessage({id,ok:false,errorType,diagnostic:errorType==='runtime'?String(error):undefined,error:errorType==='runtime'?'The compiler could not load. Check your connection and retry, or use the Python package linked under Source.':lines.at(-1)||'The review could not be prepared.'});}
};
