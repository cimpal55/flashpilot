# Hugging Face Trainer qualification

- Verdict: **FAILED**
- Scenario: `model-only`
- Adapter: `huggingface-trainer`
- Control PID: `22864`
- Terminated PID: `17432`
- Recovery PID: `6272`
- Exact comparison: `atol=0.0`, `rtol=0.0`
- Verified persisted bytes: not reported because recovery did not pass

## Deterministic gate

- `checkpoint.model`: **PASS** — Model state is present
- `checkpoint.trainer-state`: **PASS** — Trainer state is present
- `checkpoint.optimizer`: **FAIL** — Optimizer state is present
- `checkpoint.scheduler`: **FAIL** — Scheduler state is present
- `checkpoint.rng`: **FAIL** — RNG state is present
- `process.real-termination`: **PASS** — Checkpoint worker was really terminated
- `process.distinct-recovery`: **PASS** — Recovery ran in a new process
- `progress.global-step`: **PASS** — Recovered global step matches control
- `trajectory.loss-history`: **FAIL** — Loss history exactly matches control
- `state.trainable`: **FAIL** — Trainable state digest exactly matches control
- `state.evaluation`: **FAIL** — Evaluation digest exactly matches control
- `state.optimizer`: **FAIL** — Optimizer digest exactly matches control
- `state.scheduler`: **FAIL** — Scheduler digest exactly matches control

## Limitations

- Qualification covers the included local CPU Trainer contract, not arbitrary scripts.
- Offline environment controls prevent library-mediated Hub access; this is not an OS network sandbox.
- The attestation payload has no embedded signature; detached Ed25519 verification requires an explicitly trusted public key.
