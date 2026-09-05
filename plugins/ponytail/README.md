# Ponytail core

An instruction-only adaptation of [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), retaining the reuse-first decision ladder and correctness constraints.

After adding the Agent Toolkit marketplace, install with:

```sh
codex plugin add ponytail@agent-toolkit
```

For Claude Code:

```sh
claude plugin install ponytail@agent-toolkit
```

Invoke `$ponytail:ponytail` in Codex or `/ponytail:ponytail` in Claude. For automatic use across projects, add this to the global `AGENTS.md` in each Codex home:

```markdown
## Ponytail

Apply `$ponytail:ponytail` to coding work. Read its skill and use the first suitable option: existing code, standard library, native platform feature, installed dependency, then the smallest complete implementation. Preserve requested behavior and the repository's quality requirements.
```

Normal skill selection remains enabled. No additional runtime, lifecycle hook, status line, or mode configuration is required. Existing sessions may need a restart to see the installation.

This edition omits upstream's modes, repeated prompt injection, status-line setup, scoreboards, debt ledger, auxiliary commands, benchmarks, marketing assets, and unrelated agent adapters. It follows the Agent Toolkit repository's updates; the upstream MIT license and source revision are retained in [LICENSE](LICENSE) and [SOURCES.json](https://github.com/JarrettOneSource/Agent-Toolkit/blob/main/SOURCES.json).
