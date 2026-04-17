# General Guidance

## Secrets and API Tokens

- **Never read, cat, or display the contents of `~/.secrets.env` or any secrets file.**
  Always reference tokens via environment variables (e.g., `$BUILDKITE_API_TOKEN`)
  to keep them out of conversation history.
- Tokens from `~/.secrets.env` are already available as environment variables
  in every shell session (loaded via the shell profile).

## Style/Linting

### Import Statements

Please keep import statements at the top of files whenever possible.

### Variable Naming

Please do not use single-letter variable names. Instead, favor using human-readable variable names.

### Linting

When fixing linting errors, prefer fixing the root cause of type errors rather than using comments to ignore them, unless there is a strong reason to do otherwise.

### Fallbacks

Please avoid fallbacks and warnings if something unexpected is observed. Instead, raise explicit errors to increase visibility to the issue.

### Backwards Compatibility

When making changes to not-yet-deployed branches, please favor a cleaner implementation over backwards compatbility.

### Comments

Avoid redundant comments. If a section of code is very readable and short, there is no need to have a dedicated comment for each of these sections explaining what the code does.

### Assert Statements

Please only use `assert` statements in tests, instead favoring raising appropriate, informative error types when e.g. an input parameter is of an unexpected value or type.

### Working with lists of items

When working with code that enumerates a list of items that code changes may update, please try to keep each item on its own line for cleaner diffs and better readability.

## Progress Reporting

For long-running operations that have a notion of intermediate progress (e.g. processing data in batches, iterating over files, training epochs), use `tqdm` progress bars to provide visibility into progress.

## Bug Fixing

- When fixing bugs, use the `tdd-fix` skill to follow a test-driven development approach: write a failing regression test first, then implement the fix.

## Best Practices working around Code

- When adding, updating, or deleting code, please be cognizant that nearby documentation (e.g. READMEs) or deployment files (e.g. Dockerfiles) may reference the code being changed! Make sure to check and update these files accordingly.
- Before considering a task complete, please run any formatting, linting, type-checking, and testing tools present in the repository we're working in. Often, this will look like `uv run ruff check`, `uv run pyright`, and `uv run pytest`.

## Reproducibility and one-off scripts / "fast" solutions

Please build reproducible solutions rather than one-off scripts or any other "fast" solution as a shortcut, unless I *explicitly* request otherwise.
Please only suggest a one-off script if we would *not* have to write a similar script again to accomplish the same task at a later date.

## Git - Commits

- **Never amend commits.** Always create new commits instead. This preserves history,
  avoids force-push issues, and makes it easier to review incremental changes. Repos
  that squash-merge will collapse the history anyway.

## Git - Resolving conflicts and rebasing

- Please refer to the `rebase-chain` skill whenever performing rebases.
- When merging in changes from other branches, please keep in mind that often one branch was originally branched off of the other, but both branches have had changes since then, and the older one in particular often will have rebased on a main branch to pull in fresh changes. Please keep that in mind and lean towards using the `rebase-chain` skill to handle cases like this.
- Note that I often work in repos where the norm is to squash and merge into main. This means that the commit history may look much longer on the feature branch than it does on main when trying to rebase on top of main. Again, the `rebase-chain` skill should help here.
- When resolving merge/rebase conflicts, never use blanket `git checkout --ours` or `git checkout --theirs` on entire files. Both sides almost always have changes that need to be preserved. Always inspect conflict markers and merge intentionally.
- Before running `git stash`, ALWAYS first run `git status` and `git diff --stat` to check what would be stashed. Never blindly stash — in-progress work can be lost or forgotten. If the stash contains meaningful changes, confirm with the user before proceeding.

### Rebase verification

After every `rebase --onto`, verify the result BEFORE pushing:

- Check commit count: `git log --oneline <parent>..<branch> | wc -l`
- Check content diff: `git diff <parent>..<branch> --stat`
- If a branch looks identical to its parent after rebase, the unique commits
  were silently dropped. Recover from backup tags immediately.

### Pushing rebased branch chains

When pushing multiple rebased branches, NEVER use shell variables across separate commands or subshells. Variables are lost between tool calls and when changing directories. Instead:

- **Write SHAs to a file** rather than storing in shell variables (e.g., `git rev-parse HEAD >> /tmp/branch_shas.txt`).
- **Use explicit SHAs in push commands**, not variables. Copy the SHA from the rebase output and paste it directly into the push command.
- **Never use the pattern `$var:refs/heads/branch`** in `git push` — if `$var` is empty, git interprets `:refs/heads/branch` as a DELETE operation, which will delete the remote branch and auto-close any associated PRs.
- **Push each branch individually** with explicit SHAs rather than batching multiple branches in one push command.
- **Verify after pushing** that all remote branches exist and have the correct SHAs.

### Worktree safety

When rebasing branches that are checked out in other worktrees:

- **Always ask the user before modifying other worktrees.** Other worktrees may
  have active jobs (training, tests) that depend on the current branch.
- **Never leave a worktree on detached HEAD.** After updating a branch pointer
  with `git branch -f`, always restore the worktree to its original branch.
- **Prefer `git -C <path>`** over `cd`-ing into other worktrees to avoid CWD
  confusion across tool calls.
- **Check for uncommitted changes** (`git -C <path> status --short`) before
  detaching. Stash if needed, and pop after re-attaching.

## ML Model Pipelines

- Try to avoid ad-hoc data processing and evaluation. Reproducible scripts and ideally pipelines are much better long term.

## Python Environment

- When configured in the project, please use `uv` for a python environment and dependency management.

## GitHub PRs

**Always prefer `ghpr` over raw `gh api` calls** for PR operations. `ghpr`
handles authentication and formatting automatically, avoiding permissions
issues that `gh api` can encounter. Only fall back to `gh api` when you need
data that `ghpr` doesn't expose (e.g., specific API fields, programmatic JSON
parsing).

`ghpr` is loaded into the shell profile automatically — call it directly:

```bash
ghpr comments <PR_NUMBER>
```

Available commands:

- `ghpr comments <pr>` — Show all comments (inline review, review summaries, general)
- `ghpr diff <pr>` — Show the PR diff
- `ghpr files <pr>` — List changed files
- `ghpr info <pr>` — Show PR title, state, base branch, and description
- `ghpr checks <pr>` — Show CI check status

Use `ghpr comments` when addressing PR review feedback, and `ghpr info` to
understand a PR's purpose before making changes.

## Shell Commands

- When parsing JSON output from CLI tools (e.g. `curl` to REST APIs), prefer `jq` over inline `python3 -c` one-liners. `jq` is more concise and readable for simple field extraction and filtering.
- When running long-running commands in the background, do not pipe through `tail` or `head` — the full output is written to a file anyway, and truncating it can cut off valuable information (e.g. job IDs, error messages, cluster URLs).

## Comet ML

Monitor training experiments from the terminal using the `comet` alias:

```bash
comet list <project>                    # List recent experiments with loss
comet metrics <experiment_key>          # Latest metrics
comet text <experiment_key>             # Qualitative generations
comet compare <key1> <key2> [metric]    # Compare experiments
comet url <experiment_key>              # Print experiment URL
```

The `comet` alias loads API key from `~/.secrets.env` and runs via uv.
Requires `COMET_API_KEY` and `COMET_WORKSPACE` env vars in `~/.secrets.env`.

## Plan Mode

- Feel free to enter plan mode whenever you deem appropriate!
