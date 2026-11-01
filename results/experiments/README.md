# Executed experiments, November 1, 2026

The manuscript includes three new experiments. Only the local model pilot contains new model generations. All new domain tasks and policies are researcher-authored and synthetic. This is not the planned source-grounded public-service audit.

## 1. Fresh local Llama generations

- 120 new responses: 12 field templates x 2 conditions x 5 requested seeds; three dependent operation families.
- Local Ollama 0.34.0, `llama3.2:1b`, server-reported 1.2B parameters, Q8_0. Full digest: `baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878`.
- Temperature 0.8, top_p 0.9, 512 output tokens, context 2048; seeds 17/29/43/61/89. Request order seed 20261101. Identical public examples between conditions; reference policy added only in explicit condition. Two public and four held-out cases per template.
- All requests returned. One explicit response reached its output limit. Requests, responses, timestamps, token counts, stop reasons, exact code and evaluations are preserved in `local_model_raw.jsonl`.
- **Primary strict result:** public pass and full compliance 0/60 in both conditions; macro/micro IVR undefined in both. Gate failures: missing `solution` name 112, syntax errors 7, unsupported module-level statements 1. This is not evidence of zero violations or a failed policy intervention.
- **Post hoc name-only adapter:** documented after the first 55 failures. Seventy single two-argument functions were eligible for name normalization, fifty were ineligible, and seven eligible functions still failed the language gate. Nothing in the function body or interface arguments was repaired. All raw strict results remain unchanged.
- Adapter public pass: 9/60 ambiguous and 8/60 explicit. Full compliance: 0/60 and 4/60. Task-macro IVR: 100.0% over seven qualifying templates and 58.3% over six; micro IVR: 100.0% and 50.0%. Do not compare those different qualifying sets as a causal effect. Only three synthetic families and one small model were used; no confirmatory significance claim is made.
- Authored positive controls pass all six cases for all twelve templates through the same sandbox. Prohibited host-file access is rejected at the AST gate.

Files: `local_model_metadata.json`, `local_model_raw.jsonl`, `local_model_summary.json`, `local_model_adapter_raw.jsonl`, `local_model_adapter_summary.json`, `local_model_controls.json`. Designs and the explicit post hoc amendment are in `data/experiments/`.

## 2. Synthetic protocol stress test

Three families x sixteen hazard compositions x four variants x three authored strategies x two authored policies = 1,152 evaluations on 192 distinct synthetic fixtures. Variants are not independent samples. Nine ordinary-case family/strategy controls pass.

The identity-alias control intentionally defeats count and non-ID payload checks while corrupting IDs. Under preservation, false reassurance occurs on 60/64 optional-field, 52/64 deduplication and 60/64 lookup fixtures: 172/192 total. This is an adversarial test of oracle sensitivity, not a model-error prevalence estimate. Preservation versus filtering reverses compliance ranking on fixtures where policies differ. Neither policy is independently legitimized. Arbitrary A/B labels are not demographic groups.

Implementation detail relative to the local design: the final weak payload check compares every non-ID field, strengthening the planned text-only check; the filter-and-pad control is concretely implemented as identity aliasing of restored payloads. These are reported design clarifications, not sampled real behaviors.

Files: `protocol_stress_raw.jsonl`, `protocol_stress_summary.json`.

## 3. Archived reference sensitivity and matched comparison

359 nonempty task/subset rescoring evaluations on frozen archived outcomes (181 Claude-labeled, 178 GPT-labeled). Macro means average subsets within tasks first.

| Reference selection | Claude label | GPT label |
|---|---:|---:|
| Full reference | 54.5% | 63.5% |
| Uniform nonempty-subset mean | 42.8% | 48.9% |
| Single-constraint mean | 36.2% | 40.8% |
| Subset-sensitive tasks | 19/47 | 23/46 |

Outputs never change. The nonincrease when removing constraints follows mathematically from the union-of-failures definition; the experiment measures its extent on these logs, not improvement in models.

On the 45 common qualifying tasks, macro IVRs are 56.9% and 62.7%. GPT-minus-Claude: 5.8 percentage points; exploratory paired-task bootstrap interval 0.9-12.0 points, 10,000 resamples, seed 20261101. The interval is conditional on this matched corpus and does not establish a general model ranking. File: `reference_sensitivity.json`.

## Reproduce

From `Research_DeveloperIntent`, using Python 3.10+ and NumPy:

```sh
python3 scripts/run_protocol_stress.py
python3 scripts/run_reference_sensitivity.py
python3 -m unittest discover -s tests -v
```

For the fresh-model experiment, use the installed Ollama service and the frozen `llama3.2:1b` digest. Generation requires loopback service access. Evaluation requires macOS `sandbox-exec`; it fails closed if unavailable. Candidates use a restricted Python subset, isolated Python (-I -S), restricted builtins, a network/write/fork-denying sandbox, and CPU/wall limits. Read-only host visibility remains; this is not a production-grade container. Model imports, dunder access, unsupported attributes and syntax are rejected, so scores are specific to this execution protocol.

```sh
python3 scripts/run_local_model_pilot.py --analyze-only
python3 scripts/validate_model_controls.py
python3 scripts/analyze_interface_adapter.py
```

The runner resumes existing raw records, so running without `--analyze-only` does **not** automatically draw a new sample. To run a truly separate replication, copy the scripts and frozen designs to a new experiment directory and assign a new run ID/seed schedule rather than overwriting the original raw data. Do not combine duplicated records as independent generations.

No new conference submission, cloud-model run, institutional audit, human-participant research, or stakeholder consultation was performed. The original `Research-DevIntent` files were not modified.
