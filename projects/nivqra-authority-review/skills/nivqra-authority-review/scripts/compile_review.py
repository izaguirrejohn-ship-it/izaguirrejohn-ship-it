#!/usr/bin/env python3
"""Compile inert mandate documents and test specifications. No network or authority."""
import argparse
import csv
import io
import json
from datetime import datetime
from pathlib import Path

TEXT = ('principal','agent_id','agent_name','purpose','currency','approval_owner','new_counterparty_approval_owner','revocation_owner','valid_from','expires_at','notes')
LISTS = ('allowed_categories','blocked_categories','approved_counterparties','allowed_tools','approved_resources')
NUMBERS = ('per_action_limit_cents','period_limit_cents','approval_threshold_cents','max_uses')
FLAGS = ('require_new_counterparty_approval',)
FIELDS = TEXT + LISTS + NUMBERS + FLAGS
OPTIONAL = {'agent_id','max_uses','notes','allowed_tools','approved_resources','new_counterparty_approval_owner'}
GAPS = {'valid_from','expires_at','max_uses','allowed_tools','approved_resources'}
MAX_INT = 9_007_199_254_740_991

class InputError(ValueError):
    pass

def date(value):
    try:
        d = datetime.fromisoformat(value.replace('Z','+00:00'))
        if d.tzinfo is None or d.utcoffset() is None:
            raise ValueError()
        return d
    except (ValueError, AttributeError):
        raise InputError('Dates must be ISO 8601 datetimes with a timezone.') from None

def text_ok(v):
    return isinstance(v,str) and 0 < len(v.strip()) <= 4000 and not any(ord(c)<32 and c not in '\n\r\t' for c in v)

def normalize(src):
    if not isinstance(src,dict) or set(src) != {'schema_version','mandate','evidence'}:
        raise InputError('Expected schema_version, mandate and evidence only.')
    if type(src['schema_version']) is not int or src['schema_version'] != 1:
        raise InputError('schema_version must be integer 1.')
    raw,e = src['mandate'],src['evidence']
    if not isinstance(raw,dict) or not isinstance(e,dict):
        raise InputError('Mandate and evidence must be objects.')
    if (set(raw)|set(e)) - set(FIELDS):
        raise InputError('Unknown field; runtime flags and commands are not accepted.')
    m = {k:raw.get(k) for k in FIELDS}
    for k,v in m.items():
        if v is None: continue
        if k in TEXT:
            if not text_ok(v): raise InputError(f'{k} must be a nonempty string or null.')
            m[k]=v.strip()
        elif k in LISTS:
            if not isinstance(v,list) or len(v)>100 or any(not text_ok(x) for x in v):
                raise InputError(f'{k} must be a string array or null.')
            m[k]=[x.strip() for x in v]
            if len({x.casefold() for x in m[k]}) != len(v): raise InputError(f'{k} contains duplicates.')
        elif k in NUMBERS:
            if type(v) is not int or not 0 <= v < MAX_INT: raise InputError(f'{k} must be a nonnegative safe integer or null.')
            if k=='max_uses' and v==0: raise InputError('max_uses must be positive or null.')
        elif type(v) is not bool: raise InputError(f'{k} must be a boolean or null.')
    if m['currency'] not in (None,'EUR'): raise InputError('EUR only; do not silently convert currencies.')
    for k in ('valid_from','expires_at'):
        if m[k] is not None: date(m[k])
    if any(not text_ok(v) for v in e.values()): raise InputError('Evidence must contain nonempty source notes.')
    return m,{k:v.strip() for k,v in e.items()}

def findings(m,e):
    out=[]
    def add(code,fields,detail,severity='decision'):
        out.append(dict(code=code,fields=fields,detail=detail,severity=severity))
    for k in FIELDS:
        if m[k] is None and k not in OPTIONAL: add('needs_human_input',[k],f'Needs human input: {k}.')
        elif m[k] is not None and k not in e: add('missing_provenance',[k],f'No supporting source recorded for {k}.')
    if m['agent_id'] is None: add('identity_not_bound',['agent_id'],'Resolve the registered agent identity before runtime integration.','integration')
    allowed,blocked=m['allowed_categories'],m['blocked_categories']
    if allowed==[]: add('empty_allowlist',['allowed_categories'],'Resolve the intended scope and empty-list backend semantics; no authority is inferred.')
    if allowed and blocked and {s.casefold() for s in allowed}&{s.casefold() for s in blocked}:
        add('category_conflict',['allowed_categories','blocked_categories'],'The same category is both allowed and blocked.')
    for k in NUMBERS[:3]:
        if m[k]==0: add('zero_boundary',[k],'Zero is not interpreted as unlimited. Confirm intent and server semantics.')
    cap,budget,threshold=[m[k] for k in NUMBERS[:3]]
    if cap is not None and budget is not None and cap>budget:
        add('cap_above_period',list(NUMBERS[:2]),'Per-action ceiling exceeds the whole monthly cap; clarify the design.')
    if cap is not None and threshold is not None and threshold>=cap:
        add('unreachable_amount_review',[NUMBERS[0],NUMBERS[2]],'Amount-based review is unreachable inside the hard per-action ceiling; confirm intent.')
    if m['valid_from'] and m['expires_at'] and date(m['expires_at'])<=date(m['valid_from']):
        add('invalid_window',['valid_from','expires_at'],'Expiry must be later than the start of validity.')
    if m['require_new_counterparty_approval'] is False:
        add('new_counterparty_scope',['require_new_counterparty_approval'],'Confirm which other control limits counterparties when new-counterparty review is disabled.')
    if m['require_new_counterparty_approval'] is True and m['new_counterparty_approval_owner'] is None:
        add('needs_human_input',['new_counterparty_approval_owner'],'Needs human input: the new-counterparty approver. Do not infer this from the amount-threshold approver.')
    gaps=[k for k in FIELDS if k in GAPS and m[k] is not None]
    if gaps: add('verify_runtime_coverage',gaps,'Verify these design controls in the complete execution path; this package does not enforce them.','integration')
    return out

def scenarios(m):
    out=[]
    def add(i,name,setup,expect,required=()):
        out.append(dict(id=i,name=name,status='not_run',setup=setup,expected_assertion=expect,
          missing_inputs=[k for k in required if m[k] is None],
          precondition='Draft remains inactive. Active-path tests require separate human activation of a test copy in an authorized test environment.'))
    add('S01','Draft has no authority',{'mandate_state':'draft'},'Refuse execution under an inactive draft.')
    add('S02','Within the stated boundary',{'use':'Known category and counterparty; inside all positive numeric boundaries and validity.'},
        'After separate test activation, the canonical engine permits only if all applicable checks pass. Inspect its evidence.',
        ('allowed_categories','approved_counterparties','per_action_limit_cents','period_limit_cents','approval_threshold_cents','valid_from','expires_at'))
    for i,name,field,expect in [('S03','Per-action hard ceiling','per_action_limit_cents','Refuse an over-limit request; routing to approval alone is insufficient.'),
        ('S05','Human approval threshold','approval_threshold_cents','Inside hard limits and other rules, route to the named human without execution. Resolve an unreachable threshold first.')]:
        v=m[field]
        setup={'amount_cents':v+1 if v is not None else None}
        if i=='S05': setup['approval_owner']=m['approval_owner']
        add(i,name,setup,expect,(field,'approval_owner') if i=='S05' else (field,))
    add('S04','Monthly cap exhausted',{'spent_this_month_cents':m['period_limit_cents'],'amount_cents':1},
        'Refuse another one-cent action after a positive monthly cap is exhausted. Resolve zero-cap semantics first.',('period_limit_cents',))
    add('S06','New counterparty',{'is_new_counterparty':True,'review_required':m['require_new_counterparty_approval'],'approval_owner':m['new_counterparty_approval_owner']},
        'When review is required, route to the named new-counterparty approver. Otherwise verify the explicitly supplied counterparty scope.',('require_new_counterparty_approval','new_counterparty_approval_owner','approved_counterparties'))
    add('S07','Outside category scope',{'category':'A category outside the supplied allowlist'},'Refuse an out-of-scope category. Resolve empty-list semantics first.',('allowed_categories',))
    add('S08','Outside validity window',{'valid_from':m['valid_from'],'expires_at':m['expires_at']},
        'Refuse before valid_from and at/after expires_at in the complete execution path. This is an unverified coverage requirement.',('valid_from','expires_at'))
    add('S09','Revocation',{'revocation_owner':m['revocation_owner']},'After an authorized human revokes the test mandate, later and retried actions cannot execute.',('revocation_owner',))
    add('S10','Replay and concurrency',{'use':'Repeat an intent identifier and race two requests against the remaining cap'},'No duplicate execution or double draw; aggregate authority cannot be overspent. Verify in the execution path.')
    if m['max_uses'] is not None: add('S11','Use cap',{'completed_uses':m['max_uses']},'Refuse the next action after the use cap is exhausted.')
    if m['allowed_tools'] is not None or m['approved_resources'] is not None:
        add('S12','Tool and resource boundaries',{'allowed_tools':m['allowed_tools'],'approved_resources':m['approved_resources']},'Verify refusal for an out-of-scope tool/resource in the actual control layer; record any missing implementation.')
    add('S13','Exactly at the amount-review threshold',{'amount_cents':m['approval_threshold_cents'],'is_new_counterparty':False},
        'At a positive threshold, amount alone does not require review because the rule is strictly above. All other checks still apply.',('approval_threshold_cents',))
    add('S14','Exactly at the per-action hard limit',{'amount_cents':m['per_action_limit_cents']},
        'A request equal to a positive ceiling does not exceed it. It may still need human review or refusal under other rules.',('per_action_limit_cents',))
    if m['blocked_categories']:
        add('S15','Explicitly blocked category',{'category':m['blocked_categories'][0],'amount_cents':1},
            'Refuse this explicitly blocked category even for one cent. If also allowlisted, resolve the document conflict and verify refusal precedence.')
    return sorted(out,key=lambda x:x['id'])

def show(v):
    if v is None: return 'Needs human input'
    if v==[]: return 'Explicitly empty'
    if isinstance(v,list): return '; '.join(v)
    if type(v) is bool: return 'Yes' if v else 'No'
    return str(v)

def md(v):
    return show(v).replace('|','\\|').replace('\n',' ').replace('\r',' ').replace('<','&lt;').replace('>','&gt;')

def csv_safe(v):
    s=show(v)
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s

def build(src):
    m,e=normalize(src); issues=findings(m,e); cases=scenarios(m)
    state='needs_human_input' if any(x['severity']=='decision' for x in issues) else 'complete_for_human_review'
    d=dict(schema_version=1,package_version='1.0.0',status='draft',active=False,label='DRAFT · NOT ACTIVE',review_status=state,
           data_origin='user_supplied_design',runtime_verified=False,period='calendar_month',mandate=m,evidence=e,findings=issues)
    buf=io.StringIO(newline=''); w=csv.writer(buf); w.writerow(['Field','Proposed value','Evidence','Coverage'])
    lines=['# NIVQRA · Agent Authority Review','','**DRAFT · NOT ACTIVE**','',f"Agent: {md(m['agent_name'])}. Principal: {md(m['principal'])}.",'',
      'An authoring review of supplied information. No live workspace was read and no authority was granted, changed or revoked.','',
      f"Review state: **{state.replace('_',' ')}**. Amounts are EUR cents; period is calendar month.",'','## Permission matrix','','| Field | Proposed value | Evidence |','|---|---|---|']
    for k in FIELDS:
        w.writerow([k,csv_safe(m[k]),csv_safe(e.get(k)),'Requires runtime verification' if k in GAPS else 'Design review only'])
        lines.append(f'| {k} | {md(m[k])} | {md(e.get(k))} |')
    lines+=['','## Findings','']
    lines.extend([f"- **{x['code']}**: {x['detail']}" for x in issues] or ['No document-consistency findings. Human review and runtime validation are still required.'])
    lines+=['','## Scenario specifications','','All cases are **not run**. Expectations are test requirements, not observed policy decisions.','',
      '| Case | Test | Expected assertion | Missing inputs |','|---|---|---|---|']
    for c in cases: lines.append(f"| {c['id']} | {c['name']} | {md(c['expected_assertion'])} | {md(c['missing_inputs']) if c['missing_inputs'] else 'None for this specification'} |")
    lines+=['','## Human handoff','','Resolve findings with the responsible principal. Validate scenarios against the canonical NIVQRA backend in an authorized test environment. Activation is a separate human action. These files are not a drop-in runtime import.','']
    return {'mandate-draft.json':json.dumps(d,indent=2,ensure_ascii=False)+'\n','permission-matrix.csv':buf.getvalue(),
      'scenario-tests.json':json.dumps(dict(schema_version=1,status='not_run',live_actions=False,cases=cases),indent=2,ensure_ascii=False)+'\n',
      'authority-review.md':'\n'.join(lines)}

def reject_constant(_):
    raise InputError('Non-finite numeric values are not accepted.')

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--input',required=True,type=Path); p.add_argument('--out',required=True,type=Path); a=p.parse_args()
    try:
        if a.input.stat().st_size>1_000_000: raise InputError('Input exceeds 1 MB; use a task-specific description.')
        files=build(json.loads(a.input.read_text(encoding='utf-8'),parse_constant=reject_constant))
        a.out.mkdir(parents=True,exist_ok=False)
        for name,content in files.items(): (a.out/name).write_text(content,encoding='utf-8')
        print(json.dumps(dict(status='created',directory=str(a.out.resolve()),files=list(files),authority_granted=False)))
    except (InputError,json.JSONDecodeError,OSError) as exc: p.exit(2,f'Cannot create review: {exc}\n')

if __name__=='__main__': main()
