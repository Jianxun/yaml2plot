#!/usr/bin/env python3
"""List unfinished tasks from agents/context/tasks.yaml."""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - best-effort re-exec
    venv_python = (
        Path(__file__).resolve().parents[1] / "venv" / "bin" / "python"
    )
    if venv_python.exists() and os.access(venv_python, os.X_OK):
        os.execv(venv_python, [str(venv_python), *sys.argv])
    raise


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the top level.")
    return data


def collect_tasks(tasks_data: dict) -> list[dict]:
    tasks: list[dict] = []
    for key, value in tasks_data.items():
        if key == "schema_version":
            continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    tasks.append(item)
    return tasks


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_path = repo_root / "agents/context/tasks.yaml"
    state_path = repo_root / "agents/context/tasks_state.yaml"

    try:
        tasks_data = load_yaml(tasks_path)
    except Exception as exc:  # noqa: BLE001 - keep CLI output simple
        print(str(exc), file=sys.stderr)
        return 2

    try:
        state_data = load_yaml(state_path)
    except Exception as exc:  # noqa: BLE001 - keep CLI output simple
        print(str(exc), file=sys.stderr)
        return 2

    unfinished: list[tuple[str, str, str]] = []
    for task in collect_tasks(tasks_data):
        task_id = task.get("id")
        title = task.get("title", "")
        if not isinstance(task_id, str):
            continue
        state = state_data.get(task_id, {})
        status = state.get("status") if isinstance(state, dict) else None
        if status != "done":
            status_label = status if isinstance(status, str) else "missing"
            unfinished.append((task_id, status_label, title))

    if not unfinished:
        print("All tasks in agents/context/tasks.yaml are done.")
        return 0

    print("Unfinished tasks:")
    for task_id, status, title in unfinished:
        suffix = f" — {title}" if title else ""
        print(f"- {task_id} [{status}]{suffix}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
