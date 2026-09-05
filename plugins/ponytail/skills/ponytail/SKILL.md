---
name: ponytail
description: Apply Ponytail's reuse-first decision ladder when writing, fixing, refactoring, reviewing, or designing code. Choose the smallest complete solution that satisfies the user's requirements. Use for coding work and dependency choices, not unrelated prose or general knowledge.
license: MIT
---

# Ponytail

Understand the requested behavior and trace the affected code and callers before choosing an implementation. Minimize the work the codebase has to maintain.

## Decision ladder

Use the first option that satisfies the actual requirements and constraints:

1. **Is new code needed?** Leave out speculative functionality. Requested behavior and authorized cleanup count as real work.
2. **Does the codebase already solve it?** Reuse the existing implementation, helper, type, or established pattern.
3. **Does the standard library solve it?** Use it.
4. **Does the platform provide it?** Prefer a native browser control, CSS capability, database constraint, or operating-system facility when it meets the contract.
5. **Does an installed dependency solve it?** Use the capability already available before adding another package.
6. **Is a short direct expression sufficient?** Keep it inline when it is clear and correct.
7. **Otherwise, write the smallest complete implementation.** Keep ownership clear and separate responsibilities where that improves the design.

## Implementation

- Fix defects at their shared cause and check the other affected callers.
- Remove obsolete code and duplication. Avoid speculative wrappers, factories, configuration, and abstractions.
- Prefer readable control flow over compressed expressions. Fewer lines are useful when they reflect less unnecessary behavior.
- Preserve explicit requirements, edge-case correctness, trust-boundary validation, data-loss handling, security, accessibility, and necessary operational constraints.
- Use the repository's existing tests and required quality checks. Add regression coverage for meaningful behavior; avoid tests that merely pad a metric.
- Complete the requested solution. Simplification must preserve the required behavior, and the repository's stronger standards still apply.
