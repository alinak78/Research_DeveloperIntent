"""Reanalyze stored booleans; never execute candidate code or contact a model."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def summarize(data: dict, resamples: int = 10_000, seed: int = 42) -> dict:
    tasks = data["per_task"]
    if not tasks:
        raise ValueError("No tasks")
    task_rates, excluded = [], []
    total = passing = violations = hidden_failures = fully_compliant = 0
    per_task = {}
    for task_id, samples in tasks.items():
        if not samples:
            raise ValueError(f"No samples for {task_id}")
        for sample in samples:
            if type(sample.get("passes_stated")) is not bool:
                raise ValueError(f"Invalid passes_stated in {task_id}")
            for key in ("passed_hidden", "failed_hidden"):
                if not isinstance(sample.get(key), list):
                    raise ValueError(f"Invalid {key} in {task_id}")
            if not sample["passed_hidden"] and not sample["failed_hidden"]:
                raise ValueError(f"No reference outcome in {task_id}")
            if set(sample["passed_hidden"]) & set(sample["failed_hidden"]):
                raise ValueError(f"Conflicting reference outcome in {task_id}")
        p = sum(s["passes_stated"] for s in samples)
        v = sum(s["passes_stated"] and bool(s["failed_hidden"]) for s in samples)
        h = sum(bool(s["failed_hidden"]) for s in samples)
        rate = v / p if p else None
        if rate is None:
            excluded.append(task_id)
        else:
            task_rates.append(rate)
        per_task[task_id] = {"n": len(samples), "public_passers": p,
                             "violations_among_passers": v, "ivr": rate}
        total += len(samples)
        passing += p
        violations += v
        hidden_failures += h
        fully_compliant += p - v
    # Match the original RandomState algorithm, reseeded for each model.
    if task_rates:
        rng = np.random.RandomState(seed)
        rates = np.array(task_rates)
        means = np.array([rng.choice(rates, len(rates), replace=True).mean()
                          for _ in range(resamples)])
        ci = [float(x) for x in np.percentile(means, [2.5, 97.5])]
    else:
        ci = None
    return {
        "model_label_from_log": data.get("model", "unknown"),
        "n_tasks": len(tasks), "n_generations": total,
        "n_qualifying_tasks": len(task_rates), "excluded_task_ids": excluded,
        "public_passers": passing, "violations_among_passers": violations,
        "reference_failures_all_generations": hidden_failures,
        "fully_compliant": fully_compliant,
        "public_pass_rate": passing / total,
        "macro_ivr": float(np.mean(task_rates)) if task_rates else None,
        "micro_ivr": violations / passing if passing else None,
        "joint_public_pass_reference_fail_rate": violations / total,
        "reference_failure_rate_all_generations": hidden_failures / total,
        "full_compliance_rate": fully_compliant / total,
        "macro_ivr_ci95": ci, "bootstrap_resamples": resamples,
        "bootstrap_seed": seed, "per_task": per_task,
    }


def pct(value):
    return "undefined" if value is None else f"{100 * value:.1f}%"


def main():
    output = {}
    for name in ("claude_sonnet_4_6", "gpt_4_1"):
        path = ROOT / "data" / "pilot" / f"{name}.json"
        raw = path.read_bytes()
        result = summarize(json.loads(raw))
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        result["input_file"] = str(path.relative_to(ROOT))
        output[name] = result
    outdir = ROOT / "results"
    outdir.mkdir(exist_ok=True)
    (outdir / "pilot_summary.json").write_text(json.dumps(output, indent=2) + "\n")
    lines = ["# Reanalysis of archived algorithm pilot", "",
             "Stored pass/fail logs only; no new generation or candidate execution. "
             "Model identities are log labels, not independently verified snapshots.", "",
             "| Log label | N outputs | Qualifying tasks | Public pass | Macro IVR (95% CI) | Micro IVR | Joint failure | Full compliance |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in output.values():
        lo, hi = r["macro_ivr_ci95"]
        lines.append(f"| {r['model_label_from_log']} | {r['n_generations']} | "
                     f"{r['n_qualifying_tasks']}/{r['n_tasks']} | {pct(r['public_pass_rate'])} | "
                     f"{pct(r['macro_ivr'])} ({pct(lo)}-{pct(hi)}) | {pct(r['micro_ivr'])} | "
                     f"{pct(r['joint_public_pass_reference_fail_rate'])} | {pct(r['full_compliance_rate'])} |")
    lines += ["", "Macro IVR averages task-level conditional rates. Micro IVR pools qualifying outputs. "
              "Joint failure is public-pass/reference-fail over all outputs. Full compliance passes both sets. "
              "Undefined task IVRs are excluded, never treated as zero. CIs resample tasks 10,000 times with seed 42."]
    for r in output.values():
        lines += ["", f"## {r['model_label_from_log']}", "",
                  f"Public passers: {r['public_passers']}; violations among passers: {r['violations_among_passers']}; "
                  f"reference failures across all outputs: {r['reference_failures_all_generations']} "
                  f"({pct(r['reference_failure_rate_all_generations'])}).",
                  "Excluded tasks: " + ", ".join(r["excluded_task_ids"]),
                  f"Input SHA-256: `{r['input_sha256']}`"]
    lines += ["", "These purposively selected algorithm tasks do not estimate stakeholder harms, discrimination, "
              "or public-service deployment prevalence. The logs do not distinguish crashes from other failed tests."]
    report = "\n".join(lines) + "\n"
    (outdir / "pilot_summary.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
