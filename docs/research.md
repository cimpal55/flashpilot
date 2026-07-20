# Research and prior art

This is a positioning scaffold, not an implementation backlog. FlashPilot does
not claim that checkpoint scheduling, adapter-only persistence, compression,
incremental checkpoints, atomic writes, checksums, or chaos testing are novel.
Its intended contribution is the integrated developer workflow that tests
continuation correctness, uses GPT-5.6 for evidence-bounded diagnosis, applies a
typed bounded repair, re-verifies deterministically, and reports logical storage
impact only after recovery passes.

Prompt 8 rechecked the linked primary paper or official conference page on
2026-07-18. The descriptions below remain deliberately limited to each source's
stated problem and to FlashPilot's narrower implemented boundary.

## Prior-art table required by the V4.1 override

| Work | What it solves | How FlashPilot differs |
| --- | --- | --- |
| [CheckFreq](https://www.usenix.org/conference/fast21/presentation/mohan) | Profiles DNN training and chooses fine-grained checkpoint frequency to balance overhead and lost work. | FlashPilot does not implement frequency optimization in P0; it tests whether a supported checkpoint actually enables correct continuation. |
| [Check-N-Run](https://www.usenix.org/conference/nsdi22/presentation/eisenman) | Uses differential checkpointing and quantization for large recommendation-model checkpoints. | FlashPilot neither reimplements those techniques nor claims them as novel; it verifies controlled recovery semantics and bounded repair. |
| [ExCP](https://arxiv.org/abs/2406.11257) | Compresses LLM training checkpoints using adjacent residuals, weight-momentum shrinking, and quantization. | FlashPilot P0 measures logical bytes for two explicit safe strategies and adds no generic compression system. |
| [Amber](https://dblp.org/rec/conf/icpp/WangZZY00X25) | Explores fast, space-efficient incremental checkpointing for LLM training. | FlashPilot focuses on auditable crash/restore correctness for one small native-PyTorch workload rather than incremental-checkpoint performance at scale. |
| [IncrCP](https://www.vldb.org/pvldb/vol18/p1049-du.pdf) | Records and organizes changed recommendation-model parameters for incremental checkpoints and faster recovery. | FlashPilot does not implement incremental chunks; it verifies required training state and trajectory against an uninterrupted control. |
| [OPT-175B logbook](https://arxiv.org/abs/2205.01068) | Documents the operational experience and failures encountered while training OPT. | FlashPilot turns the checkpoint-recovery concern into a local reproducible developer test; it does not emulate OPT scale. |
| [MegaScale](https://arxiv.org/abs/2402.15627) | Co-designs large-scale LLM training efficiency, observability, stability, and fault tolerance above 10,000 GPUs. | FlashPilot is intentionally CPU-only and single-workload in P0, emphasizing observable recovery evidence rather than distributed-scale throughput. |
| [FlashRecovery](https://arxiv.org/abs/2509.03047) | Targets fast detection, scale-independent restart, and checkpoint-free one-step recovery for large LLM clusters. | FlashPilot uses persisted checkpoints and cross-process comparison; it does not implement checkpoint-free or cluster recovery. |
| [REO](https://doi.org/10.3390/electronics14040738) | Dynamically adjusts NAND erase latency and voltage to improve device lifetime and performance. | FlashPilot has no device or firmware control and makes no physical NAND-lifetime claim. |
| [MiDAS](https://www.usenix.org/conference/fast24/presentation/oh) | Reduces write amplification in log-structured systems through adaptive grouping and hot-data isolation. | FlashPilot operates at application-level logical checkpoint writes and does not measure or control write amplification. |
| [FDP / WARP](https://www.usenix.org/conference/fast26/presentation/song) | Studies Flexible Data Placement SSD behavior and provides an emulator for placement and write-amplification research. | FlashPilot neither targets FDP devices nor emulates SSD firmware; FDP/WARP remains roadmap context only. |
| [ZipLLM](https://arxiv.org/abs/2505.06252) | Combines model-family clustering, tensor deduplication, and lossless delta compression for model-hub storage. | FlashPilot compares training checkpoint writes inside one verified run and does not implement model-family deduplication or hub storage. |

## Verified impact framing

Use only this exact statement unless later primary-source verification supports a
change:

> During OPT-175B training on 992 A100 GPUs, hardware failures caused at least
> 35 manual restarts and an estimated 70-plus automatic restarts over two
> months.

Expected loss of half a checkpoint interval is a mathematical uniform-failure
approximation, not an OPT measurement. Do not use the “678 interruptions at 32K
GPUs” figure in narration without verification against the complete
FlashRecovery paper.

## Research categories for later documentation

1. Checkpoint scheduling: CheckFreq and related interval-selection work.
2. Differential and incremental checkpoints: Check-N-Run, ExCP, Amber, and IncrCP.
3. Recovery and large-scale failures: OPT, MegaScale, and FlashRecovery.
4. Application-level write reduction: adapter-aware state selection and honest logical-byte measurement.
5. SSD-level roadmap only: REO, MiDAS, FDP/WARP, and related device research.

## Adapter-aware checkpoint positioning

Saving only trainable adapter weights while retaining an immutable frozen base
is treated here as established parameter-efficient training practice, not a
FlashPilot invention. Prompt 2's narrower engineering contribution is the
explicit continuation contract around that structure: the recurring safe
checkpoint also carries optimizer, scheduler, global step, and relevant RNG
state; it binds the external base by identity and SHA-256; and direct restore is
compared with the uninterrupted control.

The measured recurring-byte difference is a structural result for this one
controlled model and serialization format. The immutable base is counted
separately and included in first-write cost. No general compression, physical
device savings, SSD lifetime improvement, or recovery verdict is inferred.

## PyTorch Lightning checkpoint contract

The V0.3 adapter follows Lightning's documented native behavior rather than
claiming a new checkpoint format. Full checkpoints are documented to include
model, optimizer, scheduler, callback/data-module, hyperparameter, and loop
state, and training resumes through `Trainer.fit(..., ckpt_path=...)`.
Lightning also documents `save_weights_only=True` as a weights-only mode. The
FlashPilot qualification adds a small workload-owned, JSON-safe RNG/history
bridge because exact stochastic continuation is stricter than merely loading
model weights. Sources: [Lightning checkpoint contents and resume](https://lightning.ai/docs/pytorch/stable/common/checkpointing_basic.html),
[Lightning checkpoint saving options](https://lightning.ai/docs/pytorch/stable/common/checkpointing_intermediate.html).

## Checkpoint conversion equivalence positioning

Hugging Face PEFT documents that an adapter checkpoint contains adapter
parameters and configuration rather than the base model, and that merging
folds adapter weights into the base model. FlashPilot's V0.3 fixture follows
that structural idea with a controlled local rank-2 linear delta, but it does
not claim to emit or consume arbitrary Hugging Face PEFT repositories. Sources:
[PEFT checkpoint format](https://huggingface.co/docs/peft/main/developer_guides/checkpoint),
[PEFT tuner merge API](https://huggingface.co/docs/peft/en/package_reference/tuners).

PyTorch Distributed Checkpoint documents state-dict loading across different
cluster topologies and notes that distributed loading requires an initialized
process group. FlashPilot's sharded fixture is intentionally smaller: two
local, checksummed CPU tensor files plus a strict index are consolidated and
compared exactly. It is not an implementation or qualification of PyTorch DCP.
Source: [PyTorch Distributed Checkpoint](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html).

The version-upgrade fixture tests a FlashPilot-owned schema transition. Its
strong claim is continuation equivalence for the deterministic CI workload in
a separate process, not universal forward/backward compatibility for external
checkpoint formats.

## Partial-write fuzzing positioning

FlashPilot does not claim atomic writes, checksums, completion markers, or chaos
testing as novel. The V0.3 contribution is a reproducible qualification surface
that binds these mechanisms into one typed verdict: five independently faulted
artifacts must produce exact rejection categories, and a prematurely visible
reordered-write sequence must never validate before its full inventory exists.

The matrix is deliberately deterministic so two invocations can be compared
byte for byte. It does not model storage-controller persistence, network
filesystem semantics, distributed process coordination, or probabilistic crash
timing. Those boundaries prevent a local Windows CPU result from being
presented as general crash-consistency certification.

## Previous-valid fallback positioning

Selecting the most recent valid checkpoint is established recovery practice,
not a novel FlashPilot algorithm. The V0.3 qualification contribution is the
evidence chain around that choice: a newer committed artifact is shown to be
checksum-invalid, the candidate inventory and exact selected predecessor are
recorded, and resumed stochastic training is compared with an uninterrupted
control under the same Recovery Gate used by the native crash workflow.

The fixed test models one post-commit corruption and a two-step rollback on the
local CPU workload. It does not establish a general retention policy, repair
corrupt data, assess remote/object-store consistency, or characterize the
probability and timing of failures.

## Repeated randomized fault-timing positioning

Randomized fault injection and repeated recovery trials are established chaos
and resilience-testing practices, not a novel FlashPilot algorithm. The V0.3
contribution is the narrow evidence contract around the existing deterministic
native experiment: a recorded seed creates a reproducible completed-step
schedule, RPO 0 through 3 is covered by construction, and every real
termination must independently pass the same exact Recovery Gate.

The qualification binds every complete trial directory and its underlying
result to the aggregate, so schedule reproducibility cannot stand in for
recovery proof. It measures recovery-process duration and achieved completed-
step rollback for this fixed local CPU workload. It does not characterize a
failure probability distribution, mid-instruction crashes, distributed
coordination, network filesystems, physical persistence, or general recovery
time objectives.
