---
description: Help rebase chained feature branches using `git rebase --onto`. Use when working with branches that were branched off other feature branches, especially after the parent branch has been rebased or merged.
model: opus
argument-hint: "[branch-names...]"
---

# Rebase Chain Skill

Help rebase chained feature branches, particularly when using `git rebase --onto`.

## Context

This skill helps with a common pattern when working with chained feature branches:

- Branch B was branched off of branch A
- Both branches have had changes since
- Branch A may have been rebased onto main
- Need to rebase B onto the updated A using `git rebase --onto`

When rebasing B onto the updated A, focus only on the commits that are new since B branched off of A. The goal is to replay just B's unique commits onto the new base.

### Handling Squashed Commits

When A's changes have been squashed (common when A = main after a squash-and-merge), the original commit history is lost. In this case:

- The commits that were on A before squashing no longer exist in the history
- Use `git rebase --onto` to replay only B's unique commits onto the squashed version
- You may need to use diffs (e.g., `git diff`) to get a full picture of what changed, since the commit-by-commit history is no longer available

## Goals

- Propagate changes through multiple chained feature branches
- Maintain linear commit history for easy merging and organization of changes
- Ensure code remains functional after each rebase

## Workflow

After completing each rebase:

1. Resolve any merge conflicts (see below).
2. Run linting and type checking (e.g., `uv run ruff check`, `uv run pyright`). Please run over any shared code as well as any specific changes made to ensure no unintended breaks were introduced.
3. Run tests (e.g., `uv run pytest`). Please run over any shared code as well as any specific changes made to ensure no unintended breaks were introduced.
4. Ensure all checks pass before moving to the next branch in the chain.

Only proceed to rebasing the next branch once the current branch is verified to be functional.

## Handling Merge Conflicts

When merge conflicts arise, carefully inspect the changes from both branches:

- Do not assume one branch has the "correct" implementation based on file name alone
- Read and understand the intent of changes from both sides
- Ensure no crucial changes are lost from either branch
- When in doubt, ask for clarification rather than guessing
