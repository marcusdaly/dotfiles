"""MCP server exposing GitHub PR helpers as typed tools.

Shells out to the `gh` CLI for data access so that existing `gh auth` state
works with no extra configuration. Returns structured data (not prose) so
Claude can filter and reason about it without parsing log output.

Every tool accepts an optional `repo` argument in `owner/name` form. When
omitted, `gh` falls back to the repo associated with the current directory.
"""

import json
import subprocess
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ghpr")


class GhError(RuntimeError):
    """Raised when the `gh` CLI returns a non-zero exit status."""


def _run_gh(args: list[str]) -> str:
    """Run `gh <args>` and return stdout, raising on non-zero exit."""
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GhError(
            f"gh {' '.join(args)} exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def _gh_json(args: list[str]) -> object:
    """Run `gh <args>` expecting JSON stdout; parse and return."""
    return json.loads(_run_gh(args))


def _pr_view_args(pr: int, repo: str | None, json_fields: str) -> list[str]:
    """Build args for `gh pr view`, including optional --repo override."""
    args = ["pr", "view", str(pr)]
    if repo:
        args.extend(["--repo", repo])
    args.extend(["--json", json_fields])
    return args


def _api_repo_prefix(repo: str | None) -> str:
    """Return the `repos/<owner>/<repo>` prefix for `gh api` calls.

    When `repo` is None, uses gh's placeholder syntax so the current repo is
    resolved from the working directory.
    """
    return f"repos/{repo}" if repo else "repos/{owner}/{repo}"


@mcp.tool()
def ghpr_list(
    state: Literal["open", "closed", "merged", "all"] = "open",
    head: str | None = None,
    base: str | None = None,
    author: str | None = None,
    label: str | None = None,
    search: str | None = None,
    limit: int = 20,
    repo: str | None = None,
) -> list[dict]:
    """List pull requests, optionally filtered by state, branch, author, or label.

    Args:
        state: PR state filter. Defaults to "open".
        head: Filter by head (source) branch name.
        base: Filter by base (target) branch name.
        author: Filter by author username.
        label: Filter by label name.
        search: Free-text search query (GitHub search syntax).
        limit: Maximum number of PRs to return (default 20, max 100).
        repo: Optional `owner/name` to target a specific repo.
    """
    args = ["pr", "list", "--state", state, "--limit", str(min(limit, 100))]
    if head:
        args.extend(["--head", head])
    if base:
        args.extend(["--base", base])
    if author:
        args.extend(["--author", author])
    if label:
        args.extend(["--label", label])
    if search:
        args.extend(["--search", search])
    if repo:
        args.extend(["--repo", repo])
    args.extend(
        [
            "--json",
            "number,title,state,baseRefName,headRefName,author,url,isDraft,createdAt,updatedAt,labels",
        ]
    )
    return _gh_json(args)  # type: ignore[return-value]


@mcp.tool()
def ghpr_info(pr: int, repo: str | None = None) -> dict:
    """Return title, state, base/head branches, author, URL, and body for a PR.

    Args:
        pr: The pull request number.
        repo: Optional `owner/name` to target a specific repo. Defaults to
            the repo of the current working directory.
    """
    fields = "number,title,state,baseRefName,headRefName,author,url,body,isDraft"
    return _gh_json(_pr_view_args(pr, repo, fields))  # type: ignore[return-value]


@mcp.tool()
def ghpr_comments(
    pr: int,
    kind: Literal["all", "inline", "review", "general"] = "all",
    repo: str | None = None,
) -> list[dict]:
    """Return comments on a PR, optionally filtered by kind.

    `inline` = line-level review comments. `review` = review summaries with a
    non-empty body. `general` = issue-thread comments (not tied to lines).
    `all` (default) returns every kind in a single list tagged with `kind`.

    Args:
        pr: The pull request number.
        kind: Which category of comments to return.
        repo: Optional `owner/name` to target a specific repo.
    """
    prefix = _api_repo_prefix(repo)
    collected: list[dict] = []

    if kind in ("all", "inline"):
        inline = _gh_json(["api", f"{prefix}/pulls/{pr}/comments"])
        assert isinstance(inline, list)
        for comment in inline:
            collected.append(
                {
                    "kind": "inline",
                    "id": comment["id"],
                    "author": comment["user"]["login"],
                    "path": comment["path"],
                    "line": comment.get("line") or comment.get("original_line"),
                    "body": comment["body"],
                }
            )

    if kind in ("all", "review"):
        reviews = _gh_json(["api", f"{prefix}/pulls/{pr}/reviews"])
        assert isinstance(reviews, list)
        for review in reviews:
            if not review.get("body"):
                continue
            collected.append(
                {
                    "kind": "review",
                    "id": review["id"],
                    "author": review["user"]["login"],
                    "state": review.get("state"),
                    "body": review["body"],
                }
            )

    if kind in ("all", "general"):
        issues = _gh_json(["api", f"{prefix}/issues/{pr}/comments"])
        assert isinstance(issues, list)
        for comment in issues:
            collected.append(
                {
                    "kind": "general",
                    "id": comment["id"],
                    "author": comment["user"]["login"],
                    "body": comment["body"],
                }
            )

    return collected


@mcp.tool()
def ghpr_diff(pr: int, repo: str | None = None) -> str:
    """Return the unified diff for a PR as a single string.

    Args:
        pr: The pull request number.
        repo: Optional `owner/name` to target a specific repo.
    """
    args = ["pr", "diff", str(pr)]
    if repo:
        args.extend(["--repo", repo])
    return _run_gh(args)


@mcp.tool()
def ghpr_files(pr: int, repo: str | None = None) -> list[dict]:
    """Return the list of files changed in a PR with per-file stats.

    Args:
        pr: The pull request number.
        repo: Optional `owner/name` to target a specific repo.
    """
    result = _gh_json(_pr_view_args(pr, repo, "files"))
    assert isinstance(result, dict)
    return result.get("files", [])


@mcp.tool()
def ghpr_checks(pr: int, repo: str | None = None) -> list[dict]:
    """Return CI check status for a PR.

    Args:
        pr: The pull request number.
        repo: Optional `owner/name` to target a specific repo.
    """
    result = _gh_json(_pr_view_args(pr, repo, "statusCheckRollup"))
    assert isinstance(result, dict)
    return result.get("statusCheckRollup", [])


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
