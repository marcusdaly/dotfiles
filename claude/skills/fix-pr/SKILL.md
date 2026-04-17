---
description: Address PR review comments and fix CI failures. Fetches review feedback, presents proposed fixes for approval, implements them, then ensures lint/type checks/tests pass.
model: opus
argument-hint: "[PR number or branch name]"
---

# Fix PR Skill

Get a PR ready for merge by addressing all review comments and ensuring CI passes.

## Workflow

### 1. Identify the PR

Determine which PR to fix:

- If a PR number is provided as argument, use it directly
- If a branch name is provided, find its PR via `gh pr list --head <branch>`
- If no argument, use the current branch: `gh pr view --json number`

Fetch PR metadata:

```bash
gh pr view <number> --json number,title,headRefName,baseRefName,state
```

### 2. Gather Review Comments

Fetch all review comments from the PR using `ghpr` (preferred over `gh api`
for reliability and auth handling):

```bash
# All comments: inline review, review summaries, and general discussion
ghpr comments <number>
```

Only fall back to `gh api` if you need structured JSON output for programmatic
processing that `ghpr` doesn't support.

### 3. Categorize Comments

For each comment, determine its status:

**Unaddressed — needs action:**

- Comments requesting changes that haven't been implemented yet
- Read the current code **on the PR's head branch** (not just the local worktree, which
  may be a different branch) to check if the issue still exists:
  `git show origin/<head-branch>:<file> | sed -n '<line-range>p'`

**Fixed downstream:**

- For each comment, check if downstream branches in the chain have already addressed it:
  1. Identify the file and code region from the comment
  2. Find downstream PRs via the PR's base/head chain
  3. Diff the downstream branch against the current branch for the specific file
  4. If the downstream diff modifies the flagged code region, mark as "fixed downstream in `<branch>`"

**Already addressed:**

- The current code on the PR's head branch already reflects the requested change
- When confirming a fix, identify **which branch and commit** introduced it:
  1. Use `git log --all --oneline -S "<relevant code>" -- <file>` to find commits that touched the flagged code
  2. Use `git branch -a --contains <commit>` to determine which branch introduced it
  3. If the fix is a later commit within the same PR, note "fixed later in this PR (commit `<short-sha>`: `<subject>`)"
  4. If the fix originates from the base branch (upstream), verify the current branch
     doesn't *undo* it — diff the flagged region between the base branch tip and the
     PR head branch. If the fix is preserved, note "fixed upstream in `<branch>`, still
     present on head". If the current branch reverts or conflicts with the fix, treat
     it as **unaddressed**.

**Thread context matters:** When a comment has replies, read the full thread to understand
the resolution. A human may have acknowledged a bot suggestion, disagreed with a reviewer,
or proposed an alternative approach. Use the full thread context — not just the original
comment — to determine the appropriate action.

**Verify uncertain deferrals:** When a user reply expresses uncertainty about whether an
issue is fixed elsewhere (e.g., "I think we may fix this in a subsequent PR", "this might
be handled downstream"), do NOT assume it's fixed. Always verify by diffing the relevant
file across all downstream branches in the chain. If no downstream branch modifies the
flagged code region, classify the comment as **unaddressed** and propose a fix. Only
classify as "fixed downstream" when you can point to a specific branch and diff that
addresses the issue.

### 4. Present Summary

Show a categorized summary to the user. Format:

```markdown
## PR #<number>: <title>

### Unaddressed Comments
1. **[file.py:42]** @author: "description of issue"
   **Proposed fix:** Brief description of what will change

2. **[file.py:100]** @author: "description"
   **Proposed fix:** Brief description

### Fixed Downstream
3. **[file.py:300]** @author: "description"
   → Already fixed in `feature/downstream-branch`

### Already Addressed
4. **[file.py:400]** @author: "description"
   → Code already reflects this change
```

**Wait for user approval before proceeding.** The user may:

- Approve all proposed fixes
- Skip specific items (add TODO comments for deferred items)
- Modify the approach for specific items
- Flag items as intentional / won't fix

### 5. Implement Fixes

For each approved item:

1. Read the relevant code
2. Implement the fix
3. For items explicitly deferred by the user, add a TODO comment in the code:

   ```python
   # TODO(PR#<number>): <description of deferred issue>
   ```

### 6. CI Verification

Run the full CI suite. Detect tools from the repo configuration rather than hardcoding:

**Tool detection:**

1. Check `pyproject.toml` for configured tools:
   - `[tool.ruff]` → linting/formatting
   - `[tool.pyright]` or `[tool.mypy]` → type checking
   - `[tool.pytest]` → testing
2. Check CI config files for actual commands:
   - `.buildkite/pipeline.yml`
   - `.github/workflows/*.yml`
3. Use detected commands with appropriate runners (`uv run`, `poetry run`, `python -m`, etc.)

**Run order:**

1. **Lint**: e.g., `uv run ruff check`
2. **Format**: e.g., `uv run ruff format --check`
3. **Type checks**: e.g., `uv run pyright` (full repo)
4. **Tests**: e.g., `uv run pytest` (confirm with user if full suite is slow)

**Important:** Run checks on the **full repo**, not just changed files. Partial checks
have repeatedly missed errors that CI catches. The only exception is known pre-existing
errors from unrelated packages (e.g., optional dependencies not installed) — filter
those from the output.

Fix any failures iteratively:

- For each failure, fix the issue and re-run that specific check
- After all individual checks pass, do a final full run to confirm no regressions

### 7. Report

Summarize results:

```markdown
## Fix Summary

### Addressed
- [x] file.py:42 — Description of fix
- [x] file.py:100 — Description of fix

### Deferred (with TODO)
- [ ] file.py:200 — Reason for deferral (TODO added)

### CI Status
- Lint: PASS
- Type checks: PASS
- Tests: PASS (N passed, M skipped)
```

## Important Notes

- **Present before fixing**: Always show the user proposed fixes before implementing. This prevents wasted effort on misunderstood comments.
- **Read full threads**: Don't just look at the original comment — read replies to understand the full context and resolution status.
- **Full CI, not partial**: Run checks on the full repo to match what CI does. Partial checks have missed errors that CI catches.
- **No chain propagation**: This skill fixes a single PR's branch. Use the `rebase-chain` skill separately to propagate changes through a branch chain.
- **Don't over-fix**: Only fix what's in scope for this PR. Don't refactor nearby code or fix pre-existing issues unless they're blocking CI.
