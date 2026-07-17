# Research and prior art

This is a positioning scaffold, not an implementation backlog. FlashPilot does
not claim that checkpoint scheduling, adapter-only persistence, compression,
incremental checkpoints, atomic writes, checksums, or chaos testing are novel.
Its intended contribution is the integrated developer workflow that tests
continuation correctness, uses GPT-5.6 for evidence-bounded diagnosis, applies a
typed bounded repair, re-verifies deterministically, and reports logical storage
impact only after recovery passes.

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
