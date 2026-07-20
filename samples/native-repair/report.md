# FlashPilot bounded repair report

The failure is intentional and deterministic, but GPT-5.6 does not receive the injection label. It receives only the sanitized checkpoint manifest, restore behavior, failed Recovery Gate checks, and trajectory evidence.

Final verdict: **VERIFIED**

Only the deterministic Recovery Gate sets this verdict; the replayed GPT-5.6 response does not declare recovery.

## Initial failure

- Worker PID: 31412
- Recovery PID: 16600
- Gate passed: False
- Failed checks: state.optimizer, state.scheduler, state.python_rng, state.numpy_rng, state.torch_rng, trajectory.final_trainable, trajectory.final_evaluation, trajectory.loss_history, contract.no_mandatory_omission

## Bounded repair

- Provider mode: fixture replay of an accepted secret-free GPT-5.6 structured response
- Captured response ID: resp_0d7e808cd722f97f016a5a90f0300481908d22e7befa15e3fe
- Proposed actions: change_supported_checkpoint_strategy, persist_optimizer_state, persist_scheduler_state, persist_python_rng_state, persist_numpy_rng_state, persist_torch_rng_state, restore_state_before_next_batch
- Applied actions: persist_optimizer_state, persist_scheduler_state, persist_python_rng_state, persist_numpy_rng_state, persist_torch_rng_state, restore_state_before_next_batch
- Unsupported actions: change_supported_checkpoint_strategy
- Rejected actions: none
- Repair attempts: 1
- New strategy ID: native-repaired-complete-v1
- include_optimizer: True
- include_scheduler: True
- include_python_rng: True
- include_numpy_rng: True
- include_torch_rng: True
- restore_before_next_batch: True

## Repaired verification

- Worker PID: 27632
- Recovery PID: 31396
- Gate passed: True
- Exact atol/rtol: 0.0/0.0
- Original failed checkpoint unmodified: True

## Post-verification storage measurement

- safe_full recurring logical bytes: 44998
- repaired recurring logical bytes: 27681
- one-time frozen base bytes: 18475
- structural reduction: 17317 bytes (38.48%)

## Measurement limitation

Logical checkpoint bytes were measured in the controlled demo. Physical NAND writes, write amplification, and SSD lifetime were not measured.
