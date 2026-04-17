# bk-mcp

MCP server exposing Buildkite CI helpers as typed tools. Uses the Buildkite
REST API directly and falls back to the `gh` CLI to resolve PR numbers to
branches.

## Tools

| Tool | Purpose |
| ---- | ------- |
| `bk_status` | Build state, commit, branch, passed/failed/running job counts |
| `bk_builds` | Recent builds for a branch |
| `bk_pr_build` | Latest build for a PR's head branch |
| `bk_job_log` | Log for a single job, matched by case-insensitive substring |
| `bk_failures` | Tail logs for every failed job in a build |

All tools take optional `pipeline` and `org` arguments. When omitted, they
default to the `$BK_PIPELINE` / `$BK_ORG` environment variables. If neither
is set, the tool raises a clear error.

## Prerequisites

- `$BUILDKITE_API_TOKEN` in the environment (loaded from `~/.secrets.env`)
- `$BK_PIPELINE` and `$BK_ORG` set (or pass as tool arguments)
- `gh` CLI on PATH (only for `bk_pr_build`)
- [uv](https://docs.astral.sh/uv/) and the `claude` CLI

## Setup

From the dotfiles repo root:

```bash
./setup_mcp.sh
```

Idempotent: installs deps, registers the server with Claude Code at user
scope, and adds `mcp__bk` to `~/.claude/settings.json` permissions.

## Notes

- The `bk` shell function in `~/dotfiles/scripts/bk.sh` remains for manual
  terminal use. The MCP server is preferred for Claude sessions — it returns
  structured data instead of shell-formatted output.
- Buildkite log timestamps (`_bk;t=<number>` prefixes) are stripped from log
  output.
