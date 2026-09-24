# ML evolution artifact schema

Each project profile provides an evolution root. Use this layout:

```text
<evolution-root>/
├── raw/
│   └── manifests/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── skill-impact.md
│   └── patterns/
└── candidates/
```

## Raw manifest

Raw manifests are write-once Markdown files:

```markdown
---
id: stable-lowercase-id
captured_at: ISO-8601 timestamp
scope: bounded experiment or receipt
result: success | failure | partial | interrupted | pending-evaluation
sensitivity: sanitized | restricted-reference
---

# Evidence bundle title

## Objective

What was attempted and what authority it had.

## Sources

- Path, SHA-256, size, and timestamp for each source.

## Observed outcome

Only results directly supported by the sources.

## Evidence locations

- Timestamp, line, JSON key, or artifact path and the fact it proves.

## Limits

What this evidence does not establish.
```

Never edit an admitted manifest. Correct it with a new manifest containing
`supersedes: <id>`. Reference existing append-only sources rather than copying
large rollout, checkpoint, or metric files.

## Pattern page

```markdown
# Pattern title

Status: provisional | corroborated | validated | superseded
Scope: project stage or subsystem
Last updated: ISO-8601 timestamp

## Problem
## Root cause
## Failure evidence
## Successes and counterexamples
## Reusable guidance
## Applicability limits
## Open questions
```

Evidence entries name raw manifest IDs and exact locations. Distinguish policy
behavior from harness, simulator, statistics, and publication failures.

## Index

Use one routing entry per pattern:

```markdown
- [pattern-id](patterns/pattern-id.md): PROBLEM; ROOT CAUSE; RESPONSE. Scope: ... Status: ...
```

## Evolution log

Append one entry per pass:

```markdown
## <timestamp> — <pass-id>

- Evidence admitted: ...
- Patterns created or updated: ...
- Candidate: <id> | none
- Gate outcome: accepted | rejected | insufficient-evidence
- Installed skill hash: <sha256> | unchanged
- Summary: distinguish observed, validated, installed, and model-promotion state.
```

## Skill impact ledger

```markdown
## <candidate-id>

- Timestamp: ...
- Target skill: ...
- Patterns: ...
- Baseline skill hash: ...
- Candidate diff: ...
- Positive scenario: pass | fail — evidence
- Negative scenario: pass | fail — evidence
- Regression scenario: pass | fail — evidence
- Project invariant: pass | fail — evidence
- Outcome: accepted | rejected | insufficient-evidence
- Reason: ...
- Installed skill hash: ... | unchanged
```

Retain rejected entries. Revisit them only with new evidence or a materially
different intervention.

## Candidate directory

```text
candidates/<candidate-id>/
├── proposal.md
├── candidate.diff
├── validation.md
└── skill/
```

The candidate skill is isolated from the installed skill. Skill validation
does not authorize model training, checkpoint promotion, repository publication,
or production replacement.

## Confidence

- Training completion proves execution, not improvement.
- Sampled training metrics are not deterministic or heldout evaluation.
- Surrogate utility is not task success unless the project profile explicitly
  establishes that equivalence.
- A selected checkpoint is exploratory until evaluated on data not used for
  selection.
- A candidate checkpoint, accepted checkpoint, packaged checkpoint, production
  checkpoint, and live-proven policy are separate states.
