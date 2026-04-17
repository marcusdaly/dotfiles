"""MCP server exposing Buildkite CI helpers as typed tools.

Uses the Buildkite REST API directly (via `requests`) and falls back to the
`gh` CLI to resolve PR numbers to branches. Returns structured data so Claude
can filter and reason about build state without parsing log output.

Pipeline/org resolution (highest precedence first):
  1. Explicit `pipeline=` / `org=` tool arguments.
  2. `$BK_PIPELINE` / `$BK_ORG` environment variables.
  Tools raise a clear error if neither source yields a value.
"""

import os
import re
import subprocess
from pathlib import Path

import requests
from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bk")

_BK_TOKEN_ENV = "BUILDKITE_API_TOKEN"
_BK_API_ROOT = "https://api.buildkite.com/v2"
_LOG_TIMESTAMP_PATTERN = re.compile(r"_bk;t=\d+")


class BkConfigError(RuntimeError):
    """Raised when required config (token, pipeline, org) is missing."""


class BkApiError(RuntimeError):
    """Raised when the Buildkite API returns a non-success response."""


def _from_secrets_env(var_name: str) -> str | None:
    """Fetch a single var from ~/.secrets.env without polluting os.environ."""
    secrets_path = Path.home() / ".secrets.env"
    if not secrets_path.exists():
        return None
    return dotenv_values(secrets_path).get(var_name)


def _token() -> str:
    token = os.environ.get(_BK_TOKEN_ENV) or _from_secrets_env(_BK_TOKEN_ENV)
    if not token:
        raise BkConfigError(
            f"${_BK_TOKEN_ENV} is not set and was not found in ~/.secrets.env."
        )
    return token


def _resolve(pipeline: str | None, org: str | None) -> tuple[str, str]:
    """Resolve pipeline/org from args, then env, erroring if neither is set."""
    effective_pipeline = pipeline or os.environ.get("BK_PIPELINE")
    effective_org = org or os.environ.get("BK_ORG")
    if not effective_pipeline:
        raise BkConfigError(
            "No pipeline set. Pass pipeline=... or export BK_PIPELINE."
        )
    if not effective_org:
        raise BkConfigError("No org set. Pass org=... or export BK_ORG.")
    return effective_pipeline, effective_org


def _pipeline_url(pipeline: str, org: str) -> str:
    return f"{_BK_API_ROOT}/organizations/{org}/pipelines/{pipeline}"


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_token()}"}


def _bk_get(path: str, params: dict | None = None) -> requests.Response:
    response = requests.get(path, headers=_headers(), params=params, timeout=30)
    if not response.ok:
        raise BkApiError(
            f"Buildkite API {response.request.method} {path} -> "
            f"{response.status_code}: {response.text[:300]}"
        )
    return response


def _summarize_build(build: dict) -> dict:
    return {
        "number": build["number"],
        "state": build["state"],
        "commit": (build.get("commit") or "")[:10],
        "branch": build.get("branch"),
        "created_at": build.get("created_at"),
        "passed_count": sum(
            1 for job in build.get("jobs", []) if job.get("state") == "passed"
        ),
        "failed": [
            job["name"]
            for job in build.get("jobs", [])
            if job.get("state") == "failed" and job.get("name")
        ],
        "running": [
            job["name"]
            for job in build.get("jobs", [])
            if job.get("state") == "running" and job.get("name")
        ],
    }


def _strip_timestamps(log: str) -> str:
    return _LOG_TIMESTAMP_PATTERN.sub("", log)


@mcp.tool()
def bk_status(
    build: int, pipeline: str | None = None, org: str | None = None
) -> dict:
    """Summarize a Buildkite build (state, commit, branch, job counts).

    Args:
        build: Build number.
        pipeline: Optional pipeline slug; defaults to $BK_PIPELINE.
        org: Optional organization slug; defaults to $BK_ORG.
    """
    effective_pipeline, effective_org = _resolve(pipeline, org)
    url = f"{_pipeline_url(effective_pipeline, effective_org)}/builds/{build}"
    return _summarize_build(_bk_get(url).json())


@mcp.tool()
def bk_builds(
    branch: str,
    count: int = 5,
    pipeline: str | None = None,
    org: str | None = None,
) -> list[dict]:
    """List recent Buildkite builds for a branch.

    Args:
        branch: Git branch name.
        count: Number of recent builds to return (default 5).
        pipeline: Optional pipeline slug; defaults to $BK_PIPELINE.
        org: Optional organization slug; defaults to $BK_ORG.
    """
    effective_pipeline, effective_org = _resolve(pipeline, org)
    url = f"{_pipeline_url(effective_pipeline, effective_org)}/builds"
    response = _bk_get(url, params={"branch": branch, "per_page": count})
    return [
        {
            "number": build["number"],
            "state": build["state"],
            "commit": (build.get("commit") or "")[:10],
            "created_at": (build.get("created_at") or "")[:19],
        }
        for build in response.json()
    ]


@mcp.tool()
def bk_pr_build(
    pr: int,
    repo: str | None = None,
    pipeline: str | None = None,
    org: str | None = None,
) -> dict:
    """Summarize the most recent Buildkite build for a PR's head branch.

    Uses the `gh` CLI to resolve the PR number to its head branch, then
    queries Buildkite for builds on that branch.

    Args:
        pr: GitHub pull request number.
        repo: Optional GitHub repo in `owner/name` form. When omitted, `gh`
            uses the repo of the current working directory.
        pipeline: Optional Buildkite pipeline slug; defaults to $BK_PIPELINE.
        org: Optional Buildkite organization slug; defaults to $BK_ORG.
    """
    effective_pipeline, effective_org = _resolve(pipeline, org)
    gh_args = ["gh", "pr", "view", str(pr)]
    if repo:
        gh_args.extend(["--repo", repo])
    gh_args.extend(["--json", "headRefName", "-q", ".headRefName"])
    result = subprocess.run(
        gh_args,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            f"Could not resolve PR #{pr} to a branch: {result.stderr.strip()}"
        )
    branch = result.stdout.strip()
    url = f"{_pipeline_url(effective_pipeline, effective_org)}/builds"
    response = _bk_get(url, params={"branch": branch, "per_page": 1})
    builds = response.json()
    if not builds:
        return {"branch": branch, "build": None}
    return {"branch": branch, "build": _summarize_build(builds[0])}


@mcp.tool()
def bk_job_log(
    build: int,
    job_match: str,
    pipeline: str | None = None,
    org: str | None = None,
) -> dict:
    """Fetch the log for a single job, matched by case-insensitive substring.

    Args:
        build: Build number.
        job_match: Substring to match against job names (case-insensitive).
        pipeline: Optional pipeline slug; defaults to $BK_PIPELINE.
        org: Optional organization slug; defaults to $BK_ORG.
    """
    effective_pipeline, effective_org = _resolve(pipeline, org)
    pipeline_url = _pipeline_url(effective_pipeline, effective_org)
    build_response = _bk_get(f"{pipeline_url}/builds/{build}")
    needle = job_match.lower()
    matched_job = next(
        (
            job
            for job in build_response.json().get("jobs", [])
            if job.get("name") and needle in job["name"].lower()
        ),
        None,
    )
    if matched_job is None:
        available = [
            job["name"]
            for job in build_response.json().get("jobs", [])
            if job.get("name")
        ]
        raise RuntimeError(
            f"No job matching '{job_match}' in build {build}. "
            f"Available: {available}"
        )
    log_url = f"{pipeline_url}/builds/{build}/jobs/{matched_job['id']}/log.txt"
    log_response = _bk_get(log_url)
    return {
        "job_id": matched_job["id"],
        "job_name": matched_job["name"],
        "log": _strip_timestamps(log_response.text),
    }


@mcp.tool()
def bk_failures(
    build: int,
    tail_lines: int = 80,
    pipeline: str | None = None,
    org: str | None = None,
) -> list[dict]:
    """Return tail logs for every failed job in a build.

    Args:
        build: Build number.
        tail_lines: How many trailing log lines to return per failed job.
        pipeline: Optional pipeline slug; defaults to $BK_PIPELINE.
        org: Optional organization slug; defaults to $BK_ORG.
    """
    effective_pipeline, effective_org = _resolve(pipeline, org)
    pipeline_url = _pipeline_url(effective_pipeline, effective_org)
    build_response = _bk_get(f"{pipeline_url}/builds/{build}")
    failed_jobs = [
        job
        for job in build_response.json().get("jobs", [])
        if job.get("state") == "failed"
    ]
    results: list[dict] = []
    for job in failed_jobs:
        log_response = _bk_get(
            f"{pipeline_url}/builds/{build}/jobs/{job['id']}/log.txt"
        )
        log_text = _strip_timestamps(log_response.text)
        tail = "\n".join(log_text.splitlines()[-tail_lines:])
        results.append(
            {
                "job_id": job["id"],
                "job_name": job.get("name"),
                "tail_log": tail,
            }
        )
    return results


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
