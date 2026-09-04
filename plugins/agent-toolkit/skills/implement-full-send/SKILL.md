---
name: implement-full-send
description: Apply strict implementation discipline for coding tasks where the user wants the clean, recommended solution end-to-end instead of incremental patches. Use when Codex should do a full cutover, avoid fallbacks and backwards compatibility layers, debug to root cause, keep new functionality enabled by default, split growing monoliths into cohesive files when appropriate, remove features with complete scoped cleanup, and clean up touched code before finishing.
---

# Implement Full Send

Use this skill when the user wants the code changed the right way, not merely made to pass. Favor the intended end state, complete cutover, and maintainable structure over temporary compatibility layers or defensive clutter.

## Plan To The Size Of The Work

- Implement small changes end-to-end without stopping for a large planning phase.
- Propose a minimal implementation plan before coding larger features or structural work.
- Include the target structure, ownership boundaries, extension points, and cutover path in that plan.
- Stop and confirm scope with the user before proceeding if the correct solution requires significant refactoring beyond the apparent request.

## Implement The Intended End State

- Implement the clean, recommended solution fully instead of layering on transitional code.
- Complete the cutover instead of leaving old and new paths active together.
- Keep new functionality enabled by default unless the user explicitly asks for a flag or staged rollout.
- Refuse to add environment-variable gating, compatibility shims, or fallback behavior by default.
- Remove superseded code paths when the new design replaces them.

## Remove Features Surgically

- When removing a feature, remove it cleanly and completely instead of disabling it or leaving dead paths behind.
- Keep cleanup scoped to the removed feature and its direct integration points.
- Make the removal surgical and thorough: delete the implementation, wiring, types, tests, docs, and references that exist only for that feature.
- Avoid opportunistic cleanup outside the removal scope unless it is required to keep the system correct.

## Structure Code Deliberately

- Keep files small, cohesive, and easy to navigate.
- Decide explicitly whether a growing file must remain a single file.
- Keep a necessary single file organized with clear sections, extracted helpers, and local types.
- Split a file into a folder of smaller files when responsibilities are separable.
- Prefer clear ownership boundaries over convenience dumping grounds.

## Debug To Root Cause

- Find the root cause before choosing a fix.
- For a persistent problem, add robust debug logs or equivalent instrumentation to narrow the failure and observe the real behavior.
- Pinpoint and confirm the exact source of the bug before fixing it. Do not guess.
- State briefly why the chosen fix works.
- If an attempted fix fails, undo it, clean up any debugging or partial changes that are no longer needed, and try again from a different angle.
- Avoid band-aids that only mask symptoms or preserve flawed behavior.

## Avoid Legacy Baggage

- Avoid fallbacks, backwards compatibility layers, and legacy-preservation work unless the user explicitly requires them.
- Prefer one correct path over multiple partially supported paths.
- Treat "support both" as a scope increase that requires explicit user direction.

## Finish Cleanly

- Clean up touched code before finishing.
- Remove dead branches, stale helpers, unused types, and obvious structural leftovers created during the work.
- Leave the final state consistent with the new implementation approach, not halfway migrated.
