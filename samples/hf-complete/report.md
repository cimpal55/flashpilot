# Hugging Face Trainer qualification

- Verdict: **VERIFIED**
- Scenario: `complete`
- Adapter: `huggingface-trainer`
- Control PID: `31380`
- Terminated PID: `32392`
- Recovery PID: `17736`
- Exact comparison: `atol=0.0`, `rtol=0.0`
- Verified persisted bytes: 41635 bytes

## Deterministic gate

- `checkpoint.model`: **PASS** — Model state is present
- `checkpoint.trainer-state`: **PASS** — Trainer state is present
- `checkpoint.optimizer`: **PASS** — Optimizer state is present
- `checkpoint.scheduler`: **PASS** — Scheduler state is present
- `checkpoint.rng`: **PASS** — RNG state is present
- `process.real-termination`: **PASS** — Checkpoint worker was really terminated
- `process.distinct-recovery`: **PASS** — Recovery ran in a new process
- `progress.global-step`: **PASS** — Recovered global step matches control
- `trajectory.loss-history`: **PASS** — Loss history exactly matches control
- `state.trainable`: **PASS** — Trainable state digest exactly matches control
- `state.evaluation`: **PASS** — Evaluation digest exactly matches control
- `state.optimizer`: **PASS** — Optimizer digest exactly matches control
- `state.scheduler`: **PASS** — Scheduler digest exactly matches control

## Limitations

- Qualification covers the included local CPU Trainer contract, not arbitrary scripts.
- Offline environment controls prevent library-mediated Hub access; this is not an OS network sandbox.
- The attestation is unsigned and provides integrity, not publisher authentication.
