---
name: tdd
description: Test-driven development for features, bug fixes, and integration behavior. Use when the user requests tests first or a behavior change benefits from a failing regression scenario. Test through stable interfaces and keep the process proportional to the risk.
---

# Test-Driven Development

Build one behavior slice at a time: a meaningful failing test, the implementation that makes it pass, then any cleanup justified by what the slice revealed.

Read relevant domain context and architectural decisions so the tests use the project's terms and contracts. See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for test-double guidance.

## Choose the interface

A test should exercise observable behavior through a stable public interface: an API, module boundary, command, or user flow. Prefer the existing interface that reaches the actual behavior without exposing private implementation details.

Routine regression tests at established interfaces are already authorized. Choose them from the request, callers, and existing tests. Ask the user only when the expected behavior or a consequential new interface is unclear; do not require approval for each test location.

## Work in slices

1. Select one behavior or failure path that matters to the requested outcome.
2. Write a test whose assertion would detect that behavior being wrong. Run it and confirm it fails for the intended reason.
3. Implement the behavior and run the focused check again.
4. Simplify the affected code and tests when useful, keeping the checks green. Then move to the next necessary slice.

For bugs that cannot be reproduced automatically, use the best available repeatable observation and state its limits. Documentation and low-impact edits may need review or format validation instead of a new test suite.

## Tests worth keeping

- Assert observable results, important state transitions, and meaningful failure behavior.
- Derive expectations from the specification, a known-good example, or independently established evidence.
- Keep tests insensitive to internal refactoring when the public contract is unchanged.
- Model external dependencies only as far as the scenario needs, preserving real boundary behavior.

Avoid assertions about mocks alone, expected values recomputed from the implementation, broad snapshots of incidental details, and bulk tests for imagined future behavior. Do not add tests solely to reach a coverage percentage or kill a mutation that preserves the actual contract.

Run focused checks during the loop and the repository's required checks before delivery. Once they pass, expand testing only when changes or unresolved risks warrant it.
