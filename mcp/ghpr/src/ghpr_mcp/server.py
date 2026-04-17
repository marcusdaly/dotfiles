"""MCP server exposing GitHub PR helpers as typed tools.

Shells out to the `gh` CLI for data access so that existing `gh auth` state
works with no extra configuration. Returns structured data (not prose) so
Claude can filter and reason about it without parsing log output.
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


@mcp.tool()
def ghpr_info(pr: int) -> dict:
    """Return title, state, base/head branches, author, URL, and body for a PR.

    Args:
        pr: The pull request number.
    """
    fields = "number,title,state,baseRefName,headRefName,author,url,body,isDraft"
    return _gh_json(["pr", "view", str(pr), "--json", fields])  # type: ignore[return-value]


@mcp.tool()
def ghpr_comments(
    pr: int,
    kind: Literal["all", "inline", "review", "general"] = "all",
) -> list[dict]:
    """Return comments on a PR, optionally filtered by kind.

    `inline` = line-level review comments. `review` = review summaries with a
    non-empty body. `general` = issue-thread comments (not tied to lines).
    `all` (default) returns every kind in a single list tagged with `kind`.

    Args:
        pr: The pull request number.
        kind: Which category of comments to return.
    """
    repo_ref = "repos/{owner}/{repo}"
    collected: list[dict] = []

    if kind in ("all", "inline"):
        inline = _gh_json(["api", f"{repo_ref}/pulls/{pr}/comments"])
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
        reviews = _gh_json(["api", f"{repo_ref}/pulls/{pr}/reviews"])
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
        issues = _gh_json(["api", f"{repo_ref}/issues/{pr}/comments"])
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
def ghpr_diff(pr: int) -> str:
    """Return the unified diff for a PR as a single string.

    Args:
        pr: The pull request number.
    """
    return _run_gh(["pr", "diff", str(pr)])


@mcp.tool()
def ghpr_files(pr: int) -> list[dict]:
    """Return the list of files changed in a PR with per-file stats.

    Args:
        pr: The pull request number.
    """
    result = _gh_json(["pr", "view", str(pr), "--json", "files"])
    assert isinstance(result, dict)
    return result.get("files", [])


@mcp.tool()
def ghpr_checks(pr: int) -> list[dict]:
    """Return CI check status for a PR.

    Args:
        pr: The pull request number.
    """
    result = _gh_json(
        ["pr", "view", str(pr), "--json", "statusCheckRollup"]
    )
    assert isinstance(result, dict)
    return result.get("statusCheckRollup", [])


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
