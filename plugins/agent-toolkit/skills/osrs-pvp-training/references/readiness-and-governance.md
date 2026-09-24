# OSRS PvP readiness and governance

## Execution hosts

- Mac authoritative repository: `/Users/jarrett/osrs-pvp-sim`
- Linux mirror/inspection repository: `/home/user/osrs-pvp-sim`
- Simulator, training, evaluation, and tests run only on the M2 Mac mini.

Re-check the current Mac handoff and live job state before using any version,
checkpoint, or experiment path from an older session.

## Player-ready combat contract

A candidate is player-ready only when heldout evaluation proves:

- at least 90% decisive true wins overall;
- at least 90% in 1v1;
- at least 90% across combined 2v2–4v4 team play;
- no broad required slice below 85% or materially regressed from the accepted
  parent;
- random unseen loadouts;
- `general_pvp` and `lms` rulesets;
- both team sides;
- strong frozen historical opponents, not weak bots;
- disjoint seeds with Wilson confidence intervals;
- at least 1,000 decisive fights per required aggregate.

Mirror and self-play results are reported separately and do not replace these
gates.

## Win-predictor contract

The predictor must:

- improve heldout log loss and Brier score over the constant baseline and the
  accepted V61 reference;
- reach AUROC at least 0.80;
- reach ECE at most 0.05;
- replicate on at least two of three seeds;
- introduce no material policy or combat regression.

Report calibration and discrimination together. A high AUROC with poor
calibration is not sufficient.

Before accepting predictor gains, reconstruct the declared constant and
calibrated-reference predictions from their bound datasets and saved
fit/calibration parameters. Require those predictions to match the stored
baseline logits before comparing independently recomputed metrics; internally
consistent metrics alone do not verify the named baselines. Do not refit on
heldout data or rerun valid collections to perform this check.

## Required native gates

Before an unbounded lineage or promotion, preserve all current handoff gates for:

- deterministic inference;
- simulator and Python-oracle parity;
- observation, action, mask, and roster contracts;
- optimizer continuity and named state;
- checkpoint schema, corruption rejection, and resume;
- provenance and exact artifact identity;
- numerical health, ESS, importance sampling, KL, clipping, and finite values;
- end-to-end throughput and the current five-input gate.

Do not weaken a gate merely because a candidate is promising.

## Scientific state labels

```text
planned
preflight-valid
running
interrupted
mechanism-pass
mechanism-fail
confirmation-pass
confirmation-fail
combat-pass
combat-fail
promotion-candidate
promoted
sealed-champion
player-ready
```

Use only the strongest label proven by current artifacts.

## Intermediate checkpoint governance

An intermediate checkpoint discovered by inspecting a failed lineage is an
exploratory hypothesis. It may receive one preregistered fresh confirmation,
but no fallback ladder on the same unopened data. A pass can authorize a new
combat protocol; it cannot retroactively amend the failed parent study or
directly promote the checkpoint.

## Interrupted-run governance

If a process stops before its terminal result:

1. preserve the run directory and record the interruption;
2. verify which artifacts are complete and which telemetry is missing;
3. follow a preregistered resume rule if one exists;
4. otherwise replay the exact frozen experiment separately and compare the
   reproduced prefix;
5. never infer missing metrics from checkpoints or combine partial telemetry
   without a new, explicit protocol.

## Completion report template

```text
Experiment:
Stage:
Outcome:
Combat win rates measured: none | exact bracket table
Policy/surrogate metrics:
Health and provenance:
Work since last update:
Next authorized step:
Blockers:
Watch items:
Candidate/promotion state:
```
