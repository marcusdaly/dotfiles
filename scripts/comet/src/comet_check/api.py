"""Library functions for querying Comet ML experiments.

Each function returns plain dicts/lists so it can be consumed by the CLI or
the MCP server without parsing printed output. Workspace is resolved from
the optional `workspace` arg, falling back to `$COMET_WORKSPACE`.
"""

import os
from pathlib import Path

from comet_ml import API
from dotenv import dotenv_values


class CometConfigError(RuntimeError):
    """Raised when required Comet config (API key, workspace) is missing."""


def _from_secrets_env(var_name: str) -> str | None:
    """Fetch a single var from ~/.secrets.env without polluting os.environ."""
    secrets_path = Path.home() / ".secrets.env"
    if not secrets_path.exists():
        return None
    return dotenv_values(secrets_path).get(var_name)


def _api() -> API:
    api_key = os.environ.get("COMET_API_KEY") or _from_secrets_env("COMET_API_KEY")
    if not api_key:
        raise CometConfigError(
            "$COMET_API_KEY is not set and was not found in ~/.secrets.env."
        )
    return API(api_key=api_key)


def _resolve_workspace(workspace: str | None) -> str:
    effective = (
        workspace
        or os.environ.get("COMET_WORKSPACE")
        or _from_secrets_env("COMET_WORKSPACE")
    )
    if not effective:
        raise CometConfigError(
            "No workspace set. Pass workspace=..., export COMET_WORKSPACE, "
            "or add it to ~/.secrets.env."
        )
    return effective


def list_projects(workspace: str | None = None) -> list[str]:
    """Return project names in a workspace.

    Args:
        workspace: Optional workspace; defaults to $COMET_WORKSPACE.
    """
    api = _api()
    effective_workspace = _resolve_workspace(workspace)
    return api.get_projects(effective_workspace)


def list_experiments(
    project: str,
    workspace: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Return the most recently started experiments for a project.

    Args:
        project: Comet project name.
        workspace: Optional workspace; defaults to $COMET_WORKSPACE.
        limit: Max number of experiments to return (newest first).
    """
    api = _api()
    effective_workspace = _resolve_workspace(workspace)
    experiments = api.get_experiments(effective_workspace, project_name=project)
    sorted_experiments = sorted(
        experiments,
        key=lambda experiment: experiment.start_server_timestamp,
        reverse=True,
    )

    results: list[dict] = []
    for experiment in sorted_experiments[:limit]:
        summary = experiment.get_metrics_summary("train_loss")
        train_loss = (
            float(summary["valueCurrent"]) if summary else None
        )
        results.append(
            {
                "key": experiment.key,
                "name": experiment.name,
                "train_loss": train_loss,
                "state": getattr(experiment, "state", None),
                "url": experiment.url,
            }
        )
    return results


def get_metrics(
    experiment_key: str,
    metric_names: list[str] | None = None,
) -> dict:
    """Return the latest value for each requested metric on an experiment.

    Args:
        experiment_key: Comet experiment key.
        metric_names: List of metric names. If None, uses a small default set.
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)

    effective_names = metric_names or [
        "train_loss",
        "learning_rate",
        "samples_trained",
    ]

    metrics: dict[str, dict] = {}
    for metric_name in effective_names:
        points = experiment.get_metrics(metric_name)
        if points:
            latest = points[-1]
            metrics[metric_name] = {
                "value": float(latest["metricValue"]),
                "step": latest["step"],
            }

    return {
        "key": experiment_key,
        "name": experiment.name,
        "url": experiment.url,
        "metrics": metrics,
    }


def compare_experiments(
    key1: str,
    key2: str,
    metric: str = "train_loss",
) -> list[dict]:
    """Return the current value of `metric` for two experiments side-by-side.

    Args:
        key1: First experiment key.
        key2: Second experiment key.
        metric: Metric name to compare.
    """
    api = _api()
    results: list[dict] = []
    for key in [key1, key2]:
        experiment = api.get_experiment_by_key(key)
        summary = experiment.get_metrics_summary(metric)
        value = float(summary["valueCurrent"]) if summary else None
        results.append(
            {
                "key": key,
                "name": experiment.name,
                "metric": metric,
                "value": value,
            }
        )
    return results


def get_text(experiment_key: str, limit: int = 3) -> list[dict]:
    """Return the most recent logged text entries for an experiment.

    Args:
        experiment_key: Comet experiment key.
        limit: Max number of entries to return (most recent last).
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    text_entries = experiment.get_text() or []
    return [
        {
            "step": entry.get("step"),
            "text": entry.get("text", entry.get("value", "")),
        }
        for entry in text_entries[-limit:]
    ]


def get_url(experiment_key: str) -> str:
    """Return the Comet UI URL for an experiment."""
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    return experiment.url


def get_metric_history(
    experiment_key: str,
    metric_name: str,
) -> dict:
    """Return the full step-by-step trajectory of a metric on an experiment.

    Unlike `get_metrics`, which only returns the final value, this returns
    every logged point. Useful for plotting a metric over steps/epochs (e.g.,
    diagnosing the overfit-onset epoch from train_loss vs val_loss).

    Args:
        experiment_key: Comet experiment key.
        metric_name: Metric name (e.g., "train_loss", "val_loss").

    Returns:
        Dict with experiment identity and a `points` list. Each point has
        `step`, `epoch`, `value`, and `timestamp` (ms since epoch, as
        returned by Comet).
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    raw_points = experiment.get_metrics(metric_name) or []

    points: list[dict] = []
    for point in raw_points:
        points.append(
            {
                "step": point.get("step"),
                "epoch": point.get("epoch"),
                "value": float(point["metricValue"]),
                "timestamp": point.get("timestamp"),
            }
        )

    return {
        "key": experiment_key,
        "name": experiment.name,
        "url": experiment.url,
        "metric": metric_name,
        "points": points,
    }


def get_params(experiment_key: str) -> dict:
    """Return the hyperparameters logged for an experiment.

    Useful for verifying what config a run actually used (as opposed to what
    the code said) — e.g. isolating the effect of a single HP change.

    Args:
        experiment_key: Comet experiment key.

    Returns:
        Dict with experiment identity and a `params` mapping of
        `{name: value}` for every logged parameter. Values are returned as
        strings (Comet stores them that way).
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    summary = experiment.get_parameters_summary() or []

    params: dict[str, str] = {}
    for entry in summary:
        name = entry.get("name")
        if name is None:
            continue
        params[name] = entry.get("valueCurrent", entry.get("valueMax"))

    return {
        "key": experiment_key,
        "name": experiment.name,
        "url": experiment.url,
        "params": params,
    }


def list_assets(
    experiment_key: str,
    asset_type: str = "all",
) -> dict:
    """List assets logged to an experiment (plots, images, artifacts, etc.).

    Args:
        experiment_key: Comet experiment key.
        asset_type: Filter by Comet asset type. Defaults to "all". Common
            values include "image", "model-element", "notebook", "source_code".

    Returns:
        Dict with experiment identity and an `assets` list. Each asset has
        `assetId`, `fileName`, `type`, `step`, `fileSize`, and `link`.
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    raw_assets = experiment.get_asset_list(asset_type=asset_type) or []

    assets: list[dict] = []
    for asset in raw_assets:
        assets.append(
            {
                "assetId": asset.get("assetId"),
                "fileName": asset.get("fileName"),
                "type": asset.get("type"),
                "step": asset.get("step"),
                "fileSize": asset.get("fileSize"),
                "link": asset.get("link"),
            }
        )

    return {
        "key": experiment_key,
        "name": experiment.name,
        "url": experiment.url,
        "asset_type": asset_type,
        "assets": assets,
    }


_ASSET_DOWNLOAD_ROOT = Path("/tmp/comet_assets")


def download_asset(
    experiment_key: str,
    asset_name: str,
    output_dir: str | None = None,
) -> dict:
    """Download an asset from an experiment to the local filesystem.

    Resolves the asset by filename (first match wins) and writes the bytes
    to `output_dir`. Caller can then read/open the file (e.g., view a PNG).

    For safety, `output_dir` is constrained to `/tmp`: any path that does
    not resolve under `/tmp` raises `ValueError`. The default puts each
    experiment's assets in its own subdirectory.

    Args:
        experiment_key: Comet experiment key.
        asset_name: Filename of the asset as shown in `list_assets` (e.g.,
            "reliability_diagram.png").
        output_dir: Directory to write the file into. Must resolve to a
            path under `/tmp`. Defaults to
            `/tmp/comet_assets/<experiment_key>/`.

    Returns:
        Dict with the resolved `assetId`, `fileName`, `path` (absolute path
        to the downloaded file), and `fileSize` in bytes.

    Raises:
        ValueError: If the asset does not exist on the experiment, or if
            `output_dir` resolves to a location outside of `/tmp`.
    """
    api = _api()
    experiment = api.get_experiment_by_key(experiment_key)
    raw_assets = experiment.get_asset_list(asset_type="all") or []

    match = next(
        (asset for asset in raw_assets if asset.get("fileName") == asset_name),
        None,
    )
    if match is None:
        available = [asset.get("fileName") for asset in raw_assets]
        raise ValueError(
            f"Asset '{asset_name}' not found on experiment {experiment_key}. "
            f"Available assets: {available}"
        )

    requested_dir = Path(output_dir) if output_dir else _ASSET_DOWNLOAD_ROOT / experiment_key
    resolved_dir = requested_dir.resolve()
    tmp_root = Path("/tmp").resolve()
    if tmp_root not in resolved_dir.parents and resolved_dir != tmp_root:
        raise ValueError(
            f"output_dir must resolve under /tmp for safety; got '{resolved_dir}'."
        )

    resolved_dir.mkdir(parents=True, exist_ok=True)
    destination = resolved_dir / asset_name

    asset_bytes = experiment.get_asset(match["assetId"], return_type="binary")
    destination.write_bytes(asset_bytes)

    return {
        "key": experiment_key,
        "assetId": match["assetId"],
        "fileName": asset_name,
        "path": str(destination),
        "fileSize": len(asset_bytes),
    }
