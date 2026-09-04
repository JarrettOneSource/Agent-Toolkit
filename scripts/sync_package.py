#!/usr/bin/env python3
"""Keep release versions and packaged working instructions synchronized."""

import argparse
import json
from pathlib import Path


def synchronize(root: Path, *, check: bool) -> list[Path]:
    version = (root / "VERSION").read_text().strip()
    files = {
        root / "plugins/agent-toolkit/AGENTS.md": (root / "AGENTS.md").read_text(),
    }
    for path in sorted((root / "plugins").glob("*/.*-plugin/plugin.json")):
        manifest = json.loads(path.read_text())
        manifest["version"] = version
        files[path] = json.dumps(manifest, indent=2) + "\n"
    changed = []
    for path, content in files.items():
        if path.exists() and path.read_text() == content:
            continue
        changed.append(path)
        if not check:
            path.write_text(content)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    changed = synchronize(root, check=arguments.check)
    for path in changed:
        print(f"{'Out of date' if arguments.check else 'Updated'}: {path.relative_to(root)}")
    return int(arguments.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
