# ghpr-mcp

MCP server exposing GitHub PR helpers as typed tools. Shells out to the `gh`
CLI so it inherits your existing `gh auth` state.

## Tools

| Tool | Purpose |
| ------ | --------- |
| `ghpr_list` | List PRs filtered by state, branch, author, label, or search query |
| `ghpr_info` | Title, state, base/head, author, URL, body |
| `ghpr_comments` | All comments, filterable by kind (`inline` / `review` / `general` / `all`) |
| `ghpr_diff` | Unified diff as a string |
| `ghpr_files` | Changed files with per-file stats |
| `ghpr_checks` | CI check rollup |

Most tools take `pr: int` and an optional `repo: str` in `owner/name` form.
When `repo` is omitted, `gh` uses the repo of the current working directory.
`ghpr_list` takes optional filters (`state`, `head`, `base`, `author`, `label`,
`search`, `limit`) instead of a PR number. `ghpr_comments` also takes an
optional `kind` filter.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python env management
- [`gh`](https://cli.github.com/) CLI, authenticated (`gh auth status` should succeed)
- [Claude Code](https://claude.com/claude-code) CLI on PATH

## Setup

From the repo root:

```bash
./setup_mcp.sh
```

This is idempotent: it installs dependencies via `uv sync` and registers the
server with Claude Code at user scope. Re-run with `--force` to re-register.

## Manual registration

If you'd rather not use the setup script:

```bash
cd ~/dotfiles/mcp/ghpr && uv sync
claude mcp add --scope user ghpr -- \
  uv run --project ~/dotfiles/mcp/ghpr ghpr-mcp
```

Verify with `claude mcp list` — you should see `ghpr: ... - ✓ Connected`.

## Notes

- The server inherits the current working directory, so `gh` picks up the repo
  you have active. For cross-repo calls, `cd` first or set `gh repo set-default`.
- The shell function `ghpr` in `scripts/ghpr.sh` remains available for manual
  terminal use. The MCP server is the preferred interface for Claude sessions.
