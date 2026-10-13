# Frontmatter and statuses

Every one of the four feature documents starts with the same YAML block. The scripts parse it with a minimal parser, so keep it flat: scalar values and simple lists only.

```yaml
---
feature: user-management/user-roles   # must equal the folder path under the docs root
code: UM-UR                            # feature code, identical in all four files
doc: prod-doc                          # prod-doc | user-doc | test-cases | tech-doc
title: User roles
status: draft                          # draft | approved | current | deprecated
owner:                                 # person or team accountable for the content
last_reviewed: 2026-10-11              # ISO date, bump whenever someone confirms the content is right
related_prs: []                        # list of PR links or numbers
prototype: none                        # user-doc only: Figma or Lovable link, "implemented UI (<path>)", or none
---
```

## Statuses

| Status | Meaning | Who moves it here |
| --- | --- | --- |
| draft | Being written or changed. Nothing downstream should rely on it yet. | author |
| approved | Reviewed and agreed. Downstream work (tests, code) may start from it. | reviewer, after an explicit OK |
| current | Matches what is shipped. The document is the truth about production. | feature-close |
| deprecated | The feature or document is withdrawn. Kept for history. | owner |

Typical transitions per document:

- **prod-doc**: draft during the interview, approved when the owner signs off, current at feature-close. If the implementation forced a spec change, the doc goes back to draft, gets the change, and is re-approved before close.
- **user-doc**: draft from prototype, approved after a product review, current when published alongside the release.
- **test-cases**: draft while being derived, approved when QA accepts the list, current when every automated case is found in the code and the manual checklist has been run once.
- **tech-doc**: draft with only the Design half, approved after design review, current once the Walkthrough half is written from the shipped code.

The trace check treats some combinations as errors: any document marked current while the prod-doc is still draft, and a status value outside the four above.

## Other fields

- `last_reviewed` drives the "stale" warning: a current document older than `review_after_days` in the config is flagged. Bump the date whenever a human confirms the content, not only when the text changes.
- `related_prs` accumulates over the feature's life. Add the docs PR and the implementation PR.
- `owner` is free text. Leave it empty rather than guessing.
