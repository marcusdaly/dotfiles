"""MCP server exposing Comet ML experiment queries as typed tools.

Thin wrapper over `comet_check.api` (from ~/dotfiles/scripts/comet/). The
library functions do the real work; this module just registers them as MCP
tools with typed signatures.
"""

from mcp.server.fastmcp import FastMCP

from comet_check import api

mcp = FastMCP("comet")


@mcp.tool()
def comet_projects(workspace: str | None = None) -> list[str]:
    """List project names in a Comet workspace.

    Args:
        workspace: Optional workspace; defaults to $COMET_WORKSPACE.
    """
    return api.list_projects(workspace=workspace)


@mcp.tool()
def comet_list(
    project: str,
    workspace: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """List the most recent experiments in a Comet project.

    Args:
        project: Comet project name.
        workspace: Optional workspace; defaults to $COMET_WORKSPACE.
        limit: Max experiments to return (newest first).
    """
    return api.list_experiments(project, workspace=workspace, limit=limit)


@mcp.tool()
def comet_metrics(
    experiment_key: str,
    metric_names: list[str] | None = None,
) -> dict:
    """Return the latest value for each requested metric on an experiment.

    Args:
        experiment_key: Comet experiment key.
        metric_names: Metric names to fetch. If omitted, uses a default set
            (train_loss, learning_rate, samples_trained).
    """
    return api.get_metrics(experiment_key, metric_names)


@mcp.tool()
def comet_compare(
    key1: str,
    key2: str,
    metric: str = "train_loss",
) -> list[dict]:
    """Compare a metric between two experiments.

    Args:
        key1: First experiment key.
        key2: Second experiment key.
        metric: Metric name to compare (default train_loss).
    """
    return api.compare_experiments(key1, key2, metric=metric)


@mcp.tool()
def comet_text(experiment_key: str, limit: int = 3) -> list[dict]:
    """Return recent logged text entries for an experiment (e.g., generations).

    Args:
        experiment_key: Comet experiment key.
        limit: Max entries to return (most recent last).
    """
    return api.get_text(experiment_key, limit=limit)


@mcp.tool()
def comet_url(experiment_key: str) -> str:
    """Return the Comet UI URL for an experiment.

    Args:
        experiment_key: Comet experiment key.
    """
    return api.get_url(experiment_key)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
