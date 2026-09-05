---
name: ai-desloppification
description: Remove unnecessary complexity and filler from code or copy. Use when asked to desloppify, simplify an overengineered change, remove unnecessary abstractions or defensive layers, or tighten user-facing language. Preserve intended behavior and real contracts.
---

# AI Desloppification

Make the requested result easier to understand and maintain. The smallest complete solution may require removing more code than it adds.

## Scope and review

1. Inspect the current code or copy, its callers, and the requested behavior.
2. Identify concrete redundancy, defects, or unnecessary machinery. Respect standing cleanup authorization and explicit exclusions.
3. Make cohesive corrections that support the task. Record unrelated or costly improvements separately instead of widening every change into a project audit.
4. Review the resulting behavior and diff, then run the relevant checks.

Use the project's acceptance criteria. This skill adds no numerical quality gates. Coverage, mutations, complexity, and size can identify review priorities; none justifies invented contracts, meaningless tests, unsafe casts, removed resilience, or arbitrary file splits. Explain relevant gaps and justified exceptions rather than hiding them.

Routine implementation choices and already-authorized cleanup do not need another approval. Ask when a material behavior, compatibility, data, or scope decision cannot be established from the request and existing contracts.

## Code to simplify

- Remove wrappers, factories, adapters, helpers, and generic utilities that add indirection without isolating useful behavior.
- Consolidate genuinely duplicated logic. Keep distinct domain cases separate even when their syntax looks similar.
- Remove unused APIs, speculative overloads, aliases, and null-object implementations after checking actual consumers. Preserve intentional extension points and supported contracts.
- Complete authorized replacements across their callers and remove the superseded paths. Retain compatibility only when the user or an existing contract requires it.
- Remove speculative guards, retries, catch-and-swallow blocks, normalization layers, and fallback defaults. Preserve validation and resilience required by external input, I/O, or live concurrent state.
- Remove obsolete comments, temporary diagnostics, dead configuration, and tests that exist only for deleted behavior.

Do not add abstractions or rename and move files merely to make the diff look organized. Keep short, single-use logic inline when clearer. Extract behavior with its state, helpers, and types when there is a real ownership boundary. Before a substantial split, describe that boundary and the cutover; a cohesive long file can remain intact unless an explicit project limit requires otherwise.

## Tests

Keep tests that detect an observable regression, contract violation, important failure path, or integration risk. Strengthen assertions when a meaningful mutation survives.

Avoid tests that only:

- Assert mocks or internal wiring.
- Check trivial getters, forwarding wrappers, or framework behavior already covered elsewhere.
- Repeat an existing case with different literals but no different risk.
- Preserve impossible states or speculative fallback behavior that should be removed.
- Pin formatting, timestamps, generated IDs, or snapshots unrelated to the contract.

Uncovered lines and surviving mutations need interpretation. Document equivalent mutations and unresolved significance; do not force a score by asserting arbitrary implementation details. Documentation and reversible copy edits can be validated by review and the existing format or packaging checks.

## User-facing copy

Remove clauses that add no information:

- Reassurance tails and repeated privacy or simplicity promises.
- Prose that narrates controls already visible beside it.
- A fact or joke immediately restated in an explanatory tail.
- Internal field names, protocol details, or developer terminology that do not help the reader decide or act.
- Filler intensifiers such as "seamlessly", "effortlessly", or "powerful".
- Repetitive flourishes where one clear statement carries the meaning.

Keep established vocabulary, useful guarantees, and the product's voice. Put each fact where it belongs and say it once. Review changed copy in context.

## Removal and verification

When removing a feature, field, or output, remove its exclusive implementation, wiring, types, tests, docs, and configuration. Use omission rather than placeholders or replacement explanations unless the user requests them. Remove unwanted output at its producer; add a sanitizer layer only when that is the requested solution.

Before finishing, check affected callers and references, remove obsolete scaffolding, and run the relevant repository checks. Once those checks pass, repeat them only for new changes, failures, or unresolved concerns. Report the concrete cleanup, verification, and any material follow-up work.
