# OSRS PvP Training

Move the native PvP learner toward verified player readiness without confusing
infrastructure, surrogate improvement, combat performance, or promotion.

## Start from authoritative state

1. Read the top **Current authoritative state** section of the Mac
   `/Users/jarrett/osrs-pvp-sim/HANDOFF.md`.
2. Verify current Mac process/job state, repository/worktree identity, artifact
   mtimes, hashes, and free resources. A handoff can lag a live job.
3. Inspect `/home/user/osrs-pvp-sim/HANDOFF.md` only as a mirror/locator unless
   its hash is verified against the Mac.
4. Preserve frozen champions, experiment directories, protocols, results, and
   unrelated work.

Run simulator, training, evaluation, and tests only on the M2 Mac mini. Linux is
for inspection, editing, orchestration, and artifact reconciliation. Do not
silently move a workload to Windows, WSL, ROCm, or Python because a Mac run is
slow or blocked.

For exact readiness, evidence, and reporting requirements, read
[references/readiness-and-governance.md](readiness-and-governance.md).

## Pipeline ownership

- Native C++ owns simulation, batched actor/critic inference, trajectory
  storage, GAE, PPO updates, and production checkpoint execution.
- Python is the correctness, differential-testing, statistics, evaluation, and
  promotion oracle. Do not restore per-tick Python orchestration or resume
  Python-simulator training as a workaround.
- A checkpoint, optimizer state, protocol, plan, screen receipt, evaluation,
  and champion record are separate artifacts with separate identities.

## Design experiments before opening outcomes

Freeze a protocol before training or evaluation. It must identify:

- source and anchor checkpoints plus logical identity;
- named optimizer state and resume semantics;
- implementation and executable hashes;
- roster, loadout, ruleset, team-side, and seed generation;
- training, calibration, screening, confirmation, and combat partitions;
- heldout identity and disjointness;
- metric definitions, confidence intervals, health gates, broad-harm gates,
  and stop conditions;
- checkpoint publication authorization;
- interruption and recovery behavior.

Do not amend a protocol after seeing protected outcomes. A harness bug may be
repaired only when the fix preserves the frozen scientific question and the
protected outcomes remain unopened; record the failed attempt and exact repair.

## Close transfer risk before extended training

Before authorizing an unbounded lineage or one projected to run longer than one
workday, require a frozen target-surface conformance bundle:

- calibration and disjoint validation traces from the target client/server;
- an exact deployment mapping for every actor observation and five-input logical
  action, including measured delay, missingness, legality, reset, and acceptance;
- controlled one-step and short-horizon mechanics/event comparisons;
- fixes for known mismatches and domain randomization only for residual
  uncertainty supported by calibration traces, with a nominal parity lane kept;
- shadow inference, a deterministic action-executor canary, and a bounded
  zero-authority policy canary before the next training-budget rung.

An RSPS bridge can be an integration rung but is not proof of the target client.
Python/C++ parity and Wiki-rule agreement likewise do not prove deployment
fidelity. If the target surface is unavailable, keep work to bounded
preflight/mechanism/ceiling studies that cannot authorize a long lineage or
promotion; record transfer evidence as missing. Fix a pure client-executor bug
at that seam rather than automatically retraining the strategic policy.

## Interpret the right evidence layer

Use these stages explicitly:

```text
preflight -> mechanism/surrogate training -> unopened confirmation -> combat gate -> promotion -> player-ready
```

- Preflight proves contracts, not learning.
- Surrogate utility proves only the preregistered surrogate claim.
- An exploratory intermediate selected on one result needs fresh unopened
  confirmation before combat evaluation.
- Combat success requires true decisive wins by the requested brackets.
- Promotion requires all policy, predictor, determinism, provenance, safety,
  and regression gates.

Classify a failure before responding: harness, simulator/parity, checkpoint,
optimizer, experimental design, statistical uncertainty, policy regression, or
machine/access state. Do not call a harness exception a model failure, and do
not switch languages to solve a governance error.

## Monitoring and interruptions

Use `start_job` and `wait_job` when remaining active. Use `monitor` only
when ending the turn immediately for its callback. A wait timeout observes the
same job; do not restart it. Report requested status before waiting again. Report meaningful boundaries and final outcomes. If the user needs
the Mac, preserve state only when the process supports it and state exactly what
CPU, RAM, disk, and swap are or are not released.

For an interrupted run, use only a recovery path frozen in advance. Otherwise
preserve the prefix and perform a clean exact replay or design a new protocol;
do not stitch telemetry or invent continuation rules after the crash.

Consult Fable or Claude only as a second opinion for genuinely high-impact
architecture, curriculum, promotion, rollback, or statistical-design forks.
Codex remains responsible for the decision and verifies every claim.

## Reporting

After every completed experiment or training session, report:

- win percentages for every combat bracket actually evaluated;
- explicitly **none measured** when the stage was non-combat;
- work completed since the prior user update;
- next action;
- current blockers and watch items, separately;
- candidate, quarantine, promotion, and champion state.

Never reuse old win rates as if the current experiment measured them.

## Promotion and readiness

Quarantine new checkpoints until the complete gate passes. Do not promote a
noisy `best_eval` artifact, self-play proxy, weak-opponent result, or same-data
checkpoint selection. Preserve the accepted parent and seal rejected branches.

Player readiness means the exact contract in the governance reference, not
“learning looks healthy,” a promising pilot, or infrastructure completion.

## Evidence isolation and workflow evolution

Ordinary training uses this skill and the current frozen protocol. Do not load
`/home/user/.codex/ml-evolution/osrs-pvp/wiki/` into training or evaluation
turns. When the user asks to consolidate cross-run lessons or improve this
procedure, use `ml-experiment-skill-evolution` with the OSRS profile.

Do not modify this skill automatically during an experiment. Preserve exact
evidence for a later evolution pass instead.

## Finish cleanly

Update the Mac handoff with only verified state, current jobs, exact hashes,
results, and the next authorized boundary. Keep investigated, implemented,
tested, trained, evaluated, promoted, and player-ready states distinct.
