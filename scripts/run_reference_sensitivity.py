"""New reference-set perturbation experiment on archived outcomes, not new generations."""
from __future__ import annotations
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def task_sensitivity(samples):
    public = [s for s in samples if s['passes_stated']]
    ids = sorted({x for s in samples for x in s['passed_hidden']+s['failed_hidden']})
    if not ids:
        raise ValueError('No reference constraints')
    if any(set(s['passed_hidden']) & set(s['failed_hidden']) or
           set(s['passed_hidden']+s['failed_hidden']) != set(ids) for s in samples):
        raise ValueError('Inconsistent reference outcomes')
    if not public:
        return {'qualifies': False, 'public_passers': 0, 'subsets': []}
    subsets = []
    for size in range(1, len(ids)+1):
        for subset in itertools.combinations(ids, size):
            violations = sum(bool(set(subset) & set(s['failed_hidden'])) for s in public)
            subsets.append({'ids': list(subset), 'ivr': violations / len(public), 'violations': violations})
    singles = [r['ivr'] for r in subsets if len(r['ids']) == 1]
    return {'qualifies': True, 'public_passers': len(public), 'n_constraints': len(ids),
            'full_ivr': subsets[-1]['ivr'],
            'minimum_ivr': min(r['ivr'] for r in subsets),
            'maximum_ivr': max(r['ivr'] for r in subsets),
            'uniform_subset_mean_ivr': float(np.mean([r['ivr'] for r in subsets])),
            'single_constraint_mean_ivr': float(np.mean(singles)), 'subsets': subsets}


def main():
    output = {'run_utc': datetime.now(timezone.utc).isoformat(),
              'provenance': 'exhaustive reference-subset rescoring of archived outcomes; no prompts or generations changed',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'models': {}}
    for label in ['claude_sonnet_4_6', 'gpt_4_1']:
        path = ROOT/'data/pilot'/f'{label}.json'
        raw = path.read_bytes()
        data = json.loads(raw)
        per_task = {t: task_sensitivity(samples) for t,samples in data['per_task'].items()}
        qualified = [r for r in per_task.values() if r['qualifies']]
        summary = {'model_label': data['model'], 'input_sha256': hashlib.sha256(raw).hexdigest(),
                   'qualifying_tasks': len(qualified),
                   'n_task_subset_evaluations': sum(len(r['subsets']) for r in qualified),
                   'tasks_sensitive_to_subset': sum(r['minimum_ivr'] != r['maximum_ivr'] for r in qualified)}
        for key in ['full_ivr','minimum_ivr','maximum_ivr','uniform_subset_mean_ivr','single_constraint_mean_ivr']:
            summary['macro_'+key] = float(np.mean([r[key] for r in qualified]))
        output['models'][label] = {'summary': summary, 'per_task': per_task}
    c = output['models']['claude_sonnet_4_6']['per_task']
    g = output['models']['gpt_4_1']['per_task']
    common = sorted(t for t in c if c[t]['qualifies'] and g[t]['qualifies'])
    differences = np.array([g[t]['full_ivr']-c[t]['full_ivr'] for t in common])
    rng = np.random.RandomState(20261101)
    bootstrap = np.array([rng.choice(differences,len(differences),replace=True).mean() for _ in range(10000)])
    output['paired_common_support'] = {
        'n_tasks': len(common), 'task_ids': common,
        'excluded_task_ids': sorted(set(c)-set(common)),
        'claude_common_macro_ivr': float(np.mean([c[t]['full_ivr'] for t in common])),
        'gpt_common_macro_ivr': float(np.mean([g[t]['full_ivr'] for t in common])),
        'gpt_minus_claude_macro_ivr': float(differences.mean()),
        'paired_task_bootstrap_ci95': [float(x) for x in np.percentile(bootstrap,[2.5,97.5])],
        'n_bootstrap': 10000, 'seed': 20261101,
        'interpretation': 'exploratory paired task comparison; no new model generation or population inference'}
    path=ROOT/'results/experiments/reference_sensitivity.json'
    path.write_text(json.dumps(output,indent=2)+'\n')
    for label,r in output['models'].items():
        print(label,json.dumps(r['summary'],indent=2))
    print(json.dumps(output['paired_common_support'],indent=2))


if __name__ == '__main__':
    main()
