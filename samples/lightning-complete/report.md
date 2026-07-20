# PyTorch Lightning qualification

- Verdict: **VERIFIED**
- Scenario: `complete`
- Adapter: `pytorch-lightning`
- Control PID: `30976`
- Terminated PID: `17600`
- Recovery PID: `12104`
- Exact comparison: `atol=0.0`, `rtol=0.0`
- Verified persisted bytes: 22703 bytes

## Deterministic gate

- `checkpoint.model`: **PASS** — Model state is present
- `checkpoint.loop-state`: **PASS** — Loop state is present
- `checkpoint.optimizer`: **PASS** — Optimizer state is present
- `checkpoint.scheduler`: **PASS** — Scheduler state is present
- `checkpoint.rng`: **PASS** — RNG state is present
- `checkpoint.loss-history`: **PASS** — Loss history is present
- `process.real-termination`: **PASS** — Checkpoint worker was really terminated
- `process.distinct-recovery`: **PASS** — Recovery ran in a new process
- `progress.global-step`: **PASS** — Recovered global step matches control
- `trajectory.loss-history`: **PASS** — Loss history exactly matches control
- `state.trainable`: **PASS** — Trainable state digest exactly matches control
- `state.evaluation`: **PASS** — Evaluation digest exactly matches control
- `state.optimizer`: **PASS** — Optimizer digest exactly matches control
- `state.scheduler`: **PASS** — Scheduler digest exactly matches control

## Limitations

- Qualification covers the included CPU LightningModule, not arbitrary modules.
- The RNG bridge is explicit module checkpoint state required by this contract.
- The attestation is unsigned and provides integrity, not publisher authentication.
