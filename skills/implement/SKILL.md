---
name: implement
description: This skill should be used when implementing a feature that has docs-driven specifications: the user says "implement the feature", "build it according to the spec", "make the tests pass for", names a domain/feature with an approved prod-doc, or asks to code something that has a feature folder under the docs root. It reads prod-doc, user-doc, test-cases and the tech-doc design, implements to satisfy them, names automated tests with case IDs, keeps a deviations list instead of silently changing behaviour, and runs the trace check before reporting.
argument-hint: [domain/feature]
---

# Implement

Build the feature so that it does exactly what the prod-doc and user-doc say and passes the test cases. Target: `$ARGUMENTS`.

## Read before coding

1. `prod-doc.md`: every live requirement, in order. These are the acceptance criteria.
2. `user-doc.md`: labels, steps, messages and defaults the customer has been promised. The UI must match it word for word where it quotes text.
3. `test-cases.md` (and `test-cases.feature` if present): the automated cases are the tests to write; the expected results are the assertions.
4. `tech-doc.md`, Design half: the agreed approach, data model, interfaces and decisions. Follow it; if it turns out to be wrong, that is a deviation to record, not a reason to improvise quietly.
5. The domain `overview.md` for cross-feature rules and `glossary.md` for naming in code.
6. `docs-driven.json` for `test_tag_style`.

If the prod-doc or test-cases are still draft, say so and continue only on the user's explicit go-ahead.

## Plan

Produce a short plan that maps requirements to the code changes that satisfy them and the test cases that prove them. Every live requirement must appear in the plan; a requirement with no planned change is either already satisfied (say where) or a gap. Present the plan, then proceed.

## Build

- Work requirement by requirement, writing the automated test for each case before or alongside the code it checks. Put the case ID in the test name: `it("[UM-UR-T03] ...")`, `test_um_ur_t03_...` with a `# UM-UR-T03` comment, or whatever reads naturally in the framework, as long as the literal ID appears in the file. The trace check finds tests by that string.
- Write tests only at the Test seams agreed in the tech-doc design. If a case needs a seam that was not agreed, add it to the deviations list rather than inventing one silently.
- Assert the expected result from the case, including exact messages. Before reporting, run the undefined check from `${CLAUDE_PLUGIN_ROOT}/references/testing.md` on every test you wrote: a test that would still pass if the imported code returned `undefined` does not cover its case.
- Quote user-visible strings from the user-doc, not paraphrases.
- Keep a running **deviations list** in your notes: anything where the code cannot or should not follow a document, with the ID, what was done instead, and why. Common causes: a requirement that contradicts an existing platform rule, a message that does not fit the UI, a design decision that did not survive contact with the code.
- Do not edit the prod-doc, user-doc or test-cases during implementation. They change through their own skills after the user decides.

## Finish

1. Run the project's test suite and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature>`. Every automated case should now be found in source. Fix anything flagged.
2. Report: which requirements are implemented, which tests cover them, and the deviations list verbatim with a recommendation per item (change the doc or change the code).
3. Next stages: `tech-doc` in walkthrough mode, then `feature-close`. If the deviations list is not empty, the affected documents go back through their skills first.
