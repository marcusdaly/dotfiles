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

## Safety: Always Create Backup Tags First

Before any rebase operation, create backup tags for all branches in the chain:

```bash
# Create backup tags for all branches
git tag backup/branch-A feature/branch-A
git tag backup/branch-B feature/branch-B
git tag backup/branch-C feature/branch-C
# ... for all branches in the chain
```

If using signed tags (e.g., `tag.gpgsign=true`), you may need:

```bash
git -c tag.gpgsign=false tag backup/branch-A feature/branch-A
```

These backups let you:

- Reference original commit ranges with `git merge-base backup/X backup/Y`
- Rollback if something goes wrong: `git checkout feature/X && git reset --hard backup/X`
- Compare before/after: `git diff backup/X feature/X`

## Workflow

For each branch in the chain (starting from the earliest):

1. **Identify the old base**: `git merge-base <branch> <parent-branch>`
2. **Rebase onto updated parent**: `git rebase --onto <parent-branch> <old-base> <branch>`
3. **Resolve any merge conflicts** (see below)
4. **Run linting and type checking** (e.g., `uv run ruff check`, `uv run pyright`)
5. **Run tests** (e.g., `uv run pytest`) on shared code and specific changes
6. **Verify the commit count matches expectations**: `git log --oneline <parent>...<branch>` should show only the unique commits
7. **Push the updated branch**: `git push --force-with-lease`
8. **Proceed to the next branch** in the chain

Only proceed to rebasing the next branch once the current branch is verified to be functional.

**Red flag**: If the rebase encounters many conflicts, especially on files that shouldn't have conflicts, the old-base is likely wrong. Abort and find a more recent old-base (see "Finding the Correct Old-Base After Squash Merges").

## Finding the Correct Old-Base After Squash Merges

**Critical**: When the parent branch has been squash-merged into main, `git merge-base` often returns the wrong commit. This is the most common cause of rebase conflicts.

### The Problem

Consider this scenario:

- `feature/A` was squash-merged into `main` as commit `abc123`
- `feature/B` was branched off `feature/A` and has commits `A1, A2, A3, B1, B2`
- You want to rebase `feature/B` onto `main`

If you run `git merge-base feature/B main`, it returns a commit that's too old (before A1). Using this as old-base means git tries to replay A1, A2, A3 which already exist in main (via the squash), causing conflicts.

### The Solution

**Find the last parent-branch commit in your branch's history, not the merge-base**:

```bash
# Wrong - returns commit before both A and B diverged from main
git merge-base feature/B main

# Right - find the last A commit in B's history
# Look at B's log and identify where A's commits end
git log --oneline feature/B | head -20
```

Then use that commit as old-base:

```bash
# If A3 (hash: def456) is the last A commit in B's history
git rebase --onto main def456 feature/B
```

### Quick Identification Method

The unique commits are those AFTER the last commit from the parent branch:

```bash
# See commits on B that aren't on the updated parent
git log --oneline <updated-parent>..feature/B

# The old-base should be the commit just BEFORE the first unique commit
```

If you see commits in this list that belong to the parent branch (already squash-merged), your old-base is wrong - find a more recent old-base.

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

## Updating Branch Pointers After Rebase

When using `git rebase --onto` with a backup tag (e.g., `backup/branch-B`), you'll end up in a detached HEAD state. Update the branch pointer:

```bash
# After: git rebase --onto feature/branch-A <old-base> backup/branch-B
# You're now in detached HEAD with the rebased commits

# Update the branch to point to the rebased HEAD
git branch -f feature/branch-B HEAD

# Optionally switch to the branch
git checkout feature/branch-B
```

## Fixing Issues in a Branch Chain

When you discover an issue (e.g., failing tests) after rebasing:

1. **Identify which branch introduced the issue** - Don't fix in the final branch if the problem was introduced earlier
2. **Fix in the correct branch** - Make the fix commit in the branch where the issue was introduced
3. **Rebase all downstream branches** - Use `rebase --onto` to propagate the fix forward

Example: If tests fail on `feature/C` but the issue was introduced in `feature/A`:

```bash
# 1. Fix on feature/A
git checkout feature/A
# ... make fix ...
git commit -m "Fix issue"

# 2. Rebase feature/B onto fixed feature/A
git rebase --onto feature/A <old-base-B> feature/B

# 3. Rebase feature/C onto updated feature/B
git rebase --onto feature/B <old-base-C> feature/C
```

This ensures the fix exists at the right point in history and propagates cleanly.

## Batch Rebasing Multiple Downstream Branches

When rebasing a long chain (e.g., 6+ branches), you can batch the `rebase --onto` operations. Git will automatically skip commits that already exist upstream:

```bash
# For each downstream branch, find old base from backups and rebase
for branch in grad-norm-logging hyperparam-studies reward-weighted-regression; do
  OLD_BASE=$(git merge-base backup/$branch backup/<parent-branch>)
  git rebase --onto feature/<parent-branch> $OLD_BASE backup/$branch
  git branch -f feature/$branch HEAD
done
```

Git will output "dropping ... -- patch contents already upstream" for duplicate commits, which is expected and safe.
