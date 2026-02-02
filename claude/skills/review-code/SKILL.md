---
description: Review code changes for common issues, pattern adherence, and test coverage. Compares current branch to base branch.
model: opus
argument-hint: "[base-branch]"
---

# Code Review Skill

Review code changes on the current branch, checking for common issues, pattern adherence, and test coverage.

## What This Skill Checks

### Inline Imports (Python)

Imports should generally be at the top of files. Flag imports that appear inside functions or methods unless there's explicit motivation (e.g., avoiding circular imports, optional dependencies, performance-critical lazy loading).

### Variable Naming

Variable names should be reasonably human-readable. This includes:

- **No single-character names**: Only `_` is acceptable (Python convention for unused values). Names like `i`, `j`, `x`, `y` should use more descriptive alternatives (e.g., `index`, `row_idx`, `coordinate_x`).
- **Meaningful names**: Names should convey purpose or meaning, not just satisfy length requirements. `aa` or `xx` are not improvements over `a` or `x`.
- **Context-appropriate verbosity**: Short but clear names are fine in narrow scopes; broader scopes warrant more descriptive names.

### Test Coverage for New Logic

Assess whether new logic has appropriate test coverage. Use case-by-case judgment:

- Not every function needs tests, but many do if we want to guarantee functionality
- Prefer broader-scope tests that are agnostic to implementation details
- Flag when tests would meaningfully help guarantee functionality

### Pattern Adherence

Check if changes align with existing codebase conventions:

- Naming conventions (classes, functions, files)
- Code organization patterns
- Use of shared utilities vs. duplicating logic
- Architectural patterns in the module/package

Use the Explore agent to understand repo conventions before comparing.

## Severity Assignment

Assess severity dynamically based on context, not by check type:

- **Error**: Critical issues likely to cause bugs, security problems, or major maintenance burden
- **Warning**: Issues that should generally be fixed, but context may justify exceptions
- **Info**: Worth noting, may be intentional design choices

Examples:

- Inline import causing circular dependency → Error
- Inline import for optional/rarely-used feature → Info
- Pattern divergence introducing inconsistency → Warning or Error
- Pattern divergence with clear architectural justification → Info

## Workflow

### 1. Determine Base Branch

If a base branch is provided as an argument, use it. Otherwise:

1. Identify the likely base branch (usually `main` or the repo's default branch)
2. Check if histories have diverged significantly (e.g., via `git merge-base`)
3. **Confirm with the user** which base branch to use, especially if:
   - The branch appears to be based on another feature branch
   - Histories have diverged and a rebase may be needed
   - It's ambiguous which branch the changes should be compared against

If a rebase is needed before review makes sense, suggest that first.

### 2. Identify Changed Files

Run `git diff <base>..HEAD --name-only` to get the list of changed files.

### 3. Analyze Each File

Read changed files and run checks for:

- Inline imports
- Variable naming
- Test coverage gaps

### 4. Explore Patterns

Use an Explore agent to understand repo conventions for pattern adherence checks.

### 5. Generate Report

Produce a categorized checklist (see Output Format below).

### 6. Surface Questions

Ask about uncertainties and arguable design decisions.

### 7. Offer Fixes

After discussion, offer to fix identified issues.

## Output Format

Present findings as a markdown checklist:

```markdown
## Code Review Summary

### Errors (must fix)

- [ ] `path/to/file.py:42` - Description of the issue

### Warnings (should fix)

- [ ] `path/to/file.py:15` - Description of the issue

### Info (consider)

- [ ] `path/to/file.py:88` - Description of the issue

### Questions / Design Decisions

- Question about an ambiguous design choice?
```

## After Review

Once the review is complete and questions are resolved:

1. Ask if the user wants to proceed with fixes
2. Address issues in order of severity (Errors first, then Warnings)
3. For each fix, explain what changed
4. After fixes, re-run any relevant linting/type checking to verify no regressions
