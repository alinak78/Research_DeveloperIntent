# Local experiment specification v1

Written before the first execution of the two new experiment scripts. This is a local design record, not an externally preregistered study.

## Laboratory protocol stress test

Evaluate three researcher-authored implementation strategies (preserve, filter, filter-and-pad) for three families (optional email, name-based duplicate collapse, unmatched lookup join). Use two researcher-authored reference policies per family: retain every record versus filter under the explicit family-specific rule. None is institutionally or stakeholder validated.

Construct twelve-row fixtures with six arbitrary A labels and six B labels. Vary the number of hazardous rows independently in each group over 0, 1, 3, 6. The two groups and hazard distributions are deliberately constructed; they do not represent human populations. Six hazards per group is a stress boundary. Apply four transformations to each fixture: original, reversed order, swapped A/B labels, and bijectively renamed identifiers. Total: 3 families x 16 compositions x 4 variants x 3 implementations x 2 policies = 1,152 implementation/fixture/policy evaluations, based on 192 distinct family/composition/variant fixtures. Reused fixture variants are not independent observations.

All implementations must pass family-specific ordinary-case public tests before stress evaluation. Compare two weaker checks (output count and sorted output text values) with exact ID-aware reference comparison. Report false reassurance when both weaker checks pass but ID-aware compliance fails. Compute identity loss under the preservation policy only; an authorized filtering policy does not make excluded identities compliance violations. Retain full outputs and reference results. No model generations or arbitrary candidate execution.

## Archived-reference sensitivity

For each of the original two 49-task outcome logs, hold the public-test-passing set fixed. Enumerate all nonempty subsets of the task's recorded reference constraints (up to three). Calculate IVR per subset, each task's minimum/maximum, and average over uniform subsets within task before macro averaging across qualifying tasks. Additionally calculate the single-constraint subset average. These are descriptive measurement perturbations on archived outcomes, not interventions on model prompts or new generations.

Compare original full-reference macro IVRs on common qualifying tasks, with a task-paired 10,000-resample bootstrap of GPT-labeled minus Claude-labeled IVR and seed 20261101. Independent units are the common tasks; completions are not independent units. Treat this as exploratory; no confirmatory significance claim, no population generalization, and no CI-overlap test. Input hashes and raw per-task/subset data are required.
