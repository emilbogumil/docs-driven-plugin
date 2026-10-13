# Testing discipline: seams and real assertions

Adapted from the `principle-test-behavior-not-implementation` skill in [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT) and the seams and anti-pattern sections of the `tdd` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See THIRD_PARTY_NOTICES.md.

A test case is only covered when a test asserts what the case's Expected line says. Running the code is not enough.

## Seams

A **seam** is the public boundary a test observes behaviour through: an HTTP route, a page as the user drives it, a library's exported function. Tests live at seams, never against internals.

- Agree the seams in the tech-doc design, before tests are written: which seam each group of cases is tested at, and what that seam catches and misses.
- Prefer existing seams to new ones and the highest seam that is practical. Fewer seams across the codebase is better.
- Each automated case is tested at one agreed seam. The test-cases file names the level (UI, API or unit) in the case's first step.

## The undefined check

Rewrite or delete any test that would still pass if every imported function returned `undefined` or a wrong value. These shapes fail it:

- loose or no assertion: `toBeDefined`, `toBeTruthy`, `not.toThrow`, `toBeGreaterThan(0)`;
- call or absence only: `toHaveBeenCalled`, `toBeUndefined`, `toEqual([])` without a matching presence check on another input;
- tautology: the expected value is computed the way the code computes it, for example `expect(add(a, b)).toBe(a + b)`;
- restating a constant, a config default or a table row instead of exercising the code that reads it;
- asserting on data the test built itself, with no call to the code under test.

Fix: call the code the way its users do, with one concrete input, and assert the literal result or effect from the case's Expected line, including exact messages. For a mock, assert the payload it received.

## Applying it

- **test-cases**: a case is `automated` only when a test passes the undefined check for that case's Expected line. A test that exercises the path but asserts less makes the case `planned`, or splits it.
- **implement**: write each case's test before or alongside its code, and run the undefined check on it before reporting.
- **spec-check --deep**: the spec reviewer applies the check to every test named for a case.
