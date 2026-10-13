---
name: feature-init
description: This skill should be used when the user wants to start a new feature in a docs-driven project, says "new feature", "scaffold the docs for", "create the feature folder", "set up docs-driven in this repo", or names a domain/feature pair to begin. It creates the docs root if missing, scaffolds the four feature documents from templates with a feature code and frontmatter, registers the feature in the domain overview, and opens a documentation branch.
argument-hint: <domain>/<feature> [--code XX-YY] [--title "..."]
---

# Feature init

Create everything a new feature needs before the first word of its prod-doc is written. Arguments: `$ARGUMENTS`.

## Steps

1. **Locate or create the docs root.** Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py init --docs-root <path> --product "<name>"` only when no `docs-driven.json` exists anywhere up the tree. Default the path to `docs` at the repository root. Ask for the product name only if it cannot be read from the repository (package name, README title). After init, show the user the generated `CLAUDE-snippet.md` and add its content to the project's CLAUDE.md, creating the file if there is none; then delete the snippet file.
2. **Agree the feature key and code.** The key is `<domain>/<feature>` in kebab-case; the domain should match an existing folder when one fits. Propose a code before scaffolding: domain token shared with sibling features (read it from their frontmatter), feature token short and pronounceable, letters only. `user-management/user-roles` becomes `UM-UR`; `billing/invoices` becomes `BIL-INV`. Check the code is not already used by grepping the docs root. The code is embedded in test names later and cannot change, so a bad guess here is expensive; state the proposal and proceed with it unless the user objects.
3. **Scaffold.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py feature <domain>/<feature> --code <CODE> --title "<Title>"`. Add `--gherkin` when the config's `test_format` is gherkin or the user asked for it. The script never overwrites, registers the feature in `overview.md`, and adds the domain to the config.
4. **Fill the two one-liners the script cannot.** The domain description in `docs-driven.json` and the summary cell of the feature row in `overview.md`, from what the user said about the feature. Leave `owner` empty unless told.
5. **Branch.** If the project is a git repository, create `docs/<domain>-<feature>` from the current branch and commit the scaffold with the message `docs(<domain>/<feature>): scaffold feature docs`. Skip when the user says to work on the current branch.
6. **Hand over.** Report the folder, the code, and that the next step is the prod-doc. If the user already described the feature's behaviour in this conversation, offer to go straight into the prod-doc interview with that as input.

## Notes

- One feature per folder. If the user describes something that is really two features (two actors, two independent lifecycles), say so and scaffold both.
- Cross-cutting concerns (auth, i18n, errors, audit) get their own domain, typically `platform`, so feature docs can reference their rules instead of restating them.
- The scaffold creates `assets/` for prototype exports; nothing goes there until stage 2.
