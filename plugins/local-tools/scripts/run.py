#!/usr/bin/env python3
"""Start the bundled stdio MCP server without installing a Python package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_tools_mcp.server import main

if __name__ == "__main__":
    raise SystemExit(main())
