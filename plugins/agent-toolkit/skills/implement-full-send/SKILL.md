---
name: implement-full-send
description: Deliver a clean implementation end-to-end. Use for full cutovers, root-cause fixes, complete removals, or changes that need coordinated callers and cohesive ownership. Avoid unnecessary transitional paths while preserving the user's scope and existing contracts.
---

# Implement Full Send

Deliver the intended end state, including the callers and lifecycle behavior needed to make it work.

## Plan to the size of the work

Handle small changes directly. For substantial work, identify the target structure, ownership, dependencies, and acceptance checks before editing.

Routine fixes and restructuring within existing authorization can proceed. Ask only when an unresolved product choice, external action, or material scope expansion needs the user's decision. Do not repeat approvals already given.

## Complete the change

- Use one canonical implementation and update affected callers in the same change.
- Remove superseded paths, aliases, wiring, types, tests, docs, and configuration when the replacement or removal is authorized.
- Preserve compatibility required by the user or an established contract. Do not invent fallback paths or compatibility layers for hypothetical consumers.
- Enable requested functionality by default unless a flag or staged rollout is requested or required by the agreed deployment plan.
- Handle genuine boundary failures without hiding defects behind speculative retries, broad exception handling, or silent defaults.

## Keep ownership clear

Keep related state and invariants together. Extract cohesive responsibilities when it reduces coupling or necessary complexity; keep short, single-use logic inline when clearer. File size alone does not determine the right module boundary.

For a substantial split, explain the target files and cutover. Move each responsibility with its private helpers and types, and remove the old definitions after updating their callers.

## Fix and verify

Establish the cause of a defect from a reproduction, focused test, trace, or other concrete evidence. Use targeted instrumentation when needed and remove unsuccessful attempts before trying a different fix. State any limit on what the evidence proves.

Verify the changed behavior and meaningful failure paths using the repository's existing checks. Follow explicit project acceptance gates; do not add universal numerical targets or tests that only make metrics look complete.

Finish with a review of the affected code, callers, and artifacts. Resolve defects necessary for the requested outcome, record broader improvements separately, and stop once the agreed result and its checks are complete.
