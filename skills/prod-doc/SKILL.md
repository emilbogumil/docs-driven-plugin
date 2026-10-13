---
name: prod-doc
description: This skill should be used when writing or revising the business specification of a feature in a docs-driven project: the user says "write the prod-doc", "spec out", "describe the business logic", "define the rules for", wants requirements with IDs, or starts describing how a feature should behave right after feature-init. It interviews for actors, rules, edge cases, limitations and FAQ, writes prod-doc.md with stable requirement IDs in a retrieval-friendly structure, checks terms against the glossary, and moves the status to approved on sign-off.
argument-hint: [domain/feature]
---

# Prod-doc

Write the single source of truth for what a feature does. Readers are product, support, QA and a customer-facing assistant that will answer questions from this text one chunk at a time. Target: `$ARGUMENTS`, or the feature whose prod-doc is still draft if omitted.

## Before writing

Read, in this order: the existing `prod-doc.md` (it may be a bare template or a partial draft), the domain `overview.md` for cross-feature rules, `glossary.md`, and the prod-docs of sibling features the user mentions. Read `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md` for the prod-doc register and `references/ids-and-traceability.md` for the ID rules.

## Interview

Run the interview as a grilling session: read `${CLAUDE_PLUGIN_ROOT}/references/grilling.md` and follow it. The six topics below are the top branches of the design tree. Each answer opens the branches beneath it, and each round asks every question whose prerequisites are settled, numbered, with your recommended answer.

1. **Purpose and actors.** Who uses it, what they are trying to achieve, which existing actors from the glossary are involved.
2. **Main flow.** The happy path, step by step, in the user's words. Each step that changes state becomes a requirement.
3. **Rules and constraints.** Permissions, limits, validation, ordering, timing, defaults. Ask "what stops someone from..." and "what is the maximum...".
4. **Edge cases.** Empty states, duplicates, concurrent edits, the last item, deletion of something in use, offline or failed calls. Each is a requirement with its exact user-visible message.
5. **Out of scope.** What the user explicitly does not want now, phrased as a limitation the support assistant can state.
6. **Questions customers will ask.** Three to eight, in customer words.

Look facts up instead of asking for them: the code, sibling prod-docs and the glossary answer many questions, and a subagent can search them while you ask the rest of the round.

Build the domain language while you interview: read `${CLAUDE_PLUGIN_ROOT}/references/domain-modeling.md`. Challenge terms that conflict with the glossary, replace vague words with precise ones, test concept boundaries with invented scenarios, and update the glossary as soon as a term is settled.

When the feature already exists (retrofit), the code answers most questions. Present each round with the code's behaviour as the recommendation, so the user confirms or says "the code is wrong here". Contradictions between code and design notes are Open questions, never silently resolved.

While the interview runs, collect unsettled points in Open questions. Do not write the requirements as final until the user confirms the shared understanding.

Open questions are part of the interview, not a substitute for it. Whatever their source (the retrofit, a design note, a subagent, your own drafting), ask every unanswered one in a grilling round before sign-off, then fold each answer into the document: a decision goes into the requirements, a deferral becomes a line under Limitations and out of scope, and the row is deleted; only questions waiting for someone else stay, with an owner (`references/grilling.md`, Finishing). Delete the section when it is empty. Never present a document for approval with open questions the user has not seen.

## Writing

- Fill the template sections in place; keep the headings, since the scripts and the assistant rely on them.
- One rule per `### CODE-Rnn: title` heading, numbered consecutively from the last existing ID, given/when/then body, rationale line. Never renumber or reuse; to withdraw, keep the heading and start the body with `Deprecated on <date>: <reason>`.
- Use glossary terms exactly. If the interview introduces a term two features would share, add it to the glossary; otherwise define it in the Terms section.
- Keep every section self-contained: no "as above", no bare pronouns referring to other sections.
- Granularity: one requirement per distinct outcome. Several refusals that share one message template may be one requirement with a reason table; refusals with different messages are separate requirements. A matrix (roles by actions) is one requirement whose body is the table. Plan the whole list before numbering, so main rules and edge cases both come out in document order.
- Backend-only and security features have no customer vocabulary for some rules. Keep the given/when/then shape, define the technical nouns in Terms, and mark messages nobody sees in the UI as "(API message)".
- If the glossary disagrees with the shipped UI's wording, use the UI's words, define them in Terms, and note the glossary change for the reconciling pass. If you cannot edit the glossary right now (parallel work), the Terms section is the fallback.
- Delete the `<!-- guide: ... -->` comments as you fill each section; the trace check flags any that remain once the document leaves draft.
- Put anything customers must not see between the `<!-- internal -->` markers only.
- Add a changelog row and keep `status: draft`.

## Finishing

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature>` and fix structural or ID findings. Coverage errors are expected at this stage.
2. Ask any open question that is still unanswered (the trace check reports them once the status is approved), then show the user the requirement list (IDs and titles only) and ask for sign-off. On an explicit yes, set `status: approved`, bump `last_reviewed`, and update the feature row status in `overview.md` (or note it for whoever owns the overview, if it is out of bounds).
3. If the feature has a user interface, the next step is a prototype and then `user-doc`; otherwise go to `test-cases`.

## Open questions that need someone else

When Open questions are owned by someone other than the user (counsel, a customer, a security reviewer, another team), offer a questionnaire: read `${CLAUDE_PLUGIN_ROOT}/references/questionnaire.md`, ask who it goes to and what is needed back, and write it to the feature's `assets/` folder. When the answers come back, fold them in as requirement changes or closed questions, with a changelog row.

## Revising an approved prod-doc

Set status back to draft, make the change, add a changelog row naming the IDs touched, and re-run the sign-off. The downstream documents that reference the touched IDs need review: grep the feature folder for each ID and list the hits for the user.
