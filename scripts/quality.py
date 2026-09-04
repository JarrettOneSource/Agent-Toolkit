#!/usr/bin/env python3
"""Measure the authored Python code's size and implementation complexity."""

import ast
from pathlib import Path

from cognitive_complexity.api import get_cognitive_complexity
from radon.complexity import cc_visit
from radon.metrics import h_visit


def measurements(path: Path) -> tuple[int, int, int, float]:
    source = path.read_text()
    blocks = cc_visit(source)
    for block in list(blocks):
        blocks.extend(getattr(block, "methods", []))
    cyclomatic = max((block.complexity for block in blocks), default=0)
    functions = (
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    cognitive = max((get_cognitive_complexity(node) for node in functions), default=0)
    difficulty = max((metric.difficulty for _, metric in h_visit(source).functions), default=0.0)
    return len(source.splitlines()), cyclomatic, cognitive, difficulty


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = sorted((root / "plugins/local-tools").glob("src/**/*.py"))
    paths += sorted((root / "plugins/local-tools/scripts").glob("*.py"))
    paths += sorted((root / "scripts").glob("*.py"))
    failures = 0
    print("File | Lines | Cyclomatic | Cognitive | Halstead difficulty")
    for path in paths:
        lines, cyclomatic, cognitive, difficulty = measurements(path)
        print(f"{path.relative_to(root)} | {lines} | {cyclomatic} | {cognitive} | {difficulty:.2f}")
        if lines >= 1000 or cyclomatic >= 22 or cognitive >= 22 or difficulty >= 80:
            failures += 1
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
