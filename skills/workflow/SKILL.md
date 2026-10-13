---
name: workflow
description: This skill should be used whenever work touches feature documentation in a docs-driven project, or when the user talks about starting a new feature, writing a spec, prod-doc, user-doc, tech-doc, test cases, requirement IDs, "docs first", "spec first", or asks which stage a feature is at. It explains the docs-driven workflow (prod-doc, prototype and user-doc, test-cases, implementation, tech-doc, close) and routes to the stage skill for the task at hand. Consult it before editing anything under a docs root that contains docs-driven.json, even if the user did not name the workflow.
---

# Docs-driven workflow

A feature is a folder `<docs root>/<domain>/<feature>/` holding four documents that are written in a fixed order and kept consistent by IDs. The documents are the specification: code is written to satisfy them, not the other way round.

```
docs/
  docs-driven.json            config, marks the docs root
  glossary.md                 shared vocabulary
  user-management/            a domain
    overview.md               purpose, feature table, domain-wide rules
    user-roles/               a feature
      prod-doc.md             business rules, requirement IDs  (stage 1)
      user-doc.md             customer-facing, from prototype  (stage 2)
      test-cases.md           QA cases covering requirements   (stage 3)
      tech-doc.md             design before, walkthrough after (stages 4 and 6)
      assets/                 prototype exports, screenshots
```

## Stages and skills

| Stage | What happens | Skill |
| --- | --- | --- |
| 0 | Create the feature folder, code and branch | `feature-init` |
| 1 | Write the business rules as numbered requirements | `prod-doc` |
| 2 | Prototype in Figma or Lovable, then write the customer doc from it | `user-doc` |
| 3 | Derive test cases that cover every requirement | `test-cases` |
| 4 | Write the design half of the tech-doc, get it reviewed | `tech-doc` (design) |
| 5 | Implement to satisfy prod-doc and user-doc and pass the cases | `implement` |
| 6 | Write the walkthrough half of the tech-doc from the code | `tech-doc` (walkthrough) |
| any | Check consistency and traceability | `spec-check` |
| 7 | Flip statuses, changelog, PR description, merge | `feature-close` |

Each stage ends with a status change on its document (draft, approved, current, deprecated). A later stage starts from an approved earlier document, which is the review gate that makes the pattern work. Do not skip a gate silently: if the user wants to jump ahead, say which document is still draft and carry on at their request.

## Finding the right stage

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status_report.py` to see every feature with per-document statuses, or `trace_check.py --feature <domain>/<feature>` for one feature. The first document that is still draft is usually where the work is. When no docs root exists yet, the task is `feature-init`.

## Principles that every stage follows

- **IDs are permanent.** Requirement `UM-UR-R03` means the same thing forever. Withdraw by marking deprecated; never renumber. See `references/ids-and-traceability.md`.
- **Deviations are surfaced, not absorbed.** When the implementation or the prototype cannot follow the spec, say so and change the document in the same change, with the changelog row. Quietly doing something different is the failure mode this workflow exists to prevent.
- **Different readers, different registers.** The prod-doc reads like a rulebook, the user-doc like a help page, the test-cases like a QA script, the tech-doc like an onboarding guide. `references/style-guide.md` has the rules per file.
- **Scripts do the mechanical parts.** Scaffolding, trace checking and status reports are deterministic and live in `scripts/`. Use them rather than re-deriving the checks by hand.

## Retrofit: documenting a feature that already exists

The stages assume the docs come first. When the code already exists (a new project adopting the workflow, or an undocumented feature), run the same stages in the same order with these substitutions, and say in each changelog that the document was written retroactively:

- The interview's interviewee is the code and whatever design notes exist. Read the implementation first, then the design documents; where they disagree, the code is what ships and the disagreement goes into Open questions and the tech-doc's Deviations section.
- The implemented UI is the prototype. Read the components for labels and messages and set `prototype: implemented UI (<path>)`.
- Sign-off gates are not skipped, they are batched: write all four documents at `draft`, then ask once for approval of the set.
- Test cases that an existing test covers are `automated` and name the file; cases that could be automated but are not yet are `planned`; only genuinely manual checks are `manual`. Tagging the existing tests with case IDs is part of the retrofit, not an afterthought, because until then the trace check cannot prove anything.
- The tech-doc Design half is mined from the design notes' decision tables and the step-by-step notes' "deviations" sections; the Walkthrough half from the code. Date decisions from the notes or commits, else today with a note.

## Shared rules and parallel work

A rule belongs to exactly one feature. Other features reference it by ID and path instead of restating it, so the trace check and a reader have one place to look. Rules that genuinely apply to a whole domain go into the domain `overview.md` as `DOMAINCODE-Rnn` and can be covered by any feature's cases. When several features are written at the same time, reference siblings by path only, keep glossary and overview edits for a single reconciling pass afterwards, and list the terms, overlaps and open questions each feature needed in its report so that pass has its input. The reconciling pass ends with one grilling round that asks every open question of the batch; a batch is not ready for sign-off while any of them is unasked.

## Where things are

`${CLAUDE_PLUGIN_ROOT}` is the plugin root, two levels above this skill's directory. Templates are in `templates/`, scripts in `scripts/`, writing rules and schemas in `references/` (including the shared methods: `grilling.md` for interviews, `domain-modeling.md` for the glossary and decision threshold, `questionnaire.md` for open questions owned by others, `testing.md` for seams and real assertions), and the implementation-versus-spec reviewer in `agents/spec-reviewer.md`. The project's own settings are in `docs-driven.json` at its docs root; `references/config.md` lists the fields.
