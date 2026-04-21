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


@mcp.tool()
def comet_metric_history(
    experiment_key: str,
    metric_name: str,
    limit: int | None = 500,
) -> dict:
    """Return the step-by-step trajectory (step -> value) of a metric.

    Unlike `comet_metrics`, which only returns the final value, this returns
    points across the run. Useful for diagnosing training dynamics such as
    the overfit-onset epoch (e.g., train_loss vs val_loss over steps).

    Long runs can log tens of thousands of points, which easily exceeds
    MCP token limits. By default this uniformly subsamples to at most
    `limit` points (first and last always preserved). The response
    includes `total_points` and `stride` so the caller knows what was
    dropped. Pass `limit=null` to get every point.

    Args:
        experiment_key: Comet experiment key.
        metric_name: Metric name (e.g., "train_loss", "val_loss").
        limit: Max points to return. Defaults to 500. Pass null for every
            point.
    """
    return api.get_metric_history(experiment_key, metric_name, limit=limit)


@mcp.tool()
def comet_params(experiment_key: str) -> dict:
    """Return the hyperparameters logged for an experiment.

    Useful for verifying what config a run actually used (as opposed to
    what the code said) — e.g. isolating the effect of a single HP change.

    Args:
        experiment_key: Comet experiment key.
    """
    return api.get_params(experiment_key)


@mcp.tool()
def comet_assets(experiment_key: str, asset_type: str = "all") -> dict:
    """List assets logged to an experiment (plots, images, artifacts).

    Args:
        experiment_key: Comet experiment key.
        asset_type: Filter by Comet asset type. Defaults to "all". Common
            values include "image", "model-element", "notebook", "source_code".
    """
    return api.list_assets(experiment_key, asset_type=asset_type)


@mcp.tool()
def comet_download_asset(
    experiment_key: str,
    asset_name: str,
    output_dir: str | None = None,
) -> dict:
    """Download an asset from an experiment to the local filesystem.

    Returns the absolute path on disk so the file can then be opened/read
    (e.g., viewing a reliability_diagram.png as an image).

    For safety, `output_dir` must resolve under `/tmp`; any other path
    raises ValueError.

    Args:
        experiment_key: Comet experiment key.
        asset_name: Filename of the asset as shown in `comet_assets`
            (e.g., "reliability_diagram.png").
        output_dir: Directory to write the file into. Must be under `/tmp`.
            Defaults to `/tmp/comet_assets/<experiment_key>/`.
    """
    return api.download_asset(experiment_key, asset_name, output_dir=output_dir)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
