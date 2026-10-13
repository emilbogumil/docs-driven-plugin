# Domain modeling: glossary and decisions

Adapted from the `domain-modeling` skill and its glossary and ADR formats in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See THIRD_PARTY_NOTICES.md.

The glossary is the project's shared language. Agents that know it write shorter, more precise documents and name code consistently. Building it is active work during every interview, not a cleanup afterwards.

## During an interview

- **Challenge against the glossary.** When the user uses a term that conflicts with the glossary, say so at once: "The glossary defines 'grant' as X, but you seem to mean Y. Which is it?"
- **Sharpen fuzzy words.** When a term is vague or overloaded, propose one precise term: "By 'account', do you mean the user or the organisation?"
- **Test boundaries with scenarios.** Invent concrete edge cases that force a precise answer about where one concept ends and the next begins.
- **Cross-check with the code.** When the user states how something works, check whether the code agrees, and surface the contradiction.
- **Write it down now.** When a term is settled, update the glossary immediately, not at the end. If the glossary is frozen (parallel work), put the term in the document's Terms section and list it for the reconciling pass.

## Glossary rules

- One row per concept: the term, a definition of one or two sentences saying what it is, the synonyms to avoid, and the neighbouring concept it is most often confused with.
- Be opinionated. When several words exist for one concept, pick one and list the rest under Avoid. "Sealed copy; avoid: wrapped key, encrypted key."
- Only project concepts. General programming terms do not belong, however often the project uses them.
- No implementation details. The glossary is not a spec or a design note.

## When a decision deserves a row

The tech-doc Decisions table records a decision only when all three are true:

1. **Hard to reverse**: changing it later costs real effort.
2. **Surprising without context**: a future reader would wonder why it was done this way.
3. **A real trade-off**: there were genuine alternatives and one was chosen for specific reasons.

If any is missing, leave it out: the obvious choice needs no record, and an easily reversed one will just be reversed. Typical qualifiers are architectural shape, integration patterns between domains, technology with lock-in, scope boundaries, deliberate deviations from the obvious path, constraints the code cannot show, and rejected alternatives whose rejection is not obvious. A decision row can be a single sentence of context, choice and reason.
