# Validation

Validated on Linux with Codex 0.153.3, Claude Code 2.1.261, and Python 3.11.15. CI runs Python 3.11 and 3.12.

## Functional checks

- 52 tests pass: 17 packaging/watcher checks and 35 Local Tools checks.
- The watcher selected the waiting option in a real, isolated tmux pane. Fixture-driven checks cover navigation, rechecking a changed screen, copy mode, dead panes, current-socket discovery, and leaving permission dialogs untouched.
- Local Tools tests exercise stdio protocol handling, multiple dashboard clients, cancellation, process lifecycle, log cursors, monitor callbacks, and host timezone/DST formatting.
- Both plugins install and uninstall successfully under isolated Codex and Claude configuration directories.
- Codex's native `skills/list` discovers all 21 namespaced skills from the installed package. Native MCP discovery identifies the optional Local Tools plugin. Direct stdio execution exposes all ten tools without a package installation.
- Both Codex plugin manifests and Claude's plugin/marketplace manifests validate. The packaged guidance, release versions, direct skill references, and linked skill resources are checked together.

## Measurements

Run `sh scripts/validate.sh` to reproduce the measurements. No coverage exclusions or metric suppressions were added.

| Check | Result |
| --- | --- |
| Ruff lint and formatting | Pass |
| Shell syntax | Pass |
| Largest authored Python file | 843 lines; limit `< 1000` |
| Maximum cyclomatic complexity | 13; limit `< 22` |
| Maximum cognitive complexity | 16; limit `< 22` |
| Maximum Halstead Difficulty | 6.25; limit `< 80` |
| High-confidence Vulture findings | 0 |
| Statement coverage | 82.81% |
| Branch coverage | 71.19% |
| Combined statement/branch coverage | 80.03% |
| Packaging synchronization and complexity-check scripts | 100% statement and branch coverage |

The imported Local Tools implementation still has uncovered paths, principally error handling, dashboard requests, and asynchronous lifecycle cases. Its full coverage does **not** meet the guide's 100% target. The coverage report exposes those gaps; CI reports coverage without presenting it as a passed 100% gate.

CRAP score, mutation survival, duplication, static typing, and shell complexity have not been measured. Vulture's zero high-confidence findings do not prove an absence of every possible dead path. The existing Python JSON boundary code retains `Any` annotations. These limitations remain visible rather than being waived by exclusions or low-value tests.

## Client update limits

Startup-update behavior was verified against the exact Codex release source and current Claude documentation. Desktop and IDE startup behavior depends on their bundled backend version. Background refresh does not guarantee that an already-started session has the latest skill inventory. See [the distribution research](distribution-research.md).
