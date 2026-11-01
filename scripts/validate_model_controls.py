"""Authored controls verify the same execution path used for generated candidates."""
import json
from run_local_model_pilot import ROOT, OUT, evaluate, equivalent


def main():
    tasks=json.loads((ROOT/'data/experiments/local_model_tasks.json').read_text())
    records=[]
    for task in tasks:
        field=repr(task['field'])
        duplicate=task['family']=='name_deduplication'
        code=("def solution(rows, allowed):\n    result = []\n    seen = set()\n    for row in rows:\n"+
              ("        if row['id'] in seen:\n            continue\n" if duplicate else "")+
              "        seen.add(row['id'])\n        item = dict(row)\n"+
              f"        value = item[{field}]\n        item[{field}] = value.strip() if isinstance(value, str) else value\n"+
              "        result.append(item)\n    return result")
        cases=task['public_cases']+task['reference_cases']
        evaluation=evaluate(code,cases)
        passed=evaluation.get('status')=='evaluated' and all(
            r.get('status')=='ok' and equivalent(r.get('output'),c['expected'])
            for r,c in zip(evaluation.get('cases',[]),cases)) and len(evaluation.get('cases',[]))==len(cases)
        assert passed, (task['task_id'],evaluation)
        records.append({'task_id':task['task_id'],'authored_positive_control_pass':passed,'evaluation':evaluation})
    # Verify rejection before execution of prohibited host-file access.
    invalid=evaluate("def solution(rows, allowed):\n    return open('/etc/passwd').read()",tasks[0]['public_cases'])
    assert invalid['status']=='rejected', invalid
    (OUT/'local_model_controls.json').write_text(json.dumps({'positive_controls':records,
        'prohibited_file_access_rejected':invalid},indent=2)+'\n')
    print('PASS: all 12 authored positive controls pass all six cases through the model execution path.')
    print('PASS: prohibited host-file access is rejected before execution.')


if __name__=='__main__':main()
