# OSRS PvP evolution profile

Evolution root:

```text
/home/user/.codex/ml-evolution/osrs-pvp
```

Target execution skill: `osrs-pvp-training`, resolved from the client catalog.

Authoritative state begins with the current Mac
`/Users/jarrett/osrs-pvp-sim/HANDOFF.md`, then live process and artifact state.
The Linux mirror and old threads are locators and evidence sources, not current
training authority.

## Evidence classes

- Frozen protocol, implementation, binary, plan, screen, and checkpoint hashes.
- Simulator/parity/determinism/optimizer/checkpoint tests.
- Calibration and heldout spools with seed and roster identity.
- Surrogate utility, confidence bounds, ESS, KL, clipping, and broad-harm rows.
- Combat evaluation by 1v1, 2v2, 3v3, 4v4, ruleset, loadout, side, opponent,
  and seed.
- Win-predictor AUROC, ECE, Brier score, and log loss.
- Promotion, quarantine, champion, and player-ready receipts.

## Required distinctions

- Harness failure versus policy failure.
- Nominal target versus achieved source state.
- Screening/selection data versus unopened confirmation data.
- Surrogate mechanism gate versus real combat gate.
- Exploratory intermediate checkpoint versus authorized candidate.
- Candidate versus sealed champion versus player-ready build.

## Skill-evolution invariant

A proposed procedure must preserve outcome blindness, disjoint heldouts,
preregistered gates, exact provenance, and the rule that non-combat experiments
report no new win rates. It must not weaken the player-ready thresholds or
authorize training on Linux.

## High-value recurring patterns

- Versioned protocol/checkpoint authorization drift.
- Continuity checks against nominal rather than achieved state.
- Intermediate-checkpoint rescue after terminal regression.
- Heldout identity, ordinal, roster, and source-direction mismatches.
- Mistaking surrogate improvement for combat improvement.
- Replaying or stitching interrupted runs without a frozen recovery rule.
