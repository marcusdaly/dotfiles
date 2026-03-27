---
description: Fix bugs using test-driven development. Write a failing regression test first, then implement the fix until the test passes.
model: opus
argument-hint: "[description of the bug]"
---

# TDD Bug Fix Skill

Fix bugs using a test-driven development approach: write a failing regression test that reproduces the issue, then implement the fix.

## Workflow

### 1. Understand the Bug

Gather enough context to understand the bug being fixed:

- Read relevant code and error messages
- Identify the root cause or narrow down the area of concern
- Understand the expected vs. actual behavior

### 2. Plan

Before writing any code, present a plan to the user for approval. The plan should include:

- **Regression test**: Describe the test that will be written — what it asserts, where it will live, and why it reproduces the bug
- **Fix approach**: Outline the intended approach to fixing the bug — which files/functions will change and how

Wait for the user to approve the plan before proceeding.

### 3. Write the Regression Test

Write a test that:

- Reproduces the bug by exercising the failing behavior
- Uses the repository's existing testing framework and conventions
- Asserts the **expected** (correct) behavior, so that it **fails** under the current broken implementation
- Is focused and minimal — tests exactly the bug, not more

Run the test and confirm it fails. If it does not fail, the test is not correctly reproducing the bug — revisit before moving on.

**Important**: Once the regression test is written and confirmed to fail, do not edit it again. The test is the specification for the fix. If the test needs changes, that means the plan was wrong — go back to step 2.

### 4. Implement the Fix

With the failing test locked in:

1. Implement the fix
2. Run the regression test
3. If the test still fails, iterate on the fix (not the test)
4. Once the regression test passes, run the full test suite to check for regressions

### 5. Verify

After the fix passes the regression test:

- Run the full test suite to ensure no regressions
- Run any formatting, linting, and type-checking tools present in the repository
