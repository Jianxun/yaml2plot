#!/usr/bin/env python3
"""Lint task consistency between tasks.yaml and tasks_state.yaml."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


TASK_ID_RE = re.compile(r"^T-\d{3}$")
ALLOWED_STATUSES = {
    "backlog",
    "ready",
    "in_progress",
    "blocked",
    "ready_for_review",
    "review_in_progress",
    "review_clean",
    "request_changes",
    "escalation_needed",
    "done",
}
EARLY_STATUSES = {"backlog", "ready", "blocked"}
REVIEW_STATUSES = {
    "ready_for_review",
    "review_in_progress",
    "review_clean",
    "request_changes",
    "escalation_needed",
}
TASK_STATE_KEYS = {"status", "pr", "merged"}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the top level.")
    return data


def collect_task_ids(
    tasks: list, label: str, errors: list[str]
) -> tuple[list[str], dict[str, list[str]]]:
    ids: list[str] = []
    dependencies: dict[str, list[str]] = {}
    if not isinstance(tasks, list):
        errors.append(f"{label} must be a list.")
        return ids, dependencies
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"{label}[{index}] must be a mapping.")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str):
            errors.append(f"{label}[{index}].id must be a string.")
            continue
        if not TASK_ID_RE.match(task_id):
            errors.append(f"{label}[{index}].id '{task_id}' must match T-000 format.")
        depends_on = task.get("depends_on")
        if depends_on is not None:
            if not isinstance(depends_on, list):
                errors.append(f"{label}[{index}].depends_on must be a list.")
            else:
                deps: list[str] = []
                seen_deps: set[str] = set()
                for dep in depends_on:
                    if not isinstance(dep, str):
                        errors.append(
                            f"{label}[{index}].depends_on values must be strings."
                        )
                        continue
                    if not TASK_ID_RE.match(dep):
                        errors.append(
                            f"{label}[{index}].depends_on '{dep}' must match T-000 format."
                        )
                    if dep in seen_deps:
                        errors.append(
                            f"{label}[{index}].depends_on contains duplicate '{dep}'."
                        )
                        continue
                    seen_deps.add(dep)
                    deps.append(dep)
                if task_id in seen_deps:
                    errors.append(
                        f"{label}[{index}].depends_on cannot include itself."
                    )
                dependencies[task_id] = deps
        ids.append(task_id)
    return ids, dependencies


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    tasks_path = repo_root / "agents/context/tasks.yaml"
    state_path = repo_root / "agents/context/tasks_state.yaml"

    errors: list[str] = []

    try:
        tasks_data = load_yaml(tasks_path)
    except Exception as exc:  # noqa: BLE001 - keep CLI output simple
        errors.append(str(exc))
        tasks_data = {}

    try:
        state_data = load_yaml(state_path)
    except Exception as exc:  # noqa: BLE001 - keep CLI output simple
        errors.append(str(exc))
        state_data = {}

    if tasks_data.get("schema_version") != 2:
        errors.append(f"{tasks_path} schema_version must be 2.")

    current_sprint = tasks_data.get("current_sprint", [])
    backlog = tasks_data.get("backlog", [])
    current_ids, current_deps = collect_task_ids(
        current_sprint, "current_sprint", errors
    )
    backlog_ids, backlog_deps = collect_task_ids(backlog, "backlog", errors)
    active_ids = current_ids + backlog_ids
    active_deps = {**current_deps, **backlog_deps}

    seen_ids: set[str] = set()
    for task_id in active_ids:
        if task_id in seen_ids:
            errors.append(f"Duplicate task id '{task_id}' in tasks.yaml.")
        seen_ids.add(task_id)
    for task_id, deps in active_deps.items():
        for dep in deps:
            if dep not in seen_ids:
                errors.append(
                    f"tasks.yaml task '{task_id}' depends_on inactive or missing task '{dep}'."
                )

    if state_data.get("schema_version") != 2:
        errors.append(f"{state_path} schema_version must be 2.")

    task_states: dict[str, dict] = {}
    for task_id, payload in state_data.items():
        if task_id == "schema_version":
            continue
        if not isinstance(task_id, str):
            errors.append("tasks_state.yaml task keys must be strings.")
            continue
        if not TASK_ID_RE.match(task_id):
            errors.append(f"tasks_state.yaml task id '{task_id}' must match T-000 format.")
            continue
        task_states[task_id] = payload

    for task_id, state in task_states.items():
        if task_id not in seen_ids:
            errors.append(
                f"tasks_state.yaml includes inactive task '{task_id}'; "
                "only active tasks in tasks.yaml are allowed."
            )
        if not isinstance(state, dict):
            errors.append(f"tasks_state.yaml entry for '{task_id}' must be a mapping.")
            continue
        extra_keys = set(state.keys()) - TASK_STATE_KEYS
        missing_keys = TASK_STATE_KEYS - set(state.keys())
        if extra_keys:
            errors.append(
                f"tasks_state.yaml entry for '{task_id}' has unexpected keys: "
                f"{', '.join(sorted(extra_keys))}."
            )
        if missing_keys:
            errors.append(
                f"tasks_state.yaml entry for '{task_id}' is missing keys: "
                f"{', '.join(sorted(missing_keys))}."
            )
        status = state.get("status")
        pr_value = state.get("pr")
        merged_value = state.get("merged")

        if not isinstance(status, str):
            errors.append(f"tasks_state.yaml status for '{task_id}' must be a string.")
        elif status not in ALLOWED_STATUSES:
            errors.append(
                f"tasks_state.yaml status '{status}' for '{task_id}' is invalid."
            )

        if pr_value is None:
            pr_is_set = False
        elif isinstance(pr_value, int):
            if pr_value < 0:
                errors.append(
                    f"tasks_state.yaml pr for '{task_id}' must be a non-negative integer."
                )
            pr_is_set = pr_value > 0
        else:
            errors.append(
                f"tasks_state.yaml pr for '{task_id}' must be null or a non-negative integer."
            )
            pr_is_set = False

        if not isinstance(merged_value, bool):
            errors.append(
                f"tasks_state.yaml merged for '{task_id}' must be a boolean."
            )

        if isinstance(status, str) and status in EARLY_STATUSES:
            if pr_value is not None:
                errors.append(
                    f"tasks_state.yaml pr for '{task_id}' must be null in '{status}'."
                )
            if merged_value is not False:
                errors.append(
                    f"tasks_state.yaml merged for '{task_id}' must be false in '{status}'."
                )
        if isinstance(status, str) and status == "in_progress":
            if pr_value is not None and not pr_is_set:
                errors.append(
                    f"tasks_state.yaml pr for '{task_id}' must be a positive integer in '{status}'."
                )
            if merged_value is not False:
                errors.append(
                    f"tasks_state.yaml merged for '{task_id}' must be false in '{status}'."
                )
        if isinstance(status, str) and status in REVIEW_STATUSES:
            if not pr_is_set:
                errors.append(
                    f"tasks_state.yaml pr for '{task_id}' must be a positive integer in '{status}'."
                )
            if merged_value is not False:
                errors.append(
                    f"tasks_state.yaml merged for '{task_id}' must be false in '{status}'."
                )
        if isinstance(status, str) and status == "done":
            if not pr_is_set:
                errors.append(
                    f"tasks_state.yaml pr for '{task_id}' must be a positive integer in 'done'."
                )
            if merged_value is not True:
                errors.append(
                    f"tasks_state.yaml merged for '{task_id}' must be true in 'done'."
                )

    for task_id in seen_ids:
        if task_id not in task_states:
            errors.append(f"tasks_state.yaml is missing entry for '{task_id}'.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: tasks.yaml and tasks_state.yaml are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
