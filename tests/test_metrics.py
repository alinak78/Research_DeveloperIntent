import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_pilot import summarize


def sample(passes, fails):
    return {"passes_stated": passes, "passed_hidden": [] if fails else ["C2"],
            "failed_hidden": ["C2"] if fails else []}


class MetricsTests(unittest.TestCase):
    def test_unequal_task_denominators_and_undefined_task(self):
        report = summarize({"per_task": {
            "one": [sample(True, True)],
            "four": [sample(True, False)] * 4,
            "undefined": [sample(False, True)],
        }}, resamples=50)
        self.assertEqual(report["macro_ivr"], .5)
        self.assertEqual(report["micro_ivr"], .2)
        self.assertEqual(report["n_qualifying_tasks"], 2)
        self.assertIsNone(report["per_task"]["undefined"]["ivr"])
        self.assertEqual(report["joint_public_pass_reference_fail_rate"], 1/6)
        self.assertEqual(report["reference_failure_rate_all_generations"], 2/6)
        self.assertEqual(report["full_compliance_rate"], 4/6)

    def test_no_public_passers_is_not_zero_ivr(self):
        report = summarize({"per_task": {"task": [sample(False, True)]}}, resamples=10)
        self.assertIsNone(report["macro_ivr"])
        self.assertIsNone(report["micro_ivr"])
        self.assertIsNone(report["macro_ivr_ci95"])

    def test_missing_reference_outcomes_fail_closed(self):
        with self.assertRaises(ValueError):
            summarize({"per_task": {"task": [{"passes_stated": True,
                       "passed_hidden": [], "failed_hidden": []}]}}, resamples=10)


if __name__ == "__main__":
    unittest.main()
