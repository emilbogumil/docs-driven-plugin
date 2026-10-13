---
name: test-cases
description: This skill should be used when deriving or updating QA test cases for a feature in a docs-driven project: the user says "write the test cases", "regression tests for", "QA checklist", "cover the requirements", or a prod-doc and user-doc have just been approved. It derives cases from the prod-doc and user-doc with Covers lines pointing at requirement IDs, marks each automated or manual, writes test-cases.md (and a Gherkin file when configured), and runs the trace check so no requirement is left uncovered.
argument-hint: [domain/feature]
---

# Test cases

Turn the approved specification into the list QA runs and engineers automate. Target: `$ARGUMENTS`, or the feature whose test-cases.md is draft while prod-doc is approved.

## Inputs

`prod-doc.md` (every live requirement), `user-doc.md` (the steps and labels the tester will follow), the domain `overview.md` for cross-feature rules that apply, `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md` (test-cases section) and `references/ids-and-traceability.md`. Read `test_format` in `docs-driven.json`.

If the prod-doc is still draft, say so; proceed only on the user's say-so and note it in the changelog.

## Deriving cases

Work requirement by requirement, in ID order, and for each write:

- the happy path, once per distinct precondition that changes the outcome;
- the negative path for every "then it fails with ..." clause, quoting the message;
- the boundary for every limit (at the limit, one over);
- permission checks for every actor that must not be able to do it.

Then add cross-requirement cases for flows that span several rules (create, then edit, then delete) and for the cross-feature rules in the overview. Keep going until every live requirement has at least one case and every error message in the prod-doc appears in some Expected line.

Case shape, exactly as the template: `### CODE-Tnn: title`, then Covers, Type, Priority, Preconditions, Steps, Expected, Automated in. Preconditions are concrete data. Steps follow the user-doc's labels so the case doubles as a check of the documentation. Numbering continues from the last existing case; never renumber.

Type has three values. `automated` means a test exists (or, before implementation, will be written by the implement stage) and the case ID will appear in it. `planned` means the case can be automated but no test exists yet; the trace check accepts it until the feature is current, then demands a decision. `manual` is only for visual judgement, third-party systems or hardware. The manual cases become the regression checklist at the bottom, ordered by the flow a tester would naturally take. A case counts as `automated` only when its test passes the undefined check in `${CLAUDE_PLUGIN_ROOT}/references/testing.md`: it calls the code the way users do and asserts the case's Expected line literally. In a retrofit, a test that exercises the path but asserts less leaves the case `planned`. Each automated case names the seam it is tested at, using the Test seams agreed in the tech-doc design when one exists.

`Automated in:` names the test file, repo-relative, optionally followed by the test title in parentheses; several files may be listed. The trace check does not read this line to prove coverage (it greps source files for the case ID), but it accepts an existing file as weaker evidence and reports "named but untagged" instead of "not found". A case an existing test covers only partly is written as two cases, or marked with "(partial: ...)" after the title, never over-claimed.

Steps follow the user-doc's labels for UI cases; API-level and unit-level cases name routes or functions instead and say so in the first step.

With `test_format: gherkin`, also write `test-cases.feature`: one scenario per case, tagged `@CODE-Tnn` first and the covered requirement IDs after. The markdown file stays the index QA reads.

## Finishing

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature> --write-matrix`, which replaces the table under Coverage in place, and resolve every coverage error. Automation warnings are expected before implementation; the script is the truth, the pasted table is a convenience for readers.
   A case that mainly belongs to a sibling feature (it asserts their rule as a side effect) stays with the feature whose requirement it covers; the sibling references it by ID rather than duplicating it.
2. Show the user the case list (IDs, titles, type) and ask QA or the owner to accept. On yes, set `status: approved`, bump `last_reviewed`.
3. Next stage: `tech-doc` in design mode, then `implement`.

## When requirements change later

Re-run the trace check; it names the requirements without cases. Add cases for them and review the cases whose Covers line names a changed ID. Deprecated requirements keep their cases but the cases get `Deprecated on <date>` as the first body line so testers skip them.
