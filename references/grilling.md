# Grilling: how to interview for a spec

Adapted from the `grilling` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Used by the prod-doc skill for the business rules and by the tech-doc skill in design mode. See THIRD_PARTY_NOTICES.md.

The goal is a shared understanding with nothing silently assumed. The method treats the spec as a **design tree**: every decision has decisions hanging off it, and some questions only make sense once others are answered.

## Rounds

Work the tree in rounds. The **frontier** is every open decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you have not heard yet. Ask the whole frontier in one round, then wait.

Format each round like this:

```
❓ **Q1** - **<question title>**: <the question, with the options if there are several>

➡️ <your recommended answer, and one line on why>

---

❓ **Q2** - ...
```

- Number every question and give a recommended answer. Word the question so that "yes" accepts the recommendation, so the user can answer a round with "yes to all except Q3".
- A question whose answer depends on another question in the same round belongs to a later round.
- Each answer reshapes the tree. Recompute the frontier and ask the next round.

## Facts are your job, decisions are theirs

Never ask the user for something you can look up. When a frontier question needs a fact from the code, the existing docs or the glossary, send a subagent to find it and keep going: only the questions downstream of that lookup wait for it. The user decides; you research.

## Finishing

The session is done when the frontier is empty, and the frontier includes every row of the document's Open questions table. Questions do not only come from the interview: they are carried over from source documents, written by subagents, found while drafting, or left by an earlier session. Before asking for sign-off, collect every open question from the document (and from sibling documents written in the same batch) and ask the unanswered ones as a final round, each with a recommendation. An open question the user has not seen is an implied assumption, which is what grilling exists to remove.

Every open question ends in one of three states. The document records the outcome, not the question:

- **Resolved**: write the decision into the requirements (or the Limitations), delete the row, and name the decision and the IDs it changed in a changelog row. The answer lives in the spec; a reader should not have to consult a Q&A table to know how the feature behaves.
- **Deferred by the user**: the user explicitly chose not to decide now. State the behaviour of this version and when the question will be decided as a line under Limitations and out of scope ("... is decided with the first feature that stores real data"), delete the row, and note the deferral in the changelog.
- **Owned by someone else**: keep the row, with the Owner cell naming them and the Needed by cell saying what waits for the answer, and send it in a questionnaire (`questionnaire.md`). When the answer comes back, it becomes resolved as above.

When no row is left, delete the Open questions section. A row without an owner means the question was never asked; the trace check refuses it in an approved document. Do not write the document as final until the user confirms you have reached a shared understanding.

## In a retrofit

When the feature already exists, the code answers most questions. Run the same rounds, but present each with the answer the code gives as the recommendation. The user's job shrinks to confirming, or to saying "the code is wrong here", which becomes a deviation.
