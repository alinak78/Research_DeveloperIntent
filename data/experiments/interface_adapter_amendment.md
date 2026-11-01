# Exploratory evaluation amendment: function-name adapter

Added after observing the first 55 fresh responses. All 55 failed the strict interface/syntax gate, including 53 with no function named `solution`. The model prompts, outputs, generation order, and primary strict evaluation remain frozen and unchanged.

Secondary evaluation: if and only if the extracted source contains exactly one top-level function with exactly two positional parameters, no variadic parameters and no keyword-only parameters, rename that function definition to `solution` before applying the original AST gate and sandbox. Do not alter argument lists, function bodies, imports, syntax, or return values. Reject a candidate referring recursively to its former function name instead of rewriting its body. If already named solution, evaluate it unchanged. Preserve unsupported/incompatible-interface outcomes in denominators.

This post hoc analysis separates function-name adherence from behavior for an adapter-eligible subset. It is not the primary experimental outcome, a model repair intervention, a fresh generation, or evidence of deployment compatibility. Report both strict and adapter outcomes and count all adapter-ineligible candidates. No result is selected for promotion based on whether its score improves.
