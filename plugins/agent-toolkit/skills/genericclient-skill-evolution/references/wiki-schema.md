# GenericClient evolution workspace

Create this workspace only when an evolution pass is actually requested:

```text
/home/user/.codex/genericclient-evolution/
├── raw/
│   └── manifests/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── skill-impact.md
│   └── patterns/
└── candidates/
```

The evolution workspace is local operational state. Do not place it in the
GenericClient repository or load it during ordinary `genericclient-development`
work.

## Raw evidence manifests

Use one write-once Markdown manifest per rollout or bounded evidence bundle:

```markdown
---
id: 2026-08-28-witch-experiment-recovery
captured_at: 2026-08-28T20:40:00-04:00
scope: GenericClient live quest execution
source_path: /absolute/path/to/source.jsonl
source_sha256: <sha256>
result: success | failure | partial | interrupted
sensitivity: sanitized | restricted-reference
---

# Witch experiment recovery

## Objective

What this run attempted.

## Outcome

What was actually observed, including terminal state.

## Evidence locations

- `<path>:<line or event>` — exact receipt and why it matters.

## Known limits

Facts this run did not prove.
```

Never edit a raw manifest after it is admitted. If metadata is wrong, create a
new manifest with `supersedes: <old-id>` and retain both. Do not include hidden
reasoning, credentials, Jagex session material, account names, raw account
hashes, private keys, cookies, or remote-access tokens. For sensitive sources,
reference a sanitized derived artifact and its hash.

## Wiki index

`wiki/index.md` is a compact routing catalog. Use one entry per pattern:

```markdown
- [stable-id](patterns/stable-id.md): PROBLEM; ROOT CAUSE; FIX OR CURRENT BEST RESPONSE. Scope: <where it applies>. Status: provisional | corroborated | validated.
```

Keep the description specific enough that a proposer can decide whether to load
the pattern page. Remove stale index claims when the underlying pattern changes.

## Pattern pages

Name pages with stable lowercase hyphenated IDs. Use this shape:

```markdown
# Pattern title

Status: provisional | corroborated | validated | superseded
Scope: affected task, module, runtime, account class, or model class
Last updated: ISO-8601 timestamp

## Problem

The observable behavior and its impact.

## Root cause

The first causal divergence supported by evidence.

## Evidence

### Failures

- `<raw-manifest-id>` — exact observation or action sequence.

### Successes and counterexamples

- `<raw-manifest-id>` — what worked differently or where the pattern does not apply.

## Reusable guidance

The narrow instruction that could change future agent behavior.

## Applicability limits

When the guidance must not be generalized.

## Open questions

Evidence still needed before promotion.
```

Update an existing page when new evidence shares the same root cause. Split a
page when apparently similar symptoms have different causes. Merge duplicates
without deleting their historical IDs; leave a short supersession pointer.

## Evolution log

Append one concise entry to `wiki/log.md` per pass:

```markdown
## <timestamp> — <pass-id>

- Evidence admitted: `<raw-id>`, ...
- Patterns created or updated: `<pattern-id>`, ...
- Candidate: `<candidate-id>` or `none`
- Gate outcome: accepted | rejected | insufficient-evidence
- Installed skill hash: `<sha256>` or `unchanged`
- Summary: one paragraph distinguishing observed, validated, and installed state.
```

The log is chronological and append-only. Corrections use a later entry.

## Skill impact ledger

`wiki/skill-impact.md` prevents rejected approaches from recurring without new
evidence:

```markdown
## <candidate-id>

- Timestamp: `<ISO-8601>`
- Target: `<maintained-skill-source>/genericclient-development/<file>`
- Patterns: `<pattern-id>`, ...
- Baseline skill hash: `<sha256>`
- Candidate diff: `../candidates/<candidate-id>/candidate.diff`
- Expected behavior change: ...
- Positive scenario: pass | fail — evidence
- Negative-trigger scenario: pass | fail — evidence
- Regression scenario: pass | fail — evidence
- Replayed failure invariant: pass | fail — evidence
- Outcome: accepted | rejected | insufficient-evidence
- Reason: ...
- Installed skill hash: `<sha256>` or `unchanged`
```

Do not erase rejected entries. A later proposal may revisit one only when it
names the new evidence or materially different intervention.

## Candidate directory

Use one directory per atomic proposal:

```text
candidates/<candidate-id>/
├── proposal.md
├── candidate.diff
├── validation.md
└── skill/
```

`skill/` is an isolated copy of the target skill. `proposal.md` maps evidence to
the intended behavior change. `validation.md` records scenario inputs,
observable outcomes, and the gate decision. Generate `candidate.diff` against
the installed baseline before promotion.

After acceptance, retain the candidate records for provenance. After rejection,
discard only disposable candidate working files if necessary; preserve the diff
and validation record referenced by `skill-impact.md`.

## Evidence and confidence rules

- Evidence strength must match claim breadth. A single incident can establish an
  observed failure but rarely a universal workflow rule.
- Safety-critical guidance may be promoted from one incident only when the root
  cause and invariant are directly verified and the downside of omission is
  material; record that rationale explicitly.
- Unit tests prove code-level behavior, not installed or live behavior.
- A built artifact is not an installed artifact; an installed artifact is not a
  loaded client; a loaded client is not a live account receipt.
- Repository state, installed skill state, and wiki state are separate hashes.

## Pruning

Do not delete raw manifests. Periodically consolidate or supersede redundant
wiki pages when routing becomes noisy. Keep the index short, preserve evidence
links, and retain the evolution and impact ledgers even when a pattern is
superseded.
