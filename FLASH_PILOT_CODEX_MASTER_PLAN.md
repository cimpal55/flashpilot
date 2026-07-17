# FlashPilot — Codex Master Build Plan (V4 Final)

**Project:** FlashPilot — AI Checkpoint Reliability & Storage Autopilot  
**Hackathon:** OpenAI Build Week  
**Track:** Developer Tools  
**Implementation language:** Python 3.11  
**Primary framework:** PyTorch, CPU-only for P0  
**Primary build environment:** one official Codex thread  
**Submission deadline:** July 21, 2026 at 5:00 PM PDT  
**Riga equivalent:** July 22, 2026 at 03:00  
**Status:** scope-locked; this document supersedes V2, V3, and all prior amendments  

---

# 0. How to use this plan

1. Create a repository named `flashpilot`.
2. Put this file in the repository root as:

   ```text
   FLASH_PILOT_CODEX_MASTER_PLAN.md
   ```

3. Open the official Codex app, CLI, IDE extension, or SDK in that repository.
4. Keep the majority of core development in one primary Codex thread.
5. Send the milestone prompts from §29 sequentially in the same thread.
6. After each milestone:
   - inspect the diff;
   - run the commands yourself;
   - inspect generated artifacts;
   - read the tests;
   - commit the milestone;
   - continue only after the acceptance criteria pass.
7. Do not ask Codex to implement the entire project in one uncontrolled pass.
8. Near the end, run `/feedback` in the primary Codex thread and save the Session ID.
9. All code, UI text, README content, reports, video narration, and Devpost text must be in English.
10. This plan deliberately prioritizes a reliable end-to-end proof over feature count.

Codex should make sensible engineering defaults and ask questions only when a decision is genuinely blocking.

---

# 1. Final product decision

## 1.1 Product name

# **FlashPilot**

Subtitle:

> **AI Checkpoint Reliability & Storage Autopilot**

Tagline:

> **Crash-test recovery. Repair what failed. Optimize only after proof.**

## 1.2 One-line pitch

> FlashPilot deliberately crashes AI training, restores it in a new process, verifies the resumed run against an uninterrupted control, uses GPT-5.6 to diagnose recovery failures and propose bounded repairs, and only then reports safe reductions in checkpoint writes.

## 1.3 Core promise

> **Reduce checkpoint writes only when recovery is proven.**

## 1.4 The problem

A checkpoint can be:

- present on disk;
- checksum-valid;
- loadable by PyTorch;
- able to restore model weights;

and still be unsafe for continuing training.

Commonly omitted or mishandled recovery state includes:

- optimizer state;
- scheduler state;
- mixed-precision scaler state;
- Python RNG state;
- NumPy RNG state;
- Torch RNG state;
- data or sampler position;
- global step;
- immutable base-model identity;
- completion and integrity metadata.

A training run may restart without raising an exception and still follow a different optimization trajectory.

FlashPilot tests recovery as an observable system property rather than trusting that a checkpoint file can be loaded.

## 1.5 Main user

- ML engineers;
- AI researchers;
- developers running local or self-hosted fine-tuning;
- small teams without specialized checkpoint reliability infrastructure;
- developers building checkpoint or recovery integrations.

## 1.6 Product workflow

```text
inspect a supported training workload
→ interpret the user's recovery objective
→ infer a checkpoint contract with GPT-5.6
→ run an uninterrupted control
→ create and commit a checkpoint
→ kill the training process
→ restore in a new process
→ run a deterministic Recovery Gate
→ collect actual failure artifacts
→ GPT-5.6 diagnoses the failure
→ GPT-5.6 proposes a typed, bounded repair plan
→ deterministic code validates and applies supported repair actions
→ kill and restore again
→ run the Recovery Gate again
→ compare safe full and safe adapter-aware checkpoint writes
→ export an auditable report
```

## 1.7 Why GPT-5.6 is meaningful

GPT-5.6 is not used primarily to choose a checkpoint interval from a tiny numeric search space.

Its non-decorative responsibilities are:

1. infer the recovery contract from workload capabilities, save/restore behavior, and the user's natural-language goal;
2. analyze real failure artifacts from a failed Recovery Gate;
3. connect symptoms across state, code summary, manifest, restore order, and trajectory differences;
4. produce a typed repair plan from a strict allowlist;
5. explain evidence and tradeoffs.

Deterministic code remains the source of truth:

- it performs the crash;
- it restores the process;
- it checks correctness;
- it accepts or rejects repairs;
- it calculates metrics;
- it chooses no result based on model prose alone.

## 1.8 What is not claimed as novel

State this explicitly in README and the submission:

- saving only trainable adapters is established practice;
- checkpoint compression and incremental checkpointing have prior art;
- checkpoint frequency optimization has prior art;
- checksums and atomic writes are established engineering practices;
- chaos testing and failure injection are established disciplines.

The contribution is the integrated developer workflow:

```text
recovery-contract inference
+ real cross-process crash and restore
+ deterministic comparison with an uninterrupted control
+ GPT-assisted failure diagnosis
+ bounded repair execution
+ mandatory re-verification
+ measured storage impact
```

## 1.9 Allowed claims

Only claim what FlashPilot measured or verified:

- logical checkpoint bytes written;
- retained checkpoint footprint;
- checkpoint count;
- checkpoint duration;
- restore duration;
- rollback steps;
- process termination and restart;
- individual Recovery Gate results;
- final-state or evaluation match versus control;
- repair actions proposed and accepted;
- live or fixture source of the GPT response.

## 1.10 Prohibited claims

Do not claim:

- guaranteed additional SSD lifetime;
- measured NAND wear;
- measured write amplification without a physical media counter;
- control over FTL, garbage collection, erase voltage, or firmware;
- universal compatibility with arbitrary PyTorch repositories;
- mathematical optimality of a checkpoint schedule;
- recovery success without a passing deterministic gate;
- that GPT-5.6 itself proved recovery;
- that FlashPilot is the first tool in the world to test checkpoint recovery.

Use this safe downstream statement:

> Reducing avoidable logical writes can lower storage overhead and may reduce long-term NAND wear, but physical NAND writes and SSD lifetime are not measured by the MVP.

---

# 2. Hackathon compliance

The submission must include:

- a working project built with Codex and GPT-5.6;
- the Developer Tools track;
- a project description;
- a public YouTube demo under three minutes;
- audio explaining both Codex and GPT-5.6 use;
- a repository URL;
- a README with setup and run instructions;
- a `/feedback` Codex Session ID from the primary thread;
- installation instructions;
- supported platforms;
- a judge path that does not require rebuilding from source.

Repository options:

- public with an appropriate license; or
- private and shared with the official judging addresses listed by Devpost.

Document in README:

- where Codex accelerated implementation;
- key product and engineering decisions made by the human;
- concrete files or components created with Codex;
- how GPT-5.6 is used inside the product;
- limitations and unsupported scenarios.

Treat Codex credits and OpenAI API billing as separate concerns. Test one small live GPT-5.6 API call early. The complete judge path must also work through a clearly labeled fixture/replay provider.

Official references are listed in §36.

---

# 3. Scope lock

## 3.1 P0 — non-cuttable core

1. deterministic CPU-only PyTorch workload;
2. nonzero training-time stochasticity so RNG restoration is meaningful;
3. uninterrupted control run;
4. `NativePyTorchAdapter`;
5. safe full checkpoint strategy;
6. safe adapter-aware checkpoint strategy;
7. valid but incomplete `missing_training_state` checkpoint fixture;
8. atomic checkpoint commit;
9. real parent-controlled subprocess kill;
10. restore in a newly launched process;
11. deterministic Recovery Gate;
12. structured checkpoint contract;
13. live and fixture GPT-5.6 contract inference;
14. live and fixture GPT-5.6 failure diagnosis;
15. typed, allowlisted repair plan;
16. deterministic repair executor;
17. exactly one repair iteration;
18. second real crash and restore after repair;
19. measured comparison of safe full versus safe adapter-aware writes;
20. Rich console output;
21. JSON and Markdown reports;
22. offline fixture/replay mode;
23. one judge-ready command;
24. tests for determinism, recovery, integrity, containment, guardrails, and the repair limit;
25. README sections for Codex, GPT-5.6, prior art, supported scope, and limitations.

## 3.2 P0.5 — build only after P0 is green

1. a single self-contained `report.html` rendered from `result.json`;
2. a polished crash timeline;
3. a red-to-green Recovery Gate view;
4. packaging as a prebuilt wheel or GitHub Release artifact;
5. one clean-environment judge-path test.

## 3.3 P1 — optional stretch goals

Priority order:

1. a small Hugging Face / PEFT adapter example;
2. partial-write crash scenario;
3. corrupted-checkpoint rejection and previous-valid fallback;
4. optional bounded checkpoint policy planner;
5. optional GPT-selected failure hypothesis from an allowlist;
6. static `FlashPilot Recovery: verified` badge;
7. GitHub Actions;
8. Docker image;
9. optional GPT-generated report summary.

## 3.4 P2 — roadmap only

Do not implement before submission:

- arbitrary repository support;
- execution of untrusted third-party repositories;
- universal PyTorch instrumentation;
- distributed training;
- DeepSpeed, FSDP, or multi-node recovery;
- TensorFlow or JAX;
- automatic arbitrary source-code patches;
- general network-failure simulation;
- disk-full simulation;
- REO implementation;
- MQSim or FEMU integration;
- MiDAS or FDP implementation;
- SMART-based lifetime forecasting;
- physical SSD lifetime prediction;
- model-family deduplication;
- universal delta checkpoint compression;
- coding-agent workspace optimization.

---

# 4. Acceptance demo

The primary demo must show this exact story:

```text
1. An uninterrupted control run completes.

2. FlashPilot audits a valid, loadable, but incomplete checkpoint.

3. The parent process kills the training worker after the checkpoint commit.

4. A new process restores the checkpoint.

5. The Recovery Gate fails:
   model state              PASS
   checkpoint integrity     PASS
   global step              PASS
   optimizer state          FAIL
   scheduler state          FAIL
   RNG state                FAIL
   continued trajectory     FAIL

6. GPT-5.6 receives redacted code summaries and actual failure artifacts.

7. GPT-5.6 diagnoses the root cause and emits allowlisted repair actions.

8. The deterministic repair executor applies only supported actions.

9. FlashPilot performs a second real kill and new-process restore.

10. The Recovery Gate passes.

11. FlashPilot compares:
    safe full checkpoint bytes
    safe adapter-aware checkpoint bytes
    save duration
    restore duration
    rollback steps

12. Reports are exported.
```

The main red-to-green failure is:

```text
missing_training_state
```

The checkpoint is intentionally:

- complete according to its own manifest;
- checksum-valid;
- loadable;
- able to restore model or adapter weights and the global step;

but it omits:

- optimizer state;
- scheduler state;
- Python RNG state;
- NumPy RNG state;
- Torch RNG state.

This produces a realistic silent-recovery failure.

A physically corrupted optimizer payload is a separate fail-closed test. The correct behavior is rejection or fallback, not pretending GPT repaired corrupted bytes.

---

# 5. Technical stack

## Required

- Python 3.11;
- `src/` package layout;
- `pyproject.toml`;
- PyTorch CPU;
- Pydantic v2;
- Typer;
- Rich;
- official OpenAI Python SDK;
- Responses API;
- `model="gpt-5.6"`;
- structured outputs;
- pytest;
- Ruff.

## Optional

- `psutil` for process-level write counters;
- Jinja2 only if it materially simplifies static HTML generation;
- `coverage.py`;
- build tooling for a wheel.

## Not required for P0

- Transformers;
- PEFT;
- CUDA;
- a database;
- a web server;
- a frontend framework;
- Docker;
- external datasets;
- downloaded model weights.

---

# 6. Repository structure

```text
flashpilot/
├── AGENTS.md
├── README.md
├── LICENSE
├── pyproject.toml
├── Makefile
├── .env.example
├── .gitignore
├── FLASH_PILOT_CODEX_MASTER_PLAN.md
├── src/flashpilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── constants.py
│   ├── domain/
│   │   ├── capabilities.py
│   │   ├── contracts.py
│   │   ├── failures.py
│   │   ├── manifests.py
│   │   ├── metrics.py
│   │   ├── repairs.py
│   │   ├── results.py
│   │   └── schemas.py
│   ├── adapters/
│   │   ├── base.py
│   │   ├── native_pytorch.py
│   │   └── registry.py
│   ├── workload/
│   │   ├── data.py
│   │   ├── model.py
│   │   ├── profiles.py
│   │   ├── state.py
│   │   └── trainer.py
│   ├── checkpoints/
│   │   ├── atomic.py
│   │   ├── integrity.py
│   │   ├── loader.py
│   │   ├── retention.py
│   │   ├── strategies.py
│   │   └── writer.py
│   ├── orchestration/
│   │   ├── control_run.py
│   │   ├── crash_protocol.py
│   │   ├── events.py
│   │   ├── experiment.py
│   │   ├── subprocesses.py
│   │   └── worker.py
│   ├── verification/
│   │   ├── recovery_gate.py
│   │   ├── state_compare.py
│   │   ├── trajectory.py
│   │   └── tolerances.py
│   ├── agent/
│   │   ├── base.py
│   │   ├── contract_provider.py
│   │   ├── failure_provider.py
│   │   ├── fixture_provider.py
│   │   ├── openai_provider.py
│   │   ├── prompts.py
│   │   ├── redaction.py
│   │   └── guardrails.py
│   ├── repair/
│   │   ├── executor.py
│   │   └── capability_map.py
│   ├── reporting/
│   │   ├── console.py
│   │   ├── json_report.py
│   │   ├── markdown_report.py
│   │   └── html_report.py
│   └── security/
│       ├── paths.py
│       └── limits.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── demo/
│   ├── contract_fixture.json
│   ├── failure_analysis_fixture.json
│   ├── run_demo.sh
│   └── run_live_demo.sh
├── examples/
│   └── native_pytorch/
├── docs/
│   ├── architecture.md
│   ├── build-log.md
│   ├── codex-contributions.md
│   ├── decisions.md
│   ├── demo-script.md
│   ├── research.md
│   └── submission-checklist.md
└── runs/
    └── .gitkeep
```

---

# 7. Domain model

## 7.1 Workload capabilities

```python
from typing import Literal
from pydantic import BaseModel, Field


StateName = Literal[
    "model",
    "adapter",
    "optimizer",
    "scheduler",
    "scaler",
    "global_step",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "torch_cuda_rng",
    "sampler",
    "base_model_identity",
]


class WorkloadCapabilities(BaseModel):
    adapter_name: str
    framework: Literal["native-pytorch", "huggingface-peft"]
    has_frozen_base: bool
    has_trainable_adapter: bool
    optimizer_type: str
    scheduler_type: str | None
    uses_dropout: bool
    uses_python_rng: bool
    uses_numpy_rng: bool
    uses_torch_rng: bool
    uses_cuda_rng: bool
    batch_position_is_step_derived: bool
    supported_state: list[StateName]
    supported_repair_actions: list[str]
    assumptions: list[str] = Field(default_factory=list)
```

## 7.2 Save/restore summary

This summary is produced deterministically by the adapter. It is safer and easier to evaluate than sending arbitrary repository files.

```python
class SaveRestoreSummary(BaseModel):
    checkpoint_strategy: str
    serialized_state: list[StateName]
    restored_state: list[StateName]
    restore_order: list[str]
    integrity_controls: list[str]
    completion_protocol: list[str]
    immutable_artifacts: list[str]
    omitted_state: list[StateName]
    sanitized_source_snippets: list[str] = Field(default_factory=list)
```

If source snippets are included:

- include only explicit allowlisted project files;
- limit total characters;
- redact secrets and absolute home paths;
- never send model weights or datasets;
- persist the redacted request for auditability.

## 7.3 Checkpoint contract

```python
IntegrityControl = Literal[
    "manifest",
    "checksums",
    "completion_marker",
    "atomic_commit",
    "base_artifact_hash",
]


class ContractRequirement(BaseModel):
    state: StateName
    required: bool
    reason: str


class CheckpointContract(BaseModel):
    required_state: list[ContractRequirement]
    required_integrity_controls: list[IntegrityControl]
    restore_order_requirements: list[str]
    rollback_limit_steps: int
    correctness_priority: Literal["strict", "balanced"]
    assumptions: list[str]
    warnings: list[str]
```

The contract is proposed by GPT-5.6 and then validated by deterministic code.

Rules:

- the model may request only known state names;
- the rollback limit cannot exceed the user hard limit;
- required integrity controls cannot weaken local minimum requirements;
- the contract cannot disable mandatory Recovery Gate checks;
- unsupported requirements are surfaced, not silently ignored.

## 7.4 Repair plan

```python
RepairActionType = Literal[
    "persist_model_state",
    "persist_adapter_state",
    "persist_optimizer_state",
    "persist_scheduler_state",
    "persist_scaler_state",
    "persist_global_step",
    "persist_python_rng_state",
    "persist_numpy_rng_state",
    "persist_torch_rng_state",
    "persist_torch_cuda_rng_state",
    "persist_sampler_state",
    "add_base_model_hash",
    "add_manifest",
    "add_checksums",
    "use_atomic_checkpoint_commit",
    "restore_state_before_next_batch",
    "fallback_to_previous_valid_checkpoint",
    "quarantine_invalid_checkpoint",
    "change_checkpoint_interval",
    "change_retention_count",
    "change_supported_checkpoint_strategy",
]


class RepairAction(BaseModel):
    action: RepairActionType
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)


class RepairPlan(BaseModel):
    actions: list[RepairAction]
    expected_gate_improvements: list[str]
    risks: list[str]
    assumptions: list[str]
```

## 7.5 Failure analysis

```python
class FailureAnalysis(BaseModel):
    root_cause_hypothesis: str
    affected_gate_checks: list[str]
    confirming_evidence: list[str]
    repair_plan: RepairPlan
    confidence: Literal["low", "medium", "high"]
    limitations: list[str]
```

The model may diagnose corrupted files, but deterministic code decides whether the only safe action is rejection or fallback.

## 7.6 Evidence records

Every check and every model statement should reference stable evidence IDs.

Examples:

```text
manifest:serialized-state
gate:optimizer-state
gate:rng-state
trajectory:first-divergence
restore:order
integrity:sha256
worker:exit-code
```

This lets the report show why a diagnosis was made without exposing raw binary state.

---

# 8. TrainerAdapter interface

P0 supports only `NativePyTorchAdapter`.

```python
from abc import ABC, abstractmethod
from pathlib import Path


class TrainerAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> WorkloadCapabilities:
        ...

    @abstractmethod
    def summarize_save_restore(
        self,
        strategy_name: str,
    ) -> SaveRestoreSummary:
        ...

    @abstractmethod
    def build_control_command(self, run_dir: Path) -> list[str]:
        ...

    @abstractmethod
    def build_worker_command(
        self,
        run_dir: Path,
        strategy_name: str,
        resume_from: Path | None,
    ) -> list[str]:
        ...

    @abstractmethod
    def apply_repair_plan(
        self,
        strategy_name: str,
        plan: RepairPlan,
    ) -> str:
        ...

    @abstractmethod
    def supported_repair_actions(self) -> set[str]:
        ...
```

Rules:

- no arbitrary shell strings;
- subprocess commands are argument arrays built by trusted code;
- only registered adapters execute;
- no user-controlled path is accepted without sandbox validation;
- unsupported actions fail closed;
- repairs produce a new strategy/configuration rather than mutating historical artifacts.

---

# 9. Controlled training workload

## 9.1 Model

Build a tiny local Transformer-like language model:

- token embedding;
- positional embedding;
- one or two small Transformer blocks;
- nonzero dropout during training;
- output head;
- frozen base parameters;
- small trainable residual bottleneck adapter.

Only the adapter trains in the optimized strategy.

## 9.2 Profiles

### CI profile

- very small dimensions;
- 6–10 steps;
- one checkpoint;
- low runtime;
- intended for tests.

### Demo profile

- 20–40 steps;
- full checkpoint visibly larger than adapter-aware checkpoint;
- two or three checkpoint opportunities;
- runs comfortably on a laptop CPU;
- no downloads;
- no dummy padding files.

## 9.3 Data determinism

Synthetic token batches are derived from:

```text
(global_seed, global_step)
```

using a dedicated `torch.Generator`.

Training also uses nonzero dropout with the normal Torch RNG so restoring Torch RNG state materially affects the resumed trajectory.

Seed:

- Python;
- NumPy;
- Torch.

Set:

- deterministic algorithms where supported;
- a fixed thread count;
- stable dtype;
- CPU-only execution for P0.

The evaluation path must disable dropout and use fixed evaluation data.

## 9.4 Control run

The uninterrupted control persists:

- final global step;
- trainable adapter state;
- optimizer state summary;
- scheduler state summary;
- final parameter digest;
- fixed evaluation logits;
- loss history;
- environment metadata;
- seed;
- profile;
- git commit where available.

The control is the reference for all resumed runs.

## 9.5 Equality policy

Aim for exact reproducibility on the controlled CPU workload.

Compare:

1. exact equality for:
   - global step;
   - manifest fields;
   - hashes;
   - serialized scalar state;
2. exact tensor equality where stable;
3. otherwise explicit `atol` and `rtol` values for:
   - trainable parameters;
   - evaluation logits;
   - loss values.

Do not silently relax tolerances.

The chosen tolerance and empirical reason must be documented in `docs/decisions.md` during the Recovery Gate milestone.

---

# 10. Checkpoint strategies

## 10.1 `safe_full`

Stores:

- complete model state;
- optimizer state;
- scheduler state;
- global step;
- Python RNG;
- NumPy RNG;
- Torch RNG;
- config;
- manifest;
- checksums;
- completion marker.

Purpose:

- correct recovery reference;
- storage-heavy comparison point.

## 10.2 `safe_adapter_aware`

Stores the immutable base artifact once per run.

Recurring checkpoints store:

- trainable adapter state;
- optimizer state for trainable parameters;
- scheduler state;
- global step;
- Python RNG;
- NumPy RNG;
- Torch RNG;
- base artifact identity and SHA-256;
- manifest;
- checksums;
- completion marker.

Purpose:

- safe storage-efficient strategy;
- no claim that adapter-only storage is novel.

## 10.3 `missing_training_state`

A valid, intentionally incomplete strategy used only for the primary red-to-green demo.

Stores:

- model or adapter state;
- global step;
- base identity where relevant;
- manifest;
- checksums;
- completion marker.

Intentionally omits:

- optimizer state;
- scheduler state;
- Python RNG;
- NumPy RNG;
- Torch RNG.

The checkpoint is loadable but insufficient for exact continuation.

## 10.4 Corruption fixtures

Negative tests:

- modify one byte of a model payload;
- modify one byte of an optimizer payload;
- remove the base artifact;
- change the base hash;
- leave a temp checkpoint incomplete;
- attempt path traversal;
- create a symlink escape where the platform supports it.

Expected result:

- detect;
- reject;
- quarantine or fallback where implemented;
- never declare repaired corrupted bytes;
- never resume silently.

---

# 11. Atomic checkpoint protocol

## 11.1 Directory format

```text
checkpoint-step-000020/
├── COMPLETE
├── manifest.json
├── checksums.json
├── model.pt or adapter.pt
├── optimizer.pt
├── scheduler.pt
├── rng.pt
└── state.json
```

Exact files vary by strategy.

## 11.2 Commit algorithm

Use a temporary sibling directory on the same filesystem.

```text
1. create unique temp directory under the run checkpoint root;
2. write payload files;
3. flush and fsync payload files where practical;
4. calculate SHA-256 checksums;
5. write checksums.json;
6. write manifest.json;
7. write COMPLETE inside the temp directory;
8. fsync metadata files;
9. fsync the temp directory where supported;
10. atomically rename the temp directory to a unique final directory;
11. fsync the parent directory where supported;
12. emit checkpoint_committed only after the rename succeeds.
```

The final destination must not already exist.

## 11.3 Loader rules

Never load unless:

- the directory is final, not temporary;
- `COMPLETE` exists;
- manifest schema validates;
- all required files exist;
- checksums match;
- base artifact exists;
- base hash matches;
- all managed paths pass containment checks.

Ignore incomplete temp directories.

## 11.4 Platform note

Atomic directory rename and directory `fsync` behavior differ by platform.

P0 should:

- guarantee the strongest behavior on Linux;
- support macOS where tests pass;
- document Windows as best-effort or experimental unless verified;
- never overstate cross-platform durability.

---

# 12. Crash protocol

## 12.1 Control run

Run the workload without interruption to the final step.

## 12.2 Crash run

```text
parent starts worker subprocess
→ worker trains
→ worker commits checkpoint atomically
→ worker emits one JSON event line:
  {"event":"checkpoint_committed","step":20,"path":"..."}
→ parent validates the path is inside the run sandbox
→ parent records PID and timestamp
→ parent kills the process
→ parent confirms expected termination
→ parent locates newest valid checkpoint
→ parent launches a new process with resume arguments
→ new process restores
→ new process finishes to control final step
```

Use a true process boundary. Do not simulate the crash with an in-process exception.

## 12.3 Process termination

Use cross-platform subprocess APIs.

Record:

- PID;
- termination method;
- exit code;
- time;
- checkpoint step;
- resume PID.

On POSIX, a forceful kill may map to `SIGKILL`. On Windows, document the actual termination primitive.

## 12.4 Crash point

P0 uses a deterministic crash point after a committed checkpoint.

Optionally support a fixed seed and a short list of deterministic crash steps.

The demo should be reproducible.

## 12.5 Exactly one repair iteration

The product supports:

```text
initial crash
→ failed gate
→ GPT diagnosis
→ one bounded repair
→ second crash
→ final gate
```

No unbounded autonomous loop.

---

# 13. Recovery Gate

## 13.1 Mandatory checks

Display each check separately.

1. manifest schema valid;
2. completion marker present;
3. all checksums valid;
4. base artifact present when required;
5. base hash matches;
6. checkpoint global step is valid;
7. model or adapter state restores;
8. optimizer state restores when required;
9. scheduler state restores when required;
10. Python RNG restores when required;
11. NumPy RNG restores when required;
12. Torch RNG restores when required;
13. resumed run continues from the expected next step;
14. achieved rollback is within the hard limit;
15. fixed evaluation logits after restore match within the documented policy;
16. final trainable parameters match the uninterrupted control;
17. final evaluation logits match the uninterrupted control;
18. continued loss trajectory matches the uninterrupted control under the documented policy;
19. every FlashPilot-managed write path passed sandbox containment and symlink-escape checks;
20. no mandatory contract requirement was silently omitted.

## 13.2 Result

```python
class GateCheck(BaseModel):
    check_id: str
    label: str
    status: Literal["pass", "fail", "not_applicable"]
    evidence_ids: list[str]
    expected: str | None
    actual: str | None
    details: str | None


class RecoveryGateResult(BaseModel):
    passed: bool
    checks: list[GateCheck]
    failed_check_ids: list[str]
    achieved_rollback_steps: int
    comparison_policy: dict
```

All mandatory applicable checks must pass.

## 13.3 Contract interaction

The deterministic system has a minimum mandatory gate.

GPT-5.6 may add contract requirements, but it may not remove minimum checks.

## 13.4 Failure artifact package

After a failed gate, produce a redacted package:

```json
{
  "user_objective": {},
  "workload_capabilities": {},
  "checkpoint_contract": {},
  "save_restore_summary": {},
  "manifest_summary": {},
  "restore_order": [],
  "gate_checks": [],
  "state_differences": {},
  "trajectory_summary": {},
  "integrity_summary": {},
  "crash_metadata": {},
  "evidence_catalog": {}
}
```

Do not include:

- raw model weights;
- raw optimizer tensors;
- dataset samples;
- secrets;
- API keys;
- arbitrary local files;
- home-directory paths.

---

# 14. GPT-5.6 role A — checkpoint contract inference

## 14.1 Input

- natural-language recovery objective;
- hard rollback limit;
- workload capabilities;
- save/restore summary;
- integrity protocol;
- optional sanitized source snippets;
- supported state enum;
- mandatory minimum gate requirements.

Example goal:

> Lose no more than five training steps. Recovery correctness is more important than checkpoint size. Avoid repeatedly storing the frozen base model.

## 14.2 Output

`CheckpointContract` structured output.

## 14.3 Model call

Use the official SDK and structured parsing.

Representative shape:

```python
response = client.responses.parse(
    model="gpt-5.6",
    input=[
        {"role": "system", "content": CONTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": contract_input_json},
    ],
    text_format=CheckpointContract,
    store=False,
)
```

Verify the installed SDK's current response accessor rather than copying untested example code blindly.

## 14.4 Contract prompt rules

The system prompt must require:

- supported enums only;
- no commands;
- no file paths;
- no code patches;
- no URLs;
- no secrets;
- concise reasons, not private chain-of-thought;
- no removal of mandatory integrity controls;
- no claim that the contract is verified;
- explicit assumptions and warnings.

## 14.5 Deterministic validation

Reject or normalize only through explicit rules.

Examples:

- unknown state name → reject;
- rollback above user maximum → reject;
- missing mandatory integrity control → add deterministic minimum and report;
- unsupported state → report capability gap;
- malformed structured output → use fixture or fail clearly.

---

# 15. GPT-5.6 role B — failure diagnosis and bounded repair

## 15.1 Input

The redacted failure artifact package from §13.4.

This is the critical differentiating role.

## 15.2 Output

`FailureAnalysis` with:

- root-cause hypothesis;
- affected gate checks;
- confirming evidence;
- confidence;
- typed repair plan;
- risks;
- limitations.

## 15.3 Example diagnosis

```text
The checkpoint restores the trainable adapter and global step, but omits
optimizer, scheduler, and RNG state. The next batch therefore starts with
a reset optimizer trajectory and different dropout masks, producing the
observed divergence from the uninterrupted control.
```

## 15.4 Example repair actions

```text
persist_optimizer_state
persist_scheduler_state
persist_python_rng_state
persist_numpy_rng_state
persist_torch_rng_state
restore_state_before_next_batch
```

## 15.5 Repair rules

GPT-5.6 never:

- edits source code directly;
- executes shell commands;
- changes gate tolerances;
- deletes files;
- marks a run as verified;
- invents metrics;
- repairs corrupted binary payloads;
- bypasses integrity checks.

## 15.6 Corruption behavior

For a checksum mismatch, expected model output may include:

```text
quarantine_invalid_checkpoint
fallback_to_previous_valid_checkpoint
```

The deterministic executor decides whether fallback is available.

## 15.7 One attempt only

Persist:

- original failure analysis;
- validation result;
- accepted actions;
- rejected actions;
- repaired strategy identifier;
- second gate result.

Do not ask GPT for a second repair in P0.

---

# 16. Optional GPT-5.6 role C — policy planner

This is P1 or P0.5 only.

It may propose bounded:

- checkpoint interval;
- retention count;
- strategy from a supported enum.

It is cuttable.

Do not make the submission depend on the claim that GPT numerically beats a deterministic grid search.

If implemented:

- compare against a fixed safe reference;
- show structural savings separately from policy savings;
- let deterministic scoring select the result;
- report honestly if GPT adds no measurable benefit.

---

# 17. Fixture/replay mode

Implement:

- `OpenAIContractProvider`;
- `FixtureContractProvider`;
- `OpenAIFailureProvider`;
- `FixtureFailureProvider`.

Fixture files must contain real previously generated structured GPT-5.6 responses for the known demo profile, with secrets removed.

Every UI and report must label:

```text
GPT source: live GPT-5.6
```

or:

```text
GPT source: GPT-5.6 fixture/replay
```

Fixture mode still performs:

- real training;
- real checkpoint writing;
- real process termination;
- new-process restore;
- deterministic gate checks;
- repair execution;
- second real crash;
- metric collection.

Only the model response is replayed.

Persist agent metadata:

```json
{
  "provider": "openai-or-fixture",
  "model": "gpt-5.6",
  "role": "contract-or-failure",
  "prompt_version": "v1",
  "schema_version": "v1",
  "live_or_fixture": "fixture",
  "response_id": null,
  "timestamp": "...",
  "request_sha256": "..."
}
```

Never persist the API key.

---

# 18. Repair executor

## 18.1 Validation pipeline

```text
GPT repair plan
→ Pydantic schema validation
→ action allowlist validation
→ active-adapter capability validation
→ conflict validation
→ safety validation
→ build a new repaired strategy
→ execute in an isolated run directory
```

## 18.2 Action mapping

Example:

```text
persist_optimizer_state
→ strategy.include_optimizer = true

persist_torch_rng_state
→ strategy.include_torch_rng = true

restore_state_before_next_batch
→ adapter.restore_phase = "before_data_and_forward"

add_checksums
→ strategy.integrity.checksums = true
```

## 18.3 Conflict rules

Reject:

- actions unsupported by the adapter;
- duplicate conflicting strategy changes;
- interval above rollback limit;
- retention below the minimum needed for fallback;
- any arbitrary path or command;
- any action that weakens a mandatory integrity control;
- any attempt to alter tolerances.

## 18.4 Historical immutability

Never modify an existing failed checkpoint in place.

A repair creates:

- a new strategy identifier;
- a new isolated run;
- new checkpoints;
- a new result.

---

# 19. Storage comparison

Only compare strategies that passed the Recovery Gate.

Required comparison:

```text
safe_full
vs
repaired safe_adapter_aware
```

Measure:

- logical checkpoint bytes written;
- immutable base artifact bytes;
- recurring checkpoint bytes;
- retained checkpoint footprint;
- checkpoint count;
- mean checkpoint duration;
- maximum checkpoint duration;
- restore duration;
- achieved rollback steps;
- training throughput;
- optional process write bytes if available.

Do not include the intentionally incomplete strategy as a valid efficiency winner.

---

# 20. Metrics model

```python
MetricSource = Literal[
    "measured",
    "derived",
    "fixture-replay",
    "unavailable",
    "not-measured",
]


class MetricValue(BaseModel):
    value: int | float | bool | str | None
    unit: str | None
    source: MetricSource
    notes: str | None = None


class ExperimentMetrics(BaseModel):
    logical_checkpoint_bytes_written: MetricValue
    base_artifact_bytes_written: MetricValue
    recurring_checkpoint_bytes_written: MetricValue
    retained_checkpoint_bytes: MetricValue
    checkpoint_count: MetricValue
    mean_checkpoint_duration_seconds: MetricValue
    max_checkpoint_duration_seconds: MetricValue
    restore_duration_seconds: MetricValue
    training_steps_per_second: MetricValue
    process_write_bytes: MetricValue
    achieved_rollback_steps: MetricValue
    recovery_passed: MetricValue
    final_state_match: MetricValue
```

Reports must explicitly state:

```text
Physical NAND writes: not measured
SSD lifetime: not measured
Write amplification: not measured
```

---

# 21. Deterministic result selection

The model never selects the winner.

Order:

1. Recovery Gate passes;
2. rollback hard limit passes;
3. integrity requirements pass;
4. user write budget passes if supplied;
5. user save-pause limit passes if supplied;
6. minimize measured logical checkpoint bytes;
7. tie-break on lower maximum checkpoint pause;
8. then lower restore duration.

If no optimized strategy passes:

- select `safe_full`;
- report that no safe storage optimization was accepted;
- never hide the failure.

---

# 22. CLI

## 22.1 Required commands

```bash
flashpilot doctor
flashpilot control --profile ci
flashpilot audit --profile demo --provider fixture
flashpilot audit --profile demo --provider openai \
  --goal "Lose no more than five steps. Prioritize correctness."
flashpilot demo --provider fixture
flashpilot verify runs/<run-id>
flashpilot replay runs/<run-id>/result.json
```

## 22.2 Failure injection

```bash
flashpilot demo \
  --provider fixture \
  --inject-failure missing-training-state
```

Optional negative test command:

```bash
flashpilot test-integrity \
  --fixture corrupted-optimizer
```

## 22.3 Judge path

One command:

```bash
flashpilot demo --provider fixture
```

It must:

1. run a short control;
2. run the incomplete checkpoint crash;
3. show a failed Recovery Gate;
4. replay GPT-5.6 contract and diagnosis;
5. apply the bounded repair;
6. perform a second real crash and restore;
7. show a passed Recovery Gate;
8. compare safe checkpoint bytes;
9. generate JSON and Markdown reports;
10. generate HTML if P0.5 is complete.

## 22.4 `doctor`

Checks:

- Python version;
- PyTorch import;
- writable run directory;
- deterministic mode availability;
- free disk;
- OpenAI key presence without printing it;
- platform support level;
- fixture availability.

---

# 23. Console experience

Use Rich.

Required sections:

```text
FLASH PILOT
WORKLOAD INSPECTION
RECOVERY OBJECTIVE
CHECKPOINT CONTRACT
UNINTERRUPTED CONTROL
INITIAL CRASH TEST
PROCESS TERMINATED
NEW PROCESS RESTORE
RECOVERY GATE — FAILED
GPT-5.6 FAILURE ANALYSIS
BOUNDED REPAIR PLAN
REPAIR VALIDATION
SECOND CRASH TEST
RECOVERY GATE — VERIFIED
SAFE STORAGE COMPARISON
ARTIFACTS
LIMITATIONS
```

Example failed gate:

```text
┌──────────────── Recovery Gate — FAILED ────────────────┐
│ Checkpoint integrity            ✓ PASS                 │
│ Model / adapter state           ✓ PASS                 │
│ Global step                     ✓ PASS                 │
│ Optimizer state                 ✗ FAIL                 │
│ Scheduler state                 ✗ FAIL                 │
│ Python / NumPy / Torch RNG      ✗ FAIL                 │
│ Trajectory vs control           ✗ FAIL                 │
│ Rollback objective              ✓ PASS                 │
└────────────────────────────────────────────────────────┘
```

Example final gate:

```text
┌──────────────── Recovery Gate — VERIFIED ──────────────┐
│ Checkpoint integrity            ✓ PASS                 │
│ Model / adapter state           ✓ PASS                 │
│ Optimizer state                 ✓ PASS                 │
│ Scheduler state                 ✓ PASS                 │
│ RNG state                       ✓ PASS                 │
│ Final state vs control          ✓ PASS                 │
│ Trajectory vs control           ✓ PASS                 │
│ Rollback objective              ✓ PASS                 │
└────────────────────────────────────────────────────────┘
```

---

# 24. Reports

## 24.1 `result.json`

Source of truth.

Include:

- run ID;
- timestamp;
- git commit;
- environment;
- platform support note;
- seed;
- profile;
- user objective;
- workload capabilities;
- save/restore summary;
- checkpoint contract;
- initial strategy;
- crash metadata;
- initial gate;
- redacted failure package;
- GPT metadata;
- failure analysis;
- repair validation;
- accepted and rejected repair actions;
- repaired strategy;
- second crash metadata;
- final gate;
- full checkpoint metrics;
- adapter-aware metrics;
- reproduction command;
- limitations.

## 24.2 `report.md`

Readable summary.

Mandatory disclaimer:

> Physical NAND writes, write amplification, and SSD lifetime were not measured.

## 24.3 `report.html` — P0.5

Single self-contained file.

No server and no experiment logic.

Sections:

1. verdict banner;
2. crash timeline;
3. initial red gate;
4. GPT diagnosis and evidence;
5. accepted bounded repair actions;
6. final green gate;
7. safe full versus safe adapter-aware comparison;
8. reproducibility metadata;
9. disclaimer;
10. judge command.

Read only `result.json`.

## 24.4 Optional badge

Only after the core is complete:

```text
FlashPilot Recovery: verified
```

Avoid an arbitrary numeric score in the MVP.

---

# 25. Testing

## 25.1 Unit tests

- deterministic batch generation;
- training-time dropout is active;
- evaluation dropout is disabled;
- base/trainable parameter separation;
- capability schema;
- save/restore summary;
- contract schema;
- contract guardrails;
- repair plan schema;
- repair allowlist;
- adapter capability mapping;
- conflict rejection;
- manifest validation;
- checksum detection;
- atomic directory commit;
- incomplete temp directory ignored;
- latest-valid checkpoint selection;
- retention;
- sandbox containment;
- path traversal rejection;
- symlink escape rejection where supported;
- metric source labels;
- result serialization.

## 25.2 Integration tests

- repeated uninterrupted controls match;
- `safe_full` direct restore;
- `safe_adapter_aware` direct restore;
- real parent kill and new-process restore;
- valid repaired run matches control;
- `missing_training_state` fails the expected checks;
- fixture failure analysis proposes expected allowlisted actions;
- repair executor applies supported actions;
- repair loop executes exactly once;
- second crash passes;
- corrupted payload is rejected;
- incomplete temp checkpoint is ignored;
- missing base artifact is rejected;
- wrong base hash is rejected;
- rollback violation is rejected;
- fixture contract provider end-to-end;
- fixture failure provider end-to-end;
- mock live SDK structured parsing without network;
- no safe optimization falls back to `safe_full`;
- reports derive from `result.json`.

## 25.3 Quality gates

After every milestone:

```bash
ruff check .
ruff format --check .
pytest -q
```

Before release:

```bash
pytest --cov=flashpilot --cov-report=term-missing
```

Record real command output in `docs/build-log.md`.

Never invent test output.

---

# 26. Security and privacy

- API key only from environment;
- never print or commit the key;
- `.env` ignored;
- `runs/` ignored except `.gitkeep`;
- no arbitrary shell execution;
- no arbitrary repository execution in P0;
- no loading arbitrary `.pt` files;
- only FlashPilot-generated checkpoints;
- all writes confined to a run root;
- path containment after resolving;
- reject traversal;
- reject symlink escape;
- bounded subprocess timeout;
- bounded file sizes;
- bounded retention;
- bounded GPT input size;
- explicit source-file allowlist for optional snippets;
- secret redaction;
- no raw weights or dataset samples sent to GPT;
- fail closed on manifest, hash, or checksum errors;
- no silent continuation after a failed gate.

---

# 27. Documentation requirements

## README

Include:

1. one-line pitch;
2. problem;
3. audience;
4. 60-second quick start;
5. judge command;
6. architecture;
7. supported platforms;
8. supported adapters;
9. live GPT mode;
10. fixture/replay explanation;
11. Recovery Gate;
12. bounded repair model;
13. measured metrics;
14. what is not measured;
15. exact role of GPT-5.6;
16. exact role of Codex;
17. key human decisions;
18. testing;
19. security;
20. limitations;
21. prior art;
22. roadmap;
23. license.

## `docs/build-log.md`

For every milestone:

- date;
- objective;
- Codex contributions;
- human decisions;
- problems found;
- files changed;
- commands run;
- real test output;
- remaining risks.

## `docs/decisions.md`

Record:

- why pure PyTorch for P0;
- why the workload includes dropout;
- why control comparison is required;
- why the failure checkpoint is valid but incomplete;
- why corrupted bytes are rejected rather than "repaired";
- why arbitrary patches are excluded;
- why repair actions are allowlisted;
- why only one repair iteration;
- why selection is deterministic;
- why physical SSD claims are excluded;
- tolerance policy;
- platform support decisions;
- why optional numeric CrashScore was omitted.

## `docs/codex-contributions.md`

Name concrete work:

- modules;
- functions;
- tests;
- architecture suggestions;
- debugging steps;
- packaging;
- documentation.

Do not write only:

> Codex built the backend.

## `docs/research.md`

Organize into:

1. checkpoint scheduling;
2. differential and incremental checkpoints;
3. recovery and large-scale training failures;
4. application-level write reduction;
5. SSD-level roadmap.

Clearly distinguish prior art from FlashPilot's integrated workflow.

---

# 28. Definition of done

## P0 done

- clean install works;
- CPU-only;
- no downloads;
- repeated control runs match;
- `safe_full` works;
- `safe_adapter_aware` works;
- `missing_training_state` is valid, loadable, and fails recovery correctness;
- a real worker process is killed;
- a new process restores;
- initial gate fails for the intended reasons;
- GPT-5.6 contract inference works live or through fixture;
- GPT-5.6 failure diagnosis works live or through fixture;
- repair plan is typed and allowlisted;
- unsupported actions are rejected;
- exactly one repair iteration occurs;
- second real crash and restore succeeds;
- final gate passes;
- full and adapter-aware bytes are measured;
- JSON and Markdown reports are generated;
- fixture mode is clearly labeled;
- one judge command works;
- tests and lint pass;
- README documents Codex and GPT-5.6;
- no physical NAND claims;
- `/feedback` reminder is present.

## P0.5 done

- `report.html` generated from `result.json`;
- clean-environment installation tested;
- wheel or release artifact available;
- demo can be recorded cleanly.

---

---

# 28.5 FLASHPILOT V4.1 EXECUTION OVERRIDE (binding)

This override narrows implementation scope without changing the V4 product story. Where this section conflicts with any other section of this plan, this section wins.

1. Keep the complete RepairAction enum in the public schema, but P0 must
   implement only:
   - persist_optimizer_state
   - persist_scheduler_state
   - persist_python_rng_state
   - persist_numpy_rng_state
   - persist_torch_rng_state
   - restore_state_before_next_batch
   Optional integrity actions (must not block the primary demo):
   - fallback_to_previous_valid_checkpoint
   - quarantine_invalid_checkpoint
   Every other action must validate as a known action but be reported as
   unsupported_by_native_pytorch_adapter.

2. Do not build a generic policy engine. Implement repair by copying a typed
   CheckpointStrategyConfig (boolean fields: include_optimizer,
   include_scheduler, include_python_rng, include_numpy_rng, include_torch_rng,
   restore_before_next_batch) and changing explicit fields, assigning a new
   strategy_id, and launching a new isolated experiment.

3. Keep TrainerAdapter and NativePyTorchAdapter, but do not build plugin
   discovery, entry points, external adapter loading, or framework
   auto-detection in P0. A plain get_adapter(name) function is sufficient.

4. Checkpoint-contract inference must consume a deterministic capability and
   save/restore summary produced by NativePyTorchAdapter. Do not build AST
   analysis, repository scanning, or arbitrary source-code discovery in P0.

5. Use simple stable evidence ID strings. Do not build a general evidence
   database or graph.

6. The primary repair path remains automatic bounded repair. Also implement or
   document a submission-safe fallback:
   GPT diagnosis
   -> deterministic validation
   -> human approval of the known complete-training-state preset
      (flashpilot demo --provider fixture --repair-mode approved-preset)
   -> second real crash
   -> deterministic Recovery Gate
   If the automatic repair executor is not reliably green by July 20 at 12:00
   Riga time, freeze the human-approved preset flow as the submission path and
   name it "human-approved bounded repair", not a degraded mode.

7. The GPT failure-analysis request must not contain:
   - the injected failure label;
   - the string missing_training_state;
   - an expected diagnosis;
   - a repair preset name;
   - comments revealing which state was intentionally removed.
   Add a test enforcing this (assert the serialized payload contains none of
   the forbidden strings). Persist and expose the sanitized request as
   agent/request.redacted.json.

8. The demo must explicitly state:
   "The failure is intentional and deterministic, but GPT-5.6 does not receive
   the injection label. It receives only the sanitized checkpoint manifest,
   restore behavior, failed Recovery Gate checks, and trajectory evidence."

9. Use this exact impact framing unless later source verification supports a
   stronger statement:
   "During OPT-175B training on 992 A100 GPUs, hardware failures caused at
   least 35 manual restarts and an estimated 70-plus automatic restarts over
   two months."
   Treat expected loss of half a checkpoint interval as a mathematical
   uniform-failure approximation, not an OPT measurement. Do not use the
   "678 interruptions at 32K GPUs" figure in narration unless verified against
   the full FlashRecovery text.

10. Restore CheckFreq, Check-N-Run, ExCP, Amber, IncrCP, OPT, MegaScale,
    FlashRecovery, REO, MiDAS, FDP/WARP, and ZipLLM to docs/research.md as a
    prior-art table (work / what it solves / how FlashPilot differs).
    Do not implement these systems.

11. Group Recovery Gate checks in console/HTML output (Integrity, Required
    training state, Process recovery, Trajectory correctness, Safety and
    rollback) while keeping every individual check in result.json.

12. Do not build in P0: plugin registry, generic repository scanner, AST-based
    source analyzer, all 21 repair actions, numeric CrashScore, policy planner,
    GPT report narrator, Docker (unless trivial), multiple framework adapters.

13. Do not expand the plan further. Execute Prompt 0 now and stop after its
    acceptance criteria.

# 29. Milestone prompts for the primary Codex thread

## Prompt 0 — inspect, scaffold, deterministic workload

```text
Read FLASH_PILOT_CODEX_MASTER_PLAN.md completely.

This is the binding V4 final specification. It supersedes every earlier plan
and amendment. Act as the primary engineering agent for this OpenAI Build Week
Developer Tools project.

For this milestone only:

1. Inspect the repository and local environment.
2. Summarize the intended architecture in no more than 15 bullets.
3. State the three largest implementation risks.
4. Create:
   - AGENTS.md
   - pyproject.toml
   - src-layout package skeleton
   - tests skeleton
   - docs/architecture.md
   - docs/decisions.md
   - docs/build-log.md
   - docs/codex-contributions.md
   - docs/research.md
   - docs/submission-checklist.md
5. Implement only:
   - the deterministic CPU PyTorch workload;
   - a tiny Transformer-like model;
   - a frozen base plus trainable residual adapter;
   - nonzero dropout during training;
   - deterministic fixed evaluation;
   - step-derived synthetic batches;
   - optimizer and scheduler;
   - ci and demo profiles;
   - uninterrupted control run;
   - final-state and evaluation summaries.
6. Add tests proving repeated control runs match.
7. Run:
   - ruff check .
   - ruff format --check .
   - pytest -q
8. Update docs/build-log.md with real output.
9. Report changed files, commands, test results, assumptions, and unresolved risks.
10. Stop.

Do not implement checkpoints, GPT integration, subprocess crash orchestration,
HTML, packaging, or optional policy planning yet.

Ask only on a true blocker.
```

## Prompt 1 — safe checkpoint foundations

```text
Continue in the same primary thread with Milestone 1.

Implement checkpoint foundations:

1. Manifest, checksum, completion-marker, and path-containment domain models.
2. Correct atomic checkpoint commit:
   - write payloads into a temp sibling directory;
   - fsync where practical;
   - write checksums;
   - write manifest;
   - write COMPLETE inside the temp directory;
   - fsync temp metadata;
   - atomically rename to a unique final directory;
   - fsync the parent where supported;
   - emit no committed event before rename succeeds.
3. Loader validation and latest-valid checkpoint discovery.
4. Retention that never deletes outside run root and never deletes the latest
   verified checkpoint.
5. `safe_full` strategy with model, optimizer, scheduler, RNG, step, manifest,
   checksums, and completion marker.
6. Direct restore tests.
7. Corruption, incomplete-temp, path traversal, and containment tests.
8. Logical byte and duration metrics.
9. CLI commands for control and safe-full baseline.

Do not implement adapter-aware checkpoints, GPT, subprocess crash orchestration,
or HTML yet.

Run all quality gates, update the build log with real metrics, summarize, stop.
```

## Prompt 2 — adapter-aware and incomplete recovery fixture

```text
Continue with Milestone 2.

Implement:

1. `TrainerAdapter` abstraction.
2. `NativePyTorchAdapter`.
3. WorkloadCapabilities and SaveRestoreSummary.
4. `safe_adapter_aware`:
   - immutable frozen base stored once;
   - base SHA-256 referenced by recurring checkpoints;
   - recurring adapter checkpoint contains adapter, optimizer, scheduler, RNG,
     global step, manifest, checksums, and completion marker.
5. `missing_training_state`:
   - checksum-valid and loadable;
   - contains adapter/model state and global step;
   - intentionally omits optimizer, scheduler, and all relevant RNG state.
6. Direct restore behavior for each strategy.
7. Measured safe-full versus safe-adapter-aware byte table.
8. Missing-base and wrong-base-hash tests.
9. Tests proving missing_training_state loads but diverges after continuation.

Document that adapter-aware checkpointing is established practice, not our
invention.

Do not implement GPT or process killing yet.

Run gates, update docs with actual measurements, summarize, stop.
```

## Prompt 3 — real crash orchestration and Recovery Gate

```text
Continue with Milestone 3, the central reliability milestone.

Implement:

1. Worker subprocess entry point.
2. Parent orchestrator.
3. Machine-readable checkpoint_committed event.
4. Parent kill only after a validated atomic commit event.
5. Expected termination verification.
6. New-process restore.
7. Resume to the uninterrupted control's final step.
8. Deterministic Recovery Gate with all mandatory checks from the V4 plan.
9. Structured evidence IDs and redacted failure artifacts.
10. Achieved rollback calculation.
11. Initial red-to-green demo plumbing using missing_training_state.
12. Corrupted optimizer as a fail-closed negative test, not a repair scenario.
13. Platform support notes.
14. Integration tests for:
    - successful safe-full crash and restore;
    - successful safe-adapter-aware crash and restore;
    - missing-training-state failure;
    - corrupted payload rejection;
    - incomplete temp checkpoint;
    - missing base;
    - rollback violation;
    - unexpected exit code.

Aim for exact reproducibility on the controlled CPU workload. If a numerical
tolerance is required, establish it empirically, make it explicit, test it, and
document the decision.

No GPT or HTML yet.

Run a real demo-profile crash/restore, preserve artifacts, run quality gates,
update docs, summarize, and stop only when the gate is reliable.
```

## Prompt 4 — GPT-5.6 contract and failure analyst

```text
Continue with Milestone 4.

Integrate GPT-5.6 in two non-decorative structured roles.

Role A — checkpoint contract inference:

1. Implement CheckpointContract Pydantic models.
2. Input:
   - user natural-language objective;
   - hard rollback limit;
   - WorkloadCapabilities;
   - SaveRestoreSummary;
   - integrity protocol;
   - optional bounded sanitized source snippets.
3. Use the official OpenAI Python SDK, Responses API, model="gpt-5.6",
   structured parsing, and store=False.
4. Implement deterministic post-parse guardrails.
5. Implement live and labeled fixture providers.

Role B — failure diagnosis and bounded repair:

1. Implement FailureAnalysis, RepairPlan, and RepairAction schemas.
2. Input only the redacted structured failure artifact package.
3. Return root cause, affected checks, evidence IDs, confidence, risks,
   limitations, and allowlisted repair actions.
4. Implement live and labeled fixture providers.
5. Implement deterministic repair-plan validation:
   - action allowlist;
   - adapter capability check;
   - conflict check;
   - no arbitrary code, commands, paths, URLs, secrets, or tolerance changes.
6. Exactly one repair attempt.
7. Persist redacted request, parsed output, prompt/schema versions, provider,
   model alias, timestamp, and live-or-fixture label.
8. Never persist the API key.

If OPENAI_API_KEY is available, make one small real call for each role and save
the secret-free structured responses as demo fixtures. If it is unavailable,
complete and test the provider interfaces and clearly report the missing live
validation.

Do not connect the repair executor to a second crash yet.

Run mock SDK tests, fixture tests, invalid-output tests, guardrail tests, and
the repair-at-most-once test. Run quality gates, update docs, summarize, stop.
```

## Prompt 5 — bounded repair and second verification

```text
Continue with Milestone 5.

Connect the full reliability loop:

control
→ initial missing-training-state crash
→ new-process restore
→ failed Recovery Gate
→ GPT-5.6 failure analysis
→ repair-plan validation
→ deterministic repair executor
→ new repaired strategy
→ second real crash
→ new-process restore
→ final Recovery Gate

Requirements:

1. Never modify the failed checkpoint in place.
2. Apply only supported allowlisted actions through NativePyTorchAdapter.
3. Record accepted and rejected actions.
4. Run exactly one repair iteration.
5. Ensure the primary fixture diagnosis repairs optimizer, scheduler, and RNG
   persistence plus restore ordering where needed.
6. Verify the final run against the uninterrupted control.
7. Compare only passing safe-full and repaired safe-adapter-aware strategies.
8. Implement deterministic fallback to safe_full if the repair does not pass.
9. Generate result.json and report.md.
10. Implement:
    - flashpilot audit
    - flashpilot demo --provider fixture
    - flashpilot verify
    - flashpilot replay
11. Preserve real end-to-end artifacts.
12. Run the full fixture demo from a clean run directory.

Run quality gates, update docs and README, summarize, stop only when the complete
red-to-green workflow is reliable.
```

## Prompt 6 — product polish and judge packaging

```text
Continue with Milestone 6 only after all P0 behavior is green.

Implement the lowest-risk product polish:

1. Rich console sections and tables from the V4 plan.
2. A single self-contained report.html rendered only from result.json.
3. No server, frontend framework, or duplicated experiment logic.
4. flashpilot doctor.
5. One judge-ready command:
   flashpilot demo --provider fixture
6. Prebuilt wheel or GitHub Release artifact as the first packaging choice.
7. Clean-environment install and judge-path test.
8. Supported-platform documentation.
9. Live-versus-fixture documentation.
10. Makefile convenience commands.
11. Ensure no secrets or run artifacts are committed.

Do not add Hugging Face, Docker, policy planning, or extra chaos scenarios unless
the complete judge path is already clean and the remaining work is trivial.

Run the clean install, full judge path, quality gates, update docs, summarize,
and stop.
```

## Prompt 7 — optional stretch work

```text
Evaluate remaining time against the submission deadline.

Only if P0, P0.5, packaging, README, and the demo path are fully stable, choose
at most one stretch item:

A. a very small Hugging Face / PEFT adapter example;
B. a partial-write crash scenario;
C. previous-valid-checkpoint fallback after detected corruption;
D. a bounded optional policy planner.

Before implementing, explain:
- why the item improves the judging story;
- exact files to change;
- time estimate;
- rollback plan.

Implement only one item. Do not destabilize the primary demo.
Run gates, update docs, summarize, stop.
```

## Prompt 8 — final audit and submission package

```text
Perform the final audit.

Verify:

1. all lint and tests pass;
2. actual demo metrics are preserved;
3. no fabricated metrics;
4. no physical NAND, WAF, or SSD-lifetime claims;
5. live path uses GPT-5.6 structured outputs;
6. fixtures are labeled;
7. the crash is a real process termination;
8. restore is a new process;
9. the Recovery Gate is a hard deterministic gate;
10. missing-training-state is the primary repair demo;
11. corrupted payloads fail closed;
12. repair actions are typed and allowlisted;
13. repair loop is limited to one;
14. judge path needs no rebuild;
15. README explains concrete Codex contributions;
16. README explains both GPT-5.6 roles;
17. human decisions and prior art are documented;
18. installation, platforms, testing, and limitations are documented;
19. report.json, report.md, and report.html agree;
20. video script is under three minutes.

Create or finalize:

- docs/demo-script.md;
- docs/submission-checklist.md;
- Devpost category answer;
- Devpost project description;
- tagline;
- limitations;
- roadmap;
- release checklist.

Do not invent a /feedback Session ID. Remind me to run /feedback in this primary
thread after all final work is complete.

Stop with:
- final status;
- exact judge command;
- exact live command;
- known limitations;
- files ready for submission;
- remaining manual submission tasks.
```

---

# 30. Schedule

Absolute submission deadline:

```text
July 21, 2026 at 5:00 PM PDT
July 22, 2026 at 03:00 Riga
```

Use an internal deadline of July 21 at 20:00 Riga or earlier.

## July 16

- repository;
- primary Codex thread;
- API sanity test;
- Prompt 0;
- repeated control runs match.

## July 17

- Prompt 1;
- Prompt 2;
- real safe-full versus adapter-aware byte measurements.

## July 18

- Prompt 3;
- real kill and new-process restore;
- reliable Recovery Gate;
- tolerance decision.

Go/no-go:

If the gate is not reliable by the end of July 18:

- remove all stretch work;
- keep pure PyTorch;
- remove HTML temporarily;
- focus only on recovery correctness.

## July 19

- Prompt 4;
- live or fixture contract inference;
- live or fixture failure diagnosis;
- guardrails;
- fixtures.

## July 20

- Prompt 5;
- full red-to-green workflow;
- reporting;
- Prompt 6;
- feature freeze in the evening.

## July 21

- final audit;
- clean demo;
- video recording;
- YouTube upload;
- README polish;
- `/feedback`;
- Devpost submission.

Do not use the final overnight buffer as normal development time.

---

# 31. Cut rules

If behind schedule, remove in this order:

1. GPT report narrator;
2. numeric score or badge;
3. optional policy planner;
4. GitHub Actions;
5. Docker;
6. Hugging Face / PEFT example;
7. third crash point;
8. partial-write scenario;
9. HTML report, only if the core is still at risk.

Never cut:

- uninterrupted control;
- valid incomplete checkpoint;
- real process kill;
- new-process restore;
- deterministic Recovery Gate;
- GPT contract inference;
- GPT failure diagnosis;
- typed bounded repair;
- one repair iteration;
- second crash and restore;
- measured checkpoint bytes;
- fixture mode;
- judge command.

---

# 32. Three-minute demo outline

## 0:00–0:18 — hook

> A checkpoint can load successfully and still be unsafe for resuming training. Missing optimizer, scheduler, or random state can silently change the training trajectory after a crash.

Show FlashPilot title and natural-language objective.

## 0:18–0:35 — contract

Show GPT-5.6 contract summary:

```text
Required:
adapter
optimizer
scheduler
global step
Python / NumPy / Torch RNG
manifest
checksums
atomic commit
```

## 0:35–0:58 — first real crash

Show:

- worker PID;
- checkpoint committed;
- parent kill;
- new process PID;
- restore attempt.

## 0:58–1:20 — red gate

Show:

```text
Checkpoint integrity   PASS
Adapter state          PASS
Optimizer              FAIL
Scheduler              FAIL
RNG                    FAIL
Trajectory             FAIL
```

## 1:20–1:47 — GPT diagnosis

Show:

- root cause;
- evidence IDs;
- confidence;
- allowlisted repair actions;
- note that GPT cannot execute commands or declare success.

## 1:47–2:10 — repair and second crash

Show:

- accepted actions;
- new repaired strategy;
- second kill;
- new-process restore.

## 2:10–2:30 — green gate

Show all mandatory applicable checks passing against control.

## 2:30–2:45 — storage impact

Show measured safe strategies:

```text
Safe full checkpoint:         X MB
Safe adapter-aware:           Y MB
Logical byte reduction:       Z%
Recovery verified:            yes
```

## 2:45–3:00 — Codex and close

> Codex helped build the workload adapter, atomic checkpoint protocol, crash orchestrator, Recovery Gate, tests, and packaging. GPT-5.6 inferred recovery requirements and diagnosed the observed failure. Deterministic code independently verified every repair.

Close:

> Reduce checkpoint writes only when recovery is proven.

Show disclaimer:

```text
Physical NAND wear and SSD lifetime were not measured.
```

---

# 33. Devpost text

## Category answer

> **Developer Tools.** FlashPilot is an AI checkpoint reliability and storage autopilot for PyTorch training. It deliberately kills a training process, restores the run in a new process, and verifies the resumed state against an uninterrupted control. GPT-5.6 infers checkpoint recovery requirements and diagnoses real recovery failures from structured code and runtime evidence, while a bounded repair executor applies only supported actions and reruns the crash test. FlashPilot reports storage savings only after the repaired checkpoint passes the deterministic Recovery Gate.

## Short description

> FlashPilot crash-tests AI training checkpoints, uses GPT-5.6 to diagnose failed recovery and propose bounded repairs, verifies the repair against an uninterrupted control, and then measures safe reductions in checkpoint writes.

## Tagline

> **Reduce checkpoint writes only when recovery is proven.**

---

# 34. Risk register

## Risk 1 — cross-process reproducibility

Mitigation:

- CPU-only;
- fixed thread count;
- fixed seeds;
- deterministic algorithms;
- step-derived batches;
- restored RNG;
- fixed evaluation;
- explicit tolerance policy.

## Risk 2 — GPT appears decorative

Mitigation:

- contract inference from workload and save/restore behavior;
- real failure artifacts;
- evidence-linked diagnosis;
- typed repair plan;
- red-to-green verified result;
- no dependence on prose for acceptance.

## Risk 3 — failure appears staged

Mitigation:

- label it as a deliberate deterministic fixture;
- ensure the checkpoint is checksum-valid and loadable;
- show actual divergence;
- use the same gate for both failed and repaired runs;
- show raw evidence in artifacts.

## Risk 4 — scope expands to arbitrary repositories

Mitigation:

- explicit adapter boundary;
- P0 only Native PyTorch;
- unsupported workloads clearly reported;
- no arbitrary command execution.

## Risk 5 — time

Mitigation:

- no frontend framework;
- no downloads;
- no distributed support;
- feature freeze;
- strict cut order;
- one repair iteration.

## Risk 6 — atomic behavior differs by platform

Mitigation:

- Linux primary;
- macOS tested where possible;
- Windows documented as experimental unless verified;
- best-effort fsync note;
- never overclaim durability.

## Risk 7 — API access

Mitigation:

- test early;
- keep calls small;
- fixture/replay path;
- no API key required for judge demo.

---

# 35. Final engineering principle

The strongest submission is not:

> FlashPilot makes SSDs live longer.

It is:

```text
The checkpoint was loadable.
The process was really killed.
A new process restored it.
Recovery initially diverged.
GPT-5.6 diagnosed why.
A bounded repair was applied.
The process was killed again.
The repaired run matched the uninterrupted control.
Only then were storage savings reported.
```

Build the proof first.

---

# 36. References

## Official hackathon

- OpenAI Build Week overview:  
  https://openai.devpost.com/
- Official rules:  
  https://openai.devpost.com/rules
- FAQ:  
  https://openai.devpost.com/details/faqs
- Dates:  
  https://openai.devpost.com/details/dates

## OpenAI API

- Models:  
  https://developers.openai.com/api/docs/models
- GPT-5.6 Sol / `gpt-5.6` alias:  
  https://developers.openai.com/api/docs/models/gpt-5.6-sol
- Structured outputs:  
  https://developers.openai.com/api/docs/guides/structured-outputs

## Adjacent research

- CheckFreq, FAST 2021:  
  https://www.usenix.org/conference/fast21/presentation/mohan
- Check-N-Run, NSDI 2022:  
  https://www.usenix.org/conference/nsdi22/presentation/eisenman
- OPT-175B logbook:  
  https://arxiv.org/abs/2205.01068
- MegaScale:  
  https://arxiv.org/abs/2402.15627
- REO:  
  https://doi.org/10.3390/electronics14040738
- MiDAS, FAST 2024:  
  https://www.usenix.org/conference/fast24/presentation/oh

---

# 37. Final instruction to Codex

When this plan conflicts with an implementation shortcut, prefer:

1. deterministic evidence;
2. recovery correctness;
3. safety;
4. reproducibility;
5. honest reporting;
6. a finished narrow product;
7. only then additional features.

After every milestone, stop and report:

- files changed;
- commands executed;
- actual test results;
- acceptance criteria status;
- unresolved risks;
- the next smallest milestone.
