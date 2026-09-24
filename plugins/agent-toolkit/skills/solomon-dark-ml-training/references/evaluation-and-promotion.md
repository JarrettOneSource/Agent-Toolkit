# Solomon Dark ML evaluation and promotion

## State layers

Use these labels explicitly:

```text
planned
preflight-valid
training
training-complete
screened-train-winner
heldout-winner
packaging-candidate
packaged
production-installed
live-proven
rejected
```

A later label requires direct evidence and does not follow automatically from an
earlier one.

## Training campaign receipt

Record:

- source commit and checkpoint/trainer-state hashes;
- policy, observation, action, mask, and metrics schema versions;
- exact argv/config and machine;
- starting elements and trainable/frozen parameter scopes;
- environment steps, update numbers, checkpoint list, completion state;
- PPO health, KL maxima, clipping, entropy, gradient/value health;
- reward terms and authoritative gameplay counts;
- learned choice opportunities, selected actions, and switch rates;
- output paths and hashes.

Do not rank checkpoints from these sampled training rows alone.

## Deterministic screen

Screen the accepted baseline plus preregistered informative checkpoints on the
same fixed seeds and horizon. Report per checkpoint:

- mean and maximum wave;
- completed waves;
- kills by enemy kind and total;
- deaths/survival and terminal state;
- primary releases/holds;
- spell and loadout actions;
- pickups, consumables, items, skills, and resource use;
- return only as a diagnostic or declared tie-break.

The screen chooses candidates for holdout; it does not prove generalization.

## Holdout

Holdout seeds are disjoint from training and deterministic screening. They must
not be inspected to choose a checkpoint before the protocol allows it. Compare
the candidate with the exact accepted baseline and report uncertainty when the
sample supports it.

A material winner should improve the preregistered progression metric without a
disallowed regression in combat throughput, survival, spell use, choice
behavior, or element coverage. A return-only tie-break is not material unless
the protocol says so in advance.

## Element and head isolation

For element-specialization experiments, verify that only the intended element
adapter/tensors changed. Shared, other-element, choice, and frozen heads must
remain byte/logically identical when declared frozen.

For skill/loadout-choice experiments, report actual legal alternatives and
selected actions. A high decision count with zero alternatives does not prove
learned swapping.

## Reward changes

Audit each reward term against the scale and frequency of ordinary combat
events. A terminal penalty or bonus that outweighs dozens of ordinary events can
erase useful credit differences. After changing reward semantics, rerun a
controlled comparison; healthier sampled return alone is insufficient.

## Packaging and production

Before packaging:

- exact decoder/checkpoint schema match;
- TypeScript and Python inference parity;
- deterministic checkpoint load and corruption rejection;
- canonical Website tests and production build;
- browser runtime acceptance with no model-load error;
- rollback artifact and prior production hash retained.

Packaging, merging, pushing, deploying, and replacing the production checkpoint
are separate actions. Obtain the authority appropriate to each.

## Report template

```text
Experiment:
Training state:
Checkpoints produced:
Sampled diagnostics:
Deterministic screen:
Disjoint holdout:
Element/head isolation:
Winner/rejection decision:
Packaging/production state:
Next action:
Blockers and watch items:
```
