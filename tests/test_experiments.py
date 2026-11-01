import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from run_protocol_stress import fixture, implement, reference, checks, records
from run_reference_sensitivity import task_sensitivity


class ProtocolStressTests(unittest.TestCase):
    def test_count_and_payload_blind_spot(self):
        rows = fixture('optional_email', 0, 3)
        out = implement(rows, 'optional_email', 'identity_alias')
        self.assertEqual(checks(out, reference(rows, 'optional_email', 'preserve')), (True, True, False))
        self.assertEqual(len({r['id'] for r in out}), 9)

    def test_policy_changes_the_reference(self):
        rows = fixture('unmatched_join', 1, 3)
        out = implement(rows, 'unmatched_join', 'filter')
        self.assertTrue(checks(out, reference(rows, 'unmatched_join', 'filter'))[2])
        self.assertFalse(checks(out, reference(rows, 'unmatched_join', 'preserve'))[2])

    def test_id_multiset_detects_duplicate_even_with_same_count(self):
        a = [{'id':'1', 'value':'x'}, {'id':'2', 'value':'x'}]
        b = [{'id':'1', 'value':'x'}, {'id':'1', 'value':'x'}]
        self.assertEqual(records(a, False), records(b, False))
        self.assertNotEqual(records(a), records(b))

    def test_name_equality_is_not_identity_equality(self):
        rows = fixture('name_deduplication', 1, 1)
        self.assertEqual(len(reference(rows, 'name_deduplication', 'preserve')), 12)
        self.assertEqual(len(reference(rows, 'name_deduplication', 'filter')), 11)


class ReferenceSensitivityTests(unittest.TestCase):
    def test_overlapping_constraint_failures_use_union(self):
        samples = [
            {'passes_stated':True, 'passed_hidden':[], 'failed_hidden':['C2','C3']},
            {'passes_stated':True, 'passed_hidden':['C2'], 'failed_hidden':['C3']},
            {'passes_stated':False, 'passed_hidden':['C3'], 'failed_hidden':['C2']},
        ]
        r=task_sensitivity(samples)
        self.assertEqual(r['full_ivr'], 1.)
        self.assertEqual(r['minimum_ivr'], .5)
        self.assertEqual(r['single_constraint_mean_ivr'], .75)
        self.assertEqual(len(r['subsets']), 3)
        self.assertEqual(r['public_passers'], 2)

    def test_no_passers_does_not_create_subset_rates(self):
        r=task_sensitivity([{'passes_stated':False,'passed_hidden':[], 'failed_hidden':['C2']}])
        self.assertFalse(r['qualifies'])
        self.assertEqual(r['subsets'], [])

    def test_incomplete_outcomes_rejected(self):
        with self.assertRaises(ValueError):
            task_sensitivity([
                {'passes_stated':True,'passed_hidden':['C2'],'failed_hidden':[]},
                {'passes_stated':True,'passed_hidden':['C3'],'failed_hidden':[]},
            ])


if __name__ == '__main__':
    unittest.main()
