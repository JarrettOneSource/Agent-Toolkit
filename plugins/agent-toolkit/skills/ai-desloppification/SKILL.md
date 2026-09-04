---
name: ai-desloppification
description: Remove AI slop from code, diffs, plans, or implementation choices by enforcing exact scope, measurable quality gates, deliberate large-file boundaries, no unsolicited compatibility layers, no overly defensive code, no unnecessary modularization, and complete removals. Use when the user asks to desloppify, remove AI slop, tighten a change, simplify over-engineered work, avoid fallbacks/backwards compatibility/shims, avoid excessive guards or try/catch blocks, avoid needless helper/module extraction, or audit Codex output for unnecessary abstractions, placeholders, broad refactors, inferred requirements, or measurable code-quality failures. Also covers AI slop in user-facing copy — UI text, microcopy, error messages, marketing prose — when the user asks to deslop the copy, sweep the language, or cut drift (reassurance tails, UI-explainer prose, doubled beats, dev-speak leaks, filler adverbs).
---

# AI Desloppification

## Core Rule

Implement exactly what was requested, using the smallest correct change.

Prioritize readability and simplicity over cleverness, terseness, abstraction for its own sake, preserving a poor structure, or gaming a metric. The smallest correct change is the clearest scoped solution, not necessarily the one with the fewest edited lines.

Before making or approving any change, ask:

1. Was this explicitly requested?
2. Is this technically required to satisfy the request?

If the answer to both is no, do not make the change. If the answer is unclear and the choice affects behavior, compatibility, public API, data shape, persistence, security, or user-visible output, ask the user before proceeding.

## Workflow

1. Restate the requested outcome in concrete terms.
2. Inspect the current code or artifact before proposing changes.
3. Identify the minimal set of files, call sites, outputs, or docs that must change.
4. Remove or revise only the unnecessary AI-generated behavior.
5. Verify the diff for scope creep before finishing.

## Quantitative Quality Gates

For new or materially changed production code, enforce the repository's stricter configured limit or these defaults. Treat each `<` limit literally:

- Cyclomatic complexity per function or method: `< 22`.
- Cognitive complexity per function or method: `< 22`.
- Halstead Difficulty at the analyzer's smallest reported implementation unit: `< 80`.
- Handwritten source lines per file: `< 1000`.
- Test coverage of in-scope production code: `100%` statements, branches, functions, and lines.
- CRAP score per function or method: `< 25`.
- Surviving mutants in the in-scope mutation run: `0`.
- Dead code in the changed scope: `0`.
- Redundant or duplicated code in the changed scope: `0`.
- Explicit `any` or `unknown` types in the changed scope: `0`.

Generated, vendored, fixture, and snapshot artifacts are outside these gates only when the repository already classifies them outside authored production code. Do not create new exclusions, suppressions, ignore comments, meaningless tests, tiny forwarding wrappers, or unmeasured paths to manufacture a passing score. Simplify the implementation or improve its real tests.

Quality-gate failures do not authorize unrelated cleanup. Fix failures caused by or contained within the requested change and report pre-existing out-of-scope failures separately. If the repository lacks a required analyzer, do not invent a proxy, silently add a dependency, or claim the gate passed. Run the available checks, inspect what can be established directly, and state exactly which gates remain unmeasured.

## What To Remove

Remove these unless the user explicitly asked for them or they are technically required:

- Extra abstractions, helpers, wrappers, adapters, factories, or indirection.
- Unnecessary modularization, including new files, modules, classes, helpers, generic utilities, or split-up functions that do not reduce required complexity.
- Duplicated near-identical functions, branches, or blocks that differ only in names or literals. Consolidate one parameterized implementation when behavior is identical; do not consolidate code that only looks similar while encoding distinct cases.
- Speculative public API generated ahead of any caller, including symmetric overload families, convenience aliases, mirrored option variants, unused accessors, or null-object factories. Judge against all actual consumers before removal, and exempt deliberate, documented extension points.
- Backwards compatibility, fallbacks, aliases, shims, dual implementations, deprecated API preservation, or legacy behavior support.
- Overly defensive code, including speculative null checks, broad try/catch blocks, catch-and-swallow behavior, retries, type normalization, validation layers, or impossible-state handling that the request and existing contracts do not require.
- Opportunistic cleanup, unrelated refactors, formatting churn, dependency updates, file moves, renames, or architecture changes.
- Inferred requirements, speculative edge cases, "nice to have" behavior, or unrequested product improvements.
- Placeholder outputs such as `hidden`, `redacted`, `removed`, `value hidden`, `***`, empty strings, `null`, dummy values, or sentinel values when the requested behavior is omission.
- Post-processing sanitizers, redaction filters, scrubbers, masking wrappers, or log-cleanup passes unless the user explicitly requests them. For sensitive data, change the source path so the value is never collected, formatted, logged, persisted, or emitted in the first place.
- Comments or documentation that explain obvious behavior or preserve removed concepts.
- Useless or superfluous tests that do not protect real behavior, reproduce a real bug, lock down a public contract, or cover meaningful risk.

## Compatibility Policy

Do not add compatibility automatically. Prefer one canonical implementation.

When replacing an API or behavior:

- Update all in-scope call sites to the new canonical path.
- Remove obsolete code instead of wrapping it.
- Delete deprecated branches when they are no longer required.
- Ask before preserving old and new behavior together.

## Defensive Code Policy

Write code for the contract that exists, not for every imagined misuse.

Do not add guards, retries, broad exception handling, schema normalization, defensive cloning, fallback defaults, optional-path handling, or generic validators unless the current code path can actually receive that condition and the requested change requires handling it. Prefer letting real contract violations fail clearly over hiding them with speculative recovery.

Defensive handling at a genuine trust boundary is not slop: external APIs that return null or throw, network or filesystem I/O, parsing untrusted input, or cross-thread reads of live systems. The test is whether intermittent failure is part of that boundary's real contract. Guards that keep logging, diagnostics, or a main loop from crashing on a flaky dependency are resilience, not over-defensiveness; do not remove them just to satisfy this policy.

## Modularization Policy

Do not split code into new modules, classes, helpers, adapters, or generic utilities just to make a small change look structured.

Keep logic inline when it is used once, is short, and is clearer at the call site. Extract only when it removes real duplication, isolates necessary complexity, or matches an established local pattern required by the requested change.

File size is both a hard gate and a design signal, not permission to slice a file mechanically. Before materially changing a file that is already over the limit, or adding code that would bring it to `1000` lines, define the intended structure:

- Identify the distinct responsibilities, the owner of each responsibility, and the interface between them.
- Keep state and invariants that change together in one cohesive module.
- Move each separable responsibility with its private helpers and local types; do not extract arbitrary line ranges or one-use forwarding functions.
- Prefer a folder of plainly named cohesive files when several responsibilities share one domain.
- Update all in-scope callers in the same change, then delete the superseded definitions. Do not leave re-export shims, aliases, barrels used only for compatibility, or parallel old and new paths.
- Keep a genuinely single-responsibility file organized with clear sections and local types, but simplify its design rather than waiving the line limit.

For a substantial split, state the target file structure, ownership boundaries, and cutover path before editing. If the correct split requires a significant refactor beyond the apparent request, confirm that scope rather than quietly widening the task.

## Test Policy

Do not add tests just to make a change look rigorous.

Remove or avoid tests when they only:

- Assert mocks, stubs, fixtures, or implementation details instead of observable behavior.
- Exercise trivial getters, constants, pass-through wrappers, or framework behavior already covered elsewhere.
- Duplicate an existing test with different names, literals, or setup but no new behavioral risk.
- Lock in speculative fallbacks, compatibility paths, defensive branches, or impossible states that should be removed.
- Check that code renders, imports, or returns a truthy value without a meaningful assertion.
- Pin incidental formatting, ordering, timestamps, generated IDs, or snapshots unrelated to the requested contract.

Keep tests that prove a real contract, regression, boundary, integration point, migration, security property, data-loss risk, or high-risk behavior. Prefer one focused test that would fail for the bug or requested behavior over broad tests that only increase maintenance cost.

The `100%` coverage gate does not make low-value tests useful. Reach it through tests of observable behavior and by deleting unreachable, speculative, or redundant branches. Coverage is necessary but not sufficient; mutation survival or assertions that cannot detect a behavioral regression still fail this policy.

## User-Facing Copy Policy

AI slop in prose is drift: clauses that add no information. When the target is user-facing text — UI copy, microcopy, tooltips, error messages, empty states, onboarding, marketing or docs prose — cut these patterns:

- Reassurance tails: appended privacy, safety, or simplicity promises nobody asked for ("no account required", "your data never leaves your device", "no paper trail"). If the guarantee is real information, it gets one home where that subject lives — not a tail on every mention.
- UI-explainer prose: sentences narrating what the controls already show (describing a badge beside the badge, "click the button to…").
- Doubled beats: a fact or joke restated in the same breath — an em-dash tail that rephrases the sentence it ends ("installs in one click — browse, tap, play"), a button repeating the line above it, a punchline followed by its explanation.
- Dev-speak leaks: plumbing terms in end-user copy (protocol names, field names, internal ids), and parenthetical translations that commit to neither register ("check your crystal ball (network)").
- Filler intensifiers and hedges: "simply", "seamlessly", "effortlessly", "robust", "powerful", "of course", "just".
- Triple flourishes: "no X, no Y, no Z" runs and other rule-of-three padding where one item carries the meaning.

Say each fact exactly once, in the one place it belongs. Controls and actions get plain words that state what happens; personality lives in descriptions, empty states, and flavor text. The product's voice is content, not slop: keep established vocabulary, single-beat jokes, and brand or canon lines — cut drift, not personality. When a sentence adds nothing, delete it whole; do not compress it into a clause.

## Removal Policy

When asked to remove something, remove it completely while preserving surrounding behavior.

Do not replace removed content with placeholders, redaction markers, empty values, dummy values, sentinel values, alternate output, or explanatory text unless the user explicitly asks for that replacement.

Do not add a sanitizer as the default fix for sensitive output. Remove the sensitive field from the generated output at the producer, or replace the diagnostic with non-sensitive facts such as counts, types, booleans, safe paths, or queryless origins. Add post-processing sanitization only when the user explicitly asks for a sanitizer layer.

Example:

Requested: remove OTPs from log output.

Correct:

```text
User login successful
```

Incorrect:

```text
User login successful
OTP: [Hidden]
```

## Verification

Before finishing:

- Review the diff for changes outside the requested scope.
- Search touched code for leftover fallbacks, aliases, shims, placeholder text, deprecated branches, and unused helpers.
- For copy sweeps, list every changed string with its before, after, and location so the review is a read, not a diff hunt.
- Run focused tests or checks when available and proportionate to the change.
- Run the configured complexity, coverage, mutation, dead-code, duplication, and type checks that cover the changed scope. Record the actual measurements and name any unavailable gate instead of collapsing them into a generic "tests pass" claim.
- In the final response, state what was removed or tightened and any verification performed.
