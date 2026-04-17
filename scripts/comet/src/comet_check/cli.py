"""CLI wrapper over comet_check.api for terminal use.

All data-gathering logic lives in `comet_check.api`; this module only formats
the results for humans. The MCP server (~/dotfiles/mcp/comet/) imports from
comet_check.api directly.

Commands:
    list [project]              List recent experiments with latest loss
    metrics <key> [metric...]   Get latest metrics for an experiment
    compare <key1> <key2>       Compare metrics between two experiments
    url <key>                   Print experiment URL
    text <key>                  Fetch logged text (qualitative generations)

Environment variables:
    COMET_API_KEY               Required. Your Comet ML API key.
    COMET_WORKSPACE             Required unless overridden. Your Comet workspace.
"""

import sys

from comet_check.api import (
    CometConfigError,
    compare_experiments,
    get_metrics,
    get_text,
    get_url,
    list_experiments,
)


def cmd_list(project: str) -> None:
    for experiment in list_experiments(project):
        loss = f"{experiment['train_loss']:.4f}" if experiment["train_loss"] is not None else "N/A"
        state = experiment["state"] or "?"
        print(f"{experiment['name']:50s} loss={loss:8s} state={state:10s} {experiment['url']}")


def cmd_metrics(experiment_key: str, metric_names: list[str] | None = None) -> None:
    result = get_metrics(experiment_key, metric_names)
    print(f"Experiment: {result['name']}")
    print(f"URL: {result['url']}\n")
    for metric_name, point in result["metrics"].items():
        print(f"  {metric_name:30s}: {point['value']:10.4f}  (step {point['step']})")


def cmd_compare(key1: str, key2: str, metric: str = "train_loss") -> None:
    for entry in compare_experiments(key1, key2, metric):
        value = f"{entry['value']:.4f}" if entry["value"] is not None else "N/A"
        print(f"  {entry['name']:50s}  {entry['metric']}={value}")


def cmd_text(experiment_key: str) -> None:
    entries = get_text(experiment_key)
    if not entries:
        print("No logged text found.")
        return
    for entry in entries:
        print(f"--- Step {entry['step'] if entry['step'] is not None else '?'} ---")
        print(entry["text"])
        print()


def cmd_url(experiment_key: str) -> None:
    print(get_url(experiment_key))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]

    try:
        if command == "list":
            if len(sys.argv) < 3:
                print("Usage: comet-check list <project>")
                sys.exit(1)
            cmd_list(sys.argv[2])
        elif command == "metrics":
            if len(sys.argv) < 3:
                print("Usage: comet-check metrics <experiment_key> [metric1 metric2 ...]")
                sys.exit(1)
            metric_names = sys.argv[3:] if len(sys.argv) > 3 else None
            cmd_metrics(sys.argv[2], metric_names)
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
            cmd_url(sys.argv[2])
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
    except CometConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
