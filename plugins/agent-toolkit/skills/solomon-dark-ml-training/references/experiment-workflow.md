# Solomon Dark ML Training

Improve the learned Website bot without confusing sampled reward, deterministic
strength, packaged compatibility, or production state.

## Start from current evidence

1. Read the current ML handoff and experiment root on the Mac. Verify live
   processes, output directories, checkpoint counts, repository commit, dirty
   state, and artifact hashes before acting.
2. Treat `/home/user` and Windows/WSL copies as inspection and orchestration
   surfaces. Run CPU-heavy training, simulator campaigns, deterministic arenas,
   holdouts, and relevant test suites on the Mac mini.
3. Keep the Website repository as the maintained runtime authority. Do not write
   ML implementation or documentation into Mod Loader.
4. Treat experiment branches, packaged server assets, deployed production, and
   live game behavior as separate states.

For the evaluation and promotion contract, read
[references/evaluation-and-promotion.md](evaluation-and-promotion.md).

## Preserve the intended learning problem

- Train separate normal starts for Fire, Water, Lightning, Ether, and Earth.
- Allow natural discovery of additional primaries, Welds, secondary spells,
  skills, consumables, and equipment through authoritative game progression.
- Let the policy learn primary selection and Concentrate A/B swapping when legal
  alternatives exist.
- Keep combat/action learning distinct from skill-choice and loadout-choice
  learning so sparse choice events do not silently contaminate combat updates.
- Preserve masks, observation schema, action semantics, recurrence/state, and
  checkpoint compatibility as explicit versioned contracts.
- Make new spells learnable through data-driven schema/mask support rather than
  per-spell hard-coded policy behavior.

Use scripted navigation or steering only when the frozen experiment declares it
as an input or baseline. Do not call scripted behavior learned policy skill.

## Design one controlled experiment

Before training, freeze:

- exact source commit, checkpoint, trainer state, policy/schema version, and
  hashes;
- starting elements and tensor/optimizer scope;
- environment and action RNG seeds;
- worlds, workers, rollout horizon, action repeat, PPO settings, reward
  semantics, and KL/clip stops;
- whether skill/loadout choice heads are trainable or frozen;
- checkpoint cadence and interruption behavior;
- deterministic screen seeds and disjoint holdout seeds;
- primary metric, regressions, minimum material improvement, and production
  boundary.

Change one causal family at a time. Reward semantics, optimizer/consolidation,
observation/action schema, curriculum, and source checkpoint changes are
different experiments.

When an unproven optimizer, auxiliary objective, or reward-credit method follows
observed sampled-versus-argmax divergence, cap its first pilot at one
checkpoint-producing update and screen it immediately against the accepted
baseline. Resume a multi-update campaign only after a material deterministic
win; a tie, return-only ranking, or required-metric regression stops the pilot.
This gate does not interrupt a frozen campaign using an already validated
method.

## Interpret training conservatively

Training completion proves only that the campaign executed. Sampled batch
return, kills, wave depth, release rate, or reward totals are diagnostics, not
acceptance.

After training:

1. audit checkpoint count, trainer state, tensors, schema, and expected isolation;
2. screen baseline and informative intermediate checkpoints under deterministic
   argmax on the frozen train arena;
3. reject ties won only by a return tie-break unless that was preregistered as
   material progression;
4. evaluate genuine train winners on disjoint holdout seeds;
5. compare wave depth, completed waves, kills, survival, releases, resource use,
   choices, and regressions together;
6. select the best evidenced checkpoint, not automatically the newest or final
   checkpoint.

When wave depth improves but kills or another required metric regresses, report
the tradeoff and apply the frozen gate. Do not hide it behind a composite score.

## Failure classification

Identify whether the cause is:

- simulator/gameplay fidelity;
- observation, action, mask, target, or recurrence contract;
- reward/credit assignment;
- optimizer, KL, clipping, entropy, or value health;
- choice-event sparsity or head ownership;
- deterministic versus stochastic policy behavior;
- experimental selection or holdout leakage;
- checkpoint/schema packaging;
- production/runtime integration;
- machine/job state.

Do not respond to a reward-credit failure with more consolidation passes, or to
a packaged schema mismatch by weakening the decoder.

## Monitoring

Use `start_job` and `wait_job` when remaining active. Use `monitor` only
when ending the turn immediately for its callback. Treat a wait timeout as an
observation of the same job, and report requested status before waiting again.
Do not start duplicate trainers. If a job outlives the Codex turn,
record its exact command, PID/job identity, output path, expected boundary, and
safe continuation instructions.

Do not delete completed checkpoints before deterministic screening. Preserve
failed methods and their exact results long enough to avoid repeating them.

## Production boundary

Training and evaluation never authorize production replacement by themselves.
Before packaging or promotion, validate the checkpoint against the exact Website
decoder/schema, canonical tests, Python/TypeScript inference parity, browser
runtime, and rollback path. Replace the production checkpoint only when the user has authorized that
replacement, including authorization already supplied in the session.

Do not preserve a decoder fallback for obsolete checkpoints unless the user
explicitly asks for dual-version support. Prefer one verified packaged schema.

## Evidence isolation and workflow evolution

Ordinary ML work uses this skill, the current handoff, and the frozen experiment.
Do not load `/home/user/.codex/ml-evolution/solomon-dark/wiki/` during training or
evaluation. When the user asks to consolidate cross-run lessons or improve this
procedure, use `ml-experiment-skill-evolution` with the Solomon profile.

Do not add a permanent rule from one noisy campaign during the campaign itself.
Preserve exact evidence for the later evolution pass.

## Finish cleanly

Update the handoff with current Mac state, exact checkpoints/artifacts, completed
and pending evaluation, production status, and the next authorized action. Keep
implemented, trained, screened, heldout-validated, packaged, production-loaded,
and live-proven states separate.
