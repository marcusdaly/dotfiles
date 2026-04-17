#!/usr/bin/env python3
"""CLI to query Comet ML experiments from terminal.

Commands:
    list [project]              List recent experiments with latest loss
    metrics <key> [metric...]   Get latest metrics for an experiment
    compare <key1> <key2>       Compare metrics between two experiments
    url <key>                   Print experiment URL
    text <key>                  Fetch logged text (qualitative generations)

Environment variables:
    COMET_API_KEY               Required. Your Comet ML API key.
    COMET_WORKSPACE             Required. Your Comet workspace name.
"""

import os
import sys

from comet_ml import API


def _api() -> API:
    api_key = os.environ.get("COMET_API_KEY")
    if not api_key:
        print(
            "Error: COMET_API_KEY not set. Add it to ~/.secrets.env and source it.",
            file=sys.stderr,
        )
        sys.exit(1)
    return API(api_key=api_key)


def _workspace() -> str:
    workspace = os.environ.get("COMET_WORKSPACE")
    if not workspace:
        print(
            "Error: COMET_WORKSPACE not set. Set it in ~/.secrets.env or your shell config.",
            file=sys.stderr,
        )
        sys.exit(1)
    return workspace


def cmd_list(project: str, limit: int = 10) -> None:
    """List recent experiments with latest train_loss."""
    api = _api()
    experiments = api.get_experiments(_workspace(), project_name=project)
    sorted_exps = sorted(
        experiments,
        key=lambda experiment: experiment.start_server_timestamp,
        reverse=True,
    )

    for exp in sorted_exps[:limit]:
        summary = exp.get_metrics_summary("train_loss")
        loss = f"{float(summary['valueCurrent']):.4f}" if summary else "N/A"
        state = getattr(exp, "state", "?")
        print(f"{exp.name:50s} loss={loss:8s} state={state:10s} {exp.url}")


def cmd_metrics(experiment_key: str, metric_names: list[str] | None = None) -> None:
    """Get latest metrics for an experiment."""
    api = _api()
    exp = api.get_experiment_by_key(experiment_key)
    print(f"Experiment: {exp.name}")
    print(f"URL: {exp.url}\n")

    if metric_names is None:
        metric_names = [
            "train_loss",
            "learning_rate",
            "samples_trained",
        ]

    for metric_name in metric_names:
        try:
            points = exp.get_metrics(metric_name)
            if points:
                latest = points[-1]
                print(
                    f"  {metric_name:30s}: {float(latest['metricValue']):10.4f}"
                    f"  (step {latest['step']})"
                )
        except Exception as exc:
            print(f"  {metric_name:30s}: error ({exc})")


def cmd_compare(key1: str, key2: str, metric: str = "train_loss") -> None:
    """Compare a metric between two experiments."""
    api = _api()
    for key in [key1, key2]:
        exp = api.get_experiment_by_key(key)
        summary = exp.get_metrics_summary(metric)
        current = float(summary["valueCurrent"]) if summary else float("nan")
        print(f"  {exp.name:50s}  {metric}={current:.4f}")


def cmd_text(experiment_key: str) -> None:
    """Fetch logged text (e.g., qualitative generations) from an experiment."""
    api = _api()
    exp = api.get_experiment_by_key(experiment_key)
    text_entries = exp.get_text()
    if not text_entries:
        print("No logged text found.")
        return
    for entry in text_entries[-3:]:
        print(f"--- Step {entry.get('step', '?')} ---")
        print(entry.get("text", entry.get("value", "")))
        print()


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]

    if command == "list":
        if len(sys.argv) < 3:
            print("Usage: comet-check list <project>")
            sys.exit(1)
        cmd_list(sys.argv[2])
    elif command == "metrics":
        if len(sys.argv) < 3:
            print("Usage: comet-check metrics <experiment_key> [metric1 metric2 ...]")
            sys.exit(1)
        metrics = sys.argv[3:] if len(sys.argv) > 3 else None
        cmd_metrics(sys.argv[2], metrics)
    elif command == "compare":
        if len(sys.argv) < 4:
            print("Usage: comet-check compare <key1> <key2> [metric]")
            sys.exit(1)
        metric = sys.argv[4] if len(sys.argv) > 4 else "train_loss"
        cmd_compare(sys.argv[2], sys.argv[3], metric)
    elif command == "text":
        if len(sys.argv) < 3:
            print("Usage: comet-check text <experiment_key>")
            sys.exit(1)
        cmd_text(sys.argv[2])
    elif command == "url":
        if len(sys.argv) < 3:
            print("Usage: comet-check url <experiment_key>")
            sys.exit(1)
        api = _api()
        exp = api.get_experiment_by_key(sys.argv[2])
        print(exp.url)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
