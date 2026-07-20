# PyTorch Lightning qualification

- Verdict: **FAILED**
- Scenario: `weights-only`
- Adapter: `pytorch-lightning`
- Control PID: `9280`
- Terminated PID: `32492`
- Recovery PID: `24156`
- Exact comparison: `atol=0.0`, `rtol=0.0`
- Verified persisted bytes: not reported because recovery did not pass

## Deterministic gate

- `checkpoint.model`: **PASS** — Model state is present
- `checkpoint.loop-state`: **PASS** — Loop state is present
- `checkpoint.optimizer`: **FAIL** — Optimizer state is present
- `checkpoint.scheduler`: **FAIL** — Scheduler state is present
- `checkpoint.rng`: **FAIL** — RNG state is present
- `checkpoint.loss-history`: **FAIL** — Loss history is present
- `process.real-termination`: **PASS** — Checkpoint worker was really terminated
- `process.distinct-recovery`: **PASS** — Recovery ran in a new process
- `progress.global-step`: **PASS** — Recovered global step matches control
- `trajectory.loss-history`: **FAIL** — Loss history exactly matches control
- `state.trainable`: **FAIL** — Trainable state digest exactly matches control
- `state.evaluation`: **FAIL** — Evaluation digest exactly matches control
- `state.optimizer`: **FAIL** — Optimizer digest exactly matches control
- `state.scheduler`: **FAIL** — Scheduler digest exactly matches control

## Limitations

- Qualification covers the included CPU LightningModule, not arbitrary modules.
- The RNG bridge is explicit module checkpoint state required by this contract.
- The attestation is unsigned and provides integrity, not publisher authentication.
