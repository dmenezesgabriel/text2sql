"""Fail if any src module lacks a corresponding unit test file.

Excluded: __init__.py, i_*.py (port interfaces), main.py, composition_root.py.
Expected mapping: src/foo/bar.py -> tests/unit/foo/test_bar.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
TESTS = ROOT / "tests" / "unit"

EXCLUDED_NAMES = {"__init__.py", "main.py", "composition_root.py"}


def expected_test_path(src_file: Path) -> Path:
    relative = src_file.relative_to(SRC)
    return TESTS / relative.parent / f"test_{relative.name}"


def is_excluded(src_file: Path) -> bool:
    name = src_file.name
    return name in EXCLUDED_NAMES or name.startswith("i_")


def main() -> int:
    missing = [
        (src, expected_test_path(src))
        for src in sorted(SRC.rglob("*.py"))
        if not is_excluded(src) and not expected_test_path(src).exists()
    ]

    for src, test in missing:
        print(f"MISSING  {test.relative_to(ROOT)}  (for {src.relative_to(ROOT)})")

    if missing:
        print(f"\n{len(missing)} unit test file(s) missing.", file=sys.stderr)
        return 1

    print("All src modules have a corresponding unit test file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
