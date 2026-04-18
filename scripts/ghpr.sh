#!/usr/bin/env bash
# ghpr - GitHub PR helper functions
# Source this file from .zshrc, then use: ghpr <command> [args]
#
# Commands:
#   ghpr comments <pr>           Show all comments on a PR (reviews + inline + issue)
#   ghpr diff <pr>               Show the PR diff
#   ghpr files <pr>              List files changed in a PR
#   ghpr info <pr>               Show PR title, state, base, head, and body
#   ghpr checks <pr>             Show CI check status
#   ghpr list [state]            List PRs (default: open)

ghpr() {
    local cmd="${1:-help}"
    shift 2>/dev/null || true

    case "$cmd" in
        comments)
            local pr_number="${1:?Usage: ghpr comments <pr_number>}"
            echo "=== Review comments (inline) ==="
            gh api "repos/{owner}/{repo}/pulls/$pr_number/comments" \
                --jq '.[] | "[\(.user.login)] \(.path):\(.line // .original_line)\n\(.body)\n"'
            echo "=== Review summaries ==="
            gh api "repos/{owner}/{repo}/pulls/$pr_number/reviews" \
                --jq '.[] | select(.body != "") | "[\(.user.login)] (\(.state))\n\(.body)\n"'
            echo "=== General comments ==="
            gh api "repos/{owner}/{repo}/issues/$pr_number/comments" \
                --jq '.[] | "[\(.user.login)]\n\(.body)\n"'
            ;;

        diff)
            local pr_number="${1:?Usage: ghpr diff <pr_number>}"
            gh pr diff "$pr_number"
            ;;

        files)
            local pr_number="${1:?Usage: ghpr files <pr_number>}"
            gh pr view "$pr_number" --json files --jq '.files[].path'
            ;;

        info)
            local pr_number="${1:?Usage: ghpr info <pr_number>}"
            gh pr view "$pr_number" --json title,state,baseRefName,headRefName,body \
                --jq '"Title: \(.title)\nState: \(.state)\nBase: \(.baseRefName)\nHead: \(.headRefName)\n\n\(.body)"'
            ;;

        checks)
            local pr_number="${1:?Usage: ghpr checks <pr_number>}"
            gh pr checks "$pr_number"
            ;;

        list)
            local state="${1:-open}"
            gh pr list --state "$state"
            ;;

        help|*)
            echo "ghpr - GitHub PR helper"
            echo ""
            echo "Commands:"
            echo "  ghpr comments <pr>    Show all comments (review, inline, general)"
            echo "  ghpr diff <pr>        Show the PR diff"
            echo "  ghpr files <pr>       List changed files"
            echo "  ghpr info <pr>        Show PR metadata and description"
            echo "  ghpr checks <pr>      Show CI check status"
            echo "  ghpr list [state]     List PRs (default: open)"
            ;;
    esac
}
