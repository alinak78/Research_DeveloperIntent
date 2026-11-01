# Reanalysis of archived algorithm pilot

Stored pass/fail logs only; no new generation or candidate execution. Model identities are log labels, not independently verified snapshots.

| Log label | N outputs | Qualifying tasks | Public pass | Macro IVR (95% CI) | Micro IVR | Joint failure | Full compliance |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude-sonnet-4-6 | 245 | 47/49 | 94.3% | 54.5% (40.4%-68.1%) | 55.4% | 52.2% | 42.0% |
| gpt-4.1 | 245 | 46/49 | 92.7% | 63.5% (50.0%-76.5%) | 63.0% | 58.4% | 34.3% |

Macro IVR averages task-level conditional rates. Micro IVR pools qualifying outputs. Joint failure is public-pass/reference-fail over all outputs. Full compliance passes both sets. Undefined task IVRs are excluded, never treated as zero. CIs resample tasks 10,000 times with seed 42.

## claude-sonnet-4-6

Public passers: 231; violations among passers: 128; reference failures across all outputs: 142 (58.0%).
Excluded tasks: HumanEval/101, HumanEval/112
Input SHA-256: `0e32bbd305439486c9b0fa28c4f95114b8eab29542ffb32dfc447ed7c4723f83`

## gpt-4.1

Public passers: 227; violations among passers: 143; reference failures across all outputs: 161 (65.7%).
Excluded tasks: HumanEval/21, HumanEval/108, HumanEval/112
Input SHA-256: `e8c2458ded258c6d72de64db1a5a86f16374be638cdbaef91391ca8d3b09d3cd`

These purposively selected algorithm tasks do not estimate stakeholder harms, discrimination, or public-service deployment prevalence. The logs do not distinguish crashes from other failed tests.
