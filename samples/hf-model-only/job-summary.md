# FlashPilot CI summary

- Outcome: **FAILED**
- Evidence kind: `hf-qualification`
- Framework: `huggingface-trainer`
- Qualification profile: `exact-training-resume`
- Checks: `5/13` non-failing
- RPO: `0` steps
- RTO: `6.757010` seconds

## Exact failed requirements

- `checkpoint.optimizer` — Optimizer state is present
- `checkpoint.scheduler` — Scheduler state is present
- `checkpoint.rng` — RNG state is present
- `trajectory.loss-history` — Loss history exactly matches control
- `state.trainable` — Trainable state digest exactly matches control
- `state.evaluation` — Evaluation digest exactly matches control
- `state.optimizer` — Optimizer digest exactly matches control
- `state.scheduler` — Scheduler digest exactly matches control

This summary is derived from the same typed evidence used by the local CLI.
