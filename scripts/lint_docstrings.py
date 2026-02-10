#!/usr/bin/env python3
"""Check for missing docstrings in ASDL source files."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint docstrings in ASDL source files."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory to scan (default: src/asdl).",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Check private names regardless of size.",
    )
    parser.add_argument(
        "--private-min-lines",
        type=int,
        default=10,
        help="Require docstrings for private defs >= N lines (default: 10).",
    )
    parser.add_argument(
        "--skip-module-docstrings",
        action="store_true",
        help="Skip module docstring checks.",
    )
    return parser.parse_args()


def iter_python_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def span_len(node: ast.AST) -> int:
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return max(1, (end or start) - start + 1)


def is_public(name: str) -> bool:
    return not name.startswith("_")


def has_overload_decorator(node: ast.AST) -> bool:
    decorators = getattr(node, "decorator_list", [])
    for decorator in decorators:
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "overload":
            return True
    return False


def should_check_private(
    name: str, node: ast.AST, include_private: bool, min_lines: int
) -> bool:
    if include_private:
        return True
    if min_lines <= 0:
        return False
    return span_len(node) >= min_lines


def report(
    errors: list[str], file_path: Path, lineno: int, message: str
) -> None:
    errors.append(f"{file_path}:{lineno}: {message}")


def check_module(tree: ast.AST, path: Path, errors: list[str]) -> None:
    if not getattr(tree, "body", []):
        return
    if ast.get_docstring(tree) is None:
        report(errors, path, 1, "Missing module docstring.")


def check_defs(
    tree: ast.AST,
    path: Path,
    errors: list[str],
    include_private: bool,
    min_lines: int,
) -> None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            check_class(node, path, errors, include_private, min_lines)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            check_function(
                node, path, errors, include_private, min_lines, class_visibility=None
            )


def check_class(
    node: ast.ClassDef,
    path: Path,
    errors: list[str],
    include_private: bool,
    min_lines: int,
) -> None:
    name = node.name
    if is_public(name) or should_check_private(name, node, include_private, min_lines):
        if ast.get_docstring(node) is None:
            report(errors, path, node.lineno, f"Missing class docstring: {name}.")

    class_is_public = is_public(name)
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            check_function(
                item,
                path,
                errors,
                include_private,
                min_lines,
                class_visibility=class_is_public,
            )


def check_function(
    node: ast.AST,
    path: Path,
    errors: list[str],
    include_private: bool,
    min_lines: int,
    class_visibility: bool | None,
) -> None:
    name = getattr(node, "name", "")
    if has_overload_decorator(node):
        return

    is_public_name = is_public(name)
    private_context = name.startswith("_") or class_visibility is False
    should_check = False
    if is_public_name and class_visibility is not False:
        should_check = True
    elif private_context and should_check_private(
        name, node, include_private, min_lines
    ):
        should_check = True

    if should_check and ast.get_docstring(node) is None:
        report(errors, path, node.lineno, f"Missing function docstring: {name}.")


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    root = args.root or (repo_root / "src/asdl")
    if not root.exists():
        print(f"Root path does not exist: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in iter_python_files(root):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path}:0: Failed to read file ({exc}).")
            continue
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            lineno = exc.lineno or 1
            errors.append(f"{path}:{lineno}: Failed to parse file ({exc}).")
            continue

        if not args.skip_module_docstrings:
            check_module(tree, path, errors)
        check_defs(tree, path, errors, args.include_private, args.private_min_lines)

    if errors:
        for error in errors:
            print(error)
        print(f"{len(errors)} docstring issue(s) found.")
        return 1
    print("OK: docstring checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
