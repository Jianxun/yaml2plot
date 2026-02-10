"""Generate Markdown documentation from ASDL sources."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from asdl.docs.markdown import MarkdownRenderError, render_markdown_from_file


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Markdown documentation from ASDL source files."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="ASDL YAML file or directory (directories are scanned recursively).",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for generated Markdown.",
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="Include paths under directories named _archive.",
    )
    return parser.parse_args()


def _output_path(source: Path, out_dir: Path) -> Path:
    return out_dir / f"{source.stem}.md"


def _collect_sources(
    sources: Iterable[Path],
    *,
    include_archive: bool,
) -> list[Path]:
    files: list[Path] = []
    for source in sources:
        if source.is_dir():
            for path in sorted(source.rglob("*.asdl")):
                if not include_archive and "_archive" in path.parts:
                    continue
                files.append(path)
            continue
        files.append(source)
    return files


def _validate_sources(paths: Iterable[Path]) -> list[Path]:
    valid: list[Path] = []
    for path in paths:
        if not path.exists():
            print(f"Missing source: {path}", file=sys.stderr)
            continue
        if path.is_dir():
            valid.append(path)
            continue
        if path.suffix != ".asdl":
            print(f"Skipping non-ASDL file: {path}", file=sys.stderr)
            continue
        valid.append(path)
    return valid


def main() -> int:
    args = _parse_args()
    source_paths = [Path(item) for item in args.sources]
    out_dir = Path(args.out)

    valid_sources = _validate_sources(source_paths)
    if not valid_sources:
        print("No valid ASDL sources provided.", file=sys.stderr)
        return 1

    sources = _collect_sources(valid_sources, include_archive=args.include_archive)
    if not sources:
        print("No ASDL files found.", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    output_paths: dict[Path, Path] = {}
    exit_code = 0

    for source in sources:
        output_path = _output_path(source, out_dir)
        if output_path in output_paths:
            print(
                f"Output collision for {source} and {output_paths[output_path]}",
                file=sys.stderr,
            )
            exit_code = 1
            continue
        output_paths[output_path] = source

        try:
            markdown = render_markdown_from_file(source)
        except MarkdownRenderError as exc:
            print(str(exc), file=sys.stderr)
            exit_code = 1
            continue

        output_path.write_text(markdown, encoding="utf-8")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
