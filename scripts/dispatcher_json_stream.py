#!/usr/bin/env python3
"""
Run `codex exec` in JSON stream mode and echo events to the terminal.
"""

from __future__ import annotations

import argparse
import json
import os
import selectors
import subprocess
import sys
import time
from typing import Any, Iterable

import yaml

DEFAULT_PROMPT = "analyze the structure of the codebase"
TASKS_STATE_PATH = "agents/context/tasks_state.yaml"
MAX_REVIEW_ROUNDS = 3
IMESSAGE_SCRIPT = os.path.join(os.path.dirname(__file__), "send_imessage.sh")

ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_RESET = "\033[0m"


def build_command(prompt: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--json",
        "-s",
        "danger-full-access",
        prompt,
    ]


def format_event(payload: dict[str, Any]) -> tuple[str, str]:
    event_type = payload.get("type", "unknown")
    if event_type == "item.started":
        item = payload.get("item", {})
        item_type = item.get("type", "unknown")
        cmd = item.get("command")
        if item_type == "command_execution" and cmd:
            return f"[command.start] {cmd}", "default"
        return f"[item.start] {item_type}", "default"
    if event_type == "item.completed":
        item = payload.get("item", {})
        item_type = item.get("type", "unknown")
        if item_type == "command_execution":
            exit_code = item.get("exit_code")
            return f"[command.done] exit={exit_code}", "default"
        if item_type == "reasoning":
            text = (item.get("text") or "").strip()
            if text:
                return f"[reasoning] {text}", "reasoning"
            return "[reasoning]", "reasoning"
        if item_type == "agent_message":
            text = (item.get("text") or "").strip()
            if text:
                return f"[agent] {text}", "agent"
            return "[agent]", "agent"
        return f"[item.done] {item_type}", "default"
    if event_type == "turn.completed":
        usage = payload.get("usage", {})
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        return f"[turn.done] input_tokens={input_tokens} output_tokens={output_tokens}", "default"
    return f"[event] {event_type}", "default"


def colorize(text: str, tag: str) -> str:
    if tag == "agent":
        return f"{ANSI_GREEN}{text}{ANSI_RESET}"
    if tag == "reasoning":
        return f"{ANSI_BLUE}{text}{ANSI_RESET}"
    return text


def render_line(line: str) -> tuple[str, str, str | None]:
    stripped = line.strip()
    if not stripped:
        return "", "default", None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped, "default", None

    formatted, tag = format_event(payload)
    agent_text: str | None = None
    if payload.get("type") == "item.completed":
        item = payload.get("item", {})
        if item.get("type") == "agent_message":
            agent_text = (item.get("text") or "").strip()
    return formatted, tag, agent_text


def stream_process(command: Iterable[str], prefix: str | None = None) -> tuple[int, str | None]:
    last_agent_message: str | None = None
    try:
        proc = subprocess.Popen(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError as exc:
        print(f"Required binary not found: {exc}. Ensure codex is installed.", file=sys.stderr)
        return 127

    selector = selectors.DefaultSelector()
    if proc.stdout is not None:
        selector.register(proc.stdout, selectors.EVENT_READ, data="stdout")
    if proc.stderr is not None:
        selector.register(proc.stderr, selectors.EVENT_READ, data="stderr")

    while selector.get_map():
        for key, _ in selector.select():
            line = key.fileobj.readline()
            if line == "":
                selector.unregister(key.fileobj)
                continue
            formatted, tag, agent_text = render_line(line)
            if not formatted:
                continue
            if agent_text:
                last_agent_message = agent_text
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            if prefix:
                output = f"{prefix} [{timestamp}] {colorize(formatted, tag)}\n"
            else:
                output = f"[{timestamp}] {colorize(formatted, tag)}\n"
            if key.data == "stderr":
                sys.stderr.write(output)
                sys.stderr.flush()
            else:
                sys.stdout.write(output)
                sys.stdout.flush()

    return proc.wait(), last_agent_message


def load_tasks_state(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid tasks state structure in {path}")
    return data


def task_ids_from_state(path: str) -> list[str]:
    data = load_tasks_state(path)
    task_ids: list[str] = []
    for key in data.keys():
        if key == "schema_version":
            continue
        task_ids.append(key)
    return task_ids


def task_status(path: str, task_id: str) -> str | None:
    data = load_tasks_state(path)
    entry = data.get(task_id)
    if not isinstance(entry, dict):
        return None
    status = entry.get("status")
    if isinstance(status, str):
        return status
    return None


def build_executor_prompt(task_id: str, feedback: str | None = None) -> str:
    repo_path = os.getcwd()
    base = (
        "You are the executor agent. Read and follow your role definition "
        f"'agents/roles/executor.md'. Work on task {task_id}. Repo path: {repo_path}."
    )
    if feedback:
        base = f"{base}\nReviewer feedback:\n{feedback}"
    return base


def build_reviewer_prompt(task_id: str, summary: str | None) -> str:
    repo_path = os.getcwd()
    summary_text = summary or "No executor summary captured."
    return (
        "You are the reviewer agent. Read and follow your role definition "
        f"'agents/roles/reviewer.md'. Review task {task_id}. Repo path: {repo_path}.\n"
        "Here are the summaries from the executor agent:\n"
        f"{summary_text}"
    )


def run_codex(
    prompt: str,
    task_id: str | None = None,
    role: str | None = None,
) -> tuple[int, str | None]:
    command = build_command(prompt)
    print(f"Running: {' '.join(command)}")
    prefix = None
    if task_id and role:
        prefix = f"[{task_id}][{role}]"
    elif task_id:
        prefix = f"[{task_id}]"
    elif role:
        prefix = f"[{role}]"
    return stream_process(command, prefix=prefix)


def run_scheduler(
    task_ids: list[str],
    tasks_state_path: str,
    max_rounds: int,
) -> int:
    for task_id in task_ids:
        print(f"Starting task {task_id}")
        rounds = 0
        reviewer_feedback: str | None = None
        while rounds < max_rounds:
            executor_prompt = build_executor_prompt(task_id, feedback=reviewer_feedback)
            exit_code, executor_summary = run_codex(
                executor_prompt,
                task_id=task_id,
                role="executor",
            )
            if exit_code != 0:
                print(f"Interrupted: executor exited with code {exit_code}", file=sys.stderr)
                return exit_code

            status = task_status(tasks_state_path, task_id)
            send_imessage("executor", task_id, status, executor_summary)
            if status != "ready_for_review":
                print(
                    f"Interrupted: task {task_id} status is '{status}', expected 'ready_for_review'.",
                    file=sys.stderr,
                )
                return 1

            reviewer_prompt = build_reviewer_prompt(task_id, executor_summary)
            exit_code, reviewer_summary = run_codex(
                reviewer_prompt,
                task_id=task_id,
                role="reviewer",
            )
            if exit_code != 0:
                print(f"Interrupted: reviewer exited with code {exit_code}", file=sys.stderr)
                return exit_code

            status = task_status(tasks_state_path, task_id)
            send_imessage("reviewer", task_id, status, reviewer_summary)
            if status == "done":
                print(f"Task {task_id} completed.")
                break

            if status == "request_changes":
                rounds += 1
                if rounds >= max_rounds:
                    print(
                        f"Interrupted: task {task_id} exceeded {max_rounds} review rounds.",
                        file=sys.stderr,
                    )
                    return 1
                reviewer_feedback = reviewer_summary or "No reviewer summary captured."
                print(f"Task {task_id} requested changes; restarting executor (round {rounds + 1}).")
                continue

            print(
                f"Interrupted: task {task_id} status is '{status}', expected 'done' or 'request_changes'.",
                file=sys.stderr,
            )
            return 1
    return 0


def send_imessage(role: str, task_id: str, status: str | None, response: str | None) -> None:
    message_status = status or "unknown"
    response_text = response or "No agent response captured."
    payload = f"[{role}] [{task_id}] ({message_status}): {response_text}"
    try:
        subprocess.run(
            [IMESSAGE_SCRIPT, payload],
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        print(f"Warning: {IMESSAGE_SCRIPT} not found; skipping iMessage send.", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch codex exec in JSON stream mode and print events.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt to pass to codex exec.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Task IDs to run in order.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tasks not marked done in tasks_state.yaml (in file order).",
    )
    parser.add_argument(
        "--tasks-state",
        default=TASKS_STATE_PATH,
        help="Path to tasks_state.yaml.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=MAX_REVIEW_ROUNDS,
        help="Maximum executor-reviewer rounds per task.",
    )
    args = parser.parse_args()

    if args.all and args.tasks:
        print("Error: Use --all or --tasks, not both.", file=sys.stderr)
        return 2

    if args.all or args.tasks:
        if args.all:
            ordered_ids = task_ids_from_state(args.tasks_state)
            task_ids = [
                task_id
                for task_id in ordered_ids
                if task_status(args.tasks_state, task_id) != "done"
            ]
        else:
            task_ids = list(args.tasks or [])
        if not task_ids:
            print("No tasks to run.")
            return 0
        return run_scheduler(task_ids, args.tasks_state, args.max_rounds)

    exit_code, _ = run_codex(args.prompt)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
