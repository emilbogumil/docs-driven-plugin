---
name: user-doc
description: This skill should be used when writing or updating the customer-facing documentation of a feature in a docs-driven project: the user says "write the user doc", "help page", "user guide", "document this for customers", shares a Figma, Lovable or screenshot prototype, or has just approved a prod-doc for a feature with a UI. It writes user-doc.md from the prod-doc and the prototype in the product's tone, traces each task section to requirement IDs, and reports any prototype behaviour that contradicts the prod-doc instead of choosing silently.
argument-hint: [domain/feature]
---

# User-doc

Write the help page a customer reads while doing the task. It is published as is, so nothing internal may leak into it. Target: `$ARGUMENTS`, or the feature whose prod-doc is approved and user-doc is draft.

## Inputs

1. `prod-doc.md`, which should be approved. If it is still draft, say so and continue only if the user confirms; note in the changelog that the user-doc was written against a draft.
2. The prototype: a Figma or Lovable link given by the user, or files in the feature's `assets/` folder. Read every image in `assets/`. When a link is given and the design tool is reachable through an available connector or browser tool, open it; otherwise ask for exported screens to be dropped in `assets/`. Record the link in the `prototype` frontmatter field.
3. `audience` and `tone` from `docs-driven.json`, and any product style guide the user points to. The product's own guide wins over the plugin's.
4. `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md`, user-doc section.

Without a prototype (API-only feature, or the user wants a first draft before design), write from the prod-doc alone, set `prototype: none`, and keep status draft with a note that labels and steps are provisional.

When the feature is already implemented, the app itself is the prototype: read the page and component sources for labels, messages and step order, set `prototype: implemented UI (<path>)`, and leave `assets/` empty unless screenshots add something. The reconciliation below then compares the shipped UI against the prod-doc, which was usually written from the same code; the differences that matter are between code and the original design notes and belong in the tech-doc Deviations section, not here.

## Writing

- Task-based `## How to <verb> ...` sections, one per thing a user sets out to do. A feature that is mostly invisible (encryption, permissions) may add explanatory sections headed `## What ...` or `## Why ...` between the tasks and the Reference; keep them short and in the same register. Usually the main flow and each variant that changes the steps. Put `<!-- covers: CODE-R01, CODE-R02 -->` directly under each task heading, listing the requirements the section documents.
- Steps name controls exactly as the prototype labels them. Describe the result the user sees after the last step.
- Reference table for fields, defaults and limits, taken from the requirements; this is where limits from the prod-doc's Limitations section become user-visible.
- Troubleshooting from the prod-doc's edge cases: each error message the user might see, why, what to do.
- No requirement IDs, ticket numbers, internal names or future plans in visible text. Messages the app shows verbatim are quoted even when they look internal (`requires Users.List`), because the reader will see them.
- Every task section carries a covers comment; requirements that surface only in Reference or Troubleshooting need none.
- Overview of two or three sentences in the customer's terms, not a restatement of the summary from the prod-doc.

## Reconciling prototype and prod-doc

Compare every screen against the requirements before writing. Differences fall into three kinds, and each gets reported to the user as a list before the doc is finalised:

- the prototype shows behaviour the prod-doc lacks (a filter, a bulk action): propose a new requirement;
- the prototype contradicts a requirement (different limit, different message): ask which is right;
- a requirement has no screen: it may be backend-only, or the prototype is incomplete.

Write the user-doc to the prod-doc where they conflict and leave a `<!-- TODO: conflict with prototype, see changelog -->` marker, so the published text never describes behaviour that will not exist. Update the prod-doc through the prod-doc skill when the user decides.

## Finishing

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature>` to confirm every covers comment names an existing requirement. Add a changelog row to the prod-doc only if it changed. Ask for a product review; on an explicit yes set `status: approved` and bump `last_reviewed`. Next stage: `test-cases`.
