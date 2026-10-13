# Questionnaire: open questions for someone else

Adapted from the `to-questionnaire` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See THIRD_PARTY_NOTICES.md.

Some Open questions in a prod-doc cannot be settled by the user: they need counsel, a customer, a security reviewer or another team. Turn them into a document the user can send, or fill in together in a meeting.

## Interview the send, not the subject

Ask the user only what they can always answer, in one exchange each:

1. **Who is it going to?** The recipient's role, expertise and relationship to the user. This sets the tone and how much context the document must carry.
2. **What do you need back?** Which Open questions this recipient should answer. Default to every Open question whose owner names them.

## Write it

Save it as `assets/questionnaire-<recipient-slug>.md` in the feature folder and give the user the path. Use this shape:

```
# <Feature title>: questions for <recipient>

**Purpose:** the decision riding on the answers.
**From:** <user>  **To:** <recipient>  **How your answers will be used:** they become rules in the product specification for <feature>.

## Context
One paragraph for a reader who was not in the conversation.

## How to answer
Deadline and rough effort. "I don't know" and partial answers are useful; flag uncertainty instead of skipping.

## <Theme>
### <One question, never compound>
_Why this matters: <only when the question could be misread or invite a throwaway answer>._

>

## Anything else?
What we did not ask that we should know.
```

Order questions most important first, since an async reader may give you one pass. Write in the recipient's language, not the project's: no requirement IDs, and glossary terms explained on first use.

## When answers come back

Read the filled-in file, turn each answer into a requirement change or a closed Open question through the prod-doc skill, and add a changelog row naming the recipient. Keep the answered questionnaire in `assets/` as the source.
