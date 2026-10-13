## Docs-driven development

Feature documentation lives in `{{docs_root}}/<domain>/<feature>/` with four files: prod-doc.md (business rules, the spec), user-doc.md (customer-facing), test-cases.md (QA cases) and tech-doc.md (design and walkthrough). Requirements have IDs like `UM-UR-R01` and test cases like `UM-UR-T01`.

- The prod-doc and user-doc are the specification. Implement exactly what they say; when the code must deviate, say so and update the docs in the same change.
- Name automated tests with the test case ID they implement, for example `[UM-UR-T03]`, so the trace check can find them.
- Run the trace check before declaring a feature done.
- The docs-driven plugin provides the stage skills: feature-init, prod-doc, user-doc, test-cases, tech-doc, implement, spec-check, feature-close.
