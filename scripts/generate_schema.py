#!/usr/bin/env python3
"""
Generate ASDL schema artifacts from Pydantic models.

Outputs:
- schema.json: JSON Schema for the ASDL YAML document
- schema.txt:  Human-readable overview (like ams-compose)

Usage:
  python -m ASDL.scripts.generate_schema [--out DIR]
  or run directly: ./generate_schema.py --out DIR
"""

from __future__ import annotations

import argparse
from pathlib import Path

from asdl.ast.schema import write_schema_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ASDL schema artifacts")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Output directory (defaults to this scripts directory)",
    )
    args = parser.parse_args()

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path, txt_path = write_schema_artifacts(out_dir)

    print(f"Wrote: {json_path}")
    print(f"Wrote: {txt_path}")


if __name__ == "__main__":
    main()
