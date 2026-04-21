# comet-mcp

MCP server exposing Comet ML experiment queries as typed tools. Thin wrapper
over the `comet_check.api` library in `~/dotfiles/scripts/comet/`.

## Tools

| Tool | Purpose |
| ---- | ------- |
| `comet_projects` | List project names in a workspace (useful for discovery) |
| `comet_list` | Recent experiments in a project (with latest train_loss) |
| `comet_metrics` | Latest value for each requested metric |
| `comet_metric_history` | Full step-by-step trajectory of a metric (for plotting / overfit diagnosis) |
| `comet_params` | Hyperparameters logged to an experiment |
| `comet_compare` | Side-by-side metric comparison of two experiments |
| `comet_text` | Recent logged text entries (e.g., qualitative generations) |
| `comet_assets` | List assets (plots, images, artifacts) on an experiment |
| `comet_download_asset` | Download an asset to the local filesystem (restricted to `/tmp`) |
| `comet_url` | Comet UI URL for an experiment |

`comet_list` takes an optional `workspace` argument. When omitted, it falls
back to `$COMET_WORKSPACE`; if neither is set, the tool raises a clear error.

## Prerequisites

- `$COMET_API_KEY` and `$COMET_WORKSPACE` in the environment (loaded from
  `~/.secrets.env`)
- [uv](https://docs.astral.sh/uv/) and the `claude` CLI

## Setup

From the dotfiles repo root:

```bash
./setup_mcp.sh
```

Idempotent: installs deps, registers the server with Claude Code at user
scope, and adds `mcp__comet` to `~/.claude/settings.json` permissions.

## Notes

- The `comet` CLI alias (defined in `~/dotfiles/zsh_config/.zshrc`) remains
  for manual terminal use. The MCP server is preferred for Claude sessions.
- Both this server and the CLI share the same `comet_check.api` library, so
  behavior stays consistent across interfaces.
