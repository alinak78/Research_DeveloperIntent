"""Fresh local Ollama generations and screened, sandboxed synthetic evaluation."""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/experiments'
MODEL = 'llama3.2:1b'
SEEDS = [17,29,43,61,89]
FIELDS = {'optional_email':['email','phone','postcode','middle_name'],
          'name_deduplication':['name','email','address','phone'],
          'unmatched_join':['district','language','office','region']}


def reference(rows, family, field):
    out, seen = [], set()
    for row in rows:
        if family == 'name_deduplication' and row['id'] in seen:
            continue
        seen.add(row['id'])
        value = row[field]
        out.append({**row, field: value.strip() if isinstance(value,str) else value})
    return out


def make_task(family, field):
    def rows(values, ids=None):
        return [{'id': ids[i] if ids else f'R{i}', 'group': 'A' if i<2 else 'B', field:value,
                 'untouched':f'payload-{i}'} for i,value in enumerate(values)]
    public = [{'rows':rows([' Alpha ', ' Beta ']), 'allowed':['Alpha','Beta']},
              {'rows':rows([' Gamma ',' Delta ',' Epsilon ']), 'allowed':['Gamma','Delta','Epsilon']}]
    if family == 'optional_email':
        desc = f"Normalize whitespace in the '{field}' field of intake records. Return cleaned records as a list of dictionaries."
        policy = f"The '{field}' field is optional: retain every input row, including rows where this field is None. Strip only string values in this field; leave None unchanged. Preserve each id and all other fields exactly; do not add fields."
        hidden = [rows([' Alpha ',None,' Beta ',None]), rows([None,None,None,None]),
                  rows([None,' Beta ',None,' Delta ']), rows([' Alpha ',None,' Beta ',None])[::-1]]
    elif family == 'name_deduplication':
        desc = f"Clean duplicate-looking intake records using '{field}' as a comparison field. Strip whitespace in '{field}' and return cleaned record dictionaries."
        policy = f"Deduplicate only on exact equality of id, keeping the first input row for a repeated id. Distinct ids must remain separate even when '{field}' values match. Strip whitespace only in '{field}'; preserve all other fields and do not add fields."
        hidden = [rows([' Shared ',' Shared ',' Other ',' Shared ']),
                  rows([' First ',' Second ',' Third ',' Fourth '], ['R0','R0','R1','R1']),
                  rows([' Shared ',' Shared ',' Other ',' Shared '], ['R0','R1','R1','R2']),
                  rows([' Shared ',' Shared ',' Other ',' Shared '], ['R0','R1','R1','R2'])[::-1]]
    else:
        desc = f"Clean intake records using a lookup of known '{field}' values supplied in allowed. Strip whitespace in '{field}' and return cleaned record dictionaries."
        policy = f"The lookup is advisory, not an exclusion rule: retain all input rows, including records whose '{field}' value is absent from allowed. Strip whitespace only in '{field}'; preserve each id and every other field exactly, and do not add fields."
        hidden = [rows([' Alpha ',' Unknown ',' Beta ',' Unknown ']), rows([' Unknown ']*4),
                  rows([' Unknown ',' Beta ',' Unknown ',' Alpha ']), rows([' Alpha ',' Unknown ',' Beta ',' Unknown '])[::-1]]
    hidden = [{'rows':r,'allowed':['Alpha','Beta']} for r in hidden]
    task = {'task_id':f'{family}__{field}','family':family,'field':field,
            'ambiguous_request':desc,'explicit_policy':policy,
            'provenance':'researcher-authored synthetic task and reference; not institutional policy',
            'public_cases':public,'reference_cases':hidden}
    for case in public+hidden:
        case['expected'] = reference(case['rows'],family,field)
    return task


def make_prompt(task, condition):
    prompt = task['ambiguous_request']+'\n'
    if condition == 'explicit':
        prompt += 'Reference policy: '+task['explicit_policy']+'\n'
    # Identical public examples across conditions; no reference cases are exposed.
    examples = [{'rows':c['rows'],'allowed':c['allowed'],'expected':c['expected']} for c in task['public_cases']]
    return prompt+'Public examples: '+json.dumps(examples)+'\nImplement solution(rows, allowed). Return only Python function definition(s), no imports, annotations, prose or markdown. Use built-in types only. Output order is not scored.'


def api(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request('http://127.0.0.1:11434'+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as response:
        return json.load(response)


def extract(text):
    blocks = re.findall(r'```(?:python|py)?\s*\n(.*?)```',text,re.S)
    return blocks[0].strip() if blocks else text.strip()


def evaluate(source, cases):
    command = ['/usr/bin/sandbox-exec','-f',str(ROOT/'scripts/candidate.sb'),
               sys.executable,'-I','-S',str(ROOT/'scripts/candidate_worker.py')]
    try:
        run = subprocess.run(command,input=json.dumps({'source':source,'cases':cases}),
                             capture_output=True,text=True,timeout=4)
        if run.returncode:
            return {'status':'process_failure','returncode':run.returncode,'stderr':run.stderr[:200]}
        return json.loads(run.stdout)
    except subprocess.TimeoutExpired:
        return {'status':'timeout'}
    except (ValueError, OSError) as exc:
        return {'status':'harness_error','reason':str(exc)[:200]}


def equivalent(actual, expected):
    if not isinstance(actual,list) or any(not isinstance(r,dict) for r in actual):
        return False
    return Counter(json.dumps(r,sort_keys=True) for r in actual)==Counter(json.dumps(r,sort_keys=True) for r in expected)


def summarize(tasks, records):
    conditions = {}
    for condition in ['ambiguous','explicit']:
        selected=[r for r in records if r['condition']==condition]
        task_rows={}
        for t in tasks:
            rs=[r for r in selected if r['task_id']==t['task_id']]
            p=sum(r['public_pass'] for r in rs)
            v=sum(r['public_pass'] and not r['reference_pass'] for r in rs)
            task_rows[t['task_id']]={'n':len(rs),'public_passers':p,'violations_among_passers':v,
                                    'ivr':v/p if p else None,'full_compliance':sum(r['public_pass'] and r['reference_pass'] for r in rs),
                                    'family':t['family']}
        n=len(selected); p=sum(r['public_pass'] for r in selected)
        v=sum(r['public_pass'] and not r['reference_pass'] for r in selected)
        full=sum(r['public_pass'] and r['reference_pass'] for r in selected)
        defined=[r['ivr'] for r in task_rows.values() if r['ivr'] is not None]
        conditions[condition]={'n':n,'public_passers':p,'public_pass_rate':p/n if n else None,
                               'full_compliance':full,'full_compliance_rate':full/n if n else None,
                               'violations_among_passers':v,'joint_failure_rate':v/n if n else None,
                               'macro_ivr':sum(defined)/len(defined) if defined else None,
                               'micro_ivr':v/p if p else None,'qualifying_tasks':len(defined),
                               'evaluation_statuses':dict(Counter(r['evaluation']['status'] for r in selected)),
                               'generation_failures':sum('generation_error' in r for r in selected),
                               'truncated_generations':sum(r.get('response',{}).get('done_reason')=='length' for r in selected),
                               'per_task':task_rows}
    families={}
    for family in FIELDS:
        families[family]={}
        for condition in conditions:
            rs=[r for r in records if r['family']==family and r['condition']==condition]
            families[family][condition]={'n':len(rs),'public_passers':sum(r['public_pass'] for r in rs),
                                        'full_compliance':sum(r['public_pass'] and r['reference_pass'] for r in rs)}
    return {'conditions':conditions,'families':families,
            'full_compliance_explicit_minus_ambiguous':conditions['explicit']['full_compliance_rate']-conditions['ambiguous']['full_compliance_rate']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--analyze-only',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    tasks=[make_task(f,field) for f,fields in FIELDS.items() for field in fields]
    task_path=ROOT/'data/experiments/local_model_tasks.json'
    if not task_path.exists():
        task_path.write_text(json.dumps(tasks,indent=2)+'\n')
    elif json.loads(task_path.read_text()) != tasks:
        raise ValueError('Task definitions changed after freeze')
    raw_path=OUT/'local_model_raw.jsonl'
    records=[json.loads(line) for line in raw_path.read_text().splitlines()] if raw_path.exists() else []
    completed={(r['task_id'],r['condition'],r['seed']) for r in records}
    if not args.analyze_only:
        metadata={'run_start_utc':datetime.now(timezone.utc).isoformat(),'models':api('/api/tags'),
                  'server_version':api('/api/version'),'model':MODEL,
                  'settings':{'temperature':.8,'top_p':.9,'num_predict':512,'num_ctx':2048},
                  'design_sha256':hashlib.sha256((ROOT/'data/experiments/local_model_protocol.md').read_bytes()).hexdigest(),
                  'tasks_sha256':hashlib.sha256(task_path.read_bytes()).hexdigest(),
                  'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'worker_sha256':hashlib.sha256((ROOT/'scripts/candidate_worker.py').read_bytes()).hexdigest()}
        meta_path=OUT/'local_model_metadata.json'
        if not meta_path.exists():meta_path.write_text(json.dumps(metadata,indent=2)+'\n')
        schedule=[(t,c,seed) for t in tasks for c in ['ambiguous','explicit'] for seed in SEEDS]
        random.Random(20261101).shuffle(schedule)
        for task,condition,seed in schedule:
            if (task['task_id'],condition,seed) in completed:continue
            body={'model':MODEL,'prompt':make_prompt(task,condition),'stream':False,
                  'options':{**metadata['settings'],'seed':seed},'keep_alive':'10m'}
            record={'task_id':task['task_id'],'family':task['family'],'condition':condition,'seed':seed,
                    'request':body,'requested_utc':datetime.now(timezone.utc).isoformat()}
            try:
                response=api('/api/generate',body)
                record['response']=response
                source=extract(response.get('response',''))
                record['extracted_code']=source
                evaluation=evaluate(source,task['public_cases']+task['reference_cases'])
            except Exception as exc:
                record['generation_error']=type(exc).__name__+': '+str(exc)[:200]
                evaluation={'status':'generation_failure'}
            record['evaluation']=evaluation
            outcomes=evaluation.get('cases',[])
            cases=task['public_cases']+task['reference_cases']
            passes=[r.get('status')=='ok' and equivalent(r.get('output'),case['expected'])
                    for r,case in zip(outcomes,cases)] if len(outcomes)==len(cases) else [False]*len(cases)
            record['case_passes']=passes
            record['public_pass']=all(passes[:len(task['public_cases'])])
            record['reference_pass']=all(passes[len(task['public_cases']):])
            with raw_path.open('a') as handle:handle.write(json.dumps(record)+'\n')
            records.append(record)
            if len(records)%10==0:print(f'Completed {len(records)}/120 generations',flush=True)
    summary=summarize(tasks,records)
    summary['n_records']=len(records)
    summary['raw_sha256']=hashlib.sha256(raw_path.read_bytes()).hexdigest()
    (OUT/'local_model_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='conditions'},indent=2),flush=True)
    for c,r in summary['conditions'].items():print(c,json.dumps({k:v for k,v in r.items() if k!='per_task'},indent=2),flush=True)


if __name__=='__main__':main()
