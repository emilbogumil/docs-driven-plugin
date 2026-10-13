# IDs and traceability

The point of the IDs is that a requirement written on day one can be found in the test list, in the automated tests, in the user documentation and in the code map on day five hundred, with grep alone.

## Feature code

Every feature has a short code such as `UM-UR` (user management, user roles) or `BIL-INV` (billing, invoices). Rules:

- one to three tokens of capital letters, joined by hyphens, letters only;
- the first token is the domain code and is shared by every feature in that domain;
- unique across the whole docs root;
- chosen at feature-init and never changed, because it is embedded in test names in the code.

Letters-only tokens matter: the scripts split `UM-UR-R01` into code `UM-UR` and suffix `R01`, and a token like `R1` in the code would make that ambiguous.

## ID kinds

| Pattern | Lives in | Means |
| --- | --- | --- |
| `CODE-R01` | prod-doc headings | a requirement, a single testable rule |
| `CODE-T01` | test-cases headings, test names in code, Gherkin tags | a test case |
| `CODE-D01` | tech-doc decisions table | an architecture decision |

Numbers are two or more digits, zero-padded, assigned in order, never reused. A withdrawn requirement keeps its heading and gets the line `Deprecated on <date>: <reason>` as the first line of its body. The trace check then stops requiring coverage for it.

Domain-wide rules live in the domain overview with the domain code only, for example `UM-R01`, and feature cases may cover them.

## How the links are expressed

- A test case lists `- **Covers:** CODE-R01, CODE-R02`. One case may cover several requirements, and a requirement normally has several cases: the happy path, each edge case, each error message.
- A user-doc task section carries `<!-- covers: CODE-R01 -->` right under its heading. This is invisible to readers and lets a requirement change point to the paragraph that must be rewritten.
- An automated test puts the case ID in its name, for example `it("[UM-UR-T03] rejects demoting the last admin", ...)` or `def test_um_ur_t03_...` with a `# UM-UR-T03` comment on the line above. Any occurrence of the ID in a source file counts, so pick whatever reads well in the test framework.
- A Gherkin scenario is tagged with the case ID first and the requirements after: `@UM-UR-T03 @UM-UR-R02`.
- The tech-doc code map lists the requirements each path implements.

## Parser contract

The scripts recognise exactly these forms; anything else is ignored silently.

| Element | Exact form |
| --- | --- |
| Requirement | `### CODE-R01: title` heading in prod-doc.md (or in overview.md for domain-wide rules) |
| Deprecated requirement or case | first non-empty body line starts with `Deprecated on ` |
| Test case | `### CODE-T01: title` heading in test-cases.md |
| Covers line | `- **Covers:** CODE-R01, CODE-R02` (only R IDs count) |
| Type line | `- **Type:** automated` / `planned` / `manual` |
| Automated-in line | `- **Automated in:** path/to/test.ts (optional test title)`; first token is checked as a path relative to the code root |
| User-doc trace | `<!-- covers: CODE-R01, CODE-R02 -->` anywhere in user-doc.md |
| Gherkin | a tag line `@CODE-T01 @CODE-R01 @CODE-R02` above a scenario in test-cases.feature |
| Test tag in code | the literal case ID anywhere in a source file under the code root (skipping node_modules, dist, .git and the docs root) |
| Template guidance | `<!-- guide: ... -->` comments; must be deleted before a document leaves draft |
| Overview row | `| [Title](feature/prod-doc.md) | CODE | status | summary |` in overview.md; its status is compared with the prod-doc's |

Automation findings are warnings while the feature is in progress and errors once the prod-doc or tech-doc is `current`.

## What the trace check enforces

Errors (fail the check): missing files, invalid status, codes that disagree between files, a case covering a requirement that exists neither in the prod-doc nor in the domain overview, a live requirement with no case, a user-doc comment naming an unknown requirement, a source file naming a case that is not in test-cases.md, a current document on top of a draft prod-doc, guide comments left in a current document, and, once the feature is implemented, an automated case with no evidence in source or a `planned` case still undecided.

Warnings (grouped per feature and kind): skipped numbers, cases without a Type line, automated cases whose named test file exists but does not carry the ID yet, automated or planned cases not yet found while the feature is still in progress, guide comments in an approved document, an overview row whose status disagrees with the prod-doc, and current documents past their review date.
