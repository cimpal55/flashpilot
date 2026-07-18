# FlashPilot demo script

This English voiceover is designed for the installed judge path and is 372
spoken words, excluding headings, timecodes, and on-screen directions. At 130
words per minute it takes about 2 minutes 52 seconds.

## 0:00-0:20 - Hook and contract

**On screen:** Run `flashpilot doctor`, then `flashpilot demo --provider fixture`.

**Voiceover:** A checkpoint can be checksum-valid and loadable, yet still be
unsafe for resuming training. FlashPilot is a checkpoint recovery qualification
and verification harness. GPT-5.6 first inferred that this workload requires the
adapter, optimizer, scheduler, global step, Python, NumPy, and Torch random state,
plus manifest, checksums, and atomic commit.

## 0:20-0:50 - Valid incomplete checkpoint and real crash

**On screen:** Show the control, initial checkpoint, worker PID, termination,
and recovery PID.

**Voiceover:** FlashPilot completes an uninterrupted CPU control. It then writes
an intentionally incomplete checkpoint. The file is valid, checksummed, and
loadable, but it omits training continuation state. After the atomic commit, the
parent really terminates the worker. Recovery starts in a distinct new process;
this is not an in-process exception or simulated restart.

## 0:50-1:20 - Red Recovery Gate

**On screen:** Show the failed individual checks.

**Voiceover:** Loadability is not the verdict. The deterministic Recovery Gate
passes integrity, adapter state, global step, process recovery, and rollback,
but fails optimizer, scheduler, Python, NumPy, and Torch random state. Continued
training then diverges from the control in trainable parameters, evaluation, and
loss history. Nine exact checks fail.

## 1:20-1:50 - Blind GPT-5.6 diagnosis and guardrails

**On screen:** Show the GPT source label and action decision table.

**Voiceover:** The response shown is a captured live GPT-5.6 structured response,
replayed offline for judges. GPT did not receive the failure-injection label,
expected diagnosis, repair preset, tensors, samples, secrets, or absolute paths.
It received only sanitized manifest, restore, failed-gate, and trajectory
evidence. GPT proposed typed actions. Deterministic guardrails accepted exactly
six native actions and rejected the unsupported strategy-change action from
execution.

## 1:50-2:20 - One bounded repair and second crash

**On screen:** Show attempt one, the new strategy ID, second worker PID, and new
recovery PID.

**Voiceover:** FlashPilot copies a six-boolean strategy configuration into a new
isolated run. It never edits the failed checkpoint, and it permits exactly one
repair attempt. The repaired worker commits, the parent performs a second real
termination, and another distinct process restores before the next batch.

## 2:20-2:43 - Green Gate and measured result

**On screen:** Show `VERIFIED`, 24 of 24, and the storage table.

**Voiceover:** The same Recovery Gate now passes all 24 checks with exact
comparison: zero absolute and relative tolerance. Only now does FlashPilot report
storage impact. The safe-full recurring checkpoint used 126,218 logical bytes.
The repaired recurring checkpoint used 32,743, a reduction of 93,475 bytes, or
74.06 percent. The 93,987-byte frozen base is a separate one-time cost.

## 2:43-2:55 - Close and limitations

**On screen:** Show `result.json`, `report.md`, and `report.html`.

**Voiceover:** Codex implemented the workload, atomic protocol, crash
orchestration, deterministic gate, bounded repair, tests, reports, and packaging.
GPT-5.6 inferred requirements and diagnosed evidence; it never declared success.
This MVP supports one controlled CPU PyTorch adapter. Windows directory fsync is
best-effort. Physical NAND writes, write amplification, and SSD lifetime were not
measured. Reduce checkpoint writes only when recovery is proven.
