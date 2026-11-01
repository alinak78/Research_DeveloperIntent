# Research design: Whose Intent Counts?

Status: original source-grounded study plan, October 28, 2026. Update November 1: separate synthetic/local-model experiments are now completed and documented in `results/experiments/README.md`; the institutional study below remains prospective. The domain study is proposed, not performed. Existing evidence now also includes a synthetic stress test, an archived-reference sensitivity experiment, and a 120-generation local-model pilot. These are separate from the planned institutional study.

## Niche and contribution

Study **record retention and exclusion in LLM-generated Python data-cleaning code for public-service intake**. Keep the empirical unit to one transformation, rather than an entire eligibility system. Missing-value handling, duplicate resolution, and join semantics can change which records reach later review. The study asks whether passing basic tests hides deviations from documented retention requirements, and who has authority to define those requirements.

Primary focus: **Evaluations and evaluation practices**. Secondary: **Normative foundations and implications**. These match the measurement and requirement-authority questions. Add System development and deployment only if an evaluated intervention becomes substantial. Do not claim an interaction study without participants.

Contributions sought: (1) a requirement provenance protocol, (2) denominator-aware nonconformance measurement retaining IVR, (3) a source-grounded case audit with controlled information conditions, and (4) an account of contested and unresolved requirements. Extra hidden tests alone are not novel. Drop SQS prediction, universal ambiguity scoring, recursive self-improvement, embedding-based drift, developer productivity claims, and a broad multi-domain benchmark.

## Research questions

| Question | Required evidence | Permissible inference |
|---|---|---|
| RQ1: How often does public-test-passing code violate a documented retention rule? | Frozen domain tasks/tests and independent generations | Nonconformance within the corpus and configurations |
| RQ2: What changes when the policy is explicit or elicited? | Matched task/model conditions with information accounting | Intervention-associated change, not internal model intent |
| RQ3: Who authorizes a requirement and where do sources disagree? | Source excerpts, independent labels, disagreement/adjudication | Situated account of test construction and authority |
| RQ4: Which records disappear, and does loss differ across justified fixture groups? | Row traces and group denominators | Mechanism on synthetic fixtures, not population discrimination |

RQ4 is secondary. Without justified group definitions, report row-level loss without demographic labels.

## Corpus and grounding

Target 12-20 independently sourced tasks across optional-field missingness, duplicate resolution, and unmatched joins, within one intake context. This is a bounded case audit, not a representative benchmark. Freeze inclusion rules and task count before inspecting model outcomes. Variants of one source workflow form one cluster, not multiple independent tasks.

Use public documentation, issue reports, data dictionaries, or permitted organizational artifacts. Record source URL, access date, version/hash, relevant excerpt, reuse terms, and exactly what it supports. Generic data-science examples cannot establish a specific agency's practice. The current synthetic example has no domain provenance and is ineligible for this grounded corpus.

Create synthetic rows with stable IDs, avoiding real applicant records. Record which values exercise which branches. Do not invent realistic demographic frequencies or label missingness itself as a protected group.

For every task prepare an ambiguous prompt and public tests, documented reference policies and policy-specific hidden tests, a canonical implementation, and a deliberate public-passing counterimplementation. Check that each hidden test isolates the omitted rule and that public tests do not leak it. A passing canonical establishes satisfiability, not the legitimacy of a policy.

Each **requirement card** contains task ID, source/excerpt, policy authority, affected parties, omitted requirement, alternatives, consequences, operationalization, test IDs, annotation status, and unresolved concerns. Two independent annotators should judge source support, prompt explicitness, and test validity. Preserve raw labels, disagreements, and adjudication. Report agreement and its small-sample limits. This is planned annotation, not completed consultation. Practitioner review does not substitute for affected-party participation.

Keep conflicting documented policies as separate references or mark the task unresolved. Do not pick whichever policy makes the model fail. Institutional authority and ethical legitimacy are distinct.

## Experimental conditions

Freeze prompts, reference tests, exclusions, analysis, model identifiers, settings, and randomization before generation. A timestamped protocol is useful; do not retroactively call it preregistered.

| Condition | Information | Purpose |
|---|---|---|
| A: Ambiguous | Ambiguous prompt plus public tests | Baseline residual nonconformance |
| B: Explicit | A plus documented policy | Information-rich reference condition |
| C: Generic clarification | A; at most one question and scripted answer | Established clarification baseline |
| D: Retention-focused clarification | A; one question prompted toward retention policy and scripted answer | Test targeted elicitation |

Answers come from frozen requirement cards and are **simulated**, not stakeholder responses. Supply a policy only when requested; retain irrelevant questions, nonquestions, refusals, and unresolved ambiguities in the intention-to-treat comparison. Log question/answer content, tokens, turns, and latency. B has more information than A; it is not a token-matched control. If C and D reveal different information, do not attribute their difference solely to question quality.

Target two accessible frozen model snapshots, ten independent completions per task per condition: 960-1,600 final-code generations, plus clarification calls. More completions do not replace independent workflows. Preserve requests/responses, timestamps, settings, retries, provider metadata, and costs. No paid API calls are part of this adaptation.

Run candidate code in a separately configured disposable environment with no network, credentials, or host mounts and with resource limits. A subprocess timeout is not a security sandbox. The current example validator invokes authored functions only; it is not a candidate execution framework.

## Measurement and analysis

For task t and completion j, S_tj means passing all public tests; H_tj means failing at least one applicable reference test.

`IVR_t = sum(S_tj * H_tj) / sum(S_tj)` if public-test passers exist; otherwise **undefined**.

Retain the name IVR for continuity, but interpret it as **reference-requirement nonconformance**, not direct measurement of latent intent or fairness.

- Macro IVR: unweighted mean over qualifying tasks; publish excluded IDs/counts.
- Micro IVR: violating public-test passers divided by all public-test passers.
- Public pass rate, joint public-pass/reference-fail rate, reference failure rate, and full-compliance rate: each over **all** generations. Report errors/timeouts separately in new runs.
- Condition contrasts: public-pass and full-compliance differences on all tasks; IVR differences on tasks qualifying in both conditions, with exclusions. Also show condition-specific IVRs. Conditioning on public-test success can change composition.

Use 10,000 task-cluster bootstrap resamples with recorded seed, keeping all variants, models, and conditions of a workflow together. Purposive sampling limits population inference. Treat model comparisons as secondary; overlapping CIs alone do not establish equality or difference.

Group row-loss rate is distinct input IDs lacking authorized output representation divided by distinct input IDs in the group, under a preservation policy. Define deduplication equivalence and authorized exclusions; unknown groups remain separate and empty denominators yield undefined rates. Publish counts and predeclared absolute contrasts. Synthetic group gaps do not estimate real human harm.

Code qualitative mechanisms: missingness deletion, unjustified collapsing, unmatched-join exclusion, explicit uncertainty, and escalation. Preserve negative and contradictory cases. An explained policy violation remains a violation; score behavior and explanation separately.

## Existing evidence

Two copied logs contain 49 algorithm tasks and five completions per task. Reanalysis preserves macro IVR and adds denominator diagnostics. Model names are log labels; exact snapshots, original requests, timing, and settings cannot be reconstructed from those logs alone. The source manuscript reports temperature 1.0, but log-only reanalysis cannot verify it.

The executable synthetic example checks an optional-email rule: both authored functions pass normal-case normalization tests, while dropping missing-email rows violates the reference retention rule. Groups A/B only demonstrate the effect of constructed missingness; no social identities or actual populations are represented.

## Completion criteria

Suggested content budget, maximum 14 pages: introduction 1.5; related work/conceptual framing 2; provenance 2; audit design 2; results 2.5; case analysis/implications 2; limitations/conclusion 1.5. This is a budget, not a minimum. The draft is shorter because the domain results do not exist.

Before a submission-ready claim:

1. Confirm representative abstract registration, author approval, and publication eligibility.
2. Complete source-grounded corpus, requirement cards, test review, and disagreement account.
3. Run frozen conditions in isolated execution; archive raw outcomes and errors.
4. Replace proposed-study text with actual methods and findings, including null results.
5. Verify citations, AI model/version disclosure, ethics/human-research status, and all authors' factual review.
6. Rebuild, visually inspect, check page limits, and anonymize supplements.

If only the algorithm pilot and synthetic example are available, keep the domain study explicitly proposed. FAccT has no automatic proposal-paper exception. A conceptual submission would require a mature, defended argument in its own right; this package is not a claim of readiness or acceptance.
