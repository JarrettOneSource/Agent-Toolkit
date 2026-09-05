---
name: diagnosing-bugs
description: Diagnose bugs and performance regressions using a repeatable signal, focused hypotheses, and evidence-backed fixes. Use when something is broken, failing, intermittently wrong, or slow; scale the investigation to the uncertainty and impact.
---

# Diagnosing Bugs

Find and verify the cause of the reported failure. Read the relevant code, domain context, and architectural decisions before choosing a fix.

## Establish a useful signal

Capture the actual symptom and the conditions that trigger it. Prefer a focused failing test, command, HTTP request, browser scenario, or replayed trace that detects the reported behavior.

Inspecting code can help build the reproduction; it does not have to wait for a perfect harness. When a full reproduction is unavailable, use existing logs, a narrower invariant, or a small experiment and distinguish confirmed evidence from inference. Ask for missing access or observations only when they are needed to make further progress.

Make the signal more deterministic and faster when doing so will shorten the investigation. Reduce the reproduction enough to distinguish causes; do not spend unbounded time minimizing an already useful case.

For intermittent bugs, use a bounded set of repeated runs or controlled stress and record the observed failure rate. For performance problems, establish a measured baseline and compare the same workload after the fix. Do not claim reliability or performance from an unrelated proxy.

If a human must exercise a scenario, agree the observation needed. [The human-assisted loop template](scripts/hitl-loop.template.sh) is available when repeated manual observations would benefit from a script; ordinary user feedback does not require it.

## Test explanations

When the cause is uncertain, identify plausible hypotheses and what evidence would distinguish them. There is no required number of hypotheses. Share significant findings and continue with the best-supported next check without requiring a routine confirmation.

Use a debugger, targeted trace, or temporary logs at the relevant boundaries. Test one explanatory change at a time. Give temporary diagnostics a recognizable marker so they can be removed reliably.

## Fix and verify

- Address the cause in the owner of the behavior and update affected callers.
- Add a failing regression test before the fix when a useful interface and reproduction are available. Use existing public interfaces without another permission step.
- If an attempted fix fails, remove the unsuccessful change and temporary instrumentation before testing the next explanation. Preserve unrelated work.
- Rerun the original scenario after the fix, then the relevant repository checks. A smaller test alone does not establish that the original failure is resolved.

Finish when the reported behavior is fixed and supported by the available checks. Remove temporary diagnostics and experimental scaffolding, explain the cause and verification, and state any remaining uncertainty. Record broader architectural improvements separately unless they are necessary for the fix or explicitly requested.
