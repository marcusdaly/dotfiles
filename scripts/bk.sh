#!/usr/bin/env bash
# bk - Buildkite CLI wrapper
# Source this file from .zshrc, then use: bk <command> [args] [--pipeline X] [--org Y]
#
# Commands:
#   bk status <build>        Show build status and failed/running jobs
#   bk log <build> <job>     Fetch log for a job (name substring match)
#   bk builds <branch> [n]   List recent builds for a branch
#   bk pr <pr_number>        Show latest build for a PR
#   bk failures <build>      Show logs for all failed jobs
#
# Pipeline/org resolution (highest precedence first):
#   1. --pipeline X / --org Y flags
#   2. $BK_PIPELINE / $BK_ORG env vars
#   If neither is set, bk exits with an error.

bk() {
    local pipeline="${BK_PIPELINE:-}"
    local org="${BK_ORG:-}"
    local positional=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pipeline)
                if [[ -z "${2:-}" ]]; then
                    echo "Error: --pipeline requires a value" >&2
                    return 1
                fi
                pipeline="$2"
                shift 2
                ;;
            --org)
                if [[ -z "${2:-}" ]]; then
                    echo "Error: --org requires a value" >&2
                    return 1
                fi
                org="$2"
                shift 2
                ;;
            *)
                positional+=("$1")
                shift
                ;;
        esac
    done

    set -- "${positional[@]}"

    local cmd="${1:-help}"
    shift 2>/dev/null || true

    if [[ "$cmd" != "help" ]]; then
        if [[ -z "$pipeline" ]]; then
            echo "Error: no pipeline set. Use --pipeline X or export BK_PIPELINE." >&2
            return 1
        fi
        if [[ -z "$org" ]]; then
            echo "Error: no org set. Use --org X or export BK_ORG." >&2
            return 1
        fi
    fi

    if [[ -z "${BUILDKITE_API_TOKEN:-}" ]]; then
        if [[ -f ~/.secrets.env ]]; then
            # shellcheck source=/dev/null
            source ~/.secrets.env
        fi
        if [[ -z "${BUILDKITE_API_TOKEN:-}" ]]; then
            echo "Error: BUILDKITE_API_TOKEN not set. Add it to ~/.secrets.env" >&2
            return 1
        fi
    fi

    local auth="Authorization: Bearer $BUILDKITE_API_TOKEN"
    local api="https://api.buildkite.com/v2/organizations/$org/pipelines/$pipeline"

    case "$cmd" in
        status)
            local build_number="${1:?Usage: bk status <build_number>}"
            curl -sH "$auth" "$api/builds/$build_number" | jq '{
                number: .number,
                state: .state,
                commit: .commit[0:10],
                branch: .branch,
                created_at: .created_at,
                passed: [.jobs[] | select(.state == "passed") | .name] | length,
                failed: [.jobs[] | select(.state == "failed") | .name],
                running: [.jobs[] | select(.state == "running") | .name]
            }'
            ;;

        log)
            local build_number="${1:?Usage: bk log <build_number> <job_name_substring>}"
            local job_match="${2:?Usage: bk log <build_number> <job_name_substring>}"
            local job_id
            job_id=$(curl -sH "$auth" "$api/builds/$build_number" \
                | jq -r ".jobs[] | select(.name != null and (.name | ascii_downcase | contains(\"$(echo "$job_match" | tr '[:upper:]' '[:lower:]')\"))) | .id" \
                | head -1)
            if [[ -z "$job_id" ]]; then
                echo "No job matching '$job_match' in build $build_number. Available jobs:" >&2
                curl -sH "$auth" "$api/builds/$build_number" | jq -r '.jobs[] | select(.name != null) | .name'
                return 1
            fi
            curl -sH "$auth" "$api/builds/$build_number/jobs/$job_id/log.txt"
            ;;

        builds)
            local branch="${1:?Usage: bk builds <branch> [count]}"
            local count="${2:-5}"
            curl -sH "$auth" "$api/builds?branch=$branch&per_page=$count" \
                | jq '[.[] | {number, state, commit: .commit[0:10], created_at: .created_at[0:19]}]'
            ;;

        pr)
            local pr_number="${1:?Usage: bk pr <pr_number>}"
            local branch
            branch=$(gh pr view "$pr_number" --json headRefName -q .headRefName 2>/dev/null)
            if [[ -z "$branch" ]]; then
                echo "Could not find branch for PR #$pr_number" >&2
                return 1
            fi
            curl -sH "$auth" "$api/builds?branch=$branch&per_page=1" | jq '.[0] | {
                number: .number,
                state: .state,
                commit: .commit[0:10],
                branch: .branch,
                passed: [.jobs[] | select(.state == "passed") | .name] | length,
                failed: [.jobs[] | select(.state == "failed") | .name],
                running: [.jobs[] | select(.state == "running") | .name]
            }'
            ;;

        failures)
            local build_number="${1:?Usage: bk failures <build_number>}"
            local jobs_json
            jobs_json=$(curl -sH "$auth" "$api/builds/$build_number" \
                | jq -r '.jobs[] | select(.state == "failed") | "\(.id)\t\(.name)"')
            if [[ -z "$jobs_json" ]]; then
                echo "No failed jobs in build $build_number"
                return 0
            fi
            while IFS=$'\t' read -r job_id job_name; do
                echo "=== FAILED: $job_name ==="
                curl -sH "$auth" "$api/builds/$build_number/jobs/$job_id/log.txt" | tail -80
                echo ""
            done <<< "$jobs_json"
            ;;

        help|*)
            echo "bk - Buildkite CLI wrapper"
            echo ""
            echo "Usage: bk <command> [args] [--pipeline X] [--org Y]"
            echo ""
            echo "Commands:"
            echo "  bk status <build>        Show build status and failed/running jobs"
            echo "  bk log <build> <job>     Fetch log for a job (name substring match)"
            echo "  bk builds <branch> [n]   List recent builds for a branch"
            echo "  bk pr <pr_number>        Show latest build for a PR"
            echo "  bk failures <build>      Show logs for all failed jobs"
            echo ""
            echo "Pipeline/org resolution (highest first):"
            echo "  1. --pipeline / --org flags"
            echo "  2. \$BK_PIPELINE / \$BK_ORG env vars"
            ;;
    esac
}
