"""New deterministic laboratory experiment; all implementations are authored controls."""
from __future__ import annotations
import copy
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = (0, 1, 3, 6)
FAMILIES = ('optional_email', 'name_deduplication', 'unmatched_join')
STRATEGIES = ('preserve', 'filter', 'identity_alias')
VARIANTS = ('original', 'reverse', 'swap_groups', 'rename_ids')


def fixture(family, a, b):
    rows = []
    for group, count in [('A', a), ('B', b)]:
        for i in range(6):
            hazard = i < count
            rid = f'{group}{i}'
            rows.append({'id': rid, 'group': group,
                         'name': ' Shared ' if family == 'name_deduplication' and hazard else f' Person {rid} ',
                         'email': None if family == 'optional_email' and hazard else f' {rid}@example.invalid ',
                         'lookup_key': None if family == 'unmatched_join' and hazard else f'key-{rid}'})
    return rows


def normalize(rows):
    return [{**r, 'name': r['name'].strip(),
             'email': r['email'].strip() if r['email'] is not None else None}
            for r in copy.deepcopy(rows)]


def filtered(rows, family):
    """Implementation of an explicit filter policy, not a universal gold policy."""
    if family == 'optional_email':
        return [r for r in rows if r['email'] is not None]
    if family == 'unmatched_join':
        return [r for r in rows if r['lookup_key'] is not None]
    seen, result = set(), []
    for row in rows:
        if row['name'] not in seen:
            result.append(row)
            seen.add(row['name'])
    return result


def implement(rows, family, strategy):
    normalized = normalize(rows)
    if strategy == 'preserve':
        return normalized
    kept = filtered(normalized, family)
    if strategy == 'filter':
        return kept
    if strategy != 'identity_alias':
        raise ValueError(strategy)
    # Deliberate adversarial control: restore removed payloads under the wrong identity.
    # This preserves record count and non-ID content, exposing identity-blind oracles.
    kept_ids = {r['id'] for r in kept}
    alias = kept[0]['id'] if kept else '__no_surviving_id__'
    return kept + [{**r, 'id': alias} for r in normalized if r['id'] not in kept_ids]


def reference(rows, family, policy):
    """Separate specification oracle with explicit policy branches."""
    out = []
    seen = set()
    for row in rows:
        name = row['name'].strip()
        email = None if row['email'] is None else row['email'].strip()
        if policy == 'filter':
            if family == 'optional_email' and email is None:
                continue
            if family == 'unmatched_join' and row['lookup_key'] is None:
                continue
            if family == 'name_deduplication' and name in seen:
                continue
        elif policy != 'preserve':
            raise ValueError(policy)
        seen.add(name)
        out.append({**row, 'name': name, 'email': email})
    return out


def records(rows, include_id=True):
    return Counter(json.dumps({k: v for k, v in r.items() if include_id or k != 'id'}, sort_keys=True)
                   for r in rows)


def checks(output, expected):
    count_ok = len(output) == len(expected)
    payload_ok = records(output, False) == records(expected, False)
    exact_ok = records(output) == records(expected)
    return count_ok, payload_ok, exact_ok


def transform(rows, variant):
    out = copy.deepcopy(rows)
    if variant == 'reverse':
        out.reverse()
    elif variant == 'swap_groups':
        for r in out:
            r['group'] = {'A': 'B', 'B': 'A'}[r['group']]
    elif variant == 'rename_ids':
        for i, r in enumerate(out):
            r['id'] = f'renamed-{i:02d}'
    return out


def summarize_evaluations(evaluations):
    counts = defaultdict(lambda: Counter())
    for r in evaluations:
        key = (r['family'], r['strategy'], r['policy'])
        c = counts[key]
        c['n'] += 1
        for field in ('count_pass', 'payload_pass', 'exact_pass', 'weak_both_pass', 'false_reassurance'):
            c[field] += int(r[field])
    return [{'family': f, 'strategy': s, 'policy': p, **dict(c)} for (f,s,p), c in sorted(counts.items())]


def main():
    evaluations = []
    public_count = 0
    for family in FAMILIES:
        public = fixture(family, 0, 0)
        for strategy in STRATEGIES:
            assert checks(implement(public, family, strategy), reference(public, family, 'preserve')) == (True, True, True)
            public_count += 1
        for a, b in itertools.product(LEVELS, repeat=2):
            for variant in VARIANTS:
                rows = transform(fixture(family, a, b), variant)
                for strategy in STRATEGIES:
                    output = implement(rows, family, strategy)
                    for policy in ('preserve', 'filter'):
                        expected = reference(rows, family, policy)
                        count_ok, payload_ok, exact_ok = checks(output, expected)
                        row = {'family': family, 'strategy': strategy, 'policy': policy,
                               'hazard_A_before_variant': a, 'hazard_B_before_variant': b,
                               'variant': variant, 'input': rows, 'output': output, 'expected': expected,
                               'count_pass': count_ok, 'payload_pass': payload_ok, 'exact_pass': exact_ok,
                               'weak_both_pass': count_ok and payload_ok,
                               'false_reassurance': count_ok and payload_ok and not exact_ok}
                        if policy == 'preserve':
                            remaining = {r['id'] for r in output}
                            losses = {}
                            for group in ('A', 'B'):
                                ids = {r['id'] for r in rows if r['group'] == group}
                                losses[group] = len(ids - remaining) / len(ids)
                            row['group_id_loss'] = losses
                            row['B_minus_A_id_loss'] = losses['B'] - losses['A']
                        evaluations.append(row)
    assert len(evaluations) == 1152
    # Controls must be perfect under their matching policy.
    assert all(r['exact_pass'] for r in evaluations if r['strategy'] == r['policy'])
    assert any(r['false_reassurance'] for r in evaluations)
    out = ROOT / 'results/experiments'
    out.mkdir(parents=True, exist_ok=True)
    raw = ''.join(json.dumps(r, sort_keys=True) + '\n' for r in evaluations)
    (out / 'protocol_stress_raw.jsonl').write_text(raw)
    summary = {
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'design': '3 families x 16 compositions x 4 variants x 3 authored strategies x 2 authored policies',
        'provenance': 'researcher-authored synthetic data and implementations; no model generations or institutional policies',
        'n_evaluations': len(evaluations), 'n_distinct_fixtures': 192,
        'n_ordinary_case_checks_passed': public_count,
        'raw_sha256': hashlib.sha256(raw.encode()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'design_sha256': hashlib.sha256((ROOT/'data/experiments/protocol_v1.md').read_bytes()).hexdigest(),
        'group_gap_range_preserve_policy': [min(r['B_minus_A_id_loss'] for r in evaluations if r['policy']=='preserve'),
                                            max(r['B_minus_A_id_loss'] for r in evaluations if r['policy']=='preserve')],
        'cells': summarize_evaluations(evaluations),
    }
    (out / 'protocol_stress_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['cells']}, indent=2))
    for r in summary['cells']:
        print(r)


if __name__ == '__main__':
    main()
