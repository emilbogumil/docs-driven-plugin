# docs-driven.json

Lives at the docs root and marks it. Created by `scaffold.py init`. All fields are optional except `version`.

| Field | Default | Used by |
| --- | --- | --- |
| product_name | folder name | templates, glossary |
| audience | | user-doc skill, to pitch the writing |
| tone | | user-doc skill |
| test_format | markdown | `gherkin` adds a `test-cases.feature` next to test-cases.md at scaffold time |
| code_root | `..` | trace check: where to scan source files for case IDs, relative to the docs root |
| test_tag_style | bracket | implement skill: `bracket` for `[UM-UR-T03]` in test names, `comment` for a comment line above the test |
| review_after_days | 90 | trace check: age after which a current document is flagged |
| domains | {} | one-line description per domain, filled in as domains appear |

The scripts find the docs root by walking up from the current directory and looking for `docs-driven.json` either in the folder itself or in a `docs/` subfolder. Pass `--docs-root` to override.

A project that keeps docs in a separate repository sets `code_root` to the path of the code checkout, for example `../../acme-app`. The trace check still works, but merges can no longer be atomic, which is why a single repository is recommended.
