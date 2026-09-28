---
name: claude-companion
description: Consult Claude for a requested second opinion or a consequential unresolved design or diagnosis question. Codex retains implementation ownership.
---

# Claude Companion

Use Claude as a thinking partner when another perspective can resolve a
material uncertainty, or when the user requests ongoing consultation. Codex
owns the reasoning, implementation, verification, and final decision.

## Choose a useful question

Point Claude at the actual files and evidence behind a bounded decision:
architecture alternatives, an unexplained failure, or non-obvious downstream
effects. State what decision the answer should help make. Routine edits,
unfamiliar code, and completed steps do not each require a consultation.

Honor the user's requested cadence and project restrictions. Do not delegate
implementation or spawn extra reviewers merely because this skill was loaded.

## Run the consultation

Read [claude-code-cli](../claude-code-cli/SKILL.md) for session and permission
handling. Use the configured Fable alias unless the user chose another model;
an unavailable model is a capability issue, not a reason to silently change the
task's budget or permissions. Select effort for the question rather than
forcing maximum effort for every exchange.

Give the consultation the necessary repository access and explicitly state
whether it is read-only. Reading a skill does not authorize external writes.
Use print mode for a captured response; use streaming output when progress
matters. Save the session ID, resume it for the same decision, and fork only
when a distinct tangent benefits from isolation.

For long consultations, use the host's background-job lifecycle and a suitable
runtime limit. A quiet output stream or observation timeout is not completion.
Stop only a process owned by this consultation when it is abandoned.

## Use the answer

Check material claims against files or observable behavior. Disagree when the
evidence warrants it. If an answer misses the question, narrow the follow-up
instead of repeating a broad review request. Continue the authorized work once
the decision is supported; do not make agreement between models a new gate.
