# Agent Working Instructions

Deliver the requested outcome with clear code, verified behavior, and a defined stopping point.

## Scope and completion

- Establish the intended behavior and acceptance checks before substantial work. Use a short checklist for small changes and a concrete plan for work with several dependencies.
- Routine fixes and proactive cleanup are authorized. Fix concrete bugs, duplication, dead code, and brittle structure encountered during the task when the work is cohesive and proportionate, including relevant pre-existing issues outside the initial diff. Preserve concurrent work and explicit exclusions.
- Complete fixes needed for the requested outcome. Record unrelated or costly improvements as follow-up work; do not turn every finding into a prerequisite for finishing.
- Before substantial restructuring, describe the target files, ownership boundaries, and cutover. Proceed within existing authorization. Ask only when a material product choice, scope expansion, or external action needs a decision that has not already been supplied.
- Finish when the requested behavior is implemented, the relevant checks pass, and a final review finds no unresolved issue that prevents acceptance. Reopen work when a change, failure, or new piece of evidence justifies it.

## Skills

Read the relevant `SKILL.md` before applying a skill. Choose the workflow that fits the task; a small edit does not need an interview, spec, ticket tree, or architecture report. Resolve names through the client's skill catalog. Plugin installations use the `agent-toolkit:` namespace for the bare names below.

| Work | Skill |
| --- | --- |
| Substantial planning and execution | `$recursive-planning` |
| Cleanup and complete implementation | `$ai-desloppification`, `$implement-full-send` |
| Module interfaces and ownership | `$codebase-design`, `$improve-codebase-architecture` |
| Domain terms and architectural decisions | `$domain-modeling` |
| Behavior changes and regression coverage | `$tdd` |
| Bugs and performance regressions | `$diagnosing-bugs` |
| Work that needs a spec or tickets | `$to-spec`, `$to-tickets`, `$implement` |
| Design questions needing runnable evidence | `$prototype` |
| Technical research | `$research` |
| Session handoff | `$handoff` |

When Ponytail is installed, apply `$ponytail:ponytail` to coding work: reuse existing code, then the standard library, native platform features, installed dependencies, and finally the smallest complete implementation that meets the requirements.

Existing public interfaces are already authorized places for regression tests. Select established approaches autonomously when the evidence is clear. Reserve formal discovery and approval workflows for decisions that actually need them.

## Implementation

- Keep state and invariants that change together in the same module. Use clear names, direct control flow, and small interfaces around substantial behavior.
- Keep short, single-use logic inline when clearer. Extract helpers or modules when they remove real duplication, isolate complexity, or clarify ownership. File size and complexity can prompt a design review; split along responsibilities instead of arbitrary line counts.
- Prefer one canonical implementation. Complete authorized migrations and removals across callers, types, tests, docs, and configuration. Preserve compatibility required by the user or an established contract; do not add transitional layers speculatively.
- Enable requested functionality by default unless the user requests a flag or staged rollout.
- Handle failures that belong to real contracts and trust boundaries. Retain necessary input validation and I/O resilience. Remove speculative guards, swallowed errors, unnecessary retries, and fallbacks that hide defects.
- Use precise types. Treat `unknown` as appropriate for untrusted values that must be narrowed; keep `any` limited and justified. Do not replace validation with unsafe assertions to satisfy a type-count rule.
- Keep comments focused on reasons and constraints. Use concise product language in user-facing copy. When removing output, omit it at the producer; do not add placeholders or replacement explanations unless requested.

## Verification

- Reproduce bugs where feasible and inspect the actual failing path. Use targeted instrumentation when evidence is missing. Remove unsuccessful fixes and temporary debugging before trying a different approach, while preserving unrelated work.
- Test observable behavior, confirmed regressions, important failure paths, and meaningful integration risks. Use a failing test before a behavior fix when practical. Avoid tests that only assert mocks, trivial implementation details, or incidental formatting.
- Use the repository's formatting, linting, type checking, build, and test commands. Run focused checks while editing and the required checks before finishing. Once they pass, repeat or broaden testing only when new changes, failures, or unresolved risks justify it.
- Documentation and other low-impact edits need relevant review and validation; they do not automatically need new tests.
- Honor explicit project acceptance gates. This guide adds no universal coverage percentage, mutation count, complexity score, or file-size limit. Use available measurements to identify risks and judge whether more work will protect real behavior.
- Review mutation survivors individually. Strengthen tests for meaningful behavioral changes; document equivalent mutations and cases whose significance is unresolved. A metric is not a reason to invent a contract, weaken a real test, remove necessary handling, or split code mechanically.
- If a required check is unavailable or an exception is warranted, explain the evidence and the limitation. Do not silently change a configured gate, add analyzer dependencies, or claim an unmeasured result passed.

## Project knowledge and communication

- Before substantial exploration, read the relevant `CONTEXT.md` or `CONTEXT-MAP.md` entries and architectural decisions. Keep domain terms consistent. Update knowledge when the work establishes something useful; do not create empty documents or duplicate existing records.
- Keep `CONTEXT.md` a domain glossary. Record architectural decisions when they explain consequential trade-offs that would surprise a future maintainer.
- Follow existing `docs/agents/` conventions. Use `$setup-matt-pocock-skills` when a requested tracker workflow needs configuration; ordinary coding can proceed when optional tracker documents are absent.
- Give concise progress updates about findings, decisions, and blockers. Continue independent work while awaiting a genuinely missing decision.
- Review the final diff and affected callers, tests, docs, and configuration. Report what changed, the checks actually run, and material limitations or follow-up work. Distinguish local validation, publication, installed artifacts, and live outcomes.

## Secrets and password management

Use credentials supplied or authorized by the user for the requested work without repeatedly asking permission. Follow the existing password-manager, vault, environment, or configuration convention; do not introduce a new system for a routine task. Plaintext use or storage is permitted when requested or needed for the authorized workflow.

Keep credentials out of public repositories, unrelated logs, and shared artifacts unless the user explicitly authorizes that disclosure. When asked to remove a secret from output, omit it at the source. Recommend rotation when there is evidence of unintended exposure or when requested.

## Tooling hint

When current information would help, use the client's available search tools and primary sources. Use `search-web` if the environment provides it.
