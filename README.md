# DeveloperIntent for ACM FAccT 2027

**Working title:** Whose Intent Counts? Auditing Requirement Violations in LLM-Generated Data-Cleaning Code

**Chosen niche:** accountability for record retention and exclusion in AI-generated data-cleaning scripts for public-service intake. The paper asks who defines a requirement, how it becomes an executable test, and whose records disappear when a model fills in an unspecified policy.

**Primary focus area:** Evaluations and evaluation practices. **Secondary:** Normative foundations and implications. These are reviewer-matching areas, not separate paper tracks. Recommended submission type: archival, subject to publication eligibility and the authors' choice.

## New experiments completed November 1, 2026

The open manuscript now incorporates **120 fresh local `llama3.2:1b` generations**, a **1,152-evaluation synthetic protocol stress test**, and an exhaustive reference-subset sensitivity analysis on the archived logs. See [experiment results and reproduction](results/experiments/README.md). The strict model interface produced no public passers; the post hoc name-only adapter is reported separately. The source-grounded institutional audit remains unperformed. The old exported PDF predates these results; the current LaTeX source and editor preview are authoritative until a new export is requested.

## Deliverables

- [Manuscript source](paper/facct_paper.tex) (current; the previously exported PDF is outdated): anonymous ACM development draft with the existing algorithm pilot, new executed laboratory experiments, and the proposed source-grounded domain audit. **Not a completed empirical submission.**
- [Research design](DESIGN_DOC.md): research questions, provenance protocol, sampling, conditions, analysis, and completion criteria.
- [Registration text](ABSTRACT_REGISTRATION.md): copy-ready title and abstract, with timing and research-status caveats.
- [Conference requirements](formatting.md): verified FAccT 2027 rules and dates.
- [Evidence ledger](EVIDENCE_AND_MIGRATION.md) and [related work](RELATED_WORK.md).
- `scripts/audit_pilot.py`: offline reanalysis of copied evaluation logs, with macro/micro IVR, denominator counts, all-generation rates, hashes, and bootstrap intervals.
- `scripts/validate_examples.py`: checks two authored functions on synthetic rows. These are not model generations or research findings.

## Core adaptation

Retain ambiguous/clarified specification pairs and Intent Violation Rate (IVR). Replace the assumption that a developer's unstated preference is automatically correct with a **documented reference requirement**. Each requirement needs a source, affected-party rationale, executable test, and record of disagreement. A failed hidden test establishes reference-requirement nonconformance, not injustice or a model's mental intent.

The 49-task HumanEval+ pilot remains preliminary algorithmic evidence. It cannot be relabeled as a data-cleaning audit or discrimination finding. The proposed domain study is unperformed. No interviews, stakeholder validation, institutional ethics approval, or actual harms are claimed. The new local-model calls use authored synthetic tasks and are fully logged.

## Reproduce

Python 3.10+ and NumPy are needed for the pilot audit; the example and unit tests use the standard library. The archived-log and authored-control experiments need no API key. The fresh-generation runner requires the installed local Ollama service; candidate evaluation uses the screened macOS sandbox. See the experiment README for commands and limits.

```sh
python3 scripts/audit_pilot.py
python3 scripts/validate_examples.py
python3 -m unittest discover -s tests -v
```

The analysis writes `results/pilot_summary.json` and `results/pilot_summary.md`. Scripts resolve paths relative to themselves.

Build with an installed TeX distribution containing `acmart`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf paper/facct_paper.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf paper/facct_paper.tex
```

## Immediate timing

The [official CFP](https://facctconference.org/2027/cfp.html), checked October 28, 2026, lists abstract registration October 27 at 23:59 AoE (**October 28 at 07:59 New York**) and papers November 3 at 23:59 AoE (**November 4 at 06:59 New York**, after daylight saving ends). The user reports no abstract registration. No registration or submission was made here. Confirm the deadline against the current time before acting.

Before presenting a completed domain audit, collect a grounded corpus, document requirement adjudication, run the comparison conditions, and analyze the outcomes. If that cannot be done rigorously, retain this as a development package. The original `../Research-DevIntent` is unchanged. Only two evaluation logs were copied; legacy ACL plans, identifying badges, API code, and caches were not imported.
