---
name: genericclient-skill-evolution
description: "Improve the GenericClient development skill from evidence across runs. Excludes routine coding, account automation, and releases."
---

# GenericClient Skill Evolution

Evolve the installed `genericclient-development` skill from accumulated evidence
without exposing its full historical wiki to ordinary execution turns.

## Keep the layers separate

Use `~/.codex/genericclient-evolution` as the persistent evolution
workspace. Maintain three distinct layers:

- **Raw:** immutable evidence manifests that identify source rollouts, logs,
  receipts, tests, screenshots, and outcomes. Never store hidden reasoning,
  credentials, account names, session material, or copied secrets.
- **Wiki:** consolidated success and failure patterns, root causes, rejected
  interventions, counterexamples, and evolution history.
- **Skill:** the approved `genericclient-development` guidance. Resolve its
  installed location from the client catalog and edit its maintained source
  checkout when it is distributed by a plugin.

Ordinary GenericClient execution must use only the approved development skill.
Do not load the evolution wiki into routine coding or live-client turns. The
wiki is evidence for maintainers and proposers, not an extra runtime prompt.

For the workspace layout and exact artifact formats, read
[references/wiki-schema.md](references/wiki-schema.md).

## Evolution workflow

### 1. Establish the evidence set

Inspect the current installed skill, the requested evolution objective, and the
specific historical runs placed in scope. Resolve current paths and hashes; do
not assume an older rollout, repository checkout, installed JAR, or live account
state is still current.

Create immutable raw manifests for evidence that is actually used. Prefer
references to existing append-only rollout files and logs over duplicating
them. If a source contains sensitive material, create a sanitized evidence
artifact and record only its path and hash.

Classify every receipt precisely:

```text
observed -> corroborated -> candidate -> validated -> accepted -> installed -> live-proven
```

Do not promote a finding beyond the evidence available.

### 2. Maintain the wiki

Compare successful and failing traces. Diagnose the first causal divergence,
not merely the final error message. Record concrete action patterns, relevant
environment state, why the behavior occurred, the narrowest reusable guidance,
and conditions under which that guidance does not apply.

Update an existing pattern when the root cause is the same. Create a new page
only for a distinct, generalizable pattern. Keep provisional findings in the
wiki; one incident does not automatically become a universal skill rule.

Update the wiki index and chronological log on every evolution pass. The index
entry must let a proposer judge relevance without loading the full page. Keep
rejected proposals and their validation outcomes in `skill-impact.md` so they
are not repeated without new evidence.

### 3. Propose one atomic change

Before proposing anything, read:

1. `wiki/index.md`;
2. `wiki/skill-impact.md`;
3. the relevant pattern pages;
4. the current target skill file or reference;
5. the minimum raw evidence needed to verify the root cause.

Produce one candidate that targets one cohesive instruction seam. Prefer a
narrow patch to an existing section or reference. Create a new reference only
when conditional detail would otherwise bloat `SKILL.md`. Do not copy the wiki,
case history, or project documentation into the execution skill.

The proposal must state:

- the pattern IDs and exact evidence supporting it;
- the decision or behavior it is meant to change;
- when it applies and when it must not apply;
- the expected improvement and likely regression risks;
- the validation scenarios that will decide acceptance.

Skill evolution does not authorize GenericClient product changes, live account
actions, publication, or memory updates. Obtain the authority required for
those separately.

### 4. Gate the candidate

Apply the proposal first to an isolated candidate copy. Validate frontmatter and
structure with:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" <candidate-skill-directory>
```

When that Codex validator is unavailable, use the current client's skill or
plugin validator. Exercise realistic scenarios proportional to the change:

- a positive trigger where the new guidance should alter the decision;
- a negative trigger where this skill must not activate or interfere;
- an ordinary GenericClient regression scenario;
- a previously failing evidence case, replayed or checked against its exact
  observable invariant.

Prefer observable behavior over wording assertions. Use an independent
forward-test only when it adds material confidence and the user has authorized
delegation; it is not mandatory.

Accept the proposal only when it produces a demonstrable improvement without a
material regression. Treat a neutral foundational proposal as unaccepted unless
the user explicitly chooses to promote it. On rejection, discard the candidate
skill change but retain the wiki updates and a complete impact record.

### 5. Promote and record

Promote an accepted candidate with the smallest patch to the installed skill.
Run `quick_validate.py` on the installed skill and inspect the final diff. Record
the candidate diff, validation evidence, outcome, and resulting skill hash in
`wiki/skill-impact.md`; append the decision to `wiki/log.md`.

Report installed, validated, published, and live-proven states separately. Do
not describe an accepted local skill edit as product behavior or a live account
receipt.

## Stopping conditions

Finish an evolution pass when one atomic proposal has been accepted or rejected
and all wiki/impact records are consistent. If evidence is insufficient, record
a provisional pattern and stop without modifying the installed skill. Do not
manufacture more GenericClient or live account work merely to justify a skill
change.
