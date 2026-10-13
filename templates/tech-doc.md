---
feature: {{feature}}
code: {{code}}
doc: tech-doc
title: {{title}}
status: draft
owner:
last_reviewed: {{date}}
related_prs: []
---

# {{title}}: technical documentation

<!-- guide: Two halves. The Design half is written before implementation and reviewed like a pull request. The Walkthrough half is written after implementation, from the actual code, so a new engineer can find their way around. -->

## Design

### Context and constraints
<!-- guide: What exists today, what the prod-doc requires, and the non-functional constraints (performance, security, compatibility). -->

### Approach
<!-- guide: The chosen approach in a few paragraphs. Reference requirements by ID where a design choice serves a specific rule. -->

### Data model
<!-- guide: Entities, fields, relations, migrations. -->

### Interfaces
<!-- guide: APIs, events, UI components, permissions. Include request and response shapes. -->

### Test seams
<!-- guide: The public boundaries the test cases will be automated at, which cases each takes, and what each catches and misses. -->

| Seam | Cases | Catches | Misses |
| --- | --- | --- | --- |

### Alternatives considered
| Alternative | Why not |
| --- | --- |

### Decisions
<!-- guide: Architecture decision records, only for decisions that are hard to reverse, surprising without context, and a real trade-off. Never delete a row; supersede it. -->

| ID | Date | Decision | Status | Consequences |
| --- | --- | --- | --- | --- |
| {{code}}-D01 | {{date}} | | proposed | |

## Walkthrough

### Code map
| Path | Role | Requirements |
| --- | --- | --- |

### Flows
<!-- guide: Step-by-step trace of the main flows through the code, one subsection per flow. -->

### Test map
| Test case | Automated in |
| --- | --- |

### Operations
<!-- guide: Configuration, feature flags, migrations, monitoring, rollback. -->

### Deviations from the spec
<!-- guide: Anything the implementation does differently from the prod-doc or user-doc, with the reason and the follow-up (doc change or code change). -->

## Changelog
| Date | Change | By |
| --- | --- | --- |
| {{date}} | Created | |
