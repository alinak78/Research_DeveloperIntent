import ast
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_interface_adapter import adapt
from run_local_model_pilot import make_task, make_prompt, summarize


class InterfaceAdapterTests(unittest.TestCase):
    def test_only_function_name_changes(self):
        source='def clean(rows, allowed):\n    return rows'
        output,status=adapt(source)
        self.assertEqual(status,'function_name_only')
        a=ast.parse(source).body[0];b=ast.parse(output).body[0]
        self.assertEqual(ast.dump(a.args),ast.dump(b.args))
        self.assertEqual([ast.dump(x) for x in a.body],[ast.dump(x) for x in b.body])
        self.assertEqual(b.name,'solution')

    def test_signature_and_recursive_calls_are_not_repaired(self):
        self.assertEqual(adapt('def clean(rows):\n    return rows')[1],'incompatible_signature')
        self.assertEqual(adapt('def clean(rows, allowed):\n    return clean(rows, allowed)')[1],'self_reference_not_rewritten')

    def test_public_examples_identical_between_conditions(self):
        task=make_task('optional_email','phone')
        a=make_prompt(task,'ambiguous').split('Public examples: ')[1]
        b=make_prompt(task,'explicit').split('Public examples: ')[1]
        self.assertEqual(a,b)
        self.assertNotIn('Reference policy:',make_prompt(task,'ambiguous'))

    def test_summary_keeps_undefined_ivr_and_length_stops(self):
        task=make_task('optional_email','phone')
        records=[{'task_id':task['task_id'],'family':task['family'],'condition':c,
                  'public_pass':False,'reference_pass':False,'evaluation':{'status':'rejected'},
                  'response':{'done_reason':'length'}} for c in ['ambiguous','explicit']]
        summary=summarize([task],records)
        for c in summary['conditions'].values():
            self.assertIsNone(c['macro_ivr'])
            self.assertEqual(c['truncated_generations'],1)
            self.assertEqual(c['full_compliance_rate'],0)


if __name__=='__main__':unittest.main()
