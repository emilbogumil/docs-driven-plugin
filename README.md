# docs-driven

A Claude Code plugin for docs-driven feature development. Every feature gets four documents, written in a fixed order, tied together by requirement IDs that are traced through test cases, automated tests and code.

```
docs/<domain>/<feature>/
  prod-doc.md     business rules as numbered requirements   written first
  user-doc.md     customer-facing help, from the prototype  written second
  test-cases.md   QA cases covering every requirement       written third
  tech-doc.md     design before coding, walkthrough after   written fourth and sixth
```

The documents are the specification. Implementation reproduces them and passes the cases. Nothing is merged while a document is out of step with the code.

## Install

From a marketplace:

```
/plugin marketplace add emilbogumil/docs-driven-plugin
/plugin install docs-driven@docs-driven
```

To have every clone of a project offer the plugin, commit this to the project's `.claude/settings.json`; Claude Code then asks to install it when the folder is trusted:

```json
{
  "extraKnownMarketplaces": {
    "docs-driven": { "source": { "source": "github", "repo": "<github-user>/docs-driven" } }
  },
  "enabledPlugins": { "docs-driven@docs-driven": true }
}
```

Updates: bump `version` in `.claude-plugin/plugin.json`, push, and run `/plugin marketplace update docs-driven` where it is installed.

For local development, load it straight from the folder:

```
claude --plugin-dir /path/to/docs-driven-plugin
```

## Set up a project

```
/docs-driven:feature-init user-management/user-roles
```

The first run creates `docs/docs-driven.json`, `docs/glossary.md` and a CLAUDE.md snippet, then scaffolds the feature. Edit `audience` and `tone` in the config so the user-doc skill writes in your voice. See `references/config.md`.

## Skills

| Skill | Stage | Produces |
| --- | --- | --- |
| `workflow` | any | orientation; which stage a feature is at (model-invoked) |
| `feature-init` | 0 | feature folder, code, branch |
| `prod-doc` | 1 | business spec with `CODE-Rnn` requirements |
| `user-doc` | 2 | customer doc from the prototype, traced to requirements |
| `test-cases` | 3 | QA cases with Covers lines, optional Gherkin |
| `tech-doc design` | 4 | design, alternatives, `CODE-Dnn` decisions |
| `implement` | 5 | code and tests named with `CODE-Tnn`, a deviations list |
| `tech-doc walkthrough` | 6 | code map, flows, test map, operations, deviations |
| `spec-check` | any | trace check findings; `--deep` compares code behaviour to the spec |
| `feature-close` | 7 | statuses to current, changelog, PR description |

Invoke as `/docs-driven:<skill> <domain>/<feature>`.

## Scripts

Standard-library Python, usable outside Claude Code, for example in CI.

```
scripts/scaffold.py init --docs-root docs --product "Acme"
scripts/scaffold.py feature billing/invoices --code BIL-INV
scripts/trace_check.py [--docs-root docs] [--feature billing/invoices] [--matrix] [--json] [--strict]
scripts/status_report.py [--docs-root docs]
```

`trace_check.py` exits non-zero on errors: missing documents, bad statuses, a requirement without a case, a case covering an unknown requirement, a user-doc comment naming an unknown requirement, an automated case not found in source once the feature is current, and a source file naming a case that does not exist.

## Retrofitting an existing codebase

The same stages apply to code that already exists; the `workflow` skill has a Retrofit section with the substitutions (the code is the interviewee, the shipped UI is the prototype, existing tests are tagged with case IDs, decisions are mined from design notes). Cases that could be automated but are not yet are typed `planned` and must be resolved before the feature is marked current.

## Conventions in one paragraph

A feature code like `UM-UR` is chosen once and never changed. Requirements are `### UM-UR-R01: title` headings in the prod-doc; cases are `### UM-UR-T01: title` headings in test-cases.md with a `- **Covers:** UM-UR-R01` line; decisions are `UM-UR-D01` rows in the tech-doc. Automated tests put the case ID in their name. User-doc task sections carry `<!-- covers: UM-UR-R01 -->`. Statuses are draft, approved, current, deprecated, and a later document may not be current while the prod-doc is draft. Details in `references/`.

## Layout

```
.claude-plugin/plugin.json      manifest
.claude-plugin/marketplace.json lets this repo be added as a marketplace
skills/<name>/SKILL.md          the nine skills
agents/spec-reviewer.md         implementation-versus-spec reviewer used by spec-check --deep
templates/                      the document, overview, glossary and config templates
references/                     frontmatter, IDs and traceability, style guide, config
scripts/                        scaffold, trace check, status report
```

## Credits

The interview method (grilling), the glossary and decision discipline, the questionnaire for open questions and the testing checks are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) and [pstack](https://github.com/cursor/plugins/tree/main/pstack), both MIT licensed. They are copied and rewritten into `references/` rather than declared as plugin dependencies; THIRD_PARTY_NOTICES.md lists the sources and licenses.

## License

MIT
