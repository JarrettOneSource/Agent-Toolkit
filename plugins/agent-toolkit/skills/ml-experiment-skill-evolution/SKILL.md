---
name: ml-experiment-skill-evolution
description: "Improve OSRS PvP, Solomon Dark, or Clash Royale training skills from cross-run evidence. Excludes running experiments or promoting checkpoints."
---

# ML Experiment Skill Evolution

Improve the procedure used to design, run, interpret, and promote ML
experiments. Model weights and checkpoints are experiment artifacts; they are
not the Codex skill being evolved.

## Select one isolated profile

Choose exactly one project and read only its profile:

- OSRS PvP: [references/osrs-pvp.md](references/osrs-pvp.md)
- Solomon Dark: [references/solomon-dark.md](references/solomon-dark.md)
- Clash Royale: [references/clash-royale.md](references/clash-royale.md)

Never merge their wikis. They may share artifact formats, but their simulator
semantics, metrics, reward systems, failure modes, and promotion gates are not
interchangeable.

Read [references/wiki-schema.md](references/wiki-schema.md) when creating or
editing evolution artifacts.

## Keep execution and evolution separate

Each profile has three layers:

- **Raw:** immutable manifests referencing rollouts, protocols, checkpoints,
  metrics, logs, machine receipts, and evaluation results.
- **Wiki:** consolidated causal patterns, successful strategies, rejected
  experiment designs, counterexamples, and an impact ledger.
- **Skill:** the concise approved training procedure used by ordinary Codex
  training turns.

Ordinary training agents receive only their approved project skill and current
handoff/protocol. Do not inject the wiki into training, monitoring, or
evaluation turns. The maintainer and proposer may read it during a deliberate
evolution pass.

Never store hidden reasoning, credentials, account identities, session tokens,
private keys, or copied secrets. Reference sensitive sources through sanitized
evidence with stable hashes.

## Evolution pass

### 1. Freeze the evidence set

Resolve the current thread, handoff, repository state, machine, job status, and
artifact paths. Verify hashes and timestamps before relying on them. Admit only
evidence actually used in the pass, and record whether it is observed,
validated, accepted, promoted, or live-proven.

Do not change a stopped, paused, or running experiment merely to improve the
evidence set. Starting, resuming, stopping, deleting, or publishing anything
requires separate task authority.

### 2. Consolidate causal knowledge

Compare successful and failing experiments at their first causal divergence.
Separate at least these categories:

- implementation or harness failure;
- simulator or observation-contract error;
- optimization-health failure;
- statistical or experimental-design failure;
- genuine policy regression or improvement;
- publication, installation, or production-state mismatch.

Update an existing pattern when the cause is the same. Create a new pattern only
for a distinct reusable lesson. Record counterexamples and applicability limits.
One run may justify an observed pattern, but not a broad permanent instruction
unless the invariant is directly verified and the risk warrants it.

Update the wiki index and chronological log. Preserve rejected candidates and
why they failed so they are not repeated without new evidence.

### 3. Propose one procedural change

Read the wiki index, impact ledger, relevant patterns, current target skill, and
minimum supporting raw evidence. Propose one atomic patch to one cohesive seam
in the project training skill or its references.

The proposal must identify:

- evidence and pattern IDs;
- the decision it changes;
- positive and negative applicability conditions;
- expected benefit and regression risks;
- objective acceptance scenarios.

Do not copy experiment chronology into the execution skill. Promote the
smallest durable procedure that would have changed the relevant decision.

### 4. Gate in isolation

Apply the patch to an isolated copy of the target skill. Validate it with:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" <candidate-skill-directory>
```

When that Codex validator is unavailable, use the current client's skill or
plugin validator. Resolve target skills from the client catalog and edit their
maintained source checkout when they are distributed by a plugin.

Exercise:

- a positive scenario derived from the causal failure;
- a negative scenario where the instruction must not fire;
- an ordinary training or evaluation scenario that must remain unchanged;
- the project-specific invariant named by the profile.

Prefer behavioral decisions and artifact interpretation over wording checks.
Do not launch an expensive training run solely to validate a Codex skill edit.
If model-side evidence is required, record the proposal as provisional until an
independently authorized experiment supplies it.

### 5. Accept or roll back

Accept only a demonstrable procedural improvement with no material regression.
On acceptance, apply the smallest patch to the installed project skill, validate
it, and record the diff, scenarios, outcome, and installed hash. On rejection,
discard the skill patch but retain all wiki and impact records.

Skill acceptance does not promote a model checkpoint. Checkpoint evaluation and
promotion remain governed by the project execution skill.

## Finish

End after one atomic proposal is accepted, rejected, or classified as
insufficient-evidence and all manifests, patterns, index entries, log entries,
and impact records agree. Do not manufacture follow-on training to force a
conclusion.
