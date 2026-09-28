---
name: ai-desloppification
description: "Keep implementation and cleanup simple through reuse, disciplined scope, and existing contracts. Use for KISS or reuse requests, overengineered changes, and tightening user-facing copy."
---

# AI Desloppification

Make the requested result easier to understand and maintain. Start with the working system and extend the code that already owns the behavior. The smallest complete solution minimizes new concepts and maintenance burden; it may require removing more code than it adds.

## Scope and review

1. Establish the requested outcome, explicit exclusions, and any working implementation the user names as the reference. Keep later additions distinct from corrections to the original requirement.
2. Trace the relevant existing path before designing a replacement: user action, save helper, data access, scheduling, external call, and persisted result as applicable. Inspect neighboring integrations for reusable behavior. Stop once the owners and actual gap are clear; a small change does not require a repository-wide audit.
3. Identify what the current path cannot do. Reuse or extend its helpers and records before adding a parallel implementation. Compare actual behavior and callers, not just similar names.
4. Make cohesive corrections that close that gap. Respect standing cleanup authorization; record unrelated improvements separately. Proximity to the touched code, architectural neatness, and "full send" do not expand the task.
5. Review why each changed file is needed, then verify the resulting user workflow and relevant contracts.

Use the project's acceptance criteria. This skill adds no numerical quality gates. Coverage, mutations, complexity, and size can identify review priorities; none justifies invented contracts, meaningless tests, unsafe casts, removed resilience, or arbitrary file splits. Explain relevant gaps and justified exceptions rather than hiding them.

Routine implementation choices and already-authorized cleanup do not need another approval. Ask when a material behavior, compatibility, data, or scope decision cannot be established from the request and existing contracts.

## Before adding machinery

- For a new query, table, stored procedure, helper, abstraction, flag, or screen, identify the concrete requirement and why the existing owner cannot satisfy it with a simpler extension. This is an implementation decision, not a mandatory document or another approval step.
- Generalize a proven implementation by removing the assumptions that prevent its reuse. Preserve its useful vocabulary and flow. A configurable district or provider does not by itself require a generic framework, registry, or versioning system.
- Keep data with the record it describes and editing controls with the existing editor. For example, a mapping to an external location may need one field and a dropdown on the location record; introduce a separate crosswalk system only when the actual relationships or history require it.
- Preserve established API names, schemas, blank/null semantics, and business rules unless the requested change requires otherwise. Verify new required fields and validation against the real contract or observed system behavior. Implementation convenience is not a business requirement, and guessed defaults must not conceal missing data.
- Integrate at the existing owner of the business save or lifecycle event when it serves the relevant entry points. Check forms, modals, imports, and background paths as applicable; reuse existing scheduling and delivery mechanisms. Keep a successful business save and its integration outcome distinct where the workflow requires it.
- New storage or abstractions are appropriate for demonstrated needs such as durable delivery or a real ownership boundary. Choose them for that need; simplicity is not an absolute ban on SQL, helpers, resilience, or justified refactoring.

Architecture documents should reflect the agreed behavior and necessary tradeoffs. Correct an overbuilt proposal rather than implementing unnecessary machinery to fulfill its promises.

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

For integrations and UI flows, verify the route users actually take: available inputs, save and reopen, blank selections, automatic execution, and the external result where relevant and authorized. A passing helper test or manually invoked worker does not establish that the normal workflow works. Report source inspection, automated tests, actual submissions, and confirmed external effects separately, including what was not exercised.

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

Status messages should describe the current action and its actual outcome. A queued attempt is not a completed sync, and historical activity should not appear to be a new action.

## Removal and verification

When removing a feature, field, or output, remove its exclusive implementation, wiring, types, tests, docs, and configuration. Use omission rather than placeholders or replacement explanations unless the user requests them. Remove unwanted output at its producer; add a sanitizer layer only when that is the requested solution.

Before finishing, check affected callers and references, remove obsolete scaffolding, and run the relevant repository checks. For each substantive change, be able to name the requested behavior or necessary dependency it serves; remove unrelated churn from the diff. Once checks pass, repeat them only for new changes, failures, or unresolved concerns.

Report the concrete result, verification, and material follow-up work concisely. Distinguish committed code, passing CI, deployed code, and verified runtime behavior. Carry authorized work through the agreed completion point without making the user repeatedly ask to continue.
