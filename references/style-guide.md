# Writing guide for the four documents

Each file has a different reader. Keep the registers apart; mixing them is the most common way these docs fail.

## prod-doc: for product, support, QA and assistants

- Customer language throughout. Name UI elements the way the user sees them.
- One rule per requirement. If a sentence contains "and" joining two behaviours, split it.
- Given / when / then for every requirement, with the exact user-visible message in quotes when there is one.
- Every edge case is a requirement. "What happens when the list is empty" is a rule, not a footnote.
- Limitations are phrased as answers: "You cannot assign more than one role to a user" rather than "Multi-role is out of scope".
- The FAQ cites requirement IDs so an assistant can quote the rule and the answer together.
- Anything that must not reach customers goes between the `<!-- internal -->` markers and nowhere else.
- Retrieval-friendly structure: short sections, descriptive headings, no "see above", no pronouns whose referent is in another section. An assistant may see one chunk at a time.

## user-doc: for the customer doing the task

- Second person, imperative, present tense. "Select the role" rather than "The user should select a role".
- Task-based headings that start with a verb: "Assign a role to a user".
- Numbered steps, one action per step, each step naming the control as labelled in the prototype.
- No internal vocabulary, ticket numbers or requirement IDs in visible text. IDs go in the HTML comment under the heading.
- Reference tables for fields and limits, so the prose stays short.
- Troubleshooting rows in the form "what you see, why, what to do".
- When the product has a published style guide, it wins over this one. Tone and audience from `docs-driven.json` apply.

## test-cases: for QA

- Case titles state the behaviour and the condition: "Demote the last admin is rejected".
- Preconditions are concrete data: "an organisation with exactly one admin", not "appropriate setup".
- Steps are reproducible by someone who has never seen the feature.
- Expected results quote messages exactly and name the state afterwards.
- Automated cases name the file once implemented. Manual cases are the regression checklist and should be few.
- Priority high means a release blocker.

## tech-doc: for the next engineer

- Design half before code, with alternatives and the reasons they lost. A decision without a rejected alternative is usually a decision not yet made.
- Walkthrough half from the real code: file paths, function names, the order things happen in.
- The deviations section is mandatory and may be "None". It is where the implementation admits what it does differently from the spec, so nobody has to discover it in production.
