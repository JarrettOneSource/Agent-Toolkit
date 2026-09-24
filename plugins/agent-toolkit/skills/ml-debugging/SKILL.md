---
name: ml-debugging
description: "Diagnose neural-network learning failures, incorrect policy behavior, checkpoint/resume problems, and training bottlenecks; inspect models and validate learning pipelines before expensive runs."
---

# ML Debugging

Find the first supported cause of an ML failure, or establish what a bounded validation actually proves. Use the affected implementation and an independent expected result. Distinguish numerical correctness, ability to learn a controlled task, game performance, and deployment readiness.

## Start from the actual run

Read the project's current handoff and relevant model/data contracts. Identify the executed source, checkpoint, observation/action schema, optimizer state, runtime, data roles and active jobs. An old report or checkpoint filename does not establish current authority or strength.

For OSRS, Clash and Solomon, use the authorized Mac for model execution, simulation, fitting, builds, tests and benchmarks; WSL is for inspection, editing and orchestration. Refresh the live host/resource instructions before launching work, preserve exclusive timing windows and frozen studies, and leave user-stopped jobs stopped. For other ML projects, use their own execution contract. An inspection does not authorize a new training campaign or promotion.

Resolve the maintained `ML-LAB` checkout on the execution host: `/home/user/ML-LAB` on WSL or `/Users/jarrett/ML-LAB` on the Mac. Read the guide paths below relative to that checkout, independently of this skill's plugin/cache location. Start with `TOOLS-AND-PATHS.md` for tool locations. If the lab is unavailable, state which instruments cannot be used and continue checks supported by the affected implementation.

Name the observed failure, expected behavior, and the smallest case that can distinguish plausible causes. Reuse accepted evidence for unchanged components. For a new or changed learning path, state a bounded control/pilot criterion before examining its outcome.

## Choose the discriminating check

Read the inspection guide (`ML-LAB/INSPECTION.md`) before using its CLI, API or trace schema. Use the debugging guide (`ML-LAB/DEBUGGING.md`) when the failure is not yet localized. Select the relevant row; this table is not a mandatory suite.

| Evidence or question | First useful check |
| --- | --- |
| Saved model looks corrupt or resume changes behavior | Inspect named tensors with `artifact`; compare compatible snapshots. For continuation, use the existing native check of model, buffers, optimizer, RNG, normalization and sampling position. Static weights alone are insufficient. |
| Loss is invalid, a component seems frozen, or updates look wrong | Capture a cloned parameter snapshot, relevant activations, gradients and the actual optimizer step. Use `audit_module_step` and `ActivationRecorder` for owned Python modules, or the existing native instrumentation for C++. Check custom derivatives with a small independent finite-difference fixture where differentiability permits. |
| Illegal/constant actions or suspicious PPO improvement | Export a bounded real decision batch. Audit permitted observations, masks, executed-command likelihood, unchanged-weight replay, targets and the declared PPO objective with `trace` and the project's native action-law qualifier. Locate the first collection/scoring/execution disagreement. |
| Memory, batching or resets behave strangely | Replay identical weights/history stepwise, as a sequence and in carried chunks. Compare hidden/cell state and outputs; interleave independent actors and reset only one to expose contamination. |
| The network does not learn a needed behavior | Check that permitted inputs/history contain the needed information. Fit a tiny known task through the actual affected learner and score it independently. Reference `probes` can check the diagnostic setup but do not qualify the production actor/collector. |
| Reward improves while useful play stalls | Inspect each reward component and the final transformed reward; measure opportunities, preparation, attempts and successes for the missing behavior. Compare true outcomes and declared null-progress cycles. |
| A run is slow or a change claims a speedup | Use existing native timers/profilers on the same representative work, account for asynchronous completion, and separate collection, inference, update and I/O. Keep activation hooks and other synchronizing diagnostics out of timing comparisons. |
| Predictions, representations or adaptation look convincing | Use whole-encounter splits, appropriate baselines and uncertainty. Separate frozen probes from encoder-capability tests and causal interventions; compare new-task learning with retained competence. Read the interpretation guide (`ML-LAB/INTERPRETATION.md`). |

Trace the implicated boundaries: permitted state → features → memory → policy/value → requested and executed action → reward/target → gradient → optimizer update → evaluation. Instrument enough intermediate state to identify the first divergence instead of inferring its location from the final score.

## Interpret checks without false confidence

- Declare which parameters must train in the chosen positive-control case. A head may learn on fixed random features despite a disconnected encoder. Check both gradient flow and actual parameter changes; unspecified inactive heads are not automatically failures.
- Treat zero gradients, constant features, low entropy and intentional mask infinities according to their role. A strict finite-tensor report is a finding to interpret, not a universal diagnosis. Sampled `old_logp - new_logp` can be negative; raw GAE need not have zero batch mean.
- Score the actual selection law. Logical-command likelihood uses consumed arguments; exact joint entropy/KL weights all legitimate branches by their prefix probabilities. Conditional-path metrics do not establish full joint entropy/KL, and an argmax choice is not a softmax sample.
- Distinguish a true terminal from an artificial continuing-task cutoff. Bootstrap the latter from the final pre-reset observation and stop advantage recursion at the boundary. Match the project's time units, actor ownership, estimator and value transform; the toolkit's raw-GAE oracle does not verify every native target variant.
- Verify collector/exporter provenance, observation visibility and recurrent history. Hand-authored fixtures validate the checker; production readiness needs the actual actor/collector path. Recheck the current integration state before assuming a real trace exporter exists.
- Preserve evaluation roles and the unit of independence. Adjacent frames do not constitute independent matches or human opponents; repeated tuning against a final panel changes what it can establish.

For deeper input-sufficiency, reward-cycle or plasticity questions, read the relevant section of the failure-case research (`ML-LAB/research/2026-09-15-pretraining-validation-tools.md`). Use the field guide (`ML-LAB/FIELD-GUIDE.md`) for module/target design. Verify uncertain library behavior against version-matched primary sources before changing the implementation. Read historical inspection results (`ML-LAB/INSPECTION-RESULTS.md`) only when their controls or identities are relevant; their passes are not current model qualification.

## Validate the explanation and finish

For a new diagnostic or learning seam, pair the smallest positive control with a relevant deliberate fault where practical. Inject faults only into disposable fixtures/models. The fault should fail at the intended check and the restored control should pass. If it does not distinguish the explanations, revise the diagnostic before treating its score as evidence.

When fixing a defect, correct the owning path, remove unsuccessful experimental changes, and rerun the original failing case plus affected project checks. When validating a changed learner before scaling, follow passing contract checks with a tiny known-solution task through that learner and a short representative game pilot under the normal project workflow. Define the pilot's budget and criterion; a successful reference learner is not a substitute. Reuse valid prior checks when the relevant implementation and conditions are unchanged.

Save identified inputs, commands, versions, hypotheses, expected/observed results, first divergence, and scoped conclusions in the existing project diagnostic area or `ML-LAB/inspection-runs`. The toolkit writes immutable HTML/JSON reports: exit 0 means exercised checks passed, 1 means findings, and 2 means the operation stopped. Inspect `not_checked`; none of these outcomes supplies training or promotion authority.

Finish the requested inspection with an evidence-backed finding and its limits, or the requested fix with the original behavior and relevant checks verified. Explain what was checked, what remains unexercised and which next action the evidence supports. Resume the authorized project task once the diagnosed issue is resolved; optional diagnostics do not become new prerequisites. Maintain the shared guides/tools as the source of truth rather than copying them into this skill.
