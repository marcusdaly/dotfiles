---
description: Check Buildkite CI status and extract failure details for PRs or builds. Use when CI is failing and you need to diagnose the issue.
model: haiku
argument-hint: "[PR number or build number]"
---

# Buildkite CI Diagnostics

Check CI build status and extract failure details from Buildkite.

## Prerequisites

- `BUILDKITE_API_TOKEN` is available in the environment (loaded from
  `~/.secrets.env` via the shell profile).
- The `bk` shell function is loaded by `~/dotfiles/shell_setup_base` — call
  it directly, no sourcing needed.
- `$BK_PIPELINE` and `$BK_ORG` provide the session defaults. Override on any
  call with `--pipeline X` / `--org Y`.

## Workflow

### 1. Identify the build

If given a PR number, find the latest build:

```bash
bk pr <PR_NUMBER>
```

If given a build number directly, check its status:

```bash
bk status <BUILD_NUMBER>
```

### 2. Extract failures

For any build with failures, get the logs:

```bash
bk failures <BUILD_NUMBER>
```

Or for a specific job type:

```bash
bk log <BUILD_NUMBER> "run tests"
bk log <BUILD_NUMBER> "lint"
bk log <BUILD_NUMBER> "type"
```

### 3. Parse the output

Buildkite logs have `_bk;t=<timestamp>` prefixes on each line. Strip them and look
for failure indicators:

```bash
# Strip Buildkite prefixes and find failures
... | sed 's/^_bk;t=[0-9]*//' | grep -E "FAILED|ERROR|error:|assert|Exception"
```

### 4. Report findings

Present a summary of:

- Which checks passed/failed/are running
- For each failure: the specific error message and file/line
- Whether the failure is from our changes or pre-existing (check if the same test
  fails on main or the parent branch)

### 5. Check multiple PRs at once

To scan all PRs in a chain:

```bash
for pr in <PR_NUMBERS>; do
    echo "=== PR #$pr ==="
    bk pr $pr
    echo ""
done
```

### 6. Use a non-default pipeline

Override pipeline and/or org per call with flags:

```bash
bk builds main --pipeline ml-inference-handler-containers
bk failures 880 --pipeline ml-inference-handler-containers
```
