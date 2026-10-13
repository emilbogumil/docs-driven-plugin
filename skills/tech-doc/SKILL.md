---
name: tech-doc
description: This skill should be used for the engineering documentation of a feature in a docs-driven project, in two moments: before implementation, when the user says "design doc", "how should we build", "technical design", "architecture for", or test cases have just been approved; and after implementation, when the user says "write the tech doc", "document the implementation", "walkthrough", or the implement stage has finished. Design mode writes the Design half of tech-doc.md with alternatives and decision records; walkthrough mode writes the Walkthrough half from the actual code, with a code map, flows, test map, operations notes and deviations from the spec.
argument-hint: [domain/feature] [design|walkthrough]
---

# Tech-doc

The tech-doc has two halves written at different times. Arguments: `$ARGUMENTS`. If the mode is omitted: design when the Walkthrough half is still the template and no implementation exists; walkthrough when code referencing the feature code exists.

Read `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md` (tech-doc section) first.

## Design mode (before code)

Inputs: approved prod-doc and test-cases, the user-doc, the domain overview, the tech-docs of sibling features (for conventions already decided), and the codebase itself. Spend most of the effort reading the existing code: the design must fit what is there, and the alternatives table is only honest if it names the patterns the codebase already uses.

Write the Design half:

- **Context and constraints**: what exists today, which requirements drive the design (cite IDs), non-functional constraints found in the repo (framework, auth model, data store, performance budgets).
- **Approach**: the chosen design in prose, a few paragraphs. Where a choice serves a specific requirement, say which.
- **Data model** and **Interfaces** with concrete shapes: table or schema definitions, endpoint signatures, event names, component props, permission checks.
- **Test seams**: the public boundaries the test cases will be automated at (a route, a page, an exported function), which groups of cases each seam takes, and what it catches and misses. Prefer existing seams and the highest practical one; see `${CLAUDE_PLUGIN_ROOT}/references/testing.md`. The implement stage writes tests only at these seams.
- **Alternatives considered**: at least one real alternative per significant choice, and the reason it lost. A design with no rejected alternatives has not been designed.
- **Decisions**: one `CODE-Dnn` row per decision that is hard to reverse, surprising without context, and the result of a real trade-off (all three; see `${CLAUDE_PLUGIN_ROOT}/references/domain-modeling.md`). Obvious or easily reversed choices stay in the Approach prose. Status `proposed` until the design review, then `accepted`; later `superseded` (by a new row) or `rejected` for an alternative that was seriously considered and turned down. Date the row from the design note or commit that made the decision; if unknown, today's date with "(dated at documentation time)".

When retrofitting, the Design half is mined rather than invented: decision tables and "why not X" sections in the project's design notes become rows, the step notes' deviation sections become the alternatives that lost, and the Context section says which notes were used.

Settle open design questions with the user as a grilling session (`${CLAUDE_PLUGIN_ROOT}/references/grilling.md`): numbered rounds with recommended answers, facts looked up rather than asked. Then request a design review. On approval, set decision rows to `accepted`, set `status: approved`, bump `last_reviewed`. Next stage: `implement`.

## Walkthrough mode (after code)

Inputs: the implementation diff (`git diff <base>...HEAD` on the feature branch), the Design half, and the test files. Without git history, or for a retrofit, use the files that reference the feature code (grep for the code and for the messages quoted in the prod-doc) and any "files to read" lists in the project's step notes.

Write the Walkthrough half from the code as it is, not as it was planned:

- **Code map**: every file added or materially changed, its role, and the requirement IDs it implements. Order by the path a request takes.
- **Flows**: for each main flow in the prod-doc, the sequence of functions, handlers and queries, with file references. This is the section a new engineer reads first.
- **Test map**: each automated case ID and the file that implements it, taken from the test names. When tests are not yet tagged with IDs, map by test title and say so; the `Automated in:` lines in test-cases.md are the source, so keep the two consistent rather than maintaining both by hand.
- **Operations**: configuration keys, feature flags, migrations and their rollback, dashboards or logs to watch.
- **Deviations from the spec**: everything the code does differently from the prod-doc or user-doc, with the reason and whether the doc or the code should change. Write "None" explicitly when there are none. Compare against the deviations list the implement stage produced, if any. In a retrofit the prod-doc was written from the code, so this section records where the code differs from the original design notes instead, labelled as such.

Update decision rows whose status changed during implementation (superseded, with the new row). Add a changelog row. Keep `status: approved` until feature-close sets it to current.

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature>` and resolve findings in the test map.
