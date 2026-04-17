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
- `$BK_PIPELINE` and `$BK_ORG` provide the session defaults. Every tool and
  the `bk` shell function accept per-call overrides.

## Preferred interface: the `bk` MCP server

Prefer the **`bk` MCP tools** (registered via `setup_mcp.sh`) over shelling
out. They return structured data, so you can inspect state without parsing
log output:

- `bk_status(build, pipeline?, org?)` — build state, commit, branch, job counts
- `bk_builds(branch, count=5, pipeline?, org?)` — recent builds for a branch
- `bk_pr_build(pr, pipeline?, org?)` — latest build for a PR's head branch
- `bk_job_log(build, job_match, pipeline?, org?)` — single job's log
- `bk_failures(build, tail_lines=80, pipeline?, org?)` — tail logs for every
  failed job

Override pipeline/org per-call via the `pipeline`/`org` arguments. Buildkite
log timestamp prefixes (`_bk;t=<n>`) are stripped automatically.

## Shell fallback

If the MCP server isn't available, use the `bk` shell function (loaded by
`~/dotfiles/shell_setup_base`):

```bash
bk pr <PR_NUMBER>                                        # Latest build for a PR
bk status <BUILD_NUMBER>                                 # Build state + jobs
bk failures <BUILD_NUMBER>                               # Tail logs for failures
bk log <BUILD_NUMBER> "run tests"                        # Specific job log
bk builds main --pipeline ml-inference-handler-containers  # Non-default pipeline
```

## Workflow

### 1. Identify the build

If given a PR number, find the latest build via `bk_pr_build` (or
`bk pr <number>`). If given a build number, start with `bk_status`.

### 2. Extract failures

For any build with failures, call `bk_failures(build)` to get tail logs for
every failed job. For a specific job type, use `bk_job_log(build, job_match)`.

### 3. Scan log output

Scan the returned log text for failure indicators:

```text
FAILED | ERROR | error: | assert | Exception
```

### 4. Report findings

Present a summary of:

- Which checks passed / failed / are running
- For each failure: the specific error message and file/line
- Whether the failure is from our changes or pre-existing (check if the same
  test fails on main or the parent branch via `bk_builds`)

### 5. Check multiple PRs at once

Call `bk_pr_build` for each PR number in the chain and compare.
