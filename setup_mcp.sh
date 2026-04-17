#!/bin/bash
# Idempotent setup for MCP servers in this repo.
#
# For each server in mcp/<name>/:
#   1. Installs its Python dependencies via `uv sync`
#   2. Registers it with Claude Code at user scope
#   3. Allows mcp__<name> in ~/.claude/settings.json so tools from the server
#      are preapproved in every session
#
# Safe to re-run: each step is skipped if already done (use --force to
# re-register the MCP server; permissions are always re-checked).

set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
    FORCE=1
fi

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="$HOME/.claude/settings.json"

if ! command -v claude >/dev/null 2>&1; then
    echo "Error: 'claude' CLI not found on PATH. Install Claude Code first." >&2
    exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: 'uv' not found on PATH. Install uv first: https://docs.astral.sh/uv/" >&2
    exit 1
fi

grant_mcp_permission() {
    local name="$1"
    local perm="mcp__$name"

    if ! command -v jq >/dev/null 2>&1; then
        echo "  Warning: 'jq' not found; skipping permission auto-grant." >&2
        echo "  Add '\"$perm\"' to .permissions.allow in $SETTINGS_FILE manually." >&2
        return 0
    fi

    if [[ ! -f "$SETTINGS_FILE" ]]; then
        echo "  Creating $SETTINGS_FILE with initial permissions."
        mkdir -p "$(dirname "$SETTINGS_FILE")"
        echo '{"permissions":{"allow":[]}}' > "$SETTINGS_FILE"
    fi

    if ! jq empty "$SETTINGS_FILE" 2>/dev/null; then
        echo "  Error: $SETTINGS_FILE is not valid JSON, refusing to modify." >&2
        return 1
    fi

    if jq -e --arg perm "$perm" \
        '(.permissions.allow // []) | index($perm)' \
        "$SETTINGS_FILE" >/dev/null; then
        echo "  Permission '$perm' already allowed."
        return 0
    fi

    local backup
    backup="$SETTINGS_FILE.bak.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$backup"

    local tmp
    tmp=$(mktemp)
    jq --arg perm "$perm" \
        '.permissions.allow = ((.permissions.allow // []) + [$perm])' \
        "$SETTINGS_FILE" > "$tmp"

    if ! jq empty "$tmp" 2>/dev/null; then
        echo "  Error: generated invalid JSON; keeping original (backup at $backup)." >&2
        rm -f "$tmp"
        return 1
    fi

    mv "$tmp" "$SETTINGS_FILE"
    echo "  Permission granted: '$perm' (backup: $backup)"
}

register_server() {
    # Usage: register_server <name> <project_dir> <entrypoint> [env_var_name...]
    #
    # Any trailing args are treated as names of env vars to forward into the
    # MCP server's runtime environment at registration time (via
    # `claude mcp add --env KEY=VALUE`). Vars unset at setup time are
    # silently skipped — the MCP server will error cleanly at call time if
    # they're actually needed.
    local name="$1"
    local project_dir="$2"
    local entrypoint="$3"
    shift 3

    local env_args=()
    local var_name
    for var_name in "$@"; do
        local value="${!var_name:-}"
        if [[ -n "$value" ]]; then
            env_args+=("--env" "${var_name}=${value}")
        else
            echo "  Note: \$${var_name} is not set; skipping --env passthrough for '$name'."
        fi
    done

    if claude mcp get "$name" >/dev/null 2>&1; then
        if [[ "$FORCE" -eq 1 ]]; then
            echo "Re-registering MCP server '$name' (--force)"
            claude mcp remove "$name" >/dev/null 2>&1 || true
        else
            echo "MCP server '$name' already registered, skipping (use --force to re-register)"
            grant_mcp_permission "$name"
            return 0
        fi
    fi

    echo "Installing dependencies for '$name'..."
    (cd "$project_dir" && uv sync --quiet)

    echo "Registering MCP server '$name' at user scope..."
    if [[ ${#env_args[@]} -gt 0 ]]; then
        claude mcp add --scope user "$name" "${env_args[@]}" -- \
            uv run --project "$project_dir" "$entrypoint"
    else
        claude mcp add --scope user "$name" -- \
            uv run --project "$project_dir" "$entrypoint"
    fi
    echo "  Registered: $name -> $project_dir"

    grant_mcp_permission "$name"
}

echo "Setting up MCP servers from $DOTFILES_DIR/mcp/"
echo ""

register_server "ghpr" "$DOTFILES_DIR/mcp/ghpr" "ghpr-mcp"
register_server "bk" "$DOTFILES_DIR/mcp/bk" "bk-mcp" BK_PIPELINE BK_ORG
register_server "comet" "$DOTFILES_DIR/mcp/comet" "comet-mcp" COMET_WORKSPACE

echo ""
echo "Done. Verify with: claude mcp list"
