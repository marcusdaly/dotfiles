#!/bin/bash
# Idempotent setup for MCP servers in this repo.
#
# Registers each server in mcp/<name>/ with Claude Code at user scope so they
# are available globally. Safe to re-run: servers already registered are
# skipped (use --force to re-register).

set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
    FORCE=1
fi

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v claude >/dev/null 2>&1; then
    echo "Error: 'claude' CLI not found on PATH. Install Claude Code first." >&2
    exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: 'uv' not found on PATH. Install uv first: https://docs.astral.sh/uv/" >&2
    exit 1
fi

register_server() {
    local name="$1"
    local project_dir="$2"
    local entrypoint="$3"

    if claude mcp get "$name" >/dev/null 2>&1; then
        if [[ "$FORCE" -eq 1 ]]; then
            echo "Re-registering MCP server '$name' (--force)"
            claude mcp remove "$name" >/dev/null 2>&1 || true
        else
            echo "MCP server '$name' already registered, skipping (use --force to re-register)"
            return 0
        fi
    fi

    echo "Installing dependencies for '$name'..."
    (cd "$project_dir" && uv sync --quiet)

    echo "Registering MCP server '$name' at user scope..."
    claude mcp add --scope user "$name" -- \
        uv run --project "$project_dir" "$entrypoint"
    echo "  Registered: $name -> $project_dir"
}

echo "Setting up MCP servers from $DOTFILES_DIR/mcp/"
echo ""

register_server "ghpr" "$DOTFILES_DIR/mcp/ghpr" "ghpr-mcp"

echo ""
echo "Done. Verify with: claude mcp list"
