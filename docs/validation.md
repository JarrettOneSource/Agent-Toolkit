# Validation

This revision was validated on Linux with Codex 0.153.3 and Python 3.12.3. CI runs Python 3.11 and 3.12. Earlier distribution checks also covered Claude Code 2.1.261.

## Functional checks

- 64 tests pass locally: 27 packaging/watcher/client checks and 37 Local Tools checks. The native Codex check is skipped when the CLI is unavailable.
- The watcher selected the waiting option and submitted `continue` for a stalled capacity error in real, isolated tmux panes. Regression checks cover capacity errors with and without a goal, duplicate suppression, rearming after activity, stale errors, and draft preservation. Fixture-driven checks cover navigation, rechecking a changed screen, copy mode, dead panes, current-socket discovery, and leaving permission dialogs untouched.
- Local Tools tests exercise stdio protocol handling, multiple dashboard clients, cancellation, process lifecycle, log cursors, monitor callbacks, and host timezone/DST formatting. Monitor tests hold the child after its initial output and release it explicitly, so callback assertions do not depend on a half-second startup race.
- Earlier distribution checks installed and uninstalled Agent Toolkit and Local Tools under isolated Codex and Claude configuration directories.
- Codex's native `skills/list` discovers all 20 namespaced Agent Toolkit skills from a fresh installation of this revision. A native Codex thread starts the installed Local Tools server and discovers all ten tools. Direct stdio execution also works without a package installation.
- All three Codex plugin manifests pass the plugin validator, and all six revised skills pass skill validation. Automated packaging checks verify both clients' release versions, packaged guidance, direct skill references, and linked resources.
- The optional Ponytail package contains one instruction skill and no runtime hooks, MCP servers, scripts, benchmarks, or marketing assets. Its skill and both client manifests validate.
- Ponytail was installed from this GitHub marketplace into a real Codex CLI profile and three profile wrappers. Each launcher's native skill catalog reported the skill enabled from its own installed cache, with content matching the repository. Global coding guidance was added to all four profiles; existing configuration values and shared configuration symlinks were preserved.

## Measurements

Run `sh scripts/validate.sh` to reproduce the checks and measurements. Lint, formatting, package consistency, tests, shell syntax, and high-confidence dead-code checks are enforced. Size and complexity are reported for review without numerical pass/fail thresholds. No coverage exclusions or metric suppressions were added.

| Check | Result |
| --- | --- |
| Ruff lint and formatting | Pass |
| Shell syntax | Pass |
| Largest authored Python file | 844 lines |
| Maximum cyclomatic complexity | 13 |
| Maximum cognitive complexity | 16 |
| Maximum Halstead Difficulty | 6.25 |
| High-confidence Vulture findings | 0 |
| Explicit `Any` annotations | 0; enforced by Ruff ANN401 |
| Statement coverage | 83.97% |
| Branch coverage | 71.88% |
| Combined statement/branch coverage | 81.10% |
| Packaging synchronization and complexity-report scripts | 100% statement and branch coverage |

The Local Tools implementation has uncovered paths, principally error handling, dashboard requests, and asynchronous lifecycle cases. Coverage identifies further testing opportunities; the toolkit does not impose a universal percentage. Scope additional work to the behavior being changed and the risks it introduces.

CRAP score, mutation survival, duplication, static typing, and shell complexity have not been measured. Vulture's zero high-confidence findings do not prove an absence of every possible dead path. Python JSON values now have explicit recursive types; whole-program static type correctness is unverified. These are limits on the evidence, not additional universal acceptance gates.

## Client update limits

A GitHub-backed test installation was seeded from the repository's older `0.1.0` revision, then configured to track `main` while retaining the old installed snapshot. Starting the stock Codex app server refreshed the installed plugin to `0.1.1` and loaded all 21 skills from the new cache. No manual upgrade command was run.

The published implementation also passed [GitHub Actions on Python 3.11 and 3.12](https://github.com/JarrettOneSource/Agent-Toolkit/actions/runs/33929439461).

Claude's update behavior was verified against current documentation. Desktop and IDE startup behavior depends on their bundled backend version. Background refresh does not guarantee that an already-started session has the latest skill inventory. See [the distribution research](distribution-research.md).
