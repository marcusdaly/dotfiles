"""Library functions for querying Comet ML experiments.

Each function returns plain dicts/lists so it can be consumed by the CLI or
the MCP server without parsing printed output. Workspace is resolved from
the optional `workspace` arg, falling back to `$COMET_WORKSPACE`.
"""

import os

from comet_ml import API


class CometConfigError(RuntimeError):
    """Raised when required Comet config (API key, workspace) is missing."""


def _api() -> API:
    api_key = os.environ.get("COMET_API_KEY")
    if not api_key:
        raise CometConfigError(
            "$COMET_API_KEY is not set. Add it to ~/.secrets.env."
        )
    return API(api_key=api_key)


def _resolve_workspace(workspace: str | None) -> str:
    effective = workspace or os.environ.get("COMET_WORKSPACE")
    if not effective:
        raise CometConfigError(
            "No workspace set. Pass workspace=... or export COMET_WORKSPACE."
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
