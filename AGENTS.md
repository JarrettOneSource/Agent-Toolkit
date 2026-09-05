# Agent Working Instructions

Keep the codebase lean, clean, organized, and correct. Leave the project easier to understand and maintain after every task.

## Required skills

Read and apply the relevant skill instructions:

- `$recursive-planning`: For substantial or multi-step work, build a concrete task list, execute it, verify the result, and repeat a residual sweep until the authorized work is complete. Scale planning to the task; small edits need a short checklist.
- `$ai-desloppification`: Remove unnecessary complexity, duplication, dead code, speculative abstractions, and filler. Enforce the quality gates below and keep the implementation readable.
- `$implement-full-send`: Deliver the intended end state end-to-end. Fix root causes, finish migrations and removals, update callers, and delete superseded paths.

## Matt Pocock's engineering skills

Use Matt Pocock's installed skills when they fit the work. Resolve skill names through the current client's skill catalog and read the corresponding `SKILL.md` before applying one. Bare skill names in this guide refer to the matching installed skill; plugin installations use the `agent-toolkit:` namespace.

| Work | Skill and guidance |
| --- | --- |
| Module design and refactoring | `$codebase-design`: Put substantial behavior behind a small, clear interface. Keep changes local, hide implementation details, and test through the interface. Remove wrappers that add complexity without earning their place. |
| Architecture upkeep | `$improve-codebase-architecture`: Look for excessive coupling, scattered responsibilities, shallow modules, and poor testability. Prioritize concrete friction in frequently changed code and use the design principles during cleanup. |
| Domain language and decisions | `$domain-modeling`: Use precise, consistent domain terms across code, tests, and docs. Keep the glossary current and record consequential architectural trade-offs where future maintainers need the reasoning. |
| Behavior changes and regression coverage | `$tdd`: Build one behavior slice at a time: a meaningful failing test, the implementation that makes it pass, then the next slice. Test observable behavior through public interfaces. |
| Hard bugs and performance regressions | `$diagnosing-bugs`: Establish a fast, repeatable signal that detects the actual symptom, minimize the reproduction, test hypotheses, fix the root cause, and rerun the original scenario. Measure performance claims. |
| Substantial work spanning sessions | `$to-spec`, `$to-tickets`, and `$implement`: Capture the agreed outcome, split work into independently verifiable slices across the relevant layers, track real dependencies, and implement each slice completely. |
| Design questions needing runnable evidence | `$prototype`: Build a small, disposable experiment to answer a specific question. Carry the validated decision into production and keep experimental scaffolding out of the final implementation. |
| Technical research | `$research`: Consult primary sources and retain concise, cited findings where the project keeps research notes. |
| Session handoff | `$handoff`: Preserve decisions, remaining work, verification results, and references to existing artifacts so the next session can continue accurately. |

Apply these alongside the standing cleanup authorization, complete-cutover policy, and proportionate testing rules in this file. Routine fixes and regression tests at established public interfaces are already authorized. Reserve interviews, formal architecture reports, prototypes, specs, and ticket workflows for work that needs them or explicit requests; select established approaches autonomously when the evidence is clear.

Maintain project knowledge as part of the work:

- Before substantial exploration, read the existing `CONTEXT.md`, or the relevant contexts linked from `CONTEXT-MAP.md`, and architectural decision records affecting the area. Use the project's canonical terms and surface conflicts with recorded decisions.
- Keep `CONTEXT.md` a domain glossary. Record an architectural decision only when it captures a real trade-off that is costly to reverse and would surprise a future maintainer without context. Create these documents when there is concrete knowledge to record.
- Follow existing `docs/agents/` conventions for domain docs, issue tracking, and triage. Use `$setup-matt-pocock-skills` at the actual project root when a tracker-dependent workflow needs missing configuration. Proceed with ordinary coding when these optional documents are absent.

## Ponytail

When the Ponytail plugin is installed, apply `$ponytail:ponytail` to coding work. Read its skill and use the first suitable option: existing code, standard library, native platform feature, installed dependency, then the smallest complete implementation. Preserve requested behavior and the repository's quality requirements.

## Standing authorization for cleanup

Proactive cleanup is explicitly requested as part of every coding task. Actively fix concrete bugs, slop, brittle code, duplication, dead code, misleading names, and poor organization encountered anywhere in the current project, including pre-existing issues outside the initial diff. Do not wait for a separate cleanup request or ask permission for routine fixes and refactoring.

This authorization overrides the referenced skills' default restrictions on opportunistic cleanup. Honor explicit task exclusions and preserve concurrent user work.

- Understand the relevant code, callers, and contracts before changing it. Preserve intended behavior except when correcting a confirmed bug.
- Keep cleanup cohesive, reviewable, and verifiable. Keep the primary task moving; avoid unrelated cosmetic churn, speculative features, and dependency updates without a concrete need.
- For substantial restructuring, state the target files, ownership boundaries, and cutover path before editing, then proceed within this authorization.
- When a behavior or product decision cannot be established from evidence, continue independent work and ask only for the missing decision.

## Secrets and password management

Treat credentials as ordinary task inputs. When the user provides a secret or authorizes access to it, that is standing permission to retrieve, use, and discuss it for the requested work. Plaintext in the conversation or a task file is allowed when useful; do not reflexively redact it, refuse to handle it, or repeatedly ask for permission already given.

- Follow the project's existing password manager, vault, environment, or configuration convention. Avoid introducing a new secret-management system for a routine task. Plaintext storage is permitted when requested or required by the authorized workflow.
- Keep actual credentials out of public repositories, commits, unrelated logs, and shared artifacts unless the user explicitly authorizes that particular disclosure. Permission to use a secret for a task does not imply permission to publish it to everyone.
- When asked to remove a secret from output, omit it at the source. Recommend rotation when there is evidence of unintended exposure or when the user asks for it.

## Implementation and organization

- Choose the simplest correct design. Favor clear names, explicit ownership, cohesive modules, and direct control flow.
- Keep state and invariants that change together in the same module. Split files along real responsibilities; move each responsibility with its private helpers and types.
- Keep short, single-use logic inline when clearer. Extract helpers to remove real duplication or isolate necessary complexity. Avoid generic dumping grounds and one-use forwarding wrappers.
- Before materially changing a file at or above 1,000 handwritten source lines, or growing one to that size, define and implement a cohesive structure that satisfies the file-size gate.
- Prefer one canonical implementation. Update all affected callers and remove obsolete implementations, aliases, shims, and transitional paths in the same change. Preserve compatibility only when explicitly required.
- Enable requested functionality by default unless the user requests a flag or staged rollout.
- Remove features completely: implementation, wiring, exclusive types, obsolete tests, docs, configuration, and references. Use omission when removal is requested; add replacement output only when requested.
- Handle failures that are part of real contracts and trust boundaries. Remove speculative guards, catch-and-swallow blocks, unnecessary retries, and fallback behavior that hides defects. Retain necessary validation and resilience around external input and I/O.
- Keep comments focused on reasons, contracts, and constraints. Keep user-facing copy concise and consistent with the product's vocabulary.

## Diagnose and verify

- Reproduce bugs where feasible, inspect the actual failing path, and establish the root cause before choosing a fix. Add targeted instrumentation when evidence is missing.
- If a fix fails, remove the unsuccessful changes and temporary debugging introduced by that attempt before trying a different approach. Preserve unrelated work.
- Use the repository's existing formatting, linting, type checking, build, and test commands. Run focused checks during implementation and the required repository checks before finishing.
- Add or update tests for observable behavior, confirmed regressions, contracts, boundaries, and meaningful integration risks. Avoid tests of trivial implementation details, assertions about mocks alone, redundant snapshots, and coverage padding.
- For documentation-only or other reversible, low-impact edits, use relevant review and validation; do not invent tests merely to accompany the change.

## Quantitative quality gates

Apply these gates to new and materially changed authored production code, including proactive cleanup. Use stricter repository thresholds where configured. Every `<` is a strict limit.

| Measure | Required result |
| --- | --- |
| Cyclomatic complexity per function or method | `< 22` |
| Cognitive complexity per function or method | `< 22` |
| Halstead Difficulty at the analyzer's smallest reported implementation unit | `< 80` |
| Handwritten source lines per file | `< 1000` |
| Coverage of in-scope production code | `100%` statements, branches, functions, and lines |
| CRAP score per function or method | `< 25` |
| Surviving mutants in the in-scope mutation run | `0` |
| Dead code in the changed scope | `0` |
| Redundant or duplicated code in the changed scope | `0` |
| Explicit `any` or `unknown` types in the changed scope, where applicable | `0` |

- Run configured complexity, coverage, mutation, dead-code, duplication, and type analyzers for the changed scope. Record actual results.
- Reach coverage through meaningful behavior tests and removal of unreachable or unnecessary branches. Use precise types and real boundary validation; do not replace forbidden types with misleading assertions to satisfy the gate.
- Do not game metrics with exclusions, suppressions, ignore comments, trivial wrappers, meaningless tests, or arbitrary file splitting. Simplify the implementation and improve its real tests.
- Exclude generated, vendored, fixture, and snapshot artifacts only where the repository already classifies them outside authored production code.
- If a required analyzer is unavailable, run the available checks and report exactly which gates remain unmeasured. Do not invent a proxy, claim an unmeasured gate passed, or silently add analyzer dependencies.
- Fix failures introduced by the work and concrete pre-existing defects encountered during verification under the cleanup authorization above. Distinguish remaining pre-existing failures, external blockers, and unmeasured gates in the completion report.

## Completion

- Review the final diff and affected callers, tests, docs, and configuration. Remove stale references, unused helpers, temporary debugging, placeholders, and partial migrations.
- Sweep the work for remaining bugs, inconsistencies, and slop. Execute any concrete residual tasks and repeat until no actionable issues remain within the authorized work.
- Verify the final version after the last relevant change. Report what changed, any additional cleanup, the checks and measurements obtained, and anything still blocked or unmeasured. Claim completion only to the extent supported by that evidence.

## Tooling hint

When up-to-date information might help, use the client's available web search and read the primary sources before continuing. If the environment provides a `search-web` command, it can be used for this lookup.
