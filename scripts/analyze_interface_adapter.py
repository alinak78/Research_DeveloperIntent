"""Explicitly post hoc, name-only adapter on the fresh pilot outputs; never edits raw logs."""
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from run_local_model_pilot import ROOT, OUT, evaluate, equivalent, summarize


def adapt(source):
    try:
        tree=ast.parse(source)
    except SyntaxError:
        return None, 'syntax_error'
    if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):
        return None, 'not_single_function'
    function=tree.body[0]
    if len(function.args.args)+len(function.args.posonlyargs)!=2 or function.args.vararg or function.args.kwarg or function.args.kwonlyargs:
        return None, 'incompatible_signature'
    if function.name=='solution':return source, 'already_named_solution'
    if any(isinstance(n,ast.Name) and n.id==function.name for n in ast.walk(function)):
        return None, 'self_reference_not_rewritten'
    function.name='solution'
    return ast.unparse(tree), 'function_name_only'


def main():
    tasks=json.loads((ROOT/'data/experiments/local_model_tasks.json').read_text())
    by_id={t['task_id']:t for t in tasks}
    raw=(OUT/'local_model_raw.jsonl').read_bytes()
    original=[json.loads(l) for l in raw.splitlines()]
    if len(original)!=120:raise ValueError('Wait for all 120 requested generations')
    records=[]
    for r in original:
        record={k:r[k] for k in ['task_id','family','condition','seed']}
        source,adapter_status=adapt(r.get('extracted_code',''))
        record['adapter_status']=adapter_status
        record['response']={'done_reason':r.get('response',{}).get('done_reason')}
        if 'generation_error' in r: record['generation_error']=r['generation_error']
        task=by_id[r['task_id']]
        cases=task['public_cases']+task['reference_cases']
        record['evaluation']=evaluate(source,cases) if source else {'status':'adapter_ineligible'}
        outcomes=record['evaluation'].get('cases',[])
        passes=[x.get('status')=='ok' and equivalent(x.get('output'),case['expected'])
                for x,case in zip(outcomes,cases)] if len(outcomes)==len(cases) else [False]*len(cases)
        record['case_passes']=passes
        record['public_pass']=all(passes[:len(task['public_cases'])])
        record['reference_pass']=all(passes[len(task['public_cases']):])
        records.append(record)
    summary=summarize(tasks,records)
    summary['provenance']='post hoc name-only interface normalization; no additional model generations'
    summary['raw_generation_input_sha256']=hashlib.sha256(raw).hexdigest()
    summary['adapter_counts']=dict(Counter(r['adapter_status'] for r in records))
    summary['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (OUT/'local_model_adapter_raw.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    (OUT/'local_model_adapter_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='conditions'},indent=2))
    for c,r in summary['conditions'].items():print(c,json.dumps({k:v for k,v in r.items() if k!='per_task'},indent=2))


if __name__=='__main__':main()
