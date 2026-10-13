---
name: feature-close
description: This skill should be used when a feature in a docs-driven project is implemented and ready to merge: the user says "close the feature", "wrap up", "finalize the docs", "ready to merge", "mark as current", or asks for the PR description of a feature branch. It runs the final trace check, confirms the walkthrough and deviations are written, flips every document to current, writes changelog rows, updates the domain overview, builds the PR description from the docs, and stops at any gate that is not met.
argument-hint: [domain/feature]
---

# Feature close

Make the documents the truth about what shipped, then prepare the merge. Target: `$ARGUMENTS`.

## Gates

Check each and stop with a clear list if any fails; closing with a failed gate is how docs become fiction.

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py --feature <domain>/<feature> --strict` passes. Every automated case is found in source by its ID, no `planned` case remains (each became automated or manual), and no `<!-- guide: -->` comment is left in any document.
2. The project's test suite passes on the branch.
3. prod-doc, user-doc and test-cases are `approved` (or already current). A draft here means a change from implementation was never signed off.
4. tech-doc has its Walkthrough half written, including the Deviations section, and the Deviations section agrees with the documents: every listed deviation has been resolved either by a doc change (with a changelog row) or a code change.
5. The manual cases in the regression checklist have been run at least once; ask the user to confirm.

## Close

1. Set `status: current` and today's `last_reviewed` in all four documents. Add the implementation PR to `related_prs` once it exists.
2. Add a changelog row to each document: "Released with <PR or version>".
3. Update the feature row in the domain `overview.md` to `current` and make sure its summary cell is filled. Reconcile the glossary with the Terms sections of the four documents: promote terms other features also use, correct definitions the feature found wrong, and replace the local definition with a link.
4. Remove any `<!-- TODO: conflict with prototype ... -->` markers left in the user-doc; they should have been resolved at gate 3.
5. Commit on the feature branch: `docs(<domain>/<feature>): close feature, docs current`.

## PR description

Build it from the documents rather than from the diff:

```
## <Title>
<prod-doc summary paragraph>

### Requirements implemented
<ID: title, one per line, from prod-doc>

### Test coverage
<coverage matrix from trace_check --matrix>

### Design decisions
<CODE-Dnn rows with status accepted>

### Deviations from the original spec
<from tech-doc, or "None">

### Docs
<links to the four files>
```

Append the attribution lines the session requires for PR bodies. If the `gh` tool is available and the user asks, open the PR; otherwise print the description.

## After merge

Publish the user-doc through whatever pipeline the project uses, and remind the user that the prod-doc is now what the support assistant will answer from, internal block excluded.
