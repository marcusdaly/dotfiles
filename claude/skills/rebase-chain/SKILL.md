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

## Rebase --onto vs Cherry-pick

**Always prefer `git rebase --onto` over `git cherry-pick`** for propagating changes through a branch chain. This maintains linear commit history, which is critical for:

- Clean merges when branches are eventually merged to main
- Avoiding duplicate commits with different SHAs across branches
- Making `git log` and `git bisect` useful

### When to Use `rebase --onto`

Use `rebase --onto` when moving a branch's commits onto a new base:

```bash
git rebase --onto <new-base> <old-base> <branch-to-rebase>
```

Where:

- `<new-base>`: The updated parent branch (e.g., `feature/parent-branch`)
- `<old-base>`: The commit where the branch originally diverged (use `git merge-base`)
- `<branch-to-rebase>`: The branch you're updating

Example workflow:

```bash
# Find where branch-B originally diverged from branch-A
git merge-base feature/branch-B feature/branch-A  # Returns abc123

# Rebase branch-B onto updated branch-A
git rebase --onto feature/branch-A abc123 feature/branch-B
```

### When Cherry-pick Might Be Necessary

Cherry-pick should only be used as a last resort when:

1. You need to apply a **single specific commit** to an unrelated branch
2. The branches have already diverged with duplicate commits (recovery scenario)
3. You're backporting a fix to a release branch

**Warning**: Cherry-pick creates new commits with different SHAs. If you cherry-pick commits that later need to be merged, git will see them as unrelated changes, leading to:

- Merge conflicts on identical code
- Duplicate commits in history
- Confusing `git log` output

### Recovering from Cherry-pick Mistakes

If you've already used cherry-pick and have duplicate commits across branches:

1. Identify the truly unique commits in each branch (not duplicates)
2. Consider creating a fresh branch from the correct base
3. Use `rebase --onto` with `--skip` for commits that already exist
4. Or selectively cherry-pick only the unique commits to a clean branch

## Goals

- Propagate changes through multiple chained feature branches
- Maintain linear commit history for easy merging and organization of changes
- Ensure code remains functional after each rebase

## Workflow

For each branch in the chain (starting from the earliest):

1. **Identify the old base**: `git merge-base <branch> <parent-branch>`
2. **Rebase onto updated parent**: `git rebase --onto <parent-branch> <old-base> <branch>`
3. **Resolve any merge conflicts** (see below)
4. **Run linting and type checking** (e.g., `uv run ruff check`, `uv run pyright`)
5. **Run tests** (e.g., `uv run pytest`) on shared code and specific changes
6. **Push the updated branch**: `git push --force-with-lease`
7. **Proceed to the next branch** in the chain

Only proceed to rebasing the next branch once the current branch is verified to be functional.

## Handling Merge Conflicts

When merge conflicts arise, carefully inspect the changes from both branches:

- Do not assume one branch has the "correct" implementation based on file name alone
- Read and understand the intent of changes from both sides
- Ensure no crucial changes are lost from either branch
- When in doubt, ask for clarification rather than guessing

## Handling Duplicate Commits During Rebase

If `rebase --onto` encounters commits that already exist in the target (with different SHAs but same content), git will show conflicts. You can:

1. **Skip the duplicate**: `git rebase --skip` if the commit is truly a duplicate
2. **Resolve manually**: If the duplicate has slight differences, resolve the conflict
3. **Abort and reassess**: `git rebase --abort` if the situation is too complex

To check if a commit is a duplicate, compare the patch:

```bash
git show <commit-sha> --stat  # See what files changed
git diff <commit-sha>^..<commit-sha>  # See the actual diff
```
