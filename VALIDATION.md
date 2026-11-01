# Current validation: November 1, 2026

- Completed 120 fresh local model generations, 1,152 authored-control stress evaluations, and 359 archived reference-subset evaluations. Raw data and summaries are in `results/experiments/`.
- Verified all 120 task/condition/seed tuples are unique, 60 belong to each condition, and every request uses the frozen model/settings. Task, design, runner, and worker hashes match the pre-generation metadata.
- Strict results: 0/60 public passers per condition, so IVR is undefined. The separately documented post hoc name-only adapter yields 9/60 and 8/60 public passers and 0/60 and 4/60 full-compliance outputs.
- All twelve authored positive controls pass six cases each through the same sandboxed evaluation path; prohibited file access is rejected before execution.
- All fourteen unit tests pass, covering metric denominators, reference unions, protocol controls, adapter scope, identical public examples, and truncation metadata.
- Updated the existing manuscript in place; built-in LaTeX compiler succeeds.
- A pdfLaTeX `-draftmode` check generated no PDF, found no overfull boxes or unresolved references, and counted fourteen total pages including references. The manuscript is within the initial fourteen-content-page limit.
- The editor preview is current. The previously exported standalone PDF is intentionally unchanged and outdated; no replacement PDF or editor tab was created.
- `results/experiments/manifest.json` records hashes of experiment artifacts.
- No new Claude/GPT calls, institutional data collection, human-participant study, stakeholder consultation, or conference submission occurred. The source-grounded public-service audit remains prospective.

---

# Historical validation record (October 28, 2026)

Checked October 28, 2026.

- Both imported pilot JSON files match their original files byte-for-byte; SHA-256 hashes are in `results/pilot_summary.json`.
- Offline reanalysis reproduces macro IVR 54.5% (40.4%-68.1%) and 63.5% (50.0%-76.5%), with 47 and 46 qualifying tasks respectively.
- Three unit tests pass: unequal task denominators, undefined IVR with no public passers, and missing reference outcomes rejected.
- The authored synthetic example passes its checks, including identity preservation, constructed A/B loss counts, and undefined empty-group loss.
- The current LaTeX source compiles successfully with the desktop compiler and local pdfLaTeX. Final PDF: nine pages; references page 9, ethics and AI statement page 8.
- No overfull boxes or unresolved citations/references remain. The acmart reference-block warning reflects the deliberately suppressed first-page ACM citation block, permitted for initial submissions by the Author Guide FAQ.
- All final pages were rendered and visually inspected; the endmatter was also inspected at larger scale.
- Extracted PDF text contains no originating organization/repository identifier or local user name; PDF Author metadata is absent. This is a limited anonymity check, not a substitute for authors' final supplement review.
- No new model calls, candidate-code execution, source-grounded domain audit, participant study, registration, or submission occurred.

The original project was not edited. Research readiness remains subject to the completion criteria in `DESIGN_DOC.md`.
