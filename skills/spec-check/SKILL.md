---
name: spec-check
description: This skill should be used to verify consistency between a feature's documents, tests and code in a docs-driven project: the user says "check the docs", "is the spec consistent", "trace check", "what is uncovered", "does the code match the spec", "docs drift", or before any merge of a feature branch. It runs the trace check script, explains the findings, fixes mechanical issues when asked, and with --deep spawns the spec-reviewer agent to compare implementation behaviour against the prod-doc and user-doc requirement by requirement.
argument-hint: [domain/feature] [--deep] [--fix]
---

# Spec check

Find out where documents, tests and code have drifted apart. Arguments: `$ARGUMENTS`; no feature means the whole docs root.

## Mechanical check

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_check.py [--feature <domain>/<feature>] --matrix`. Read `${CLAUDE_PLUGIN_ROOT}/references/ids-and-traceability.md` for what each finding means. The script exits non-zero on errors; warnings are informational unless `--strict`.

Findings of one kind are grouped per feature (one line listing the IDs), so a feature with twenty untagged tests produces one warning, not twenty. Summarise the result for the user by feature: statuses, coverage numbers, and each finding in plain words with the action it implies. Group findings by the document that needs the edit, since that is how the user will fix them.

With `--fix`, repair what is mechanical and unambiguous: missing Type lines, a stale coverage matrix, frontmatter typos, a user-doc comment naming a requirement that was obviously renumbered. Do not invent test cases for uncovered requirements or delete references to fix them; those are content decisions and go through the `test-cases` or `prod-doc` skills. List what was fixed and what was left.

## Deep check

With `--deep`, or when the user asks whether the code actually does what the spec says, spawn the `spec-reviewer` agent from this plugin for each feature in scope, giving it the feature key and the docs root. It returns a verdict and per-requirement findings with file references. Merge its report with the mechanical findings and present the reconciliation suggestions. Do not apply code or doc changes from the deep check without the user's decision, because each one is a judgement about which side is right.

## Where to run it besides here

The script is standard-library Python and can run in CI: `python3 <plugin>/scripts/trace_check.py --docs-root docs --strict`. Suggest adding it to the project's CI when the user asks how to keep the docs honest after the feature is merged. Pointing a Stop hook at it is also possible but noisy on large repos; prefer CI and `feature-close`.
